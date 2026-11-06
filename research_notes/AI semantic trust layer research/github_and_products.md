# GitHub repositories and products closest to the Semantic Trust Layer

All checks were made on 2026-11-05. Repository existence, stars, last commit (latest commit on the default branch), licence and archive status come from the GitHub API, read that day. A licence marked with a file name was read from that file because GitHub could not classify it. Model licence, weight size, downloads and update date come from the Hugging Face API. No code or model was downloaded or run, so every reuse verdict rests on READMEs, licence files, file lists and model cards.

Reuse key: **Yes** means the licence allows it and it suits a student project. **Partly** means usable with the stated limit. **Read only** means learn from it but do not copy code. **No** means it does not fit. Pages seen only as search results, not opened, are marked "(search result)".

## Is STL already implemented anywhere, and does any project run AI on both layers on the same data?

### Takeaway
No. I found no public project or product that does all of STL: meaning-based AI on one event from both the network and application layers, a fused verdict, signed sharing, and both a user app and a server dashboard. Darktrace comes closest commercially, AiSOC and Slips come closest in open source, and Sentinel-AI comes closest at student level, but each misses at least two of these.

### Cited Findings

#### The name
- A GitHub search for the exact phrase "semantic trust layer" returned 3 repositories, and none is this idea: AiNIR guards AI-agent actions, SemanticTrustLayer detects LLM jailbreaks, and NexusBI is a business analytics tool — [AiNIR](https://github.com/hamlet-lab/AiNIR); [SemanticTrustLayer](https://github.com/pvchaitu/SemanticTrustLayer); [NexusBI](https://github.com/HeyderHesenov/NexusBI)
- Salesforce uses a similar name. Its Einstein Trust Layer sits between Salesforce apps and LLMs to mask data, score toxicity and log use. It protects LLM use, not networks or users' inboxes (search result) — [Salesforce Trailhead](https://trailhead.salesforce.com/content/learn/modules/the-einstein-trust-layer/meet-the-einstein-trust-layer)
- A web search found no source that defines Semantic Trust Layer as a named concept. Related "trust layer" papers check AI-agent actions, not incoming data (search result) — [AgentTrust, arXiv 2606.08539](https://arxiv.org/pdf/2606.08539)

#### Search for systems that use both layers
- A search for systems where agents jointly analyse network traffic and application content found none. The closest paper is a 2026 multi-agent framework that joins pre-detection, classification and LLM incident reports, but on network data only (search result) — [JSAN 15(2), 32](https://www.mdpi.com/2224-2708/15/2/32)
- A 2026 survey of attacks on LLM agents says each attack chain crosses at least two trust boundaries, so no single-layer defence sees the whole chain. This supports STL's reasoning but describes threats, not a working system (search result) — [arXiv 2604.23338](https://arxiv.org/pdf/2604.23338)

#### Closest whole systems on GitHub
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [beenuar/AiSOC](https://github.com/beenuar/AiSOC) | Self-hosted AI security operations centre. Ingests alerts through 91 connectors, runs detection rules, groups alerts into incidents, has an LLM agent investigate, logs every prompt and tool call, exports a signed evidence bundle. | 7,344 | 2026-11-05 | MIT | Coordinator, dashboard, signing idea | Partly. Core profile needs 16 services and about 8 GB RAM. Reads alerts from other tools, not raw email or packets. Young repo, created 2026-05-02. |
| [stratosphereips/StratosphereLinuxIPS](https://github.com/stratosphereips/StratosphereLinuxIPS) | Slips. Behavioural ML intrusion prevention on network traffic, with TLS/HTTPS anomaly detection, shared LLM access for modules, P2P indicator sharing with trust, and a federated learning submodule. | 903 | 2026-09-30 | GPL-2.0 | Network agent, sharing, federated learning | Partly. Strongest open match on the network side. GPL-2.0, so run it as a separate service. No application content analysis. |
| [zhadyz/AI_SOC](https://github.com/zhadyz/AI_SOC) | Local research SOC: Wazuh-format ingestion, flow classification, local Ollama triage, retrieved knowledge, incident correlation, analyst review, Sigma export. | 175 | 2026-09-21 | Apache-2.0 text (LICENSE) | Coordinator, dashboard | Yes, as a reference. README gives 16 GB RAM as a practical start. |
| [Ishu-26/Sentinel-AI--Cyber-Defense-Platform](https://github.com/Ishu-26/Sentinel-AI--Cyber-Defense-Platform) | Closest student-style match. Separate URL phishing, network flow, malware and YARA checks feed one 0-100 risk score, with a SOC dashboard and LLM copilot. Uses XGBoost and Random Forest. No live packet capture: flows are submitted by hand. | 0 | 2026-09-13 | None found | All parts, thinly | Read only. No licence. The score combines one result's confidence, severity and asset value, not two layers on one event. |
| [Seelam-Mohith/QuantShield](https://github.com/Seelam-Mohith/QuantShield) | React dashboard over separate classical ML models for email, SMS, URL and port scans. Backend has separate routes: /api/email-check, /api/sms-check, /api/url-check, /api/network-check. No fusion code found by keyword search of app.py. | 13 | 2026-07-18 | None found | App agent, thin network check, dashboard | Read only. No licence. Its models are .pkl files, which can run code when loaded. |
| [suresh3234/CyberShield-AI-driven-multi-layer-cyber-security-framework](https://github.com/suresh3234/CyberShield-AI-driven-multi-layer-cyber-security-framework) | ML checks for network intrusion, phishing email and insider threats, with a unified dashboard. | 3 | 2026-07-29 | None found | App agent, network agent, dashboard | Read only. No licence. Dashboard joins views, no fusion step found in the README. |
| [aryaachalkar/Unified-Fraud-Detection-System-for-Banking-Communication](https://github.com/aryaachalkar/Unified-Fraud-Detection-System-for-Banking-Communication) | Hybrid rule and ML fraud detection across SMS, email and links. README claims real-time correlation across channels. | 1 | 2026-04-07 | MIT | App agent, channel correlation | Partly. MIT, 1 star. Application layer only. Correlation claim not tested. |
| [emaina-SecEngr/AbuTech-ai-security-platform](https://github.com/emaina-SecEngr/AbuTech-ai-security-platform) | Description lists network intrusion detection, malware analysis, GNN threat intelligence, LLM reasoning and multi-agent SOC automation. Folders run layer1_ingestion to layer5_interface. | 0 | 2026-07-23 | MIT | Coordinator, network agent | Read only for now. MIT, 0 stars. README is an unedited GitLab template, so scope is unverified. |
| [Manoj-engineer/SentinelPrime](https://github.com/Manoj-engineer/SentinelPrime) | Proof of concept that joins identity, host and network context to ask why a flow exists. README lists 3 pre-configured correlation rules. | 0 | 2026-01-24 | MIT | Coordinator idea | Partly. MIT, 0 stars. No email, SMS or content analysis found. |
| [Khaoulahidaawi/NIPDS](https://github.com/Khaoulahidaawi/NIPDS) | Classifies network packets in HTTP and HTTPS flows as benign or phishing, using DNS records and domain name features. | 4 | 2022-08-01 | None found | Network agent detecting phishing | Read only. No licence, old. Rare example of phishing detected from network data. |
| [Western-OC2-Lab/Cross-Layer-Autonomous-Cybersecurity-Framework](https://github.com/Western-OC2-Lab/Cross-Layer-Autonomous-Cybersecurity-Framework) | AutoML for physical-layer authentication and cross-layer intrusion detection in 6G networks. | 16 | 2025-03-05 | MIT | Name only | No. Its cross-layer means physical and network layers, not application content. |
| [himanshu-23a/Anomaly-Detection-Tool-for-Application-and-Network-Layer-Attacks](https://github.com/himanshu-23a/Anomaly-Detection-Tool-for-Application-and-Network-Layer-Attacks) | Scapy and scikit-learn anomaly tool. The title says application and network, but the input is network traffic only. | 0 | 2024-10-27 | None found | Network agent | Read only. No licence. |
| [hamlet-lab/AiNIR](https://github.com/hamlet-lab/AiNIR) | Checks AI-agent actions and MCP tool calls before they run. Describes itself as a semantic trust layer. | 1 | 2026-09-08 | Apache-2.0 | Name clash only | No. Different problem: guards agents, not incoming data. |
| [pvchaitu/SemanticTrustLayer](https://github.com/pvchaitu/SemanticTrustLayer) | Research on spotting when an LLM is pushed out of its trusted behaviour, using output embeddings and internal model signals. Uses the same name and the short form STL. | 0 | 2026-03-17 | MIT | Name clash only | No. Different problem: jailbreak detection. |

#### How the closest systems compare with STL
"Not found" means the pages I read do not mention it. It does not prove the feature is absent. Sources are in the table above and in the commercial section.

| System | AI on application content | AI on network data | Both layers on one event | Signed sharing | User app and dashboard |
|---|---|---|---|---|---|
| **STL (target)** | Yes | Yes | Yes | Yes | Both |
| Darktrace | Yes, email | Yes | Partly: vendor says cross-domain attacks appear as one incident | Not found | Dashboard only |
| Microsoft Defender XDR with Security Copilot | Yes: LLM reads reported email | Partly: signals come mainly from endpoints | Partly: alerts join into incidents, and the agent can hunt across data | Not found | Dashboard only |
| Cloudflare One | Yes, email | Gateway filters DNS, network and HTTP; AI role not confirmed | Not found | Not found | Dashboard only |
| Google Messages, Phone, Chrome | Yes, mostly on device | No flow analysis found | No: Chrome mixes page signals with site metadata | Not found | User side only |
| McAfee Scam Detector, Bitdefender Scamio | Yes | Not found | No | Not found | User side only |
| AiSOC | Partly: LLM reads alerts | Partly: alerts from connected tools | Partly: at alert level, after detection | Signed evidence bundle; sharing not found | Dashboard only |
| Slips | No | Yes | No | P2P sharing with trust; peers signed by organisation key | Not checked |
| Sentinel-AI | Partly: URL features only | Partly: manual flow input | No | Not found | Dashboard only |
| QuantShield | Partly: classical ML | Partly: port scans | No: separate endpoints | Not found | Web dashboard |

### Inferences
- The new part of STL is the join, not the detectors. Good detectors already exist for every channel. Nobody I found publishes a design that reads one event at both layers and then signs the result.
- STL should not claim that nobody uses AI across both layers. Darktrace and Microsoft correlate across domains. A safer claim is an open design that checks one event by meaning at both layers and issues a verdict others can verify.
- Darktrace describes its method as learning each organisation's normal behaviour. STL checks what content means. These are different methods, and that is a useful line for the report.
- The nearest real example of both kinds of evidence on one case is Microsoft's Phishing Triage Agent: an LLM reads the email and can hunt across other data. It runs only after a user report, and only inside Microsoft's estate.
- Most student projects put several models behind one dashboard. A marker can tell this apart from real fusion, so STL's demo should show one event where neither layer alone reaches the right verdict.
- The word "semantic" is loose in this field. In uusec-waf it refers to SQL, XSS, RCE and LFI engines, which looks like parsing attack strings rather than reading human meaning. The report should define the term.
- The name collides with two small repositories and sits close to Salesforce's product. This is a clarity issue and I did not research trademarks.

### Gaps
- "Not found" only covers what search can reach. Private code, GitLab, Gitee and closed products could hold similar work.
- GitHub search treats every word as required, so long queries returned nothing. I used short queries, which can miss projects with different wording.
- Vendors do not publish enough to show whether their AI reads one event at both layers, or only joins alerts afterwards.
- The correlation claims in Unified Fraud Detection System and the scope of AbuTech were not tested, as no code was run.

## Which repositories are closest for each STL part?

### Takeaway
Every part has a usable open base except QR codes and signed verdict sharing, where only small or adjacent projects exist. Best starts: Phishpedia and PhishIntention (pages), rspamd (email), SmishX (SMS), Detoxify (toxicity), ET-BERT and netFound (encrypted traffic), Zeek with Slips (network), LangGraph (coordinator), MISP (sharing), DSSE with PyNaCl (signing), and Flower (federated learning).

### Cited Findings
Each repository link below is the source for its row.

#### Application agent: links and web pages
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [lindsey98/Phishpedia](https://github.com/lindsey98/Phishpedia) | USENIX'21 code. Finds logos on a page, matches them to a brand with a Siamese model, then checks brand against domain. Not trained on phishing data. Ships a 30k phishing benchmark. | 360 | 2025-07-26 | CC0-1.0 | App agent: links and pages | Yes. Needs a page screenshot. Badge shows 277 protected brands, so other brands are missed. |
| [lindsey98/PhishIntention](https://github.com/lindsey98/PhishIntention) | USENIX Security 2022 code. Adds a check for pages asking for credentials, and a locator that clicks login links to reach them. | 263 | 2026-06-04 | CC0-1.0 | App agent: links and pages | Yes. The clicking step needs a sandboxed browser. |
| [code-philia/PhishVLM](https://github.com/code-philia/PhishVLM) | Reference-based detector that replaces the brand list with a vision-language model. Needs two API keys. Moved from PhishLLM. | 40 | 2026-06-04 | None found | App agent: meaning-based page check | Read only. No licence. Idea fits STL well; ask the authors before copying code. |
| [code-philia/Dynaphish](https://github.com/code-philia/Dynaphish) | Add-on for reference-based detectors: brand knowledge expansion and web interaction. | 20 | 2025-08-27 | None found | App agent: links and pages | Read only. No licence. |
| [JehLeeKR/Multimodal_LLM_Phishing_Detection](https://github.com/JehLeeKR/Multimodal_LLM_Phishing_Detection) | Scripts that send page images and text to GPT, Gemini and Claude for phishing detection and brand identification. | 11 | 2025-02-26 | None found | App agent: meaning-based page check | Read only. No licence. Useful prompts to study. |
| [Antimalweb/URLNet](https://github.com/Antimalweb/URLNet) | Code for the URLNet paper: deep learning on URL text. | 175 | 2021-01-12 | Apache-2.0 | App agent: links | Partly. Old code. Useful as a baseline. |
| [x0rz/phishing_catcher](https://github.com/x0rz/phishing_catcher) | Spots phishing domains from the Certstream feed. | 1,833 | 2020-12-08 | GPL-3.0 | Links plus TLS certificate data | Partly. GPL-3.0, last commit 2020. The idea links certificates to phishing. |
| [elceef/dnstwist](https://github.com/elceef/dnstwist) | Generates lookalike domain names to find typosquatting and brand impersonation. | 5,774 | 2025-04-15 | Apache-2.0 | Links plus DNS | Yes. |
| [Phishing-Database/Phishing.Database](https://github.com/Phishing-Database/Phishing.Database) | Lists of phishing domains and URLs, checked with PyFunceble. | 1,637 | 2026-10-02 | MIT | Test data and threat feed | Yes. |
| [rf-peixoto/phishing_pot](https://github.com/rf-peixoto/phishing_pot) | Collection of phishing samples for researchers and detection developers. | 483 | 2026-11-05 | CC BY-NC 4.0 (LICENSE) | Test data | Yes for a non-commercial project. |

#### Application agent: email
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [rspamd/rspamd](https://github.com/rspamd/rspamd) | Spam filter. Its GPT plugin sends displayed text, subject, sender and URLs to an LLM and treats the answer as one classifier among several. Works with local Ollama. | 2,562 | 2026-11-01 | Apache-2.0 (LICENSE.md) | App agent: email | Yes. Best ready email base. See the plugin source below. |
| [sublime-security/sublime-platform](https://github.com/sublime-security/sublime-platform) | Free, open platform for detecting email attacks such as BEC, malware and credential phishing. | 277 | 2026-10-30 | MIT | App agent: email | Yes. Good to study or run beside STL. |
| [sublime-security/sublime-rules](https://github.com/sublime-security/sublime-rules) | Open detection rules for email attacks. | 381 | 2026-11-04 | MIT | App agent: email | Yes. Good source of test ideas and features. |
| [OpenCyberLab/PhishGuard](https://github.com/OpenCyberLab/PhishGuard) | Email phishing detection with a private local LLM. | 4 | 2026-06-05 | MIT | App agent: email | Partly. MIT, 4 stars. Read before running. |
| [laugiov/scambuster](https://github.com/laugiov/scambuster) | Turns inbound scam emails into indicators through controlled AI engagement. | 25 | 2026-11-05 | MIT | App agent, threat feed | Partly. Research lab project. |

- Rspamd's GPT plugin works with OpenAI or local Ollama, and in ensemble mode sets GPT_SPAM at 0.75 by default. It can feed verdicts into the Bayes learner — [Rspamd docs](https://docs.rspamd.com/modules/gpt/)

#### Application agent: SMS and scams
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [yizhu-joy/SmishX](https://github.com/yizhu-joy/SmishX) | SOUPS 2025 code. LLM agents explain why an SMS is phishing. Includes a re-labelled dataset and user study codebooks. Needs OpenAI and Jina Reader keys. | 7 | 2025-06-26 | MIT | App agent: SMS, by meaning | Yes. Closest open match to meaning-based SMS checks, but uses cloud LLMs. |
| [ajayagrawalgit/Apex](https://github.com/ajayagrawalgit/Apex) | Multi-agent malicious URL and phishing detection using Google ADK and Gemini. | 8 | 2025-11-18 | MIT | App agent, multi-agent | Partly. MIT, 8 stars, cloud LLM. |
| [misogare/RavenOsint](https://github.com/misogare/RavenOsint) | Multi-agent OSINT in Rust for phishing site and malicious domain analysis. | 7 | 2026-03-25 | Apache-2.0 | App agent, multi-agent | Partly. Rust may slow a Python team. |
| [gncrlatienza-eng/bantAI](https://github.com/gncrlatienza-eng/bantAI) | On-device SMS scam detection for Filipino users, with an Android app and admin side. | 3 | 2026-08-16 | None found | App agent, user app | Read only. No licence. Good model for a local-language user app. |
| [Zeronuru404/nusashield-ai](https://github.com/Zeronuru404/nusashield-ai) | Multi-agent fraud detection for Indonesian fintech: QRIS, phishing, invoice fraud, WhatsApp scams. | 44 | 2026-05-20 | None found | App agent, multi-agent | Read only. No licence, 1 commit. |

#### Application agent: QR codes
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [fouadtrad/Detecting-Quishing-Attacks-with-Machine-Learning-Techniques-Through-QR-Code-Analysis](https://github.com/fouadtrad/Detecting-Quishing-Attacks-with-Machine-Learning-Techniques-Through-QR-Code-Analysis) | Dataset and code. Detects quishing from QR structure and pixels, without opening the URL. | 10 | 2026-03-06 | CC-BY-4.0 | App agent: QR | Yes. Best QR start found. Keep the attribution CC-BY requires. |
| [aliasimcoskun/mobile-qr-code-based-phishing-url-detection](https://github.com/aliasimcoskun/mobile-qr-code-based-phishing-url-detection) | Mobile app that scans a QR code and analyses the URL with ML. | 7 | 2025-03-06 | MIT | App agent, user app | Partly. MIT. Flutter. |
| [muhammadwasif12/phishshield-App](https://github.com/muhammadwasif12/phishshield-App) | Flutter app with AI URL analysis and QR scanning. | 3 | 2026-01-13 | MIT | User app | Partly. MIT, 3 stars. |
| [spandanamotapothula0/Ai-Based-Phishing-Website-Detector](https://github.com/spandanamotapothula0/Ai-Based-Phishing-Website-Detector) | Multi-channel phishing detection using URL, SMS and QR analysis. | 2 | 2026-09-18 | None found | App agent | Read only. No licence. |
| [Piyush-ai-Miet/fraud-eye](https://github.com/Piyush-ai-Miet/fraud-eye) | Fraud detection for rural India: URL phishing, voice scams and QR fraud. | 3 | 2026-02-09 | None found | App agent | Read only. No licence. |

- A Hugging Face search for "quishing" returned no models on 2026-11-05 — [Hugging Face API search](https://huggingface.co/api/models?search=quishing)

#### Application agent: files
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [google/magika](https://github.com/google/magika) | AI detection of file content type. | 18,770 | 2026-11-05 | Apache-2.0 | App agent: files | Yes. Good first step before deeper file checks. |
| [target/strelka](https://github.com/target/strelka) | Container-based real-time file scanning. | 1,005 | 2026-08-18 | Apache-2.0 (LICENSE) | App agent: files | Yes. May be more than a demo needs. |
| [VirusTotal/yara](https://github.com/VirusTotal/yara) | Pattern matching for malware rules. | 9,997 | 2026-10-27 | BSD-3-Clause | App agent: files | Yes. |
| [mandiant/capa](https://github.com/mandiant/capa) | Finds capabilities in executable files. | 6,301 | 2026-11-03 | Apache-2.0 | App agent: files | Yes. |
| [Cisco-Talos/clamav](https://github.com/Cisco-Talos/clamav) | Open-source antivirus engine. | 7,505 | 2026-10-22 | GPL-2.0 | App agent: files | Yes, as a separate process. GPL-2.0. |

#### Toxicity, threats and protecting STL's own LLM
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [unitaryai/detoxify](https://github.com/unitaryai/detoxify) | Trained models and code for the three Jigsaw toxic comment challenges, including threats. Has original, unbiased, multilingual and small variants. | 1,312 | 2026-10-20 | Apache-2.0 | App agent: toxicity and threat | Yes. Best start for this part. |
| [conversationai/perspectiveapi](https://github.com/conversationai/perspectiveapi) | Repository for the Perspective API, a hosted service that scores the likely impact of a comment. | 921 | 2021-03-23 (archived) | Apache-2.0 | None | No. Archived, and the service is ending. See the sources below. |
| [protectai/llm-guard](https://github.com/protectai/llm-guard) | Security toolkit for LLM interactions. | 3,219 | 2026-07-08 (archived) | MIT | Protecting STL's own LLM | Partly. Archived on 2026-07-09, so no fixes. |
| [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) | Programmable guardrails for LLM-based conversational systems. | 7,434 | 2026-11-05 | Apache-2.0 (LICENSE.md) | Protecting STL's own LLM | Yes. Moved from NVIDIA/NeMo-Guardrails. |
| [meta-llama/PurpleLlama](https://github.com/meta-llama/PurpleLlama) | Tools to assess and improve LLM security. | 4,465 | 2026-10-30 | Llama 3.2 Community License text (LICENSE) | Protecting STL's own LLM | Partly. Check the Llama licence terms first. |
| [t-davidson/hate-speech-and-offensive-language](https://github.com/t-davidson/hate-speech-and-offensive-language) | Dataset and code for a 2017 hate speech paper. | 848 | 2023-06-12 | MIT | Test data | Partly. Old, English only. |
| [data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio) | Detects and masks personal data in text and images. Moved from microsoft/presidio. | 11,732 | 2026-11-02 | MIT | Privacy step before sharing | Yes. Useful for removing personal data from shared verdicts. |

- The Perspective API site says the service stays active until 2026-12-31 and will not accept new requests after that (search result) — [perspectiveapi.com](https://perspectiveapi.com/)
- A 2026 paper studies the loss of Perspective as a standard research tool (search result) — [arXiv 2604.25580](https://arxiv.org/abs/2604.25580)

#### Network agent: encrypted traffic models
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [linwhitehat/ET-BERT](https://github.com/linwhitehat/ET-BERT) | WWW 2022 model for encrypted traffic classification. Has a pre-trained model on Google Drive and the CSTNET-TLS 1.3 dataset. | 682 | 2026-07-23 | MIT | Network agent: encrypted traffic | Yes. Best-known start. Needs fine-tuning on your own labelled flows. |
| [ict-net/NetGPT](https://github.com/ict-net/NetGPT) | Generative pre-trained transformer for network traffic. Has fine-tuning scripts, with a pre-trained model and datasets on Google Drive. | 35 | 2026-09-16 | None found | Network agent: encrypted traffic | Read only. No licence. Ask the authors before reuse. |
| [ZGC-LLM-Safety/TrafficLLM](https://github.com/ZGC-LLM-Safety/TrafficLLM) | Adapts open LLMs to network traffic analysis, based on ChatGLM2 and Llama 2. Adds MCP setup for single-agent and multi-agent traffic analysis. | 453 | 2025-11-05 | None found | Network agent with LLM | Read only. No licence. Closest idea to an LLM network agent. |
| [YasodGinige/TrafficGPT](https://github.com/YasodGinige/TrafficGPT) | LLM approach to open-set encrypted traffic classification. | 62 | 2025-11-05 | MIT | Network agent: encrypted traffic | Partly. MIT. |
| [YasodGinige/TrafficLLM](https://github.com/YasodGinige/TrafficLLM) | Extended code for the TrafficGPT work, with LLaMA models. Same name as ZGC-LLM-Safety/TrafficLLM but a different project. | 12 | 2026-05-14 | MIT | Network agent: encrypted traffic | Partly. MIT, 12 stars. |
| [IDP-code/TrafficFormer](https://github.com/IDP-code/TrafficFormer) | Pre-training pipeline from pcap to bursts, with a pre-trained model on Google Drive. | 116 | 2025-01-18 | MIT | Network agent: encrypted traffic | Yes. README is thin. |
| [SNL-UCSB/netFound](https://github.com/SNL-UCSB/netFound) | Foundation model for network telemetry. Takes raw PCAP, pre-trained on UCSB traffic, with checkpoints on Hugging Face. | 42 | 2026-05-15 | MIT | Network agent: flows | Yes. Use the published checkpoints; pre-training used 128 GPUs. |
| [wangtz19/NetMamba](https://github.com/wangtz19/NetMamba) | Traffic classification with pre-trained unidirectional Mamba. | 189 | 2026-04-05 | None found | Network agent: encrypted traffic | Read only. No licence. |
| [NSSL-SJTU/YaTC](https://github.com/NSSL-SJTU/YaTC) | AAAI'23 masked autoencoder traffic transformer. | 158 | 2024-04-29 | None found | Network agent: encrypted traffic | Read only. No licence. |
| [duowuyms/NetLLM](https://github.com/duowuyms/NetLLM) | SIGCOMM 2024 framework that adapts LLMs to networking tasks. | 210 | 2024-12-07 | MIT | Background only | Partly. Networking in general, not security. |
| [lijlansg/TrafficGPT](https://github.com/lijlansg/TrafficGPT) | Road traffic tool built on SUMO and road trip data. Not network traffic. | 180 | 2023-09-17 | GPL-3.0 | None | No. Same name, wrong field. |

#### Network agent: flow and TLS metadata tools
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [nfstream/nfstream](https://github.com/nfstream/nfstream) | Flexible network data analysis framework in Python. | 1,225 | 2026-08-01 | LGPL-3.0 | Network agent: flow features | Yes. LGPL-3.0. |
| [ntop/nDPI](https://github.com/ntop/nDPI) | Deep packet inspection toolkit. | 4,668 | 2026-11-05 | LGPL-3.0 | Network agent: protocol labels | Yes. LGPL-3.0, C library. |
| [FoxIO-LLC/ja4](https://github.com/FoxIO-LLC/ja4) | JA4+ suite of network fingerprinting standards. | 2,159 | 2026-10-06 | FoxIO License 1.1 for the JA4+ tools it lists; JA4 itself not in that list, unverified | Network agent: TLS metadata | Partly. Read the FoxIO licence first. |
| [salesforce/ja3](https://github.com/salesforce/ja3) | SSL client fingerprinting. | 3,097 | 2025-05-01 (archived) | BSD-3-Clause | Network agent: TLS metadata | Partly. Archived. |
| [cisco/mercury](https://github.com/cisco/mercury) | Network metadata capture and analysis. | 522 | 2026-09-23 | BSD-style text (LICENSE) | Network agent: TLS metadata | Partly. Larger C++ tool. |
| [nprint/nprint](https://github.com/nprint/nprint) | Packet representation made for machine learning. | 124 | 2025-12-04 | Apache-2.0 | Network agent: features | Yes. |
| [noise-lab/netml](https://github.com/noise-lab/netml) | Feature extraction and ML from traffic traces. | 76 | 2024-08-01 | Apache-2.0 | Network agent: features | Yes, last commit 2024. |
| [liamdm/FlowTransformer](https://github.com/liamdm/FlowTransformer) | Framework for building transformer-based network intrusion detection. | 108 | 2023-10-17 | AGPL-3.0 | Network agent: flows | Partly. AGPL-3.0, last commit 2023. |
| [ahlashkari/CICFlowMeter](https://github.com/ahlashkari/CICFlowMeter) | Bi-flow generator and analyser for anomaly detection. | 715 | 2022-01-05 | MIT-style text (LICENSE.txt) | Network agent: features | Partly. Last commit 2022, Java. |

#### Network agent: intrusion detection with machine learning
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [ymirsky/Kitsune-py](https://github.com/ymirsky/Kitsune-py) | Online intrusion detection with incremental statistics and an autoencoder ensemble. README warns the Python version is not fast. | 401 | 2026-03-24 | MIT | Network agent: anomaly baseline | Yes. Good baseline. |
| [zeek/zeek](https://github.com/zeek/zeek) | Network analysis framework with logs for connections, DNS, TLS handshakes and SMTP. | 8,177 | 2026-11-04 | BSD-style (COPYING) | Network agent: main sensor | Yes. Best sensor choice. |
| [OISF/suricata](https://github.com/OISF/suricata) | Network IDS, IPS and monitoring engine. | 6,818 | 2026-11-02 | GPL-2.0 | Network agent: rule sensor | Yes, as a separate process. |
| [snort3/snort3](https://github.com/snort3/snort3) | Snort 3 IDS. Includes SnortML, which scores requests for exploit classes. | 3,465 | 2026-07-23 | GPL-2.0 (LICENSE) | Network agent: ML rule sensor | Yes, as a separate process. |
| [stratosphereips/zeek_anomaly_detector](https://github.com/stratosphereips/zeek_anomaly_detector) | Automated anomaly detector for Zeek conn.log files. | 87 | 2026-08-03 | GPL-2.0 | Zeek add-on | Yes, as a separate tool. |
| [zeek-flowmeter/zeek-flowmeter](https://github.com/zeek-flowmeter/zeek-flowmeter) | Zeek script that generates timing, volume and metadata features. | 62 | 2020-11-08 | MIT | Zeek add-on | Partly. Last commit 2020. |
| [NYU-HSRN-Network-Data-Science-Group/AutoZeekWatch](https://github.com/NYU-HSRN-Network-Data-Science-Group/AutoZeekWatch) | Real-time AI anomaly scores for Zeek logs. | 4 | 2024-07-25 | MIT | Zeek add-on | Partly. 4 stars, last commit 2024. |
| [dducktai/suricata-ids-with-ml](https://github.com/dducktai/suricata-ids-with-ml) | Suricata with ML for real-time detection. | 6 | 2025-08-30 | Apache-2.0 | Suricata add-on | Partly. 6 stars. |
| [activecm/rita](https://github.com/activecm/rita) | Detects command-and-control from network traffic. | 668 | 2026-06-17 | GPL-3.0 | Network agent | Yes, as a separate tool. |
| [stamparm/maltrail](https://github.com/stamparm/maltrail) | Malicious traffic detection system. | 8,655 | 2026-11-05 | MIT | Network agent, threat feed | Yes. |
| [cisagov/Malcolm](https://github.com/cisagov/Malcolm) | Analysis suite for PCAP, Zeek logs and Suricata alerts. | 2,585 | 2026-11-03 | Apache-2.0 (LICENSE.txt) | Network agent, dashboard | Partly. Large stack. |
| [Security-Onion-Solutions/securityonion](https://github.com/Security-Onion-Solutions/securityonion) | Free platform for threat hunting and security monitoring. | 4,970 | 2026-11-02 | Elastic License 2.0 (LICENSE) | Network agent, dashboard | Partly. Elastic License 2.0 is not an open-source licence. |
| [wazuh/wazuh](https://github.com/wazuh/wazuh) | Open XDR and SIEM for endpoints and cloud workloads. | 17,580 | 2026-11-04 | AGPL-3.0 engine; some shared libraries GPL-2.0 or AGPL-3.0 (LICENSE, part read) | Server dashboard, host data | Partly. Mixed licence, heavy. |
| [fuchuanpu/HyperVision](https://github.com/fuchuanpu/HyperVision) | Flow interaction graph attack detection. | 204 | 2024-05-06 | GPL-3.0 | Network agent: research | Partly. C++, GPL-3.0. |
| [doriguzzi/lucid-ddos](https://github.com/doriguzzi/lucid-ddos) | Lightweight deep learning for DDoS detection. | 169 | 2023-12-05 | Apache-2.0 | Network agent: research | Yes, narrow use. |
| [Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning](https://github.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning) | IDS with decision tree, random forest, XGBoost and stacking. | 601 | 2026-04-01 | MIT | Network agent: baseline | Yes. |
| [Safe3/uusec-waf](https://github.com/Safe3/uusec-waf) | WAF with ML anomaly detection on HTTP and four semantic engines for SQL, XSS, RCE and LFI. | 1,721 | 2026-11-04 | BSD-2-Clause | Web application attacks | Partly. Shows how the word semantic is used elsewhere. |

- Zeek's own scripts create logs for connections, DNS queries and answers, the SSL/TLS handshake, and SMTP. One sensor therefore covers STL's flow, DNS and TLS metadata inputs — [Zeek protocol scripts](https://github.com/zeek/zeek/tree/master/scripts/base/protocols)
- SnortML loads pre-trained models and returns the probability that input is an exploit. It runs alongside normal rules and was open-sourced in Snort 3.1.82.0 (search result) — [Snort docs](https://docs.snort.org/misc/snort_ml)
- SnortML started with SQL injection, and later coverage adds XSS and command injection. One article says it cannot see links across several requests (search result) — [Stack Overflow Blog](https://stackoverflow.blog/2026/07/06/when-the-sensor-starts-thinking-snortml-agentic-ai-and-the-evolving-architecture-of-intrusion-detection/)
- GitHub searches for Zeek and Suricata with machine learning returned 39 and 60 repositories. Apart from Slips (903 stars) and one antivirus project (256 stars), the top results have under 10 stars — [Zeek search](https://github.com/search?q=zeek+machine+learning&type=repositories); [Suricata search](https://github.com/search?q=suricata+machine+learning&type=repositories)

#### Multi-agent security
AiSOC, Slips and zhadyz/AI_SOC are listed in the first section.

| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Framework for building resilient agents. | 44,508 | 2026-11-05 | MIT | Coordinator | Yes. Good default for the coordinator. |
| [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Framework for agents and multi-agent workflows in Python and .NET. Successor to AutoGen. | 14,545 | 2026-11-05 | MIT | Coordinator | Yes. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | Framework for role-playing autonomous agents. | 60,527 | 2026-11-05 | MIT | Coordinator | Yes. |
| [google/adk-python](https://github.com/google/adk-python) | Python toolkit to build, test and deploy agents. | 22,112 | 2026-11-05 | Apache-2.0 | Coordinator | Yes. |
| [microsoft/autogen](https://github.com/microsoft/autogen) | Multi-agent framework. README says it is archived and no longer maintained, though GitHub does not flag it as archived. | 61,710 | 2026-10-28 | MIT code (LICENSE-CODE); CC-BY-4.0 docs | Coordinator | No for new work. Use Microsoft Agent Framework. |
| [a2aproject/A2A](https://github.com/a2aproject/A2A) | Open protocol for communication between agents. Spec has an Agent Card Signing section. | 26,427 | 2026-11-05 | Apache-2.0 | Agent messaging, signing idea | Yes, if agents need a standard protocol. |
| [FunnyWolf/agentic-soc-platform](https://github.com/FunnyWolf/agentic-soc-platform) | AI SOC: turns SIEM and webhook alerts into cases, runs LLM investigation and enrichment. | 1,224 | 2026-09-29 | None found | Coordinator, dashboard | Read only. No licence. |
| [Sec-Link/Argus-Agentic-SOC-Platform](https://github.com/Sec-Link/Argus-Agentic-SOC-Platform) | AI-native SOC with investigation, workflow automation, alert and incident management, threat intelligence. | 1,176 | 2026-11-03 | Apache-2.0 | Coordinator, dashboard | Yes, as a reference. |
| [bluesaphire76/sovereign-ai-soc](https://github.com/bluesaphire76/sovereign-ai-soc) | Local-first AI SOC with Wazuh, Suricata, DNS context, correlated incidents and human review. | 4 | 2026-09-13 | Apache-2.0 | Coordinator, dashboard | Yes, as a reference. 4 stars. |
| [MahmoudHussienMohamed/Agentic-Network-Monitoring](https://github.com/MahmoudHussienMohamed/Agentic-Network-Monitoring) | Observer, Responder and Consultant agents using fine-tuned Llama 3.2 for network monitoring. | 6 | 2026-01-29 | MIT | Network agent, multi-agent | Yes. Small and readable. Network only. |
| [aaronphifer/triagewall](https://github.com/aaronphifer/triagewall) | Local LLM alert triage for self-hosted SOCs. | 14 | 2026-09-25 | AGPL-3.0 | Coordinator | Partly. AGPL-3.0. |
| [TracecatHQ/tracecat](https://github.com/TracecatHQ/tracecat) | Security automation for teams and AI agents. | 3,890 | 2026-11-05 | AGPL-3.0 | Automation, response | Partly. AGPL-3.0. |
| [Shuffle/Shuffle](https://github.com/Shuffle/Shuffle) | General security automation platform. | 2,472 | 2026-09-28 | AGPL-3.0 | Automation, response | Partly. AGPL-3.0. |
| [socfortress/CoPilot](https://github.com/socfortress/CoPilot) | SOCFortress SOC tool. Its description gives no detail. | 542 | 2026-11-04 | AGPL-3.0 | Dashboard | Partly. AGPL-3.0. Not read in depth. |
| [TheHive-Project/Cortex](https://github.com/TheHive-Project/Cortex) | Observable analysis and active response engine. | 1,645 | 2026-10-20 | AGPL-3.0 | Enrichment | Partly. AGPL-3.0. |
| [TheHive-Project/TheHive](https://github.com/TheHive-Project/TheHive) | Incident response platform, now distributed commercially. | 3,949 | 2025-07-25 (archived) | AGPL-3.0 | Case handling | No. Archived. |
| [aliasrobotics/cai](https://github.com/aliasrobotics/cai) | Cybersecurity AI framework for offensive and defensive automation. README says it is archived and reduced to one commit. | 9,846 | 2026-08-22 (archived) | MIT parts plus proprietary research-use parts | Multi-agent reference | No. Archived, part research-use only. |
| [GreyDGL/PentestGPT](https://github.com/GreyDGL/PentestGPT) | LLM penetration testing framework. | 16,278 | 2026-07-14 | MIT | None | No. Offensive, not defensive. |
| [0x4m4/hexstrike-ai](https://github.com/0x4m4/hexstrike-ai) | MCP server that lets agents run 150+ security tools. | 13,374 | 2026-08-03 | MIT | None | No. Offensive, not defensive. |
| [microsoft/CyberBattleSim](https://github.com/microsoft/CyberBattleSim) | Simulated network for studying automated agents. | 1,805 | 2026-08-25 | MIT | Agent testing | Partly. Simulation only. |

#### Threat intelligence sharing
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [MISP/MISP](https://github.com/MISP/MISP) | Threat intelligence sharing platform. Protected events carry PGP signatures across sync hops. | 6,643 | 2026-11-01 | AGPL-3.0 | Verdict sharing | Yes. AGPL-3.0, so run as a separate service. Closest signed sharing in the field. |
| [OpenCTI-Platform/opencti](https://github.com/OpenCTI-Platform/opencti) | Threat intelligence platform. | 10,265 | 2026-11-05 | Apache-2.0 Community Edition; Enterprise files under their own licence | Verdict storage, dashboard | Partly. Large stack; avoid Enterprise files. |
| [crowdsecurity/crowdsec](https://github.com/crowdsecurity/crowdsec) | IDS, IPS, WAF and bot detection with a crowdsourced IP blocklist. | 15,469 | 2026-10-30 | MIT | Sharing model | Yes. Good model for reputation, but IP-only and central. |
| [stratosphereips/iris](https://github.com/stratosphereips/iris) | P2P network for sharing threat intelligence. Peers can be signed by an organisation key using the orgsig tool. | 2 | 2026-09-11 | MIT | Verdict sharing | Yes. MIT. Fork, 2 stars. |
| [stratosphereips/fides](https://github.com/stratosphereips/fides) | Trust model for threat intelligence sharing in hostile networks. | 1 | 2025-01-14 | AGPL-3.0 | Trust scoring | Partly. AGPL-3.0. Fork, last commit 2025. |
| [stratosphereips/p2p4slips](https://github.com/stratosphereips/p2p4slips) | Demo of the Slips peer-to-peer part, sharing network information between Slips nodes over libp2p. | 1 | 2026-09-29 | Unlicense | Verdict sharing | Partly. Demo code. |
| [JoeRu/federloom](https://github.com/JoeRu/federloom) | Decentralised IP reputation shared between self-hosted servers, with decay over time. | 0 | 2026-10-31 | MIT | Verdict sharing | Partly. MIT, new, 0 stars. Good design to read. |
| [oasis-open/cti-python-stix2](https://github.com/oasis-open/cti-python-stix2) | Python API for STIX 2. | 440 | 2026-02-12 | BSD-3-Clause | Verdict format | Yes. |
| [oasis-open/cti-taxii-server](https://github.com/oasis-open/cti-taxii-server) | Python TAXII 2 server library. | 142 | 2023-06-06 | BSD-3-Clause | Verdict transport | Partly. Last commit 2023. |
| [oasis-open/cti-taxii-client](https://github.com/oasis-open/cti-taxii-client) | Python TAXII 2 client. | 129 | 2023-06-05 | BSD-3-Clause | Verdict transport | Partly. Last commit 2023. |
| [ocsf/ocsf-schema](https://github.com/ocsf/ocsf-schema) | Open security event schema. | 913 | 2026-10-30 | Apache-2.0 | Verdict format | Yes. |
| [intelowlproject/IntelOwl](https://github.com/intelowlproject/IntelOwl) | Manages threat intelligence and enrichment at scale. | 4,798 | 2026-09-02 | AGPL-3.0 | Enrichment | Partly. AGPL-3.0. |
| [yeti-platform/yeti](https://github.com/yeti-platform/yeti) | Forensics intelligence platform and pipeline for incident response teams. | 2,039 | 2026-10-28 | Apache-2.0 | Verdict storage | Yes. |
| [certtools/intelmq](https://github.com/certtools/intelmq) | Collects and processes security feeds. | 1,142 | 2026-04-24 | AGPL-3.0 | Threat feeds | Partly. AGPL-3.0. |
| [AlienVault-OTX/OTX-Python-SDK](https://github.com/AlienVault-OTX/OTX-Python-SDK) | Python SDK for AlienVault OTX. | 402 | 2021-04-02 | Unclear (GitHub cannot classify it) | Threat feeds | Partly. Licence unclear, last commit 2021. |

- MISP protected events: the creator adds PGP instance keys, the event is signed on each sync hop, and receivers reject updates without a valid signature from those keys. Sync is limited to parties who can sign — [MISP 2.4.156 release](https://www.misp-project.org/2022/03/18/MISP.2.4.156.released.html)
- CVE-2026-86408 let any logged-in user read a protected event's signing key. Mend lists a fix in 2.5.46, while OpenCVE says no fix was provided, so the sources conflict (search result) — [Mend](https://www.mend.io/vulnerability-database/CVE-2026-86408/); [OpenCVE](https://app.opencve.io/cve/CVE-2026-86408)
- CrowdSec engines share signals from unmodified Hub scenarios, and custom scenarios are ignored. Free contributors get about 15,000 IPs. The page does not explain how consensus is calculated — [CrowdSec docs](https://docs.crowdsec.net/docs/next/central_api/community_blocklist)
- CACAO 2.0 defines signed playbooks: a JCS canonical form (RFC 8785), embedded or detached signatures, and countersigning — [CACAO v2.0](https://docs.oasis-open.org/cacao/security-playbooks/v2.0/security-playbooks-v2.0.html)
- Signing STIX was an open problem in OASIS discussions from 2017 to 2018, because JSON lacked a canonical form. Interim ideas used a custom x_signature property (search result; the site refused my attempt to open this thread, so check the wording) — [OASIS list, 2018](https://lists.oasis-open.org/archives/cti-users/201811/msg00003.html)

#### Signed verdicts
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [TimothyVang/verdict-dfir](https://github.com/TimothyVang/verdict-dfir) | Forensic agent tools whose runs seal into a hash-chained log, a Merkle root and a signed manifest, checkable offline. Verdicts are SUSPICIOUS, INDETERMINATE or NO_EVIL. | 13 | 2026-07-09 | Apache-2.0 | Signed verdict design | Yes, as a design model. Closest signed AI verdict found, but for forensics. |
| [secure-systems-lab/dsse](https://github.com/secure-systems-lab/dsse) | Dead Simple Signing Envelope: a standard for signing arbitrary data. | 114 | 2026-10-09 | Apache-2.0 | Verdict envelope | Yes. Good fit. |
| [pyca/pynacl](https://github.com/pyca/pynacl) | Python binding to NaCl, including digital signatures. | 1,209 | 2026-11-03 | Apache-2.0 | Signing library | Yes. |
| [pyca/cryptography](https://github.com/pyca/cryptography) | Python crypto primitives and recipes. | 7,834 | 2026-11-05 | Apache-2.0 or BSD, your choice (LICENSE) | Signing library | Yes. |
| [panva/jose](https://github.com/panva/jose) | JWS, JWT and related standards for JavaScript runtimes. | 7,867 | 2026-11-02 | MIT | Signing in the user app | Yes. |
| [jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) | JSON Web Tokens in Python. | 5,722 | 2026-10-14 | MIT | Signing library | Yes. |
| [in-toto/attestation](https://github.com/in-toto/attestation) | Attestation framework for software supply chains. | 389 | 2026-10-21 | Apache-2.0 (LICENSE) | Verdict format idea | Yes, as a pattern. |
| [in-toto/in-toto](https://github.com/in-toto/in-toto) | Framework to protect supply chain integrity. | 1,055 | 2026-08-27 | Apache-2.0 (LICENSE) | Pattern | Partly. |
| [sigstore/cosign](https://github.com/sigstore/cosign) | Signing and transparency for containers and binaries. | 6,413 | 2026-11-05 | Apache-2.0 | Signing models and builds | Yes. |
| [sigstore/rekor](https://github.com/sigstore/rekor) | Software supply chain transparency log. | 1,231 | 2026-11-04 | Apache-2.0 | Verdict log | Partly. Log idea fits; running one adds work. |
| [sigstore/sigstore-python](https://github.com/sigstore/sigstore-python) | Python signing tool for Sigstore. | 338 | 2026-11-04 | Apache-2.0 (LICENSE) | Signing | Yes. |
| [sigstore/model-transparency](https://github.com/sigstore/model-transparency) | Supply chain security for ML models. | 249 | 2026-10-26 | Apache-2.0 | Signing STL's models | Yes. |
| [sigstore/sigstore-a2a](https://github.com/sigstore/sigstore-a2a) | Keyless signing of A2A Agent Cards with Sigstore and SLSA provenance. | 27 | 2026-11-02 | Apache-2.0 | Agent identity | Yes. 27 stars. |
| [transparency-dev/tessera](https://github.com/transparency-dev/tessera) | Go library for tile-based transparency logs. | 257 | 2026-11-05 | Apache-2.0 | Verdict log | Partly. Stretch goal. |
| [google/trillian](https://github.com/google/trillian) | Cryptographically verifiable data store. | 3,761 | 2026-11-02 | Apache-2.0 | Verdict log | Partly. Stretch goal. |
| [microsoft/scitt-ccf-ledger](https://github.com/microsoft/scitt-ccf-ledger) | Supply chain transparency ledger on CCF. | 50 | 2026-11-04 | MIT | Verdict log | No. Too heavy. |
| [digitalbazaar/vc](https://github.com/digitalbazaar/vc) | W3C Verifiable Credentials in JavaScript. | 216 | 2026-02-05 | BSD-3-Clause | Verdict format idea | Partly. |
| [MetapriseAI/OrgKernel](https://github.com/MetapriseAI/OrgKernel) | Agent identity with Ed25519, scoped tokens and a hash-chained audit log. Works with LangGraph and CrewAI. | 2,671 | 2026-07-06 | Apache-2.0 | Agent identity, audit | Partly. 2,671 stars but only 21 commits and 1 issue. |
| [spiffe/spire](https://github.com/spiffe/spire) | Runtime for SPIFFE workload identity. | 2,605 | 2026-11-04 | Apache-2.0 | Agent identity | No. Too heavy for a demo. |
| [maxamin/decentralized-threat-intelligence](https://github.com/maxamin/decentralized-threat-intelligence) | Book-style notes on STIX, MISP, signed attestations, on-chain registries and poisoning resistance. | 0 | 2026-10-23 | Text CC BY-SA 4.0, snippets MIT (README) | Background reading | Yes, to read. 0 stars. |

- The A2A spec has an Agent Card Signing section (8.4), with canonicalisation, signature format and verification parts. I saw no mention of signing task results or messages in the part I read — [A2A specification](https://a2a-protocol.org/latest/specification/)

#### Federated learning
| Repository | What it does | Stars | Last commit | Licence | STL part | Reuse by students |
|---|---|---:|---|---|---|---|
| [flwrlabs/flower](https://github.com/flwrlabs/flower) | Federated AI framework. Moved from adap/flower. Has SecAgg+ secure aggregation and differential privacy. | 7,194 | 2026-11-05 | Apache-2.0 | Federated learning | Yes. Best fit. |
| [securefederatedai/openfederatedlearning](https://github.com/securefederatedai/openfederatedlearning) | OpenFL, an open framework for federated learning. | 844 | 2026-08-25 | Apache-2.0 | Federated learning | Yes. |
| [NVIDIA/NVFlare](https://github.com/NVIDIA/NVFlare) | NVIDIA federated learning runtime. | 1,006 | 2026-11-04 | Apache-2.0 | Federated learning | Partly. Heavier. |
| [OpenMined/PySyft](https://github.com/OpenMined/PySyft) | Data science on data held on someone else's server. | 10,051 | 2026-11-04 | Apache-2.0 | Privacy | Partly. Different model from Flower. |
| [google-parfait/tensorflow-federated](https://github.com/google-parfait/tensorflow-federated) | Framework for computation on decentralised data. Moved from tensorflow/federated. | 2,453 | 2026-11-04 | Apache-2.0 | Federated learning | Partly. Use only if the team already knows it. |
| [FederatedAI/FATE](https://github.com/FederatedAI/FATE) | Industrial federated learning framework. | 6,113 | 2024-11-19 | Apache-2.0 | Federated learning | No. Last commit 2024, heavy. |
| [FedML-AI/FedML](https://github.com/FedML-AI/FedML) | Library for distributed training and federated learning. | 4,071 | 2024-05-13 | Apache-2.0 | Federated learning | No. Last default-branch commit 2024. |
| [secretflow/secretflow](https://github.com/secretflow/secretflow) | Privacy-preserving data analysis and ML. | 2,719 | 2025-11-13 | Apache-2.0 | Privacy | No. Heavy. |
| [stratosphereips/feel_project](https://github.com/stratosphereips/feel_project) | Federated learning code used by Slips. | 3 | 2025-01-14 | GPL-2.0 | Federated network model | Partly. GPL-2.0, last commit 2025. |
| [oqadiSAK/fl-ids](https://github.com/oqadiSAK/fl-ids) | Federated IDS built on Flower and UNSW_NB15. | 35 | 2024-01-13 | None found | Federated network model | Read only. No licence. Good small example. |
| [dino-chiio/fedmse](https://github.com/dino-chiio/fedmse) | Semi-supervised federated IDS for IoT. | 28 | 2025-04-01 | None found | Federated network model | Read only. No licence. |
| [Usman-Khan707/Trust-Aware-Federated-Learning-for-Network-Intrusion-Detection](https://github.com/Usman-Khan707/Trust-Aware-Federated-Learning-for-Network-Intrusion-Detection) | Trust-aware federated IDS on CICIDS-2017 with a dual-head autoencoder. | 15 | 2026-04-12 | None found | Federated model plus trust | Read only. No licence. |
| [ojayballer/ECHOLOCK](https://github.com/ojayballer/ECHOLOCK) | Federated phishing detection with threat sharing through Redis. | 3 | 2026-08-18 | MIT | Federated phishing, sharing | Partly. MIT, 3 stars. |
| [AlihanCelik/federated-phishing-detection](https://github.com/AlihanCelik/federated-phishing-detection) | Federated phishing email detection with defence against label flipping. | 1 | 2026-05-17 | None found | Federated phishing | Read only. No licence. |
| [martinszuc/phishing-emails-detection](https://github.com/martinszuc/phishing-emails-detection) | Federated phishing email detection on Android. | 1 | 2024-05-26 | MIT | Federated phishing, user app | Partly. MIT, Kotlin, last commit 2024. |

- Flower implements SecAgg+ through SecAggPlusWorkflow and secaggplus_mod (search result) — [Flower docs](https://flower.ai/docs/framework/explanation-ref-secure-aggregation-protocols.html)
- Flower supports central and local differential privacy (search result) — [Flower 1.8 announcement](https://flower.ai/blog/2024-04-03-announcing-flower-1.8-release)

### Inferences
- A workable student stack: Zeek for network logs, NFStream and JA4-style fields for flow and TLS features, netFound or ET-BERT for encrypted traffic, small ONNX models plus an LLM for content, LangGraph as coordinator, a DSSE envelope signed with PyNaCl, and MISP for sharing. Flower can be a stretch goal.
- Build the signed verdict yourself. No shared standard for signed AI verdicts turned up. A small JSON schema, canonicalised with JCS and wrapped in DSSE, follows the CACAO and verdict-dfir patterns.
- Treat email and SMS text as hostile input to STL's own LLM. An attacker writes that text, so run a prompt injection check first, using Guardrails or the Protect AI model in the next section.
- For QR codes, decode first and reuse the URL models. Use the fouadtrad approach as an extra signal. This saves building a QR model.
- GPL and AGPL tools (Suricata, Slips, MISP) are fine when run unmodified as separate services, but changing them or copying their code into STL brings their licence terms with it. Repositories with no licence give no right to copy, even when public. Check this with your supervisor if the project may be released or sold.
- Stars need care. OrgKernel has 2,671 stars but 21 commits, decionis/govern has 247 stars and 0 watchers, and nusashield-ai has 44 stars and 1 commit. Commit history and contributors are better signals.
- Read small repositories before running them, and do it in a virtual machine. Several here use install scripts or ship .pkl model files.

### Gaps
- Three names I tried returned NOT_FOUND: code-philia/PhishIntention, ViktorAxelsen/TrafficLLM, and pirocheto/phishing-url-detection on GitHub (the Hugging Face model exists). The real TrafficLLM repository was found by search. These are excluded from the tables.
- Whether STIX 2.1 has any native signature was not confirmed from the specification. The sources found date from 2017 to 2021.
- The exact A2A signature format was not read. Third-party code describes JWS over a JCS form, and I did not confirm this in the specification (search result) — [zeph-a2a source](https://docs.rs/crate/zeph-a2a/latest/source/src/card_signing.rs)
- The Wazuh licence was only partly read, and JA4's own licence, separate from the listed JA4+ tools, was not confirmed.
- No repository was run, so accuracy, install effort and real activity are unknown.
- "Last commit" covers the default branch only. Some projects, such as Slips, show newer pushes on other branches.

## Which pretrained Hugging Face models are worth starting from?

### Takeaway
Start with small Apache or MIT models: urlbert-tiny for URLs, sms-spam-minilm for SMS, the cybersectony DistilBERT for email, Detoxify for toxicity and threats, and netFound for network data. Treat card scores with care: in one published comparison, an email model with 99.58% accuracy on its own test set scored AUC 0.606 on real multi-language smishing, a task it was not built for.

### Cited Findings
Each model link below is the source for its row. Weights are sizes listed by Hugging Face. Downloads are the Hugging Face counter on 2026-11-05. Scores are the publishers' own and were not tested.

#### Phishing: email and mixed content
| Model | Use | Licence | Weights | Downloads / likes | Updated | Card says | Verdict |
|---|---|---|---|---|---|---|---|
| [cybersectony/phishing-email-detection-distilbert_v2.4.1](https://huggingface.co/cybersectony/phishing-email-detection-distilbert_v2.4.1) | Email and URL phishing | Apache-2.0 | safetensors 267.8 MB | 306,434 / 32 | 2024-10-28 | Accuracy 99.58 on its own test set. | Start here for English email. Also has an ONNX copy. |
| [ealvaradob/bert-finetuned-phishing](https://huggingface.co/ealvaradob/bert-finetuned-phishing) | URL, email, SMS, web page | Apache-2.0 | .bin 1.34 GB | 2,195 / 36 | 2024-02-07 | Accuracy 0.9717, false positive rate 0.0249. | Good if one model must cover all forms. Large, and .bin only. |
| [Horizon-Labs/phishing-scam-detector-base](https://huggingface.co/Horizon-Labs/phishing-scam-detector-base) | Multi-language phishing, scam, spam | Apache-2.0 | safetensors 1.23 GB; ONNX 641.1 MB to 1.23 GB (2 files) | 348 / 0 | 2026-10-31 | Real smishing in 3 languages: AUC 0.925, false positive rate 0.110. Machine-translated Urdu SMS: AUC 0.947. Int8 ONNX is 641 MB. Trained on synthetic messages; sees text only. | Best multi-language pick, but new (updated 2026-10-31) and untested by others. |
| [ptouch/phishing-distilbert-cyber207](https://huggingface.co/ptouch/phishing-distilbert-cyber207) | Phishing | None in metadata | safetensors 267.8 MB | 270,385 / 0 | 2026-03-30 | No licence in metadata. | Skip. Many downloads prove nothing. |

#### URLs and domains
| Model | Use | Licence | Weights | Downloads / likes | Updated | Card says | Verdict |
|---|---|---|---|---|---|---|---|
| [CrabInHoney/urlbert-tiny-v4-phishing-classifier](https://huggingface.co/CrabInHoney/urlbert-tiny-v4-phishing-classifier) | URL phishing | Apache-2.0 | safetensors 14.8 MB | 693 / 2 | 2026-01-26 | Accuracy 0.9907, F1 0.9900, 3.69M parameters. | Start here. Small enough for a phone. |
| [CrabInHoney/urlbert-tiny-v4-malicious-url-classifier](https://huggingface.co/CrabInHoney/urlbert-tiny-v4-malicious-url-classifier) | URL: benign, phishing, malware, defacement | Apache-2.0 | safetensors 14.8 MB | 364 / 4 | 2026-01-26 | Accuracy 0.9922; phishing F1 0.9734. | Start here for four classes. |
| [pirocheto/phishing-url-detection](https://huggingface.co/pirocheto/phishing-url-detection) | URL phishing | MIT | ONNX 23.5 MB | 0 / 18 | 2023-12-01 | Linear SVM, ROC AUC 0.9868. Model card links to a GitHub repo that returned NOT_FOUND. | Good small baseline. |
| [kmack/malicious-url-detection](https://huggingface.co/kmack/malicious-url-detection) | URL or domain | Apache-2.0 | safetensors 267.8 MB | 3,616 / 3 | 2024-04-26 | No test metrics captured. | Backup. |
| [r3ddkahili/final-complete-malicious-url-model](https://huggingface.co/r3ddkahili/final-complete-malicious-url-model) | URL, 4 classes | Apache-2.0 | safetensors 438.0 MB | 65 / 14 | 2025-02-27 | 98% validation accuracy, F1 0.965. | Backup; the tiny model is lighter. |
| [protectai/codebert-base-Malicious_URLs-onnx](https://huggingface.co/protectai/codebert-base-Malicious_URLs-onnx) | URL | None in metadata | ONNX 498.9 MB | 3,690 / 5 | 2026-07-09 | No licence in metadata. | Skip unless the licence is cleared. |
| [amahdaouy/DomURLs_BERT](https://huggingface.co/amahdaouy/DomURLs_BERT) | Domain and URL encoder | None in metadata | safetensors 442.5 MB | 681 / 4 | 2026-02-05 | BERT encoder pre-trained for malicious domains and URLs. No licence in metadata. | Useful for DNS names if the licence is cleared. |

#### SMS and smishing
| Model | Use | Licence | Weights | Downloads / likes | Updated | Card says | Verdict |
|---|---|---|---|---|---|---|---|
| [hari-krishna-ai/sms-spam-minilm-l6](https://huggingface.co/hari-krishna-ai/sms-spam-minilm-l6) | SMS spam and scam, with Indian SMS | Apache-2.0 | safetensors 90.9 MB (2 files); ONNX 23.0 MB to 91.0 MB (4 files) | 63 / 0 | 2026-09-17 | Trained on UCI plus Indian scam SMS. F1 0.935 on UCI, 0.999 on India set. Card shows TF-IDF beats it on UCI alone. | Start here. Closest to South Asian SMS, with small ONNX files. |
| [mrm8488/bert-tiny-finetuned-sms-spam-detection](https://huggingface.co/mrm8488/bert-tiny-finetuned-sms-spam-detection) | SMS spam | None in metadata | safetensors 17.6 MB; .bin 17.6 MB | 27,552 / 57 | 2023-03-16 | Validation accuracy 0.98. In Horizon-Labs' test: false positive rate 0.541 on real smishing. | No licence stated. Use for tests only. |
| [mshenoda/roberta-spam](https://huggingface.co/mshenoda/roberta-spam) | Spam messages | MIT | safetensors 498.6 MB; .bin 498.7 MB | 1,218 / 33 | 2025-08-24 | In Horizon-Labs' test: real smishing AUC 0.803, false positive rate 0.332. | Solid MIT option, larger. |
| [rwnliwan/fraud-triage-smishing](https://huggingface.co/rwnliwan/fraud-triage-smishing) | Smishing, English and Indonesian | Apache-2.0 | safetensors 541.3 MB | 94 / 0 | 2026-10-23 | Card reports it failed 2 of 4 pre-set gates for Indonesian, trained on old English SMS. | Do not use. Read the card as a guide to honest testing. |

#### Toxicity, threats and Urdu
| Model | Use | Licence | Weights | Downloads / likes | Updated | Card says | Verdict |
|---|---|---|---|---|---|---|---|
| [unitary/toxic-bert](https://huggingface.co/unitary/toxic-bert) | Toxicity including threats (Detoxify original) | Apache-2.0 | safetensors 438.0 MB; .bin 438.0 MB | 184,211 / 229 | 2024-03-13 | Card warns Hugging Face versions can differ from the Detoxify library. | Start here, through the Detoxify library. |
| [unitary/unbiased-toxic-roberta](https://huggingface.co/unitary/unbiased-toxic-roberta) | Toxicity, reduced identity bias | Apache-2.0 | .bin 498.7 MB | 74,548 / 44 | 2023-08-18 | Detoxify unbiased model. | Good second option. .bin only. |
| [protectai/unbiased-toxic-roberta-onnx](https://huggingface.co/protectai/unbiased-toxic-roberta-onnx) | Same model in ONNX | Apache-2.0 | ONNX 125.5 MB to 498.9 MB (2 files) | 84,978 / 8 | 2026-07-09 | ONNX files, including a 125.5 MB file. | Use for deployment. |
| [unitary/multilingual-toxic-xlm-roberta](https://huggingface.co/unitary/multilingual-toxic-xlm-roberta) | Multi-language toxicity | Apache-2.0 | .bin 1.11 GB | 9,009 / 31 | 2023-08-18 | Detoxify multilingual model. | Large. Server only. |
| [textdetox/bert-multilingual-toxicity-classifier](https://huggingface.co/textdetox/bert-multilingual-toxicity-classifier) | 15 languages | OpenRAIL++ | safetensors 711.4 MB | 51,695 / 6 | 2025-12-08 | Hindi F1 0.7268. Urdu not in the metadata list. | Good for non-English. Check OpenRAIL++ terms. |
| [gravitee-io/distilbert-multilingual-toxicity-classifier](https://huggingface.co/gravitee-io/distilbert-multilingual-toxicity-classifier) | Multi-language toxicity | OpenRAIL++ | safetensors 541.3 MB; ONNX 135.6 MB to 541.4 MB (2 files) | 3,310 / 1 | 2026-05-08 | Has a 135.6 MB quantised ONNX file. | Lightest multi-language option found. |
| [ibm-granite/granite-guardian-hap-38m](https://huggingface.co/ibm-granite/granite-guardian-hap-38m) | English hate, abuse, profanity | Apache-2.0 | safetensors 153.8 MB; .bin 153.8 MB | 1,851 / 48 | 2024-12-19 | 4-layer binary classifier built for low latency. | Good small English filter. |
| [KoalaAI/Text-Moderation](https://huggingface.co/KoalaAI/Text-Moderation) | Hate, violence, harassment, hate/threatening | OpenRAIL | safetensors 556.8 MB; .bin 556.9 MB; ONNX 136.4 MB to 557.2 MB (8 files) | 35,392 / 99 | 2025-01-31 | Labels include threatening content. | Good for threat categories. Check OpenRAIL terms. |
| [facebook/roberta-hate-speech-dynabench-r4-target](https://huggingface.co/facebook/roberta-hate-speech-dynabench-r4-target) | Hate speech | None in metadata | safetensors 498.6 MB; .bin 498.7 MB | 81,050 / 106 | 2023-03-16 | No licence in metadata. | Skip unless the licence is cleared. |
| [martin-ha/toxic-comment-model](https://huggingface.co/martin-ha/toxic-comment-model) | Toxic comments | None in metadata | .bin 267.9 MB | 197,160 / 70 | 2022-05-06 | No licence in metadata. | Skip unless the licence is cleared. |
| [Hate-speech-CNERG/urdu-codemixed-abusive-MuRIL](https://huggingface.co/Hate-speech-CNERG/urdu-codemixed-abusive-MuRIL) | Urdu code-mixed abuse | AFL-3.0 | safetensors 950.3 MB; .bin 950.3 MB | 46 / 0 | 2023-12-23 | Few downloads; no metrics captured. | Test it for Roman Urdu. |
| [syedmuhammadwaqas/roman-urdu-toxic-model](https://huggingface.co/syedmuhammadwaqas/roman-urdu-toxic-model) | Roman Urdu toxicity | MIT | safetensors 1.11 GB | 19 / 0 | 2025-02-25 | Very few downloads; no metrics captured. | Test only. Unproven. |

#### Security text, prompt injection and network data
| Model | Use | Licence | Weights | Downloads / likes | Updated | Card says | Verdict |
|---|---|---|---|---|---|---|---|
| [protectai/deberta-v3-base-prompt-injection-v2](https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2) | Prompt injection in text | Apache-2.0 | safetensors 737.7 MB; ONNX 738.6 MB | 572,873 / 127 | 2026-07-09 | Most downloaded security classifier in this list. | Use in front of STL's LLM. |
| [cisco-ai/SecureBERT2.0-base](https://huggingface.co/cisco-ai/SecureBERT2.0-base) | Security text encoder | Apache-2.0 | safetensors 598.6 MB | 22,035 / 33 | 2025-10-30 | ModernBERT base for security language. | Good encoder for threat text. |
| [jackaduma/SecBERT](https://huggingface.co/jackaduma/SecBERT) | Security text encoder | Apache-2.0 | safetensors 336.4 MB; .bin 336.4 MB | 118,647 / 65 | 2023-06-26 | Fill-mask model. | Older option. |
| [ehsanaghaei/SecureBERT](https://huggingface.co/ehsanaghaei/SecureBERT) | Security text encoder | BigScience OpenRAIL-M | .bin 498.9 MB | 33,969 / 70 | 2025-11-01 | RoBERTa-based. RAIL licence. | Older option. |
| [fdtn-ai/Foundation-Sec-8B](https://huggingface.co/fdtn-ai/Foundation-Sec-8B) | Security LLM | Apache-2.0 | safetensors 16.06 GB in total (4 shards) | 7,954 / 336 | 2025-08-26 | 8B parameters, by Foundation AI at Cisco, built on Llama 3.1 8B. | Only with a good GPU. Check Llama base terms. |
| [snlucsb/netFound-small](https://huggingface.co/snlucsb/netFound-small) | Network encoder from raw PCAP | MIT | safetensors 213.6 MB | 52 / 2 | 2026-03-09 | Hierarchical transformer. Card lists 128 GPUs for pre-training. | Start here for the network agent. |
| [snlucsb/netFound-base](https://huggingface.co/snlucsb/netFound-base) | Network encoder | MIT | safetensors 698.8 MB | 29 / 1 | 2026-03-09 | Same family. | If small is too weak. |
| [snlucsb/netFound-large](https://huggingface.co/snlucsb/netFound-large) | Network encoder | MIT | safetensors 2.65 GB | 22 / 1 | 2026-03-09 | Same family. | Needs strong hardware. |
| [rdpahalavan/bert-network-packet-flow-header-payload](https://huggingface.co/rdpahalavan/bert-network-packet-flow-header-payload) | Packet text to attack class | Apache-2.0 | .bin 263.2 MB | 39 / 24 | 2023-07-22 | Classes include web attack types. Reads header and payload. | Quick demo only. Not for encrypted traffic. |

#### What the model cards warn about
- In a table published by Horizon-Labs, cybersectony scored AUC 0.606 with a 0.880 false positive rate on real smishing, while scoring 0.999 on English phishing and spam email. ealvaradob scored 0.797 and mshenoda 0.803 on the same test. This is one publisher comparing against its own model — [Horizon-Labs card](https://huggingface.co/Horizon-Labs/phishing-scam-detector-base)
- The same card says the model sees text only, not sender reputation, links, attachments or headers, and calls itself one signal among others — [Horizon-Labs card](https://huggingface.co/Horizon-Labs/phishing-scam-detector-base)
- On UCI SMS alone, TF-IDF with logistic regression beat MiniLM by 0.976 F1 to 0.960, and the transformer lost precision on Indian messages when trained only on UCI data — [sms-spam-minilm-l6 card](https://huggingface.co/hari-krishna-ai/sms-spam-minilm-l6)
- One card reports its Indonesian claim failed 2 of 4 gates set in advance, because no public human-labelled Indonesian smishing data exists — [fraud-triage-smishing card](https://huggingface.co/rwnliwan/fraud-triage-smishing)
- Hugging Face warns that loading pickle files can run arbitrary code, and that its scanner is not foolproof. Many .bin weights are pickle-based — [Hugging Face pickle docs](https://huggingface.co/docs/hub/security-pickle)

### Inferences
- Phone-sized models exist for URLs and SMS: urlbert-tiny is 14.8 MB, the pirocheto SVM is 23.5 MB, and sms-spam-minilm has ONNX files from 23 MB. Toxicity models start around 125 MB, so run them on the server or test them carefully on the phone.
- Prefer safetensors or ONNX. Avoid .bin files from unknown publishers, even ones with many downloads.
- Add a TF-IDF baseline for every text task. It is cheap, gives a fair comparison, and the sms-spam-minilm card shows it can win.
- Build a small local test set of real Urdu, Roman Urdu and English scam messages. The cards show that local language is where models fail, and Urdu coverage is thin.
- Use the card scores only to shortlist. Report STL's own numbers on messages the models never saw, including false positives.
- netFound is the only traffic encoder family here with weights on Hugging Face. ET-BERT, NetGPT and TrafficFormer publish theirs on Google Drive, so check those links early in case they break.

### Gaps
- No pretrained quishing model and no ET-BERT copy turned up in Hugging Face search.
- No strong model for threats in the sense of threats to a person was found beyond the toxicity sets. "Threat detection" searches mainly returned image models and tiny uploads.
- "No licence in metadata" means the Hugging Face field is empty. The card text or base model may say more, and I did not read every card in full.
- Foundation-Sec-8B is marked Apache-2.0 but is built on Llama 3.1. Whether Llama terms also apply was not checked.
- Urdu model quality is unknown. The Roman Urdu models have under 50 downloads and I captured no metrics.
- Where a row shows several files, the size is the largest single file, because those files are mostly alternative formats. Foundation-Sec-8B is the exception and shows its total.

## Which commercial products come closest, and what do they cover or miss?

### Takeaway
Darktrace is closest overall because it covers network and email and reports attacks as one incident, followed by Microsoft Defender XDR and Cloudflare One. The pages I read for these three show no signed verdict sharing and no user app for personal messages, while Google and consumer apps cover users' messages but show no network analysis.

### Cited Findings

#### Darktrace
- Covers network, email, cloud, identity, endpoint and OT. The vendor says it "reveals attacks that cross environments as one connected incident" — [Darktrace platform](https://www.darktrace.com/platform)
- Its AI learns each organisation's normal behaviour rather than relying on signatures, and an AI analyst gathers evidence and writes the incident story. The page does not mention consumer SMS or personal devices — [Darktrace platform](https://www.darktrace.com/platform)
- In October 2025 a NEXT agent was added to feed Cyber AI Analyst with endpoint, network, cloud, SaaS, identity and email context (search result, trade press) — [Techzine](https://www.techzine.eu/news/security/135718/darktrace-links-network-and-endpoint-with-next-agent)

#### Microsoft Defender XDR with Security Copilot
- Defender XDR joins alerts from endpoint, email, identity and cloud apps into incidents. Its overview lists no separate network detection product — [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/microsoft-365-defender)
- The Phishing Triage Agent uses LLM analysis to assess intent in user-reported email. Its tools include content analysis, URL and file detonation, screenshot analysis, threat intelligence, and hunting across data sources — [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/phishing-triage-agent)
- It runs only after a user reports an email, and needs Security Copilot capacity plus Defender for Office 365 Plan 2 — [Microsoft Learn](https://learn.microsoft.com/en-us/defender-xdr/phishing-triage-agent)
- Defender for Endpoint embeds Zeek. Those network signals cover connections to and from Windows devices, and Microsoft positions them as a complement to dedicated network tools (search result, 2022-2023) — [Microsoft Tech Community](https://techcommunity.microsoft.com/blog/microsoftdefenderatpblog/enrich-your-advanced-hunting-experience-using-network-layer-signals-from-zeek/3794693)

#### Cloudflare One
- Gateway filters at DNS, network and HTTP layers, and the same platform includes email security using AI against phishing and BEC. Suspicious email links can be rewritten and isolated (search result) — [Cloudflare One docs](https://developers.cloudflare.com/cloudflare-one/)

#### Abnormal AI
- Covers email, identity and AI use, with Microsoft 365, Google Workspace and Slack integrations. Uses behavioural AI and deploys through an API with no MX changes. The page does not mention network traffic analysis — [Abnormal platform](https://abnormal.ai/platform)

#### Google on-device scam detection
- Chrome 137+ uses on-device Gemini Nano on pages that trigger signals such as the keyboard lock API. It extracts signals such as page intent, and Safe Browsing makes the final call, for Enhanced Protection users only — [Google](https://blog.google/security/using-ai-to-stop-tech-support-scams-in/)
- Google Messages checks SMS, MMS and RCS from non-contacts on the device, including conversations that turn suspicious later — [Google](https://blog.google/security/new-ai-powered-scam-detection-features/)
- An opt-in Enhanced protection mode, announced 2026-10-14, uses cloud Gemini in Private AI Compute for unknown senders, and Gemini Nano to judge unfamiliar links — [Google](https://blog.google/security/new-android-scam-protections/)
- Call detection is off by default, runs on device, works on Pixel phones only in listed countries, and Google says not all scam calls can be detected. India is listed; Pakistan is not — [Google support](https://support.google.com/phoneapp/answer/15654065?hl=en)

#### Others checked
- Vectra AI covers network, identity and cloud. The search results show no email content analysis (search result) — [Vectra](https://vectra.ai/products/platform)
- Sublime Security is email only. It uses readable MQL rules, an open rule feed, and AI agents that triage reports and write rules (search result) — [Sublime docs](https://docs.sublime.security/docs/rules-overview)
- McAfee Scam Detector checks texts, email, links, QR codes, social messages and deepfakes (search result) — [McAfee](https://www.mcafee.com/blogs/?p=228419)
- Bitdefender Scamio checks email, texts, images, links and QR codes as a free second-opinion service (search result) — [Bitdefender](https://www.bitdefender.com/blog/hotforsecurity/introducing-scamio-complimentary-scam-detector-and-prevention-service-from-bitdefender/)

### Inferences
- Enterprise and consumer products split the market. The enterprise tools here see networks but not users' personal SMS. The consumer tools here see messages but not flows. STL sits across this gap, which is its clearest selling point.
- The Microsoft agent is the closest match to STL's method: an LLM reads content and can query other signals. It differs by acting only after a report, staying inside a licensed Microsoft estate, and adding no signed output for others.
- Chrome's design is worth copying: a small on-device model extracts signals and a server makes the final call. STL can do the same between its user app and coordinator, which also keeps raw messages on the phone.
- I found no product here that offers verdicts a third party can verify. This is STL's most distinctive feature, and also the one with the least evidence of demand.
- A student project should not compete on coverage or scale. It can compete on openness, explainable fused verdicts, and local language support.

### Gaps
- No independent test supports the vendors' claims. Nearly all sources are their own pages.
- Signed verdict sharing was not found in any product page, but vendors may offer related features that these pages do not show.
- Vectra, Sublime, Cloudflare, McAfee and Bitdefender pages were seen as search results, not opened. Sublime's ADE agent is listed as enterprise beta, and details may have changed.
- Norton Genie and Trend Micro ScamCheck turned up no results in my one search, so their current features are unverified. CrowdStrike, Palo Alto, Cisco and SentinelOne were not checked.
- Separate consumer products from these vendors, such as Microsoft Defender for individuals or Cloudflare's 1.1.1.1 app, were not checked.
- Prices were not researched.
- The Phishing Triage Agent's full release status was not confirmed. The page says its wider alert triage is in preview.
