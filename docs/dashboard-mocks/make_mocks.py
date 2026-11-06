"""Static dashboard mock-ups, with sample data, for choosing a look."""
from pathlib import Path

HERE = Path(__file__).parent

ROWS = [
    ("14:02:11", "email", "ahmed.raza@student.test", "Fee policy", "block", 0.97, "Application", "hate, abuse"),
    ("14:01:58", "qr", "poster camera 2", "hbl-digital-banking.test/signin", "flag", 0.91, "Application", "dangerous link"),
    ("14:01:40", "email", "billing@vendor.test", "Updated bank details for invoice", "flag", 0.72, "Both", "fraud, behaviour"),
    ("14:01:22", "session", "10.20.4.17", "TLS to update-cdn-check.test", "flag", 0.66, "Network", "behaviour"),
    ("14:00:47", "email", "registrar@nutech.test", "Spring semester fee challan", "allow", 0.04, "", ""),
    ("14:00:31", "message", "+92 300 0000000", "Mubarak ho! Aap ka inam nikla hai", "block", 0.93, "Application", "fraud"),
    ("14:00:12", "email", "council@nutech.test", "Minutes of the academic council", "allow", 0.02, "", ""),
    ("13:59:58", "link", "check page", "en.wikipedia.org/wiki/Phishing", "allow", 0.06, "", ""),
    ("13:59:41", "email", "unknown@mail.test", "Accidents happen to people who ask", "flag", 0.78, "Application", "threat"),
    ("13:59:20", "session", "10.20.4.33", "312 connections to port 445", "block", 0.89, "Network", "behaviour"),
    ("13:58:55", "file", "check page", "semester_report.pdf", "allow", 0.08, "", ""),
    ("13:58:30", "email", "it-helpdesk@mail.test", "Your mailbox is full", "warn", 0.41, "Application", "fraud"),
    ("13:58:02", "qr", "check page", "nutech.edu.pk", "allow", 0.03, "", ""),
    ("13:57:44", "email", "dean.office@nutech.test", "Exam schedule update", "allow", 0.05, "", ""),
    ("13:57:19", "session", "10.20.4.8", "HTTPS to github.com", "allow", 0.02, "", ""),
    ("13:56:51", "message", "+92 300 0000001", "Your parcel is held at customs", "warn", 0.44, "Application", "fraud"),
]
COUNTS = {"Checked": "1,204", "Allowed": "1,131", "Warned": "23", "Flagged": "38", "Blocked": "12"}
BARS = [3, 5, 2, 7, 4, 6, 9, 3, 5, 8, 4, 2, 6, 7, 3, 5, 11, 4, 3, 6, 8, 5, 2, 4, 7, 9, 3, 5, 6, 4]
NOTE = "Sample data for choosing a look"


def page(title: str, style: str, body: str) -> str:
    return f"<!doctype html><meta charset=utf-8><title>{title}</title><style>*{{box-sizing:border-box}}{style}</style>{body}"


