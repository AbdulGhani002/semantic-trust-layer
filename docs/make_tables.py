"""Turn the result files into LaTeX table rows, so no number is typed by hand."""
import csv
import json
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "docs" / "generated"
OUT.mkdir(exist_ok=True)


def load(name):
    path = RESULTS / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def pct(value, places=1):
    return "--" if value is None else f"{100 * value:.{places}f}\\%"


def num(value, places=3):
    return "--" if value is None else f"{value:.{places}f}"


def count(value):
    return f"{value:,}"


def save(name, lines):
    (OUT / f"{name}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def text_tables(data, macros):
    names = {
        ("abuse_civil", "threat"): "Civil Comments, threat",
        ("abuse_civil", "hate"): "Civil Comments, hate",
        ("abuse_civil", "abuse"): "Civil Comments, abuse",
        ("hate_unseen_source", "hate"): "Hate, unseen source",
        ("fraud_email_unseen_source", "fraud"): "Fraud email, unseen source",
        ("sms_unseen", "fraud"): "SMS, unseen messages",
        ("roman_urdu", "abuse"): "Roman Urdu, abuse",
    }
    rows = []
    for (test, label), name in names.items():
        systems = data["datasets"][test]["labels"][label]
        k, l, t = systems["keyword_filter"], systems["linear_tfidf"], systems["transformer"]
        best = max(k["f1"], l["f1"], t["f1"])
        mark = lambda score: f"\\textbf{{{num(score, 2)}}}" if score == best else num(score, 2)
        rows.append(
            f"{name} & {count(t['positives'])} / {count(t['rows'])} & {mark(k['f1'])} & {mark(l['f1'])} & {mark(t['f1'])} & "
            f"{pct(k['false_alarm_rate'])} & {pct(l['false_alarm_rate'])} & {pct(t['false_alarm_rate'])} \\\\"
        )
    save("text_rows", rows)
    threat = data["datasets"]["abuse_civil"]["labels"]["threat"]["transformer"]
    hate = data["datasets"]["hate_unseen_source"]["labels"]["hate"]
    urdu = data["datasets"]["roman_urdu"]["labels"]["abuse"]
    macros.update(
        textThreatFone=num(threat["f1"], 2), textThreatBad=count(threat["positives"]), textThreatRows=count(threat["rows"]),
        hateUnseenRecall=pct(hate["transformer"]["recall"], 0), hateUnseenFA=pct(hate["transformer"]["false_alarm_rate"]), hateUnseenLinearFA=pct(hate["linear_tfidf"]["false_alarm_rate"]),
        urduFA=pct(urdu["transformer"]["false_alarm_rate"]), urduLinearFA=pct(urdu["linear_tfidf"]["false_alarm_rate"]),
    )
    speed = data["datasets"]["abuse_civil"]["ms_per_item"]
    macros["msPerText"] = f"{speed:.1f}"
    clear_tables(data, macros)
    s = data.get("semantic_test")
    if s:
        groups = [
            ("all", "All 57 messages"),
            ("no_obvious_keyword", "No obvious keyword"),
            ("language_en", "English"),
            ("language_ru", "Roman Urdu"),
            ("language_ur", "Urdu script"),
        ]
        rows = []
        for key, name in groups:
            row = s[key]
            cell = lambda system: f"{row[system]['caught']} & {row[system]['false_alarms']}"
            rows.append(f"{name} & {cell('keyword')} & {cell('transformer')} & {cell('combined')} \\\\")
        save("semantic_rows", rows)
        macros.update(
            handKeyword=s["all"]["keyword"]["caught"], handFast=s["all"]["transformer"]["caught"], handBoth=s["all"]["combined"]["caught"], handBothWrong=s["all"]["combined"]["false_alarms"],
            plainKeyword=s["no_obvious_keyword"]["keyword"]["caught"], plainFast=s["no_obvious_keyword"]["transformer"]["caught"], plainBoth=s["no_obvious_keyword"]["combined"]["caught"],
        )
        macros["reviewSeconds"] = f"{s['median_review_seconds']:.1f}"
        macros["reviewedItems"] = str(s["reviewed_items"])
        rows = [f"{row['gate']} & {row['caught']} & {row['false_alarms']} & {pct(row['normal_mail_read'], 0)} & {pct(row['normal_comments_read'], 0)} \\\\" for row in s["gates"]]
        save("gate_rows", rows)
        by_gate = {row["gate"]: row for row in s["gates"]}
        macros.update(
            gateZeroCaught=by_gate[0.0]["caught"], gateZeroWrong=by_gate[0.0]["false_alarms"], gateHighCaught=by_gate[0.08]["caught"], gateHighWrong=by_gate[0.08]["false_alarms"],
            gateHighMail=pct(by_gate[0.08]["normal_mail_read"], 0), gateHighComments=pct(by_gate[0.08]["normal_comments_read"], 0),
        )
    sample = data.get("held_out_sample")
    if sample and sample.get("rows"):
        rows = []
        for row in sample["rows"]:
            size = row["size_each"]
            rows.append(f"{row['name']} & {row['fast_caught']}/{size} & {row['both_caught']}/{size} & {row['fast_wrong']}/{size} & {row['both_wrong']}/{size} \\\\")
        save("sample_rows", rows)
        macros["sampleSeconds"] = f"{sum(row['seconds_each'] for row in sample['rows']) / len(sample['rows']):.1f}"
        total = sum(row["size_each"] for row in sample["rows"])
        share = lambda key: pct(sum(row[key] for row in sample["rows"]) / total)
        macros.update(
            sampleSize=count(total), sampleFastCaught=share("fast_caught"), sampleBothCaught=share("both_caught"),
            sampleFastWrong=share("fast_wrong"), sampleBothWrong=share("both_wrong"),
        )
        names = {"Threat, Civil Comments": "Threat", "Abuse, Civil Comments": "Abuse", "Hate, unseen source": "HateNew", "Fraud email, unseen source": "Fraud", "Abuse, Roman Urdu": "Urdu"}
        for row in sample["rows"]:
            short = names.get(row["name"])
            if short:
                macros.update({f"sample{short}Fast": row["fast_caught"], f"sample{short}Both": row["both_caught"], f"sample{short}FastWrong": row["fast_wrong"], f"sample{short}BothWrong": row["both_wrong"]})
        macros["sampleEach"] = sample["rows"][0]["size_each"]


def clear_tables(data, macros):
    clear = data.get("clear_comments")
    if clear:
        low, high = wilson(clear["both_flagged"], clear["size"])
        macros.update(
            clearSize=str(clear["size"]), clearFast=pct(clear["fast_flagged"] / clear["size"]), clearBoth=pct(clear["both_flagged"] / clear["size"]),
            clearLow=pct(low), clearHigh=pct(high), clearShare=pct(clear["share_of_test"], 0),
        )


def link_tables(data, macros):
    h = data["held_out_domains"]
    f = data["fixture_links"]
    q = data["fixture_qr"]
    o = data["openphish_unseen_domains"]
    fresh = data.get("openphish_after_training", {})
    rows = [
        f"Held-out domains & {count(h['rows'])} links & P {pct(h['precision'])}, R {pct(h['recall'])}, FA {pct(h['false_alarm_rate'])} \\\\",
        f"OpenPhish, unseen domains & {count(o['rows'])} links & R {pct(o['recall'])} \\\\",
    ]
    if fresh.get("rows"):
        rows.append(f"OpenPhish, after training & {count(fresh['rows'])} links & R {pct(fresh['recall'])} \\\\")
        macros["linkOpenphishLater"] = pct(fresh["recall"], 2)
    sample = data.get("language_model_sample")
    before = json.loads((RESULTS / "second_run" / "links.json").read_text(encoding="utf-8"))
    old_sample, old_fixture = before["language_model_sample"], before["fixture_links"]
    if sample:
        size = sample["size_each"]
        rows.append(f"Real links, link model & {2 * size} links & Caught {sample['fast_caught']}/{size}, false alarms {sample['fast_wrong']}/{size} \\\\")
        rows.append(f"Real links, content rule & {2 * size} links & Caught {old_sample['both_caught']}/{size}, false alarms {old_sample['both_wrong']}/{size} \\\\")
        rows.append(f"Real links, final rule & {2 * size} links & Caught {sample['both_caught']}/{size}, false alarms {sample['both_wrong']}/{size} \\\\")
        macros.update(
            linkSampleEach=str(size), linkSampleCaught=str(old_sample["both_caught"]), linkSampleWrong=str(old_sample["both_wrong"]), linkSampleFastCaught=str(sample["fast_caught"]), linkSampleFastWrong=str(sample["fast_wrong"]),
            linkFinalCaught=str(sample["both_caught"]), linkFinalWrong=str(sample["both_wrong"]),
        )
    rows.append(f"Fake links, link model & 66 links & Caught {f['fraud_caught']}, false alarms {f['normal_false_alarms']} \\\\")
    rows.append(f"Fake links, content rule & 66 links & Caught {old_fixture['with_language_model_caught']}, false alarms {old_fixture['with_language_model_false_alarms']} \\\\")
    if "with_language_model_caught" in f:
        rows.append(f"Fake links, final rule & 66 links & Caught {f['with_language_model_caught']}, false alarms {f['with_language_model_false_alarms']} \\\\")
    macros.update(
        fakeLinkCaught=f["fraud_caught"], fakeLinkWrong=f["normal_false_alarms"], fakeOldCaught=old_fixture["with_language_model_caught"], fakeOldWrong=old_fixture["with_language_model_false_alarms"],
        fakeFinalCaught=f.get("with_language_model_caught", "--"), fakeFinalWrong=f.get("with_language_model_false_alarms", "--"),
    )
    rows.append(f"QR images & {q['images']} images & Read {q['read_correctly']}, right verdict {q['verdict_correct']} \\\\")
    save("link_rows", rows)
    macros.update(
        linkRows=count(h["rows"]), linkPrecision=pct(h["precision"], 2), linkRecall=pct(h["recall"], 2), linkFalseAlarm=pct(h["false_alarm_rate"], 2), linkFone=num(h["f1"], 4),
        linkAP=num(h["average_precision"], 4), linkOpenphish=pct(o["recall"], 2), linkMs=f"{data['ms_per_1000_links'] / 1000:.2f}",
        qrRead=str(q["read_correctly"]), qrRight=str(q["verdict_correct"]), qrImages=str(q["images"]), qrMs=f"{q['ms_per_image']:.1f}",
        qrWrong=str(q["images"] - q["verdict_correct"]), qrWrongCodes={1: "one", 2: "two", 3: "three"}.get(len(q["wrong_clean_codes"]), str(len(q["wrong_clean_codes"]))),
    )
    source = data["by_source"]
    macros["linkTrancoFA"] = pct(source["tranco_normal"]["flagged"], 2)
    macros["linkCrawlFA"] = pct(source["common_crawl_normal"]["flagged"], 2)


def link_rule_tables(data, macros):
    """Which rule judges a bare link, chosen on validation links."""
    names = (("Link model alone", "Link model alone"), ("Same rule as content", "Same rule as content"), ("Language model only clears", "\\textbf{Final rule}"))
    rows = []
    for key, name in names:
        cell = lambda group: f"{data['rules'][key][group]['flagged']} / {data['rules'][key][group]['warned_or_more']}"
        rows.append(f"{name} & {cell('phishing')} & {cell('normal')} & {cell('popular_normal')} \\\\")
    save("link_rule_rows", rows)
    sizes = data["rows"]
    content, final = data["rules"]["Same rule as content"], data["rules"]["Language model only clears"]
    macros.update(
        ruleEach=sizes["normal"], rulePopular=sizes["popular_normal"], ruleContentNormal=content["normal"]["flagged"], ruleFinalNormal=final["normal"]["flagged"],
        ruleContentPopular=content["popular_normal"]["flagged"], ruleFinalPopular=final["popular_normal"]["flagged"],
    )


def flow_tables(data, anomaly, macros):
    def row(name, tests, key):
        t, l = tests[key]["flow_transformer"], tests[key]["lightgbm_single_flow"]
        return (
            f"{name} & {num(t['f1'], 3)} & {pct(t['false_alarm_rate'], 2)} & {num(t.get('auc'), 3)} & "
            f"{num(l['f1'], 3)} & {pct(l['false_alarm_rate'], 2)} & {num(l.get('auc'), 3)} \\\\"
        )

    unseen = data["cic_unseen_attack_days"]["tests"]
    later = data["cic_seen_attacks_later_time"]["tests"]
    ctu = data["ctu_leave_scenarios_out"]["tests"]
    rows = [row("CIC Thursday, attacks never taught", unseen, "thursday"), row("CIC Friday, attacks never taught", unseen, "friday"), row("CIC later flows, attacks taught", later, "later_flows_all_days")]
    rows += [row(f"CTU-13 scenario {key.split('_')[1]}, held out", ctu, key) for key in sorted(ctu, key=lambda k: int(k.split("_")[1]))]
    save("flow_rows", rows)
    final = data["final_both_datasets"]["tests"]
    macros.update(
        finalLater=num(final["cic_later_flows"]["flow_transformer"]["f1"], 3),
        thursdayFone=num(unseen["thursday"]["flow_transformer"]["f1"], 3),
        fridayFone=num(unseen["friday"]["flow_transformer"]["f1"], 3),
        laterFone=num(later["later_flows_all_days"]["flow_transformer"]["f1"], 4),
        laterFA=pct(later["later_flows_all_days"]["flow_transformer"]["false_alarm_rate"], 3),
    )
    rows = []
    for key, name in (("thursday", "Thursday"), ("friday", "Friday")):
        a = anomaly["tests"][key]
        rows.append(f"{name} & {pct(a['recall'], 2)} & {pct(a['false_alarm_rate'], 2)} & {num(a['auc'], 4)} & {pct(a['recall_at_0.001_false_alarms'], 1)} \\\\")
    both = anomaly["both_models_later_flows"]
    for key, name in (("known_attack_model", "Later flows, known-attack model"), ("normal_behaviour_model", "Later flows, normal-behaviour model"), ("either_model", "Later flows, either model")):
        a = both[key]
        rows.append(f"{name} & {pct(a['recall'], 2)} & {pct(a['false_alarm_rate'], 2)} & {num(a['auc'], 4)} & -- \\\\")
    save("anomaly_rows", rows)
    macros.update(
        thursdayRecall=pct(anomaly["tests"]["thursday"]["recall"], 2), thursdayFA=pct(anomaly["tests"]["thursday"]["false_alarm_rate"], 2),
        fridayRecall=pct(anomaly["tests"]["friday"]["recall"], 2), fridayFA=pct(anomaly["tests"]["friday"]["false_alarm_rate"], 2),
        eitherRecall=pct(both["either_model"]["recall"], 2), eitherFA=pct(both["either_model"]["false_alarm_rate"], 2),
        thursdayRecallLow=pct(anomaly["tests"]["thursday"]["recall_at_0.001_false_alarms"], 1), fridayRecallLow=pct(anomaly["tests"]["friday"]["recall_at_0.001_false_alarms"], 1),
        botnetRecall=pct(anomaly["tests"]["friday"]["recall_by_attack"]["Botnet"], 1),
    )


def cross_tables(data, macros):
    known = [row["known_attack_model"]["recall"] for row in data.values()]
    alarms = [row["normal_behaviour_model"]["false_alarm_rate"] for row in data.values()]
    macros.update(crossRecallLow=pct(min(known)), crossRecallHigh=pct(max(known)), crossFALow=pct(min(alarms), 0), crossFAHigh=pct(max(alarms), 0))


def backbone_tables(data, macros):
    t = data["trained_on_this_traffic"]
    macros.update(
        backboneFlows=count(data["flows_read"]), backboneHosts=count(data["hosts_seen"]), backboneScored=count(data["flows_scored"]), backboneScoredHosts=count(data["hosts_scored"]),
        backboneKnown=pct(data["known_attack_alert_rate"], 2), backboneLab=pct(data["normal_behaviour_alert_rate"], 1),
        backboneLocal=pct(t["alert_rate_on_other_hosts"], 3), backboneSpeed=count(data["score_flows_per_second_cpu"]),
    )


def review_tables(data, macros):
    rows = [f"{row['name']} & {row['fraud_caught']} & {row['normal_flagged']} \\\\" for row in data["link_opinion"]["conditions"]]
    save("opinion_rows", rows)
    none, right, wrong = data["link_opinion"]["conditions"]
    macros.update(
        opinionNoneCaught=none["fraud_caught"], opinionNoneWrong=none["normal_flagged"], opinionRightCaught=right["fraud_caught"], opinionRightWrong=right["normal_flagged"],
        opinionBadCaught=wrong["fraud_caught"], opinionBadWrong=wrong["normal_flagged"],
    )
    if "network_note" in data:
        n = data["network_note"]
        macros.update(
            noteHarmless=str(n["harmless"]), noteHarmful=str(n["harmful"]), noteAloneFlagged=str(n["harmless_flagged_alone"]), noteWithFlagged=str(n["harmless_flagged_with_note"]),
            noteAloneCaught=str(n["harmful_caught_alone"]), noteWithCaught=str(n["harmful_caught_with_note"]),
        )
    if "disguise" in data:
        rows = [f"{row['name']} & {row['keyword']} & {row['transformer']} & {row['combined']} & {row['combined_wrong']} \\\\" for row in data["disguise"]["rows"]]
        save("disguise_rows", rows)
        disguise = {row["name"]: row for row in data["disguise"]["rows"]}
        leet, long_text, order = disguise["Letters swapped for symbols"], disguise["Hidden inside a long normal text"], disguise["An instruction to the reviewer"]
        plain = disguise["No disguise"]
        macros.update(
            plainDisguiseFast=plain["transformer"], plainDisguiseBoth=plain["combined"], leetKeyword=leet["keyword"], leetFast=leet["transformer"], leetFastWrong=leet["transformer_wrong"], leetBothWrong=leet["combined_wrong"],
            longBoth=long_text["combined"], longBothWrong=long_text["combined_wrong"], orderBoth=order["combined"], orderBothWrong=order["combined_wrong"],
            disguiseCount=data["disguise"]["messages"], disguiseHarmless=data["disguise"]["harmless"],
        )
    if "injection" in data:
        i = data["injection"]
        rows = []
        keys = ("language_model_fooled", "still_flagged", "warned_no_floor", "warned_with_floor", "unusual_no_floor", "unusual_with_floor")
        totals = dict.fromkeys(("tried",) + keys, 0)
        for row in i["rows"]:
            rows.append(" & ".join([row["name"], *(str(row[key]) for key in keys)]) + " \\\\")
            for key in totals:
                totals[key] += row[key]
        rows.append("\\midrule")
        rows.append(" & ".join([f"All, of {totals['tried']} tries", *(str(totals[key]) for key in keys)]) + " \\\\")
        save("injection_rows", rows)
        tried = totals["tried"]
        late = [row for row in i["rows"] if row["name"] in ("Fake record", "Fake exam sample")]
        late_tried, late_fooled = sum(row["tried"] for row in late), sum(row["language_model_fooled"] for row in late)
        record = next(row for row in late if row["name"] == "Fake record")
        exam = next(row for row in late if row["name"] == "Fake exam sample")
        macros.update(
            injectionFooledCount=totals["language_model_fooled"], injectionSaved=totals["warned_with_floor"] - totals["warned_no_floor"], injectionSilent=tried - totals["warned_with_floor"],
            injectionEarlyTried=tried - late_tried, injectionEarlyFooled=totals["language_model_fooled"] - late_fooled, injectionLateTried=late_tried, injectionLateFooled=late_fooled,
            injectionRecordFooled=record["language_model_fooled"], injectionExamFooled=exam["language_model_fooled"], injectionEach=record["tried"],
        )
        macros.update(
            injectionTried=count(tried), injectionFooled=pct(totals["language_model_fooled"] / tried), injectionFlagged=pct(totals["still_flagged"] / tried),
            injectionNoFloor=pct(totals["warned_no_floor"] / tried), injectionFloor=pct(totals["warned_with_floor"] / tried),
            injectionUnusualNoFloor=pct(totals["unusual_no_floor"] / tried), injectionUnusual=pct(totals["unusual_with_floor"] / tried),
            injectionCaught=str(i["caught_before_attack"]), injectionHarmful=str(i["harmful"]),
        )


def system_tables(data, macros):
    groups = [("clean_clean", "Content fine, behaviour normal"), ("harmful_content", "Content harmful, behaviour normal"), ("bad_behaviour", "Content fine, behaviour bad"), ("both_bad", "Content harmful, behaviour bad")]
    fast = load("system_no_language_model")
    rows = []
    for key, name in groups:
        last = pct(fast["both_joined"]["by_group"][key]) if fast else "--"
        rows.append(f"{name} & {pct(data['application_only']['by_group'][key])} & {pct(data['network_only']['by_group'][key])} & {pct(data['both_joined']['by_group'][key])} & {last} \\\\")
    save("system_rows", rows)
    if "clean_sessions_blocked" in data:
        macros["systemCleanBlocked"] = str(data["clean_sessions_blocked"])
    if fast:
        macros.update(
            fastSystemRecall=pct(fast["both_joined"]["recall"]), fastSystemFA=pct(fast["both_joined"]["false_alarm_rate"]), fastSystemMedian=f"{fast['seconds_per_session']['median']:.2f}",
            fastSystemBlocked=str(fast["clean_sessions_blocked"]), fastSystemPrecision=pct(fast["both_joined"]["precision"]), fastHarmful=pct(fast["both_joined"]["by_group"]["harmful_content"]),
            fastHarmfulSilent=fast["actions_by_group"]["harmful_content"].get("allow", 0),
        )
    harmful = data["actions_by_group"]["harmful_content"]
    macros.update(systemHarmful=pct(data["both_joined"]["by_group"]["harmful_content"]), systemHarmfulWarned=harmful.get("warn", 0), systemHarmfulSilent=harmful.get("allow", 0), systemCleanWarned=data["actions_by_group"]["clean_clean"].get("warn", 0))
    j = data["both_joined"]
    size = data["sessions"] // 4
    clean = j["by_group"]["clean_clean"]
    low, high = wilson(round(clean * size), size)
    macros.update(systemCleanFA=pct(clean), systemCleanLow=pct(low), systemCleanHigh=pct(high), systemGroup=str(size))
    macros.update(
        systemSessions=str(data["sessions"]), systemRecall=pct(j["recall"]), systemPrecision=pct(j["precision"]), systemFA=pct(j["false_alarm_rate"]),
        systemMedian=f"{data['seconds_per_session']['median']:.2f}", systemPninetyfive=f"{data['seconds_per_session']['p95']:.2f}",
    )


def scenario_tables(data, macros):
    rows = []
    for row in data["rows"]:
        name = row["scenario"].replace("-", " ")
        labels = ", ".join(label.replace("_", " ") for label in row["labels"]) or "none"
        rows.append(f"{name} & {row['expected']} & {row['action']} & {row['application_risk']:.2f} & {row['network_risk']:.2f} & {labels} \\\\")
    save("scenario_rows", rows)
    for row in data["rows"]:
        if row["scenario"] == "threat-as-record":
            joined = 1 - (1 - row["application_risk"]) * (1 - row["network_risk"])
            macros.update(recordApp=f"{row['application_risk']:.2f}", recordNet=f"{row['network_risk']:.2f}", recordJoined=f"{joined:.2f}", recordAction=row["action"])
        if row["scenario"] == "urdu-threat" and row.get("review_confidence") is not None:
            macros["urduConfidence"] = f"{row['review_confidence']:.2f}"
    macros.update(scenariosPassed=str(data["passed"]), scenariosTotal=str(data["total"]), demoOthersPassed=str(data["passed"] - 1))


def prompt_tables(data, macros):
    """How the prompt and the decision rule were chosen, on validation rows."""
    names = (
        ("calm_comment", "Calm comments"), ("clear_comment", "No rater objected"), ("text_harmless", "Harmless text"),
        ("abuse_comment", "Abuse"), ("hate_comment", "Hate"), ("threat_comment", "Threat"), ("text_fraud", "Fraud"),
    )
    prompts = data["prompts"]
    final = data["rules"]["flagged"]["Sure, or both readers agree"]
    sizes = data["rules"]["rows"]
    rows = []
    for key, name in names:
        cell = lambda label: f"{prompts[label][key]['flagged']}"
        rows.append(f"{name} ({sizes[key]}) & {cell('BASE')} & {cell('CALM')} & {cell('GUARD')} & \\textbf{{{final.get(key, 0)}}} \\\\")
    save("prompt_rows", rows)
    attacks = data["attacks"]
    tried = lambda label: attacks[label]["rows"] * len(attacks[label]["fooled"])
    worked = lambda label: sum(attacks[label]["fooled"].values())
    first = prompts["FIRST"]
    caught = lambda flagged: sum(flagged[key] for key in ("abuse_comment", "hate_comment", "threat_comment", "text_fraud"))
    plain = lambda label: {key: prompts[label][key]["flagged"] for key in prompts[label]}
    macros.update(
        promptFirstCaught=caught(plain("BASE")), promptTighterCaught=caught(plain("CALM")), promptGuardCaught=caught(plain("GUARD")), promptFinalCaught=caught(final),
        promptGuardCalm=prompts["GUARD"]["calm_comment"]["flagged"], promptFinalCalm=final["calm_comment"],
        promptGainBack=caught(plain("GUARD")) - caught(plain("CALM")), promptLost=caught(plain("BASE")) - caught(plain("CALM")),
    )
    macros.update(
        attackCalm=f"{worked('CALM')} of {tried('CALM')}", attackGuard=f"{worked('GUARD')} of {tried('GUARD')}",
        reasonFirstCalm=f"{first['calm_comment']['flagged']} of {first['calm_comment']['rows']}", tighterCalm=f"{prompts['CALM']['calm_comment']['flagged']} of {prompts['CALM']['calm_comment']['rows']}",
    )


def wilson(hits, size, z=1.96):
    """95% Wilson interval for a share."""
    share = hits / size
    middle = (share + z * z / (2 * size)) / (1 + z * z / size)
    half = z * sqrt(share * (1 - share) / size + z * z / (4 * size * size)) / (1 + z * z / size)
    return middle - half, middle + half


def first_run_tables(macros):
    """The first full run, kept to show what the hand-written tests hid."""
    folder = RESULTS / "first_run"
    system = json.loads((folder / "system.json").read_text(encoding="utf-8"))
    review = json.loads((folder / "review.json").read_text(encoding="utf-8"))
    macros["firstRunOpinionWrong"] = review["link_opinion"]["conditions"][2]["normal_flagged"]
    macros["firstRunOrderBoth"] = next(row["combined"] for row in review["disguise"]["rows"] if row["name"] == "An instruction to the reviewer")
    with (folder / "system_sessions.csv").open(encoding="utf-8") as handle:
        clean = [row for row in csv.DictReader(handle) if row["group"] == "clean_clean"]
    wrong = [row for row in clean if row["action"] in ("flag", "block")]
    note = review["network_note"]
    macros.update(
        firstRunCleanFA=pct(system["both_joined"]["by_group"]["clean_clean"]), firstRunWrong=str(len(wrong)), firstRunClean=str(len(clean)),
        firstRunBlocked=str(sum(row["action"] == "block" for row in wrong)), firstRunHandWrong=f"{note['harmless_flagged_alone']} of {note['harmless']}",
    )


def main():
    macros = {}
    for name, job in (("prompt_choice", prompt_tables), ("text", text_tables), ("links", link_tables), ("link_rule_choice", link_rule_tables), ("cross_dataset", cross_tables), ("backbone", backbone_tables), ("review", review_tables), ("system", system_tables), ("scenarios", scenario_tables)):
        data = load(name)
        if data:
            job(data, macros)
    first_run_tables(macros)
    flows, anomaly = load("flows"), load("anomaly")
    if flows and anomaly:
        flow_tables(flows, anomaly, macros)
    save("numbers", [f"\\newcommand{{\\{key}}}{{{value}}}" for key, value in sorted(macros.items())])
    print(len(macros), "numbers", sorted(p.name for p in OUT.glob("*.tex")))


if __name__ == "__main__":
    main()