def defender() -> str:
    style = """
    body{margin:0;font:13px/1.35 'Segoe UI',Arial,sans-serif;color:#242424;background:#fff;height:900px;overflow:hidden}
    .top{height:44px;background:#1b1a19;color:#fff;display:flex;align-items:center;padding:0 16px;font-size:14px;font-weight:600}
    .top span{margin-left:auto;font-weight:400;font-size:12px;color:#d6d6d6}
    .wrap{display:flex;height:856px}
    nav{width:208px;background:#f5f5f5;border-right:1px solid #e0e0e0;padding:8px 0}
    nav div{padding:7px 18px;color:#424242}
    nav div.on{background:#e6e6e6;font-weight:600;color:#111}
    nav small{display:block;padding:12px 18px 4px;color:#707070;font-size:11px}
    main{flex:1;padding:14px 20px;min-width:0;overflow:hidden}
    h1{font-size:20px;font-weight:600;margin:0 0 8px}
    .bar{display:flex;gap:18px;padding:6px 0;border-bottom:1px solid #e0e0e0;color:#0f6cbd}
    .bar b{color:#fff;background:#0f6cbd;padding:4px 12px;font-weight:600;border-radius:2px;margin:-3px 0}
    .bar i{margin-left:auto;font-style:normal;color:#424242}
    .filters{display:flex;gap:8px;padding:8px 0;color:#424242}
    .filters span{border:1px solid #d1d1d1;padding:2px 10px;border-radius:2px;background:#fff}
    table{width:100%;border-collapse:collapse}
    th{font-weight:600;text-align:left;border-bottom:1px solid #d1d1d1;padding:6px 8px;color:#424242;white-space:nowrap}
    td{padding:6px 8px;border-bottom:1px solid #f0f0f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:170px}
    tr.sel td{background:#ebf3fc}
    .sq{display:inline-block;width:9px;height:9px;margin-right:6px}
    .block .sq{background:#b10e1c}.flag .sq{background:#d83b01}.warn .sq{background:#c19c00}.allow .sq{background:#a0a0a0}
    aside{width:400px;flex:none;background:#fff;border-left:1px solid #d1d1d1;padding:14px 18px;box-shadow:-2px 0 6px rgba(0,0,0,.08)}
    aside h2{font-size:16px;margin:0 0 2px;font-weight:600}
    .tabs{display:flex;gap:16px;border-bottom:1px solid #e0e0e0;margin:10px 0 10px}
    .tabs span{padding:5px 0}.tabs .on{border-bottom:2px solid #0f6cbd;font-weight:600}
    dl{display:grid;grid-template-columns:120px 1fr;gap:4px 8px;margin:0 0 12px}dt{color:#616161}dd{margin:0}
    h3{font-size:13px;margin:12px 0 4px;font-weight:600}
    p{margin:0 0 6px}.foot{color:#707070;font-size:11px;padding-top:10px}
    """
    rows = "".join(
        f"<tr class='{'sel ' if i == 0 else ''}{r[4]}'><td><input type=checkbox></td><td><span class=sq></span>{r[4].title()}</td><td>{r[5]:.2f}</td><td>{r[1].title()}</td><td>{r[3]}</td><td>{r[2]}</td><td>{r[6] or '-'}</td><td>{r[0]}</td></tr>"
        for i, r in enumerate(ROWS)
    )
    counts = " &nbsp;·&nbsp; ".join(f"{k} {v}" for k, v in COUNTS.items())
    body = f"""
    <div class=top>Semantic Trust Layer<span>Text model on · Link model on · Traffic model on · Language model on</span></div>
    <div class=wrap>
    <nav><div>Overview</div><div class=on>Verdict queue</div><div>Hosts</div><div>Agents</div><small>Demonstration</small><div>Run a scenario</div><div>Check an item</div><small>Evaluation</small><div>Test results</div></nav>
    <main><h1>Verdict queue</h1>
    <div class=bar><b>Run a scenario</b><span>Refresh</span><span>Export</span><i>{counts}</i></div>
    <div class=filters><span>Action: Any</span><span>Found by: Any</span><span>Type: Any</span><span>Last 24 hours</span></div>
    <table><tr><th></th><th>Action</th><th>Risk</th><th>Type</th><th>Item</th><th>From</th><th>Found by</th><th>Time</th></tr>{rows}</table>
    <div class=foot>{NOTE}</div></main>
    <aside><h2>Fee policy</h2><div>Email to rector@nutech.test · Blocked · Risk 0.97</div>
    <div class=tabs><span class=on>Summary</span><span>Application Agent</span><span>Network Agent</span><span>Signed record</span></div>
    <p>The message uses a racial slur to attack the recipient and demands that they leave the institution.</p>
    <h3>Application Agent</h3><dl><dt>Risk</dt><dd>0.97</dd><dt>Hate</dt><dd>0.98</dd><dt>Abuse</dt><dd>0.94</dd><dt>Threat</dt><dd>0.12</dd><dt>Fraud</dt><dd>0.01</dd><dt>Model</dt><dd>MiniLM + stl, Qwen review</dd><dt>Time</dt><dd>6.4 s</dd></dl>
    <h3>Network Agent</h3><dl><dt>Risk</dt><dd>0.03</dd><dt>Behaviour</dt><dd>3 recent connections to 1 host, port 25</dd><dt>Time</dt><dd>4 ms</dd></dl>
    <h3>Record</h3><dl><dt>Signature</dt><dd>Valid, 3 signers</dd><dt>Flagged by</dt><dd>Application Agent</dd></dl>
    </aside></div>"""
    return page("Look A", style, body)


def siem() -> str:
    style = """
    body{margin:0;font:12.5px/1.4 Arial,Helvetica,sans-serif;background:#111418;color:#d7dce2;height:900px;overflow:hidden}
    .top{height:40px;background:#0a0c0f;border-bottom:1px solid #262b31;display:flex;align-items:center;gap:22px;padding:0 14px}
    .top b{color:#fff}.top span{color:#98a2ad}.top .on{color:#fff;border-bottom:2px solid #36a2eb;padding-bottom:9px;margin-bottom:-11px}
    .q{display:flex;gap:8px;padding:10px 14px;border-bottom:1px solid #262b31}
    .q div{flex:1;background:#0a0c0f;border:1px solid #333a42;padding:6px 10px;font-family:Consolas,monospace;color:#9fd3ff}
    .q span{border:1px solid #333a42;padding:6px 12px}.q b{background:#1f6feb;color:#fff;padding:6px 16px;font-weight:600}
    .main{display:flex;height:800px}
    .side{width:210px;border-right:1px solid #262b31;padding:10px 12px;color:#aab3bd}
    .side h4{margin:12px 0 4px;color:#fff;font-size:12px}.side div{display:flex;justify-content:space-between;padding:1px 0}
    .right{flex:1;min-width:0}
    .hist{height:120px;border-bottom:1px solid #262b31;padding:10px 14px}
    .hist small{color:#98a2ad}
    svg{display:block;width:100%;height:84px}
    table{width:100%;border-collapse:collapse;font-family:Consolas,monospace;font-size:12px}
    th{text-align:left;color:#98a2ad;font-weight:400;border-bottom:1px solid #262b31;padding:5px 10px;background:#161a1f}
    td{padding:4px 10px;border-bottom:1px solid #1d2227;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:280px}
    .block{color:#ff7b72}.flag{color:#ffa657}.warn{color:#e3b341}.allow{color:#8b949e}
    .ex td{background:#161a1f;white-space:normal;padding:8px 10px 10px 28px;color:#c9d1d9;max-width:none}
    .ex pre{margin:0;font:12px/1.5 Consolas,monospace}
    .foot{padding:8px 14px;color:#6e7781;font-size:11px}
    """
    bars = "".join(
        f"<rect x='{i * 3.3}%' y='{84 - h * 7}' width='2.6%' height='{h * 7}' fill='#2f81f7'/>"
        + (f"<rect x='{i * 3.3}%' y='{84 - h * 2}' width='2.6%' height='{h * 2}' fill='#f85149'/>" if i % 4 == 0 else "")
        for i, h in enumerate(BARS)
    )
    rows = []
    for i, r in enumerate(ROWS[:11]):
        rows.append(f"<tr><td>{r[0]}</td><td class={r[4]}>{r[4]}</td><td>{r[5]:.2f}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[6].lower() or '-'}</td><td>{r[7] or '-'}</td></tr>")
        if i == 0:
            rows.append("<tr class=ex><td colspan=8><pre>verdict.reason       The message uses a racial slur to attack the recipient\napplication.risk     0.97   hate 0.98  abuse 0.94  threat 0.12  fraud 0.01\napplication.model    minilm+stl, qwen3.5 review   6.4 s\nnetwork.risk         0.03   3 recent connections to 1 host, port 25   4 ms\nsignature            valid (application-agent, network-agent, coordinator)</pre></td></tr>")
    side = "".join(f"<h4>{t}</h4>" + "".join(f"<div><span>{k}</span><span>{v}</span></div>" for k, v in items) for t, items in (
        ("action", [("allow", "1,131"), ("warn", "23"), ("flag", "38"), ("block", "12")]),
        ("found_by", [("application", "31"), ("network", "14"), ("both", "5")]),
        ("kind", [("email", "702"), ("session", "388"), ("message", "61"), ("link", "33"), ("qr", "14"), ("file", "6")]),
        ("label", [("fraud", "24"), ("behaviour", "19"), ("abuse", "11"), ("hate", "6"), ("threat", "5")]),
    ))
    body = f"""
    <div class=top><b>STL</b><span class=on>Search</span><span>Hosts</span><span>Agents</span><span>Scenarios</span><span>Results</span></div>
    <div class=q><div>action:(block OR flag) AND found_by:*</div><span>Last 24 hours</span><b>Search</b></div>
    <div class=main><div class=side>{side}</div><div class=right>
    <div class=hist><small>1,204 items · 30 minute view</small><svg>{bars}</svg></div>
    <table><tr><th>time</th><th>action</th><th>risk</th><th>kind</th><th>source</th><th>item</th><th>found_by</th><th>labels</th></tr>{''.join(rows)}</table>
    <div class=foot>{NOTE}</div></div></div>"""
    return page("Look B", style, body)


def analyzer() -> str:
    style = """
    body{margin:0;font:12px/1.35 'Segoe UI',Tahoma,Arial,sans-serif;background:#f0f0f0;color:#000;height:900px;overflow:hidden}
    .menu{background:#f6f6f6;padding:3px 8px;border-bottom:1px solid #cfcfcf;display:flex;gap:14px}
    .tool{background:#ececec;padding:4px 8px;border-bottom:1px solid #bdbdbd;display:flex;gap:6px}
    .tool span{border:1px solid #b5b5b5;background:#fafafa;padding:2px 10px}
    .filter{padding:4px 8px;display:flex;gap:6px;border-bottom:1px solid #bdbdbd;align-items:center}
    .filter div{flex:1;background:#c8f7c5;border:1px solid #8fbf8b;padding:2px 6px;font-family:Consolas,monospace}
    .list{height:372px;overflow:hidden;background:#fff;border-bottom:3px solid #bdbdbd}
    table{width:100%;border-collapse:collapse;font-family:Consolas,monospace;font-size:12px}
    th{background:#ececec;border-right:1px solid #cfcfcf;border-bottom:1px solid #bdbdbd;text-align:left;padding:2px 6px;font:12px 'Segoe UI',Arial;font-weight:400}
    td{padding:1px 6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:330px}
    .block td{background:#a40000;color:#fff}.flag td{background:#f4c7c3}.warn td{background:#fff2b3}.allow td{background:#e7f6e7}
    tr.sel td{outline:1px solid #000;outline-offset:-1px}
    .tree{height:236px;background:#fff;border-bottom:3px solid #bdbdbd;padding:4px 8px;font-family:Consolas,monospace;overflow:hidden}
    .tree div{padding-left:0;white-space:nowrap}.tree .i{padding-left:22px}.tree .h{background:#dbe9ff}
    .raw{height:198px;background:#fff;padding:4px 8px;font-family:Consolas,monospace;overflow:hidden;white-space:pre}
    .raw mark{background:#ffd27f}
    .status{background:#ececec;border-top:1px solid #bdbdbd;padding:3px 8px;display:flex;gap:18px}
    """
    rows = "".join(
        f"<tr class='{'sel ' if i == 0 else ''}{r[4]}'><td>{1204 - i}</td><td>{r[0]}</td><td>{r[1].upper()}</td><td>{r[2]}</td><td>{r[4].upper()}</td><td>{r[5]:.2f}</td><td>{r[6] or '-'}</td><td>{r[3]}</td></tr>"
        for i, r in enumerate(ROWS)
    )
    tree = """
    <div>&#9656; Item 1204: EMAIL, 412 bytes, from ahmed.raza@student.test to rector@nutech.test</div>
    <div class=h>&#9662; Application Agent, risk 0.97, flagged</div>
    <div class=i>hate 0.98, abuse 0.94, threat 0.12, fraud 0.01</div>
    <div class=i>Strongest words: [hidden in this mock]</div>
    <div class=i>Language model: uses a racial slur to attack the recipient</div>
    <div>&#9662; Network Agent, risk 0.03, not flagged</div>
    <div class=i>3 recent connections to 1 host, port 25, average 812 bytes</div>
    <div>&#9656; Coordinator: joined risk 0.97, action BLOCK, 6.41 s</div>
    <div>&#9656; Signatures: application-agent valid, network-agent valid, coordinator valid</div>
    """
    raw = "Subject: Fee policy\nFrom: ahmed.raza@student.test\nTo: rector@nutech.test\n\nDear Rector, you are a <mark>[slur hidden in this mock]</mark> and you should leave this university."
    body = f"""
    <div class=menu><span>File</span><span>View</span><span>Scenarios</span><span>Agents</span><span>Results</span><span>Help</span></div>
    <div class=tool><span>Start gateway</span><span>Stop</span><span>Run scenario</span><span>Open capture</span><span>Check item</span></div>
    <div class=filter><b>Filter:</b><div>stl.action == block || stl.action == flag</div><span>Apply</span></div>
    <div class=list><table><tr><th>No.</th><th>Time</th><th>Type</th><th>Source</th><th>Action</th><th>Risk</th><th>Found by</th><th>Item</th></tr>{rows}</table></div>
    <div class=tree>{tree}</div><div class=raw>{raw}</div>
    <div class=status><span>Items 1,204</span><span>Flagged 38</span><span>Blocked 12</span><span>Models: text, link, traffic, language</span><span>{NOTE}</span></div>"""
    return page("Look C", style, body)


for name, html in (("look-a-security-portal", defender()), ("look-b-log-search", siem()), ("look-c-traffic-analyzer", analyzer())):
    (HERE / f"{name}.html").write_text(html, encoding="utf-8")
print("written")
