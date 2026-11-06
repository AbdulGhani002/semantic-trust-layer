# Cross-layer and multi-agent AI security: closest work, research gap, and venues for the Semantic Trust Layer (STL)

Checked on 5 November 2026 through the arXiv API, Crossref, OpenAlex, Semantic Scholar, and venue or publisher pages.

Tags used below:
- **[PR]** peer-reviewed. The record was confirmed in Crossref, Semantic Scholar, or on the venue's own page.
- **[PR-claim]** arXiv preprint whose authors state acceptance at the named venue. I did not find the published record, so treat it as a preprint until you do.
- **[PRE]** arXiv preprint. Not peer-reviewed as far as I could tell.
- **[STD]** published standard. **[DRAFT]** IETF Internet-Draft, which is unreviewed work in progress.
- **[WITHDRAWN]** the author has withdrawn it or asked for withdrawal. Do not cite as evidence.
- "Limit" is my own reading of the abstract or full text unless quoted. "Metadata only" means I confirmed the paper exists but did not read its abstract, so read it before citing.
- All numbers are the authors' own claims taken from abstracts. Nothing was reproduced.
- Author lists longer than eight are cut to "et al." because the lookup returned only the first eight.

## 1. What work combines network-layer and application-layer signals for security detection, and does fusion measurably help?

### Takeaway
Direct evidence is thin and mixed. The best controlled study of cross-layer fusion (5G radio plus network flows) found that at a 1% false-positive rate fusion helped only two of seven models and hurt the other five. Fusing application logs with lower layers has strong peer-reviewed support, but for forensics after the attack, not live detection. I found no study that measures the gain from fusing network-layer and application-layer meaning-based agents.

### Cited Findings

**Studies that measure fusion**
- **[PR-claim]** Hamed Fard, Ilya Komarov, Gerhard Wunder. "Cross-Layer Intrusion Detection in 5G O-RAN: Gains and Limits of Fusing Radio Telemetry with Network Flow Records." arXiv:2606.22450, 2026; states acceptance at IEEE CSR 2026. [arXiv](https://arxiv.org/abs/2606.22450). **Method:** seven architectures, run-disjoint splits, ten seeds, live 5G O-RAN dataset. **Result:** radio features match or beat flow features. Fusion gives selective ROC-AUC gains, but at 1% false-positive rate it improves detection only for GRU and Transformer and reduces it for the other five. The benefit appears only where both single-modality detection rates are below 0.75. A 27 to 46% DoS-to-Benign confusion persists across all 42 configurations. **Limit:** radio plus network layer, with no application layer. This is still the best design template for STL.
- **[PR]** Efstratios Chatzoglou, Georgios Kambourakis, Christos Smiliotopoulos, Constantinos Kolias. "Best of Both Worlds: Detecting Application Layer Attacks through 802.11 and Non-802.11 Features." *Sensors* 22(15):5633, 2022. [DOI](https://doi.org/10.3390/s22155633). **Method:** shallow and deep models on AWID3, testing 802.11 and non-802.11 features apart and together against application-layer attacks. **Result:** up to 96.7% AUC with an engineered feature. **Limit:** a best-case figure on Wi-Fi only. The abstract does not state the gain of the combined set over each set alone.
- **[PRE]** Bo Wang, Imran Khan, Martin White, Natalia Beloff. "Role-Aware Multi-modal federated learning system for detecting phishing webpages." arXiv:2509.22369, 2025. [arXiv](https://arxiv.org/abs/2509.22369). **Method:** federated URL, HTML and image heads with role-aware bucket aggregation on FedProx. **Result:** on TR-OP the fusion head reaches 97.5% accuracy at 2.4% FPR, against 95.5% at 5.9% FPR on the image subset and 95.1% at 4.6% FPR on raw HTML. **Limit:** all inputs are application-layer. There is no network signal.

**Log and provenance fusion (peer-reviewed, forensic)**
- **[PR]** Le Yu, Shiqing Ma, Zhuo Zhang, Guanhong Tao, Xiangyu Zhang, Dongyan Xu, Vincent E. Urias, Han Wei Lin, et al. "ALchemist: Fusing Application and Audit Logs for Precise Attack Provenance without Instrumentation." NDSS 2021. [DOI](https://doi.org/10.14722/ndss.2021.24445). **Method:** Datalog reasoning that couples application logs with audit logs. **Result:** on 15 applications and 14 APT attacks it derives precise provenance graphs with very small overhead and outperforms NoDoze and OmegaLog. **Limit:** host forensics after the fact, not network detection.
- **[PR]** Wajih Ul Hassan, Mohammad A. Noureddine, Pubali Datta, Adam Bates. "OmegaLog: High-Fidelity Attack Investigation via Transparent Multi-layer Log Analysis." NDSS 2020. [DOI](https://doi.org/10.14722/ndss.2020.24270). **Method:** binary analysis models application logging, then grafts those events onto the system provenance graph. **Result:** concise graphs with rich semantics at 4% average runtime overhead. **Limit:** host forensics. The paper's idea of a "semantic gap" between system layers is useful framing for STL.
- **[PR]** Yubo Song, Kanghui Wang, Xin Sun, Zhongyuan Qin, Hua Dai, Weiwei Chen, Bang Lv, Jiaqi Chen. "A multi-source log semantic analysis-based attack investigation approach." *Computers & Security* 150:104303, 2025. [DOI](https://doi.org/10.1016/j.cose.2024.104303). Metadata only.
- **[PRE]** Qizhi Cai, Yangyang Wei, Zhipeng Chen, Shouling Ji, Zhenyuan Li. "Cross-Layer Semantic Flow Reconstruction for Attack Detection in Agentic Systems." arXiv:2603.04469, 2026. [arXiv](https://arxiv.org/abs/2603.04469). **Method:** AScope links agent-level semantics to kernel audit events, and a supervisor LLM looks for flow violations and intent mismatches. **Result:** node F1 85.3% and path F1 66.7% on ten multi-agent scenarios. **Limit:** it protects agent systems themselves and covers application plus OS, not network traffic. This is the closest use of STL's vocabulary.

**Related work that uses one vantage point or infers the other layer**
- **[PR-claim]** Zhibo Dong, Yong Huang, Shubao Sun, Wentao Cui, Zhihua Wang. "BLADE: Behavior-Level Anomaly Detection Using Network Traffic in Web Services." arXiv:2511.05193, 2025; states acceptance at IEEE MSN 2025. [arXiv](https://arxiv.org/abs/2511.05193). **Method:** flow autoencoder, pseudo-operation labels, then a one-class classifier over multi-flow behaviour. **Result:** F1 0.9732 and 0.9801 on a custom set and CIC-IDS2017. **Limit:** infers application behaviour from traffic alone. It shows the problem STL targets: attacks that look benign per flow.
- **[PR]** Noe Marcelo Yungaicela-Naula, Cesar Vargas-Rosales, Jesus Arturo Perez-Diaz. "SDN-Based Architecture for Transport and Application Layer DDoS Attack Detection by Using Machine and Deep Learning." *IEEE Access* 9:108495-108512, 2021. [DOI](https://doi.org/10.1109/ACCESS.2021.3101650). **Method:** multiple ML and DL models with Mininet and ONOS emulation. **Result:** above 99% on test sets; in emulation above 98% for transport DDoS and up to 95% for application-layer DDoS. **Limit:** covers attacks at two layers, but the abstract does not describe fusing two vantage points.
- **[PRE]** Daniyal Ganiuly, Nurzhau Bolatbek, Assel Smaiyl. "Cross-Layer Detection of Wireless Misbehavior Using 5G RAN Telemetry and Operational Metadata." arXiv:2511.21803, 2025. [arXiv](https://arxiv.org/abs/2511.21803). **Method:** 5G SA testbed with an SDR adversary. **Result:** each manipulation leaves a reproducible signature not visible from any single telemetry source. **Limit:** PHY and MAC only; the abstract gives no detection rate.
- **[PRE]** Daniel Adu Worae, Spyridon Mastorakis. "An LLM-Powered AI Agent Framework for Holistic IoT Traffic Interpretation." arXiv:2510.13925, 2025. [arXiv](https://arxiv.org/abs/2510.13925). **Method:** packet captures become semantically enriched records for a RAG agent. **Result:** hybrid retrieval improves BLEU, ROUGE, METEOR and BERTScore. **Limit:** measures text quality of explanations, not detection.
- **[PRE]** Yuqing Wang, Xiao Yang. "Design and implementation of a distributed security threat detection system integrating federated learning and multimodal LLM." arXiv:2502.17763, 2025. [arXiv](https://arxiv.org/abs/2502.17763). **Method:** federated multimodal LLMs over traffic, logs, images and sensors. **Result:** 96.4% accuracy, 4.1 points over baselines, 3.8 s detection. **Limit:** the abstract names only a "10TB distributed dataset". Treat this as weak evidence until its data is checked.
- **[PRE]** Scott Freitas, Jovan Kalajdjieski, Amir Gharib, Robert McCann. "AI-Driven Guided Response for Security Operation Centers with Microsoft Copilot for Security." arXiv:2407.09017, 2024. [arXiv](https://arxiv.org/abs/2407.09017). **Method:** industry ML system inside Microsoft Defender XDR. **Result:** deployed worldwide, and it releases GUIDE: 13M evidences across 1M incidents with analyst triage labels. **Limit:** closed vendor system, but GUIDE is a usable public dataset.
- **[PRE]** Abdelkader El Mahdaouy, Issam Ait Yahia, Soufiane Oualil, Ismail Berrada. "Deep Learning for Contextualized NetFlow-Based Network Intrusion Detection: Methods, Data, Evaluation and Deployment." arXiv:2602.05594, 2026. [arXiv](https://arxiv.org/abs/2602.05594). Survey with "multimodal context" as a taxonomy axis. It warns about temporal leakage, data splitting and weak cross-dataset generalisation.

**Traps: these look relevant but are not**
- Ruizhe Yao, Ning Wang, Zhihui Liu, Peng Chen, Xianjun Sheng. "Intrusion Detection System in the Advanced Metering Infrastructure: A Cross-Layer Feature-Fusion CNN-LSTM-Based Approach." *Sensors* 21(2):626, 2021. [DOI](https://doi.org/10.3390/s21020626). "Cross-layer" here means CNN and LSTM components connected across neural-network layers, not OSI layers. Do not cite it as fusion evidence.
- Rasil Baidar, Sasa Maric, Robert Abbas. arXiv:2509.15555, 2025. [arXiv](https://arxiv.org/abs/2509.15555). "Fuses" a CNN, BiLSTM and autoencoder. That is model fusion, not signal fusion.

**Datasets and evaluation rules STL should expect reviewers to apply**
- **[PR]** Gints Engelen, Vera Rimmer, Wouter Joosen. "Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study." IEEE SPW 2021, pp. 7-12. [DOI](https://doi.org/10.1109/SPW53761.2021.00009). Finds problems in traffic generation, flow construction, feature extraction and labelling.
- **[PR]** Robert Flood, Gints Engelen, David Aspinall, Lieven Desmet. "Bad Design Smells in Benchmark NIDS Datasets." IEEE EuroS&P 2024, pp. 658-675. [DOI](https://doi.org/10.1109/EuroSP60621.2024.00042). Manual analysis of seven highly cited datasets finds six suspect design patterns that can cause severe experimental bias.
- **[PR]** Daniel Arp, Erwin Quiring, Feargus Pendlebury, Alexander Warnecke, Fabio Pierazzi, Christian Wressnegger, Lorenzo Cavallaro, Konrad Rieck. "Dos and Don'ts of Machine Learning in Computer Security." USENIX Security 2022. [Paper page](https://www.usenix.org/conference/usenixsecurity22/presentation/arp). A study of 30 top-venue papers confirms that the pitfalls are common.
- **[PR]** Giovanni Apruzzese, Pavel Laskov, Johannes Schneider. "SoK: Pragmatic Assessment of Machine Learning for Network Intrusion Detection." IEEE EuroS&P 2023, pp. 592-614. [DOI](https://doi.org/10.1109/EuroSP57164.2023.00042). Argues that papers rarely let practitioners judge real value, and it proposes pragmatic assessment.
- **[PR]** Abdullah Alsaedi, Nour Moustafa, Zahir Tari, Abdun Mahmood, Adnan Anwar. "TON_IoT Telemetry Dataset: A New Generation Dataset of IoT and IIoT for Data-Driven Intrusion Detection Systems." *IEEE Access* 8:165130-165150, 2020. [DOI](https://doi.org/10.1109/ACCESS.2020.3022862). Metadata only.
- **[PR]** Mohamed Amine Ferrag, Othmane Friha, Djallel Hamouda, Leandros Maglaras, Helge Janicke. "Edge-IIoTset: A New Comprehensive Realistic Cyber Security Dataset of IoT and IIoT Applications for Centralized and Federated Learning." *IEEE Access* 10:40281-40306, 2022. [DOI](https://doi.org/10.1109/ACCESS.2022.3165809). Metadata only.

### Inferences
- Fusion must be tested, not assumed. Fard et al. show it can lower detection at the low false-positive rates that matter in operations. STL should report each layer alone, then both, at a fixed low false-positive rate such as 1%, with run-disjoint splits.
- Fard's finding that the benefit is confined to weak single-layer models suggests where STL is most likely to win: attacks that look benign at one layer, such as BLADE's behaviour-level attacks. This is a hypothesis to test, not a result.
- "Cross-layer" means at least four things in this literature: OSI layers, radio versus flows, application versus OS, and neural-network layers. STL should define it precisely in its first paragraph.
- STL's current datasets cannot measure fusion as they stand. Section 6 explains why.

### Gaps
- I found no public dataset that pairs network traces with application-layer abuse or fraud content under one set of labels. This is absence from my searches, not proof.
- I found no independent peer-reviewed evaluation of commercial XDR fusion. OpenAlex results for that query were vendor-style or low-quality.
- OpenAlex rate-limited four of my ten fusion queries, and IEEE Xplore and the ACM Digital Library were not searched directly. Peer-reviewed coverage here is good but not complete.

## 2. What exists on multi-agent LLM systems for cyber defence, agentic security operations centres, and autonomous detection and response?

### Takeaway
This area is crowded and moving fast, so "multi-agent beats single-agent" is no longer a new claim. The most important recent finding is negative: LLMs that read attacker-controlled logs can be steered, and in one benchmark every baseline triage approach missed at least 40.4% of attack alerts. Two papers close to this topic have been withdrawn or marked for withdrawal by their authors.

### Cited Findings

**Evaluated multi-agent systems**
- **[PRE]** Saimon Amanuel Tsegai, Alex Kantchelian, Danfeng Yao, Peng Gao. "From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage." arXiv:2610.10608, 2026. [arXiv](https://arxiv.org/abs/2610.10608). **Method:** ALERT-BENCH replays enterprise telemetry through a live SIEM. Five reasoning approaches are compared on 1,247 alerts, then AIDA adds an independent challenger, a judge and an append-only ledger. **Result:** every baseline missed at least 40.4% of attack alerts. AIDA reaches F1 0.958 against 0.371 to 0.744, cuts the false-negative rate to 3.1%, and escalates 18.4% of alerts. **Limit:** one multi-stage attack scenario. This is the strongest evaluation design I found.
- **[PRE]** Bowen Wei, Yuan Shen Tay, Howard Liu, Jinhao Pan, Kun Luo, Ziwei Zhu, Chris Jordan. "CORTEX: Collaborative LLM Agents for High-Stakes Alert Triage." arXiv:2510.00311, 2025. [arXiv](https://arxiv.org/abs/2510.00311). **Method:** behaviour, evidence and reasoning agents, plus a released dataset of step-by-step SOC investigations from production. **Result:** "substantially reduces false positives" over single-agent LLMs; the abstract gives no figure. **Limit:** enterprise log and identity alerts only, with no network-layer agent stated.
- **[PR]** Haohuang Wen, Prakhar Sharma, Vinod Yegneswaran, Ashish Gehani, Phillip Porras, Zhiqiang Lin. "MobiLLM: An Agentic AI Framework for Closed-Loop Threat Mitigation in 6G Open RANs." IEEE MILCOM 2025, pp. 1-6. [DOI](https://doi.org/10.1109/MILCOM64451.2025.11310651) ([arXiv](https://arxiv.org/abs/2509.21634), which lists Sharma first). **Method:** analysis, classification (RAG over MITRE FiGHT and 3GPP) and response agents with guardrails. **Result:** "initial evaluations" show feasibility and reduced response latency. **Limit:** early evaluation; RAN only.
- **[PR]** Tianxiang Xu, Zhichao Wen, Xinyu Zhao, Jun Wang, Yan Li, Chang Liu. "L2M-AID: Autonomous Cyber-Physical Defense by Fusing Semantic Reasoning of Large Language Models with Multi-Agent Reinforcement Learning." IEEE TrustCom 2025, pp. 2198-2203. [DOI](https://doi.org/10.1109/TrustCom66490.2025.00256). **Method:** an LLM acts as a "semantic bridge" that gives state to MAPPO, tested on SWaT and a synthetic set. **Result:** 97.2% detection, over 80% fewer false positives, four times faster response. **Limit:** industrial control only, with partly synthetic data.
- **[PRE]** Arth Bhardwaj, Sia Godika, Yuvam Loonker. "MALCDF: A Distributed Multi-Agent LLM Framework for Real-Time Cyber." arXiv:2512.14846, 2025. [arXiv](https://arxiv.org/abs/2512.14846). **Method:** four LLM agents exchange encrypted, ontology-aligned messages. **Result:** 90.0% accuracy, 85.7% F1, 9.1% FPR, 6.8 s per event. **Limit:** all metrics come from one 50-record stream. Close in shape to STL, far too small as evidence.
- **[PR]** Sebastián R. Castro, Roberto Campbell, Nancy Lau, Octavio Villalobos, Jiaqi Duan, Alvaro A. Cardenas. "Large Language Models are Autonomous Cyber Defenders." IEEE CAI 2025, pp. 1125-1132. [DOI](https://doi.org/10.1109/CAI64502.2025.00195). **Method:** LLM and RL teams in CybORG CAGE 4 with a new communication protocol. **Result:** first study of LLMs in multi-agent autonomous defence, showing strengths and weaknesses of each. **Limit:** simulation.
- **[PRE]** Zefang Liu. "Multi-Agent Collaboration in Incident Response with Large Language Models." arXiv:2412.00652, 2024. [arXiv](https://arxiv.org/abs/2412.00652). Compares centralised, decentralised and hybrid teams. **Limit:** a tabletop card game (Backdoors & Breaches).
- **[PRE]** Zefang Liu, Arman Anwar. "AutoBnB-RAG: Enhancing Multi-Agent Incident Response with Retrieval-Augmented Generation." arXiv:2508.13118, 2025. [arXiv](https://arxiv.org/abs/2508.13118). Retrieval improves decision quality across eight team structures. **Limit:** same game environment.
- **[PR-claim]** Yiran Gao, Kim Hammar, Tao Li. "In-Context Autonomous Network Incident Response: An End-to-End Large Language Model Agent Approach." arXiv:2602.13156, 2026; states 2026 AAAI Summer Symposium. [arXiv](https://arxiv.org/abs/2602.13156). A single 14b model recovers up to 23% faster on incident logs. **Limit:** one agent, offline logs.
- **[PR-claim]** Yiran Gao, Tao Li, Kim Hammar. "Agentic Incident Response through Digital Twin-Enhanced Multiscale Planning." arXiv:2608.02422, 2026; states ESORICS 2026. [arXiv](https://arxiv.org/abs/2608.02422). Combines rollout planning with LLM command generation and a digital twin. It argues that repeated LLM calls are unreliable.
- **[PRE]** Hanlin Jiang, Jionghao Huang, Shaofei Li, Bojia Yu, Peng Jiang, Yuxin Ren, Ning Jia, Yao Guo, et al. "STAIR: Effective Incident Response Using an End-to-End Agentic Planning Framework." arXiv:2608.09524, 2026. [arXiv](https://arxiv.org/abs/2608.09524). Defence score 0.95 on its own 44-case benchmark, and 28.8% lower penalties in CAGE4.

**Multi-agent systems for phishing and fraud (application layer only)**
- **[PRE]** Yinuo Xue, Eric Spero, Meng Wai Woo, Wei Gao, Giovanni Russello. "MultiPhishGuard: An Explainable and Adaptive Multi-Agent LLM System for Phishing Email Detection." arXiv:2505.23803, 2025. [arXiv](https://arxiv.org/abs/2505.23803). Text, URL, metadata and adversarial agents weighted by PPO. **Result:** 97.89% accuracy, 2.73% FPR, 0.20% FNR. **Limit:** public email datasets; no network layer.
- **[PR-claim]** Daiki Chiba, Hiroki Nakano, Takashi Koide. "PhishLumos: An Adaptive Multi-Agent System for Proactive Phishing Campaign Mitigation." arXiv:2509.21772, 2025; states IEEE ICC 2026 and an IEEE Access extension. [arXiv](https://arxiv.org/abs/2509.21772). LLM agents trace shared hosting, certificates and domain registration. **Result:** found 100% of campaigns in the median case, over a week before experts confirmed them. **Limit:** I could not confirm the stated IEEE Access DOI in Semantic Scholar. This is the nearest thing to mixing content with infrastructure evidence.
- **[PR]** Ngoc Tuong Vy Nguyen, Felix D Childress, Yunting Yin. "Debate-Driven Multi-Agent LLMs for Phishing Email Detection." ISDFS 2025. [DOI](https://doi.org/10.1109/ISDFS65363.2025.11012014). Two debating agents and a judge. Mixed-agent teams beat homogeneous teams. **Limit:** email text only.
- **[PRE]** Yichen Chen, Siying Li, Yuhang Liang, Lijun Wang, Renyang Liu. "SAGE: An LLM-driven Self Reflective Agentic Framework for Fraud Detection." arXiv:2606.08146, 2026. [arXiv](https://arxiv.org/abs/2606.08146). Three agents on five fraud datasets. **Result:** average F1 up 40.86% over baselines. **Limit:** offline model optimisation on fraud datasets, not live network data.

**Benchmarks and field evidence**
- **[PR-claim]** Yiran Wu, Mauricio Velazco, Andrew Zhao, Manuel Raúl Meléndez Luján, Srisuma Movva, Yogesh K Roy, Quang Nguyen, Roberto Rodriguez, et al. "ExCyTIn-Bench: Evaluating LLM agents on Cyber Threat Investigation." arXiv:2507.14201, 2025; states ICML 2026. [arXiv](https://arxiv.org/abs/2507.14201). A controlled Azure tenant with 57 Sentinel log tables and 7,542 questions.
- **[PRE]** Lehan Wang, Boli Chen, Ruixue Ding, Pengjun Xie, Jinwei Huang, Zhendong Liu, Shuo Wang, Tao Lei, et al. "SecRespond: Benchmarking AI Agents for Real-World Post-Compromise Incident Response." arXiv:2607.26791, 2026. [arXiv](https://arxiv.org/abs/2607.26791). 23 models on 10 cyber ranges. **Result:** no model achieved complete detection and remediation on any single range.
- **[PRE]** Lauren Deason, Adam Bali, Ciprian Bejean, Diana Bolocan, James Crnkovich, Ioana Croitoru, Krishna Durai, Chase Midler, et al. "CyberSOCEval: Benchmarking LLMs Capabilities for Malware Analysis and Threat Intelligence Reasoning." arXiv:2509.20166, 2025. [arXiv](https://arxiv.org/abs/2509.20166). Metadata and partial abstract only.
- **[PRE]** Yicheng Cai, Mitchell John DeStefano, Guodong Dong, Pulkit Handa, Peng Liu, Tejas Singhal, Peiyu Tseng, Winston Jen White. "Design Principles for the Construction of a Benchmark Evaluating Security Operation Capabilities of Multi-agent AI Systems." arXiv:2603.28998, 2026. [arXiv](https://arxiv.org/abs/2603.28998). States that no systematic benchmark for coordinated multi-task blue-team AI exists. **Limit:** conceptual design.
- **[PRE]** James Bono, Justin Grana, Alec Xu. "Generative AI and Security Operations Center Productivity: Evidence from Live Operations." arXiv:2411.03116, 2024. [arXiv](https://arxiv.org/abs/2411.03116). **Result:** adoption is associated with a 30.13% lower mean time to resolution. **Limit:** observational; the authors say confounders prevent causal claims.
- **[PR]** Ahmad Mohsin, Helge Janicke, Ahmed Ibrahim, Iqbal H. Sarker, Seyit Camtepe. "A Unified Framework for Human-AI Collaboration in Security Operations Centers with Trusted Autonomy." *ACM Transactions on Internet Technology* 26(4):1-34, 2026. [DOI](https://doi.org/10.1145/3837073). Five autonomy levels mapped to human roles and trust thresholds. **Limit:** a framework, not a detection result.
- **[PR]** Joyjit Roy, Samaresh Kumar Singh. "AgentSOC: A Multi-Layer Agentic AI Framework for Security Operations Automation." IEEE ICAIC 2026, pp. 1-7. [DOI](https://doi.org/10.1109/ICAIC67076.2026.11395783). **Limit:** the abstract says "conceptually evaluated". "Multi-layer" here means software layers.

**LLMs at the network layer**
- **[PR]** Paul R.B. Houssel, Siamak Layeghy, Priyanka Singh, Marius Portmann. "eX-NIDS: A framework for explainable network intrusion detection leveraging Large Language Models." *Computers and Electrical Engineering* 129:110826, 2026. [DOI](https://doi.org/10.1016/j.compeleceng.2025.110826). The LLM explains NIDS alerts with flow context and CTI. **Limit:** explanation, not detection.
- **[PRE]** Tianyu Cui, Xinjie Lin, Sijia Li, Miao Chen, Qilei Yin, Qi Li, Ke Xu. "TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation." arXiv:2504.04222, 2025. [arXiv](https://arxiv.org/abs/2504.04222). Partial abstract read.
- **[PRE]** Thusitha Dayaratne, Ngoc Duy Pham, Viet Vo, Shangqi Lai, Sharif Abuadbba, Hajime Suzuki, Xingliang Yuan, Carsten Rudolph. "Robust Anomaly Detection in O-RAN: Leveraging LLMs against Data Manipulation Attacks." arXiv:2508.08029, 2025. [arXiv](https://arxiv.org/abs/2508.08029). LLMs stay up under hypoglyph attacks, with latency under 0.07 s. **Limit:** the authors say detection accuracy "requires further improvements". Same authors: "From Description to Detection" ([arXiv:2510.06530](https://arxiv.org/abs/2510.06530)), where detection depends on the semantic completeness of the attack description.
- **[PR-claim]** Joshua Moore, Aly Sabri Abdalla, Prabesh Khanal, Vuk Marojevic. "Integrated LLM-Based Intrusion Detection with Secure Slicing xApp for Securing O-RAN-Enabled Wireless Network Deployments." arXiv:2504.00341, 2025; states IEEE ICC 2025. [arXiv](https://arxiv.org/abs/2504.00341).
- **[PR]** Syed Mhamudul Hasan, Alaa M. Alotaibi, Sajedul Talukder, Abdur R. Shahid. "Distributed Threat Intelligence at the Edge Devices: A Large Language Model-Driven Approach." IEEE COMPSAC 2024, pp. 1496-1497. [DOI](https://doi.org/10.1109/COMPSAC61105.2024.00206). Proposes peer-to-peer knowledge sharing among edge devices. **Limit:** a two-page paper.
- **[PRE]** Survey: Shuo Yang, Xinran Zheng, Xinchen Zhang, Jinfeng Xu, Jinze Li, Donglin Xie, Weicai Long, Edith C. H. Ngai. "Large Language Models for Network Intrusion Detection Systems: Foundations, Implementations, and Future Directions." [arXiv:2507.04752](https://arxiv.org/abs/2507.04752), 2025. Also Yaokai Feng, Kouichi Sakurai, [arXiv:2510.23313](https://arxiv.org/abs/2510.23313), 2025.

**Attacks on these systems (the main risk for STL)**
- **[PRE]** Rabimba Karanjai, Yang Lu, Hemanth Hegadehalli Madhavarao, Lei Xu, Weidong Shi. "Context Contamination in LLM Analysis of Network Security Logs: Poison with Passive Prompt Injection and Mitigation Evaluation." arXiv:2607.14493, 2026. [arXiv](https://arxiv.org/abs/2607.14493). **Method:** LogInject-1.0 benchmark, 12,847 log entries with 2,569 adversarial. **Result:** up to 88.2% attack success; Context Stitching across entries reaches 76.4%; layered defences cut attacks by 90.4%, with 8.4% residual. **Limit:** the authors conclude this is an inherent confused-deputy problem.
- **[PRE]** Rohan Pandey, Archit Bhujang. "Poisoning the Watchtower: Prompt Injection Attacks Against LLM-Augmented Security Operations Through Adversarial Log Content." arXiv:2605.24421, 2026. [arXiv](https://arxiv.org/abs/2605.24421). **Result:** persona hijacks suppress 68% of malicious logs under a naive classifier; summarisation reaches 96% injection success undefended; the strongest defence still leaves 11.8%. **Limit:** one model (gpt-4o-mini).
- **[PRE]** Max Landauer, Florian Skopik, Markus Wurzenberger, Franciszek Górski, Mateusz Krzysztoń. "Just Testing, Move Along: Evasion of LLM-based System Log Interpretation by Prompt Injection." arXiv:2607.24174, 2026. [arXiv](https://arxiv.org/abs/2607.24174). Malicious traces get classified as benign, but LLM explanations often reveal the manipulation.
- **[PRE]** Haowen Dai, Alejandro Guerra-Manzanares. "StateFence: Task-State Protection Against Evidence-Chain Contamination in Blue-Team LLM Agents." arXiv:2611.02605, 2026. [arXiv](https://arxiv.org/abs/2611.02605). Injected text spreads through triage as locally plausible decisions; a string can be an attack for one task and evidence for another.
- **[PRE]** Anna Gazani, Spyridon Kounoupidis, Panagiotis Katsaros, Nikolaos Kekatos, Grigorios Tsoumakas, Georgios Koutidis. "Architecting the Secure AI-SOC: A Neurosymbolic Framework for Pipeline Integrity and Threat Mitigation." arXiv:2609.10707, 2026. [arXiv](https://arxiv.org/abs/2609.10707). SIEM decoders plus NeMo Guardrails.
- **[PRE]** Harold Triedman, Rishi Jha, Vitaly Shmatikov. "Multi-Agent Systems Execute Arbitrary Malicious Code." arXiv:2503.12188, 2025. [arXiv](https://arxiv.org/abs/2503.12188). **Result:** web content causes arbitrary code execution in 58 to 90% of trials with GPT-4o, and it works even if individual agents resist prompt injection. **Limit:** I could not confirm a peer-reviewed venue.
- **[PR]** Donghyun Lee, Mo Tiwari, Brando Miranda. "Prompt Infection: LLM-to-LLM Prompt Injection within Multi-agent Systems." Lecture Notes in Computer Science, pp. 511-520, 2026. [DOI](https://doi.org/10.1007/978-3-032-16092-8_28) ([arXiv](https://arxiv.org/abs/2410.07283)). Malicious prompts self-replicate across agents. This matters directly for agents that share verdicts.
- **[PRE]** Shaswata Mitra, Raj Patel, Subash Neupane, Sudip Mittal, Md Rayhanur Rahman, Shahram Rahimi. "Where Rules End and Judges Begin: Measuring the Judgment Boundary in Multi-Agent Systems Security." arXiv:2610.07657, 2026. [arXiv](https://arxiv.org/abs/2610.07657). **Method:** 28 deterministic checks, then four judges. **Result:** attack success falls from about 30% to about 3%, and 78% of blocked attacks are stopped by deterministic checks. A risk-score gate wrongly approves most attack proposals.
- **[PRE]** Shaswata Mitra, Raj Patel, Sudip Mittal, Md Rayhanur Rahman, Shahram Rahimi. "AgenticCyOps: Securing Multi-Agentic AI Integration in Enterprise Cyber Operations." arXiv:2603.09134, 2026. [arXiv](https://arxiv.org/abs/2603.09134). Finds tool orchestration and memory management are the two main trust boundaries. **Limit:** a design analysis.
- **[PRE]** Pallavi Zambare, Venkata Nikhil Thanikella, Ying Liu. "Securing Agentic AI: Threat Modeling and Risk Analysis for Network Monitoring Agentic AI System." arXiv:2508.10043, 2025. [arXiv](https://arxiv.org/abs/2508.10043). Confirms replay denial of service and memory poisoning in a prototype.
- **[PRE]** Zhenpeng Li. "Controllability-Aware Adversarial Examples Against LLM-Based Network Traffic Classifiers." arXiv:2607.07739, 2026. [arXiv](https://arxiv.org/abs/2607.07739). Splits flow features into directly, indirectly and un-controllable by the attacker. **Result:** LLMs show higher attack success than the averaged ML baseline on all five datasets.

**Surveys**
- **[PRE]** Sahaya Jestus Lazer, Kshitiz Aryal, Maanak Gupta, Elisa Bertino. "A Survey of Agentic AI and Cybersecurity: Challenges, Opportunities and Use-case Prototypes." [arXiv:2601.05293](https://arxiv.org/abs/2601.05293), 2026.
- **[PR-claim]** Vaishali Vinay. "The Evolution of Agentic AI in Cybersecurity: From Single LLM Reasoners to Multi-Agent Systems and Autonomous Pipelines." [arXiv:2512.06659](https://arxiv.org/abs/2512.06659), 2025; states ICAIC 2026.

**Do not cite as evidence**
- **[WITHDRAWN]** Philip Drammeh. "Multi-Agent LLM Orchestration Achieves Deterministic, High-Quality Decision Support for Incident Response." arXiv:2511.15755. [arXiv](https://arxiv.org/abs/2511.15755). The author's note says a code audit found the multi-agent arm's action list was a source constant, not model output, so the quality results are withdrawn. Its abstract still shows "100% actionable" and "80 times" claims, so it is easy to mis-cite.
- **[WITHDRAWN]** Saeid Jamshidi. "Semantic Multi-Agent Intrusion Detection for IoT: Zero-Day and Adversarial Threats with Risk-Aware Reasoning." arXiv:2606.10323. [arXiv](https://arxiv.org/abs/2606.10323). This is the closest match to STL's wording. The author's note says the manuscript "does not sufficiently substantiate all conclusions" and requests withdrawal.

### Inferences
- A claim that "multiple cooperating agents beat one" adds nothing new. Use it as a baseline.
- Pure "meaning instead of rules" looks like the wrong design. DEFER's 78% figure suggests rules should come first, with LLM judgement for what is left. AgentTrust (section 3) gives the other half of the argument.
- An LLM reading packet or log text is reading attacker-chosen input. Any STL design that passes raw fields to an LLM agent inherits the LogInject and Watchtower attacks. If STL uses compact classifiers instead (see section 6), the matching threat is adversarial evasion, as in Li 2026, not instruction injection.
- Reported per-event latency ranges from under 0.07 s in the O-RAN study to 6.8 s in MALCDF. A network-layer agent probably has to work on flows or alerts, not on every packet.
- The two withdrawals show that strong agent claims are getting checked. Keep code and raw results ready for audit.

### Gaps
- CORTEX's numeric results were not read. The abstract gives none, and my keyword scan of the full text did not extract them.
- The peer-review status of Triedman et al. and the IEEE Access record of PhishLumos are unconfirmed.
- No long-term field study of a multi-agent LLM detector was found.

## 3. What exists on an AI trust layer or semantic security layer for networks, including 6G semantic security and AI-native network security?

### Takeaway
"Semantic" and "trust layer" are in heavy use, but mostly for other things: 6G semantic communication encoders, agent identity, and semantic routing. These are surveys, visions and agent-governance papers. I found no evaluated "semantic trust layer" that detects threats in live traffic. Standards bodies are also fragmented here.

### Cited Findings

**6G semantic communication security (meaning-preserving transmission)**
- **[PR]** Rui Meng, Song Gao, Dayu Fan, Haixiao Gao, Yining Wang, Xiaodong Xu, Bizhu Wang, Suyu Lv, et al. "A survey of secure semantic communications." *Journal of Network and Computer Applications* 239:104181, 2025. [DOI](https://doi.org/10.1016/j.jnca.2025.104181) ([arXiv](https://arxiv.org/abs/2501.00842)). A 160-page survey of threats and defences across SemCom systems.
- **[PR]** Shaolong Guo, Yuntao Wang, Ning Zhang, Zhou Su, Tom H. Luan, Zhiyi Tian, Xuemin Shen. "A Survey on Semantic Communication Networks: Architecture, Security, and Privacy." *IEEE Communications Surveys & Tutorials* 27(5):2860-2894, 2025. [DOI](https://doi.org/10.1109/COMST.2024.3516819). Covers multi-agent semantic networks, a topic the authors call largely unexplored.
- **[PRE]** Lan Zhang, Chengsi Liang, Zeming Zhuang, Yao Sun, Fang Fang, Xiaoyong Yuan, Dusit Niyato. "Secure Semantic Communications via AI Defenses: Fundamentals, Solutions, and Future Directions." arXiv:2602.22134, 2026. [arXiv](https://arxiv.org/abs/2602.22134). Semantic failures can occur "even when lower-layer transmission reliability and cryptographic protection remain intact".
- **[PR]** Fabian Chukwudi Ogenyi, Chinyere Nneoma Ugwu, Okechukwu Paul-Chima Ugwu. "A comprehensive review of AI-native 6G: integrating semantic communications, reconfigurable intelligent surfaces, and edge intelligence for next-generation connectivity." *Frontiers in Communications and Networks* 6:1655410, 2025. [DOI](https://doi.org/10.3389/frcmn.2025.1655410). Notes that semantic attacks may distort meaning "without altering its bit representation".
- **[PRE]** Jiayi He, Xiaofeng Luo, Jiawen Kang, Hongyang Du, Zehui Xiong, Ci Chen, Dusit Niyato, Xuemin Shen. "Toward Mixture-of-Experts Enabled Trustworthy Semantic Communication for 6G Networks." arXiv:2409.15695, 2024. [arXiv](https://arxiv.org/abs/2409.15695). Gating network routes to attack-specific experts.

**AI-native and agentic 6G security**
- **[PRE]** Bidushi Barua, Ahsan Khan, Kangfeng Ye, Panagiotis Papanastasiou, Yifan Liu, Mohit Bidikar, Anthony Moulds, Julie McCann, et al. "Toward a Unified Security and Privacy Framework for AI-Native 6G Networks." arXiv:2607.01019, 2026. [arXiv](https://arxiv.org/html/2607.01019v1). Cross-layer threat taxonomy. States that ETSI SAI, O-RAN and AI-RAN "address AI security independently" and that there is "No security baseline for autonomous AI agents".
- **[PR]** Satyam Gaba, Devanshu Motwani, Siva Sai, Vineet Suri, Vikas Ranjan, Vinay Chamola. "Secure Agentic AI and Multimodal Intelligence in 6G Communication Systems." *IEEE Open Journal of the Communications Society* 7:8926-8944, 2026. [DOI](https://doi.org/10.1109/OJCOMS.2026.3717323). Reviews prompt and memory defences and inter-agent trust mechanisms.
- **[PR]** Hailin Feng, Thippa Reddy Gadekallu, Yuchao Xia, Yongkang Zhao, Zhihao Wen, Jijing Cai, Pronaya Bhattacharya, Kai Fang, et al. "Agentic AI Security in 6G Networks: A Survey of Emerging Attack Vectors, Vulnerabilities, and Defenses." *IEEE Open Journal of the Communications Society* 7:6334-6368, 2026. [DOI](https://doi.org/10.1109/OJCOMS.2026.3700939). A search snippet says governance "still lacks deep coupling" with AI-native 6G. Abstract not fully read.
- **[PRE]** Mohamed Amine Ferrag, Abderrahmane Lakas, Merouane Debbah. "6G Needs Agents: Toward Agentic AI-Native Networks for Autonomous Intelligence." arXiv:2605.01546, 2026. [arXiv](https://arxiv.org/abs/2605.01546). Proposes LLM agents in "a semantic control plane layered above deterministic 3GPP infrastructure", and finds a tradeoff between reasoning capability and efficiency.
- **[PRE]** Sunder Ali Khowaja, Kapal Dev, George C. Alexandropoulos. "Z²-ACT: End-to-End Verifiable Agentic Intent Control for Open 6G RAN." arXiv:2608.21049, 2026. [arXiv](https://arxiv.org/abs/2608.21049). **Method:** typed intent contracts, adversarial intent check, and a zero-knowledge proof for each commit, tested on ColO-RAN. **Result:** better actuation filtering and attack resilience at modest cost. **Limit:** near-real-time control is trace-driven. It secures control actions, not detection verdicts. Very close in spirit to STL.
- **[PRE]** Qiang Duan. "AI Agent Communications in AI-Native 6G Network: Status, Challenges and Opportunities." arXiv:2607.18138, 2026. [arXiv](https://arxiv.org/html/2607.18138v1). Suggests the UPF could act as a trusted local DID resolver. **Limit:** a vision paper.
- **[PRE]** Bilal Hussain, Muhammad Bilal, Tan Li, Haris Pervaiz, Xiao Tang, Qinghe Du, Fawad Ahmad, Muhammad Azhar, et al. "AI-Native Closed-Loop Security for 6G-Enabled Cyber-Physical Systems: From Edge Detection to Network-Wide Mitigation." arXiv:2606.08173, 2026. [arXiv](https://arxiv.org/abs/2606.08173). PRISMA survey of 128 studies, with per-slice latency contracts.
- **[PRE]** Pau Baguer, J. Xavier Salvat Lozano, Gines Garcia-Aviles, Xavier Costa-Pérez. "C-RE-ACT: Causal RE-ACTing Agent for O-RAN Forensic Triage." arXiv:2607.25828, 2026. [arXiv](https://arxiv.org/abs/2607.25828). 140 experiments on a physical testbed. Separates attacks from operational faults.
- **[PR-claim]** Sotiris Chatzimiltis, Mahdi Boloursaz Mashhadi, Mohammad Shojafar, Merouane Debbah, Rahim Tafazolli. "Agentic AI for 6G: A New Paradigm for Autonomous RAN Security Compliance." arXiv:2512.12400, 2025; states IEEE Communications Standards Magazine. [arXiv](https://arxiv.org/abs/2512.12400).
- **[PRE]** Xu Chen, Wei Feng, Ning Ge, Yan Zhang. "Zero Trust Architecture for 6G Security." arXiv:2203.07716, 2022. [arXiv](https://arxiv.org/abs/2203.07716). Software-defined ZTA across control domains, simulation only.
- **[PR]** Van-Linh Nguyen, Po-Ching Lin, Bo-Chao Cheng, Ren-Hung Hwang, Ying-Dar Lin. "Security and Privacy for 6G: A Survey on Prospective Technologies and Challenges." *IEEE Communications Surveys & Tutorials* 23(4):2384-2428, 2021. [DOI](https://doi.org/10.1109/COMST.2021.3108618). Background. Metadata only.

**Work actually titled "trust layer" or "semantic gateway"**
- An arXiv title search for "trust layer" returned six papers, all 2026. Five are about AI agents and one is about plasma physics; none is a network detection layer. [Search](https://export.arxiv.org/api/query?search_query=ti:%22trust%20layer%22).
- **[PRE]** Chenglin Yang. "AgentTrust: A Self-Improving Trust Layer for AI-Agent Actions." arXiv:2606.08539, 2026. [arXiv](https://arxiv.org/abs/2606.08539). **Result:** a hand-written rule pack lifts held-out accuracy only from 48 to 56% and moves semantic categories by 0 points, while an LLM judge handles those categories. **Limit:** agent shell and cloud actions, not traffic. Strongest support for "rules cannot see intent".
- **[PRE]** Akshay Mittal, Elyson De La Cruz. "Agent Name Service (ANS): A Proof-of-Concept Trust Layer for Secure AI Agent Discovery, Identity, and Governance in Kubernetes." arXiv:2604.26997, 2026. [arXiv](https://arxiv.org/abs/2604.26997). Also Kolawole Quadri, "KYA", [arXiv:2605.25376](https://arxiv.org/abs/2605.25376), and Mohammadreza Sediqin et al., "A Trust Layer for Agent Evaluation", [arXiv:2610.07274](https://arxiv.org/abs/2610.07274). All concern agent identity or evaluation.
- **[PRE]** Ignacio Peyrano. "From CRUD to Autonomous Agents: Formal Validation and Zero-Trust Security for Semantic Gateways in AI-Native Enterprise Systems." arXiv:2604.25555, 2026. [arXiv](https://arxiv.org/abs/2604.25555). An MCP gateway for enterprise APIs.

**IETF work (semantic here means routing and agent communication, not detection)**
- **[DRAFT]** draft-li-semantic-routing-architecture is expired. [Datatracker](https://datatracker.ietf.org/doc/draft-li-semantic-routing-architecture/). draft-farrel-rtgwg-intro-to-semantic-networking is expired. [Datatracker](https://datatracker.ietf.org/doc/draft-farrel-rtgwg-intro-to-semantic-networking/). draft-cui-semantic-routing-ai-agent-communication is active, and describes application-layer semantic routing. [Datatracker](https://datatracker.ietf.org/doc/draft-cui-semantic-routing-ai-agent-communication/).
- **[DRAFT]** draft-yang-dmsc-gateway-semantic-layer-02 and draft-ni-a2a-ai-agent-security-requirements-02 exist, but I saw only their names in search listings. [Search 1](https://datatracker.ietf.org/doc/search?name=gateway-semantic&activedrafts=on&olddrafts=on&sort=), [Search 2](https://datatracker.ietf.org/doc/search?name=agent-security&activedrafts=on&olddrafts=on&sort=).

**Name check for "Semantic Trust Layer"**
- I found no product or standard with this exact name in network security. The phrase overlaps with the "Trust" layer of the old Semantic Web stack ([W3C](https://www.w3.org/2001/12/semweb-fin/w3csw), [Springer chapter, 2006](https://link.springer.com/chapter/10.1007/3-540-31590-X_5)), Salesforce's "A2A Semantic Layer" ([blog](https://www.salesforce.com/blog/agent-to-agent-interaction/)), and a dbt certifier called semantic-trust ([GitHub](https://github.com/rj1224/semantic-trust)).

### Inferences
- "Semantic" has three different meanings in these sources: (a) 6G semantic communication, which protects meaning during transmission; (b) semantic routing, which moves traffic by content or intent; (c) LLM reasoning about intent. STL is (c). Citing (a) as direct prior art would be an error that a reviewer will catch, though (a) supports a motivation: attacks can change meaning without changing bits.
- A 6G claim needs a RAN-level test. Without one, 6G belongs in future work, not in the title.
- Expect a keyword clash with the Semantic Web "trust layer" literature. A clearer paper title would reduce confusion.

### Gaps
- No evaluated system was found that matches "AI trust layer for live network detection". This reflects my searches, not proof of absence.
- I did not read ETSI, 3GPP or O-RAN Alliance documents directly. The fragmentation claim rests on Barua et al.
- I did not read the IETF draft texts beyond their abstracts.

## 4. What exists on signed verdicts and decentralised threat intelligence sharing, such as STIX and TAXII, COSE, and trust between operators without a central authority?

### Takeaway
The building blocks are mature and standardised, and blockchain threat-sharing papers are plentiful. I found no paper that defines a signed detection verdict and evaluates it between distrusting operators. Two findings should reshape STL's design: threat feeds fail mostly on quality rather than authenticity, and one 2026 preprint found that signature-only protocols accept most lies from a compromised agent.

### Cited Findings

**Standards**
- **[STD]** RFC 9052, "CBOR Object Signing and Encryption (COSE): Structures and Process", STD 96, August 2022. [RFC](https://www.rfc-editor.org/rfc/rfc9052.html). RFC 9053, "COSE: Initial Algorithms". [RFC](https://www.rfc-editor.org/info/rfc9053). RFC 8392, "CBOR Web Token (CWT)", May 2018. [RFC](https://www.rfc-editor.org/info/rfc8392).
- **[STD]** RFC 9943, "An Architecture for Trustworthy and Transparent Digital Supply Chains" (SCITT), Standards Track, June 2026. [RFC](https://www.rfc-editor.org/rfc/rfc9943.html). Signed Statements are COSE objects and the Receipt sits in the COSE envelope. [Draft text](https://ietf-wg-scitt.github.io/draft-ietf-scitt-architecture/draft-ietf-scitt-architecture.html). Scope is supply chains, not detection.
- **[STD]** RFC 9334, "Remote ATtestation procedureS (RATS) Architecture", Informational, January 2023. [RFC](https://www.rfc-editor.org/rfc/rfc9334.html). RFC 9711, "The Entity Attestation Token (EAT)", Standards Track, April 2025. [RFC](https://www.rfc-editor.org/rfc/rfc9711.html).
- **[STD]** RFC 9132, "Distributed Denial-of-Service Open Threat Signaling (DOTS) Signal Channel Specification", Standards Track, September 2021. [RFC](https://www.rfc-editor.org/rfc/rfc9132.html). An existing standard for signalling attacks between domains.
- **[STD]** STIX 2.1, OASIS Standard, 10 June 2021. [Spec](https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html). TAXII 2.1, OASIS Standard, 10 June 2021. [Spec](https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html). My keyword scan of the STIX text for digital signing, cryptographic signing and non-repudiation found nothing, so an STL verdict appears to need an outer envelope. This is a keyword scan, not a full reading.
- **[STD]** W3C Verifiable Credentials Data Model v2.0, W3C Recommendation, 15 May 2025. [W3C](https://www.w3.org/TR/vc-data-model-2.0/).

**Does sharing work? Quality evidence**
- **[PR]** Beomjin Jin, Eunsoo Kim, Hyunwoo Lee, Elisa Bertino, Doowon Kim, Hyoungshick Kim. "Sharing cyber threat intelligence: Does it really help?" NDSS 2024. [Paper page](https://www.ndss-symposium.org/ndss-paper/sharing-cyber-threat-intelligence-does-it-really-help/). **Method:** CTI-Lense collected about 6 million STIX objects from ten sources, 2014 to 2023. **Result:** malware signatures and URLs are over 90% of the data; about 72% of URLs arrive no later than VirusTotal; 19% of Threat Actor data was incorrect; only 0.09% of Indicators contained detection rules. **Limit:** public sources only.
- **[PR]** Xander Bouwman, Harm Griffioen, Jelle Egbers, Christian Doerr, Bram Klievink, Michel van Eeten. "A different cup of TI? The added value of commercial threat intelligence." USENIX Security 2020. [Paper page](https://www.usenix.org/conference/usenixsecurity20/presentation/bouwman). **Result:** almost no overlap between two leading vendors; for 22 shared threat actors, overlap averages 2.5 to 4.0%, with about a one-month delay. **Limit:** two vendors.
- **[PR]** Vector Guo Li, Matthew Dunn, Paul Pearce, Damon McCoy, Geoffrey M. Voelker, Stefan Savage. "Reading the Tea Leaves: A Comparative Analysis of Threat Intelligence." USENIX Security 2019. [Paper page](https://www.usenix.org/conference/usenixsecurity19/presentation/li). Defines metrics for characterising feeds. Partial abstract read.
- **[PR]** Thomas D. Wagner, Khaled Mahbub, Esther Palomar, Ali E. Abdallah. "Cyber threat intelligence sharing: Survey and research directions." *Computers & Security* 87:101589, 2019. [DOI](https://doi.org/10.1016/j.cose.2019.101589). Metadata only.

**Measured gain from cooperation between operators**
- **[PR]** Daniel Wagner, Daniel Kopp, Matthias Wichtlhuber, Christoph Dietzel, Oliver Hohlfeld, Georgios Smaragdakis, Anja Feldmann. "United We Stand: Collaborative Detection and Mitigation of Amplification DDoS Attacks at Scale." ACM CCS 2021, pp. 970-987. [DOI](https://doi.org/10.1145/3460120.3485385). **Method:** data from eleven IXPs in three regions with over 2,120 members. **Result:** limited information exchange lets them mitigate most attacks and drop as much as 90% more attack traffic locally. **Limit:** amplification DDoS only; no signing or AI. This is the best real-world evidence that sharing helps.

**Blockchain and decentralised threat sharing**
- **[PR]** Hisham Ali, William J. Buchanan, Jawad Ahmad, Marwan Abubakar, Muhammad Shahbaz Khan, Isam Wadhaj. "TrustShare: Secure and Trusted Blockchain Framework for Threat Intelligence Sharing." *Future Internet* 17(7):289, 2025. [DOI](https://doi.org/10.3390/fi17070289). **Method:** Hyperledger Fabric, CP-ABE, IPFS, STIX and TAXII. **Result:** low-latency retrieval and scalable encryption. **Limit:** tests system performance, not whether shared intelligence is true. Revocation uses certificate authorities, so it is not authority-free.
- **[PRE]** Yair Allouche, Nachiket Tapas, Francesco Longo, Asaf Shabtai, Yaron Wolfsthal. "TRADE: TRusted Anonymous Data Exchange: Threat Sharing Using Blockchain Technology." arXiv:2103.13158, 2021. [arXiv](https://arxiv.org/abs/2103.13158). Blockchain access control with STIX and TAXII.
- **[PRE]** Zhang Xiaohui, Miao Xianghua. "A Reputation-based Approach using Consortium Blockchain for Cyber Threat Intelligence Sharing." arXiv:2107.06662, 2021. [arXiv](https://arxiv.org/abs/2107.06662). Proof-of-Reputation consensus aimed at compromised members who file false reports. Closest to STL's lying-peer problem.
- **[PRE]** Kealan Dunnett, Shantanu Pal, Guntur Dharma Putra, Zahra Jadidi, Raja Jurdak. "A Trusted, Verifiable and Differential Cyber Threat Intelligence Sharing Framework using Blockchain." arXiv:2208.12031, 2022. [arXiv](https://arxiv.org/abs/2208.12031). Ethereum proof of concept with selective sharing.
- **[PRE]** Dincy R. Arikkat, Mert Cihangiroglu, Mauro Conti, Rafidha Rehiman K. A., Serena Nicolazzo, Antonino Nocera, Vinod P. "SeCTIS: A Framework to Secure CTI Sharing." arXiv:2406.14102, 2024. [arXiv](https://arxiv.org/abs/2406.14102). Swarm Learning plus blockchain, with assessment of data quality and participant trust.
- **[PRE]** Nikolaos Alexopoulos, Emmanouil Vasilomanolakis, Stephane Le Roux, Steven Rowe, Max Mühlhäuser. "TRIDEnT: Building Decentralized Incentives for Collaborative Security." arXiv:1905.03571, 2019. [arXiv](https://arxiv.org/abs/1905.03571). Peer-to-peer alert markets. Argues adoption is limited by trust and incentives, not by tools.
- **[PR-claim]** Hisham Ali, Pavlos Papadopoulos, Jawad Ahmad, Nikolaos Pitropakis, Zakwan Jaroucheh, William J. Buchanan. "Privacy-preserving and Trusted Threat Intelligence Sharing using Distributed Ledgers." arXiv:2112.10092, 2021; states IEEE SINCONF 2021. [arXiv](https://arxiv.org/abs/2112.10092).
- **[PR]** Marc Lapira, Nahid Ebrahimi Majd. "A Secure Cyber Threat Intelligence Sharing Framework Using Sui Blockchain." IEEE CCWC 2026, pp. 699-705. [DOI](https://doi.org/10.1109/CCWC67433.2026.11393883). Metadata only.

**Signing and proving agent messages**
- **[PRE]** Bravish Ghosh. "PCM: A Proof-Carrying Message Protocol for Verifiable Multi-Agent Communication." arXiv:2610.39109, 2026. [arXiv](https://arxiv.org/abs/2610.39109). **Method:** each claim carries inclusion proofs from an append-only Merkle log that the agent cannot write, signed by a separate attester. **Result:** on 926 messages, 712 of them lies, PCM accepts 10 (1.4%). Plain A2A accepts all 712. Models of six deployed protocols, including RFC 9421 and SCITT, accept 504 to 712. Verification takes about 1 ms. **Limit:** single-author preprint, a general agent protocol, and the protocol models are the author's own. It needs independent checking, but it is the most important prior work for STL's signing idea.
- **[PRE]** Karol Budzyn, Adrian Brodzik, Mateusz Szczepkowski. "Cryptographically Secure Agent-to-Agent Communication in Multi-Agent Systems." arXiv:2610.23078, 2026. [arXiv](https://arxiv.org/abs/2610.23078). DIDs, verifiable credentials on a permissioned ledger, post-quantum TLS, signed CBOR envelopes and zero-knowledge proofs. **Limit:** an architecture and survey. Identity still rests on a ledger.
- **[PRE]** Zhenhua Zou, Sheng Guo, Qiuyang Zhan, Lepeng Zhao, Shuo Li, Zhuotao Liu. "InterSAGE: The Secure and Verifiable Interoperability Protocol for An Internet of Agents." arXiv:2608.13030, 2026. [arXiv](https://arxiv.org/abs/2608.13030). A positioning paper with identity, discovery, negotiation and accountability layers across organisations.
- **[PR]** Sandro Garzon, Awid Vaziry, Enis Kuzu, Dennis Gehrmann, Buse Varkan, Alexander Gaballa, Axel Küpper. "AI Agents with Decentralized Identifiers and Verifiable Credentials." ICAART 2026, pp. 252-259. [DOI](https://doi.org/10.5220/0014234400004052). Agents exchange DIDs and third-party attestations to set up trust.
- **[PRE]** Jiye Wang, Shiduo Yang, Ting Qiao, Jiayu Qin, Jianbin Li, Yu Wang, Yuanhe Zhao. "Ev-Trust: An Evolutionarily Stable Trust Mechanism for Decentralized LLM-Based Multi-Agent Service Economies." arXiv:2512.16167, 2025. [arXiv](https://arxiv.org/abs/2512.16167). Decentralised trust among LLM agents in simulation. **Limit:** factual Q&A benchmarks, not security data.
- **[PR]** Zachary Newman, John Speed Meyers, Santiago Torres-Arias. "Sigstore: Software Signing for Everybody." ACM CCS 2022, pp. 2353-2367. [DOI](https://doi.org/10.1145/3548606.3560596). Precedent for signing plus a public log. Metadata only.

**Null results from my searches**
- arXiv queries combining operators, threat intelligence, trust and 6G, and cross-organisation LLM threat work, returned nothing relevant. A web search for signed detection verdicts in SCITT logs found only a [GitHub issue](https://github.com/Just-Ipavon/Sphragis/issues/38) proposing COSE-signed verification events.

### Inferences
- A signature proves who said something, not that it is true. CTI-Lense's 19% incorrect threat-actor data and PCM's results point the same way. STL's signed verdict needs evidence attached, plus a way to score each peer's past accuracy.
- A strong STL contribution would be a verdict format: claim, confidence, evidence references, model identity, signer, log receipt. COSE gives the envelope, STIX gives vocabulary, and SCITT gives the log pattern. The combination for detection appears unpublished, though I cannot prove that.
- "No central authority" is hard to claim. TrustShare keeps certificate authorities and Budzyn et al. keep a permissioned ledger. A safer claim is "no single authority", with trust anchors stated openly.
- Signed verdicts can also spread a poisoned decision faster, as Prompt Infection suggests for prompts. This should be tested directly.

### Gaps
- No study was found of verdict sharing between real mobile operators, and none on legal limits on sharing between them.
- I did not check MISP or OpenCTI for signing features.
- PCM's results are unreviewed. If a reviewer disputes them, the argument still stands on the CTI quality studies.

## 5. What exists on federated learning for phishing, spam or intrusion detection, including privacy and poisoning risks?

### Takeaway
This area is mature, and federated models often come close to centralised ones on benchmarks, so federated learning should not be STL's novelty. Evidence on poisoning conflicts and depends on the threat model. The closest overlap with STL is a 2026 preprint that combines federated IDS, LLM-derived semantics and trust-aware aggregation.

### Cited Findings

**Surveys**
- **[PR]** Jose Luis Hernandez-Ramos, Georgios Karopoulos, Efstratios Chatzoglou, Vasileios Kouliaridis, Enrique Marmol, Aurora Gonzalez-Vidal, Georgios Kambourakis. "Intrusion Detection Based on Federated Learning: A Systematic Review." *ACM Computing Surveys* 57(12):1-65, 2025. [DOI](https://doi.org/10.1145/3731596). Taxonomy of FL-enabled IDS from 2018 to 2022 literature. Note the literature window ends in 2022.
- **[PR]** Ghadi Almaktoom, Suliman Aladhadh, Salim El Khediri. "Privacy-Preserving Phishing Detection: A Systematic Review of LLMs, Federated Learning, and Blockchain Integration." *Computer Modeling in Engineering & Sciences* 147(2), 2026. [DOI](https://doi.org/10.32604/cmes.2026.078774). Metadata and search snippet only.
- **[PRE]** Jiefei Liu, Abu Saleh Md Tayeen, Pratyay Kumar, Qixu Gong, Wenbin Jiang, Huiping Cao, Satyajayant Misra, Jayashree Harikumar. "Generative AI and Federated Learning for Intrusion Detection Systems: A Survey." [arXiv:2607.01305](https://arxiv.org/abs/2607.01305), 2026.

**Phishing, spam and scams**
- **[PR]** Chandra Thapa, Jun Wen Tang, Alsharif Abuadbba, Yansong Gao, Seyit Camtepe, Surya Nepal, Mahathir Almashor, Yifeng Zheng. "Evaluation of Federated Learning in Phishing Email Detection." *Sensors* 23(9):4346, 2023. [DOI](https://doi.org/10.3390/s23094346). **Method:** RNN and BERT under balanced and asymmetric splits. **Result:** comparable to centralised on balanced data with few organisations; the RNN drops 1.8% going from 2 to 10 organisations. **Limit:** no poisoning test in the abstract.
- **[PR-claim]** Yuwei Sun, Ng Chong, Hideya Ochiai. "Federated Phish Bowl: LSTM-Based Decentralized Phishing Email Detection." arXiv:2110.06025, 2021; states IEEE SMC 2022. [arXiv](https://arxiv.org/abs/2110.06025). **Result:** retains 83% accuracy.
- **[PR]** Wenhao Li, Selvakumar Manickam, Yung-Wey Chong. "FedPhishLLM: A privacy-preserving and explainable phishing detection mechanism using federated learning and LLMs." *Journal of King Saud University Computer and Information Sciences* 37(8):252, 2025. [DOI](https://doi.org/10.1007/s44443-025-00267-0). **Method:** FL with fine-tuned multimodal LLMs. **Result:** up to 95% accuracy, precision and F1, with 96% recall. **Limit:** application-layer data.
- **[PR]** Xiaoyang Yi, Linyu Li, Jian Zhang, Zedong Jia. "Heterogeneous federated learning for imbalanced phishing email detection." *Cybersecurity* 9(1):10, 2026. [DOI](https://doi.org/10.1186/s42400-025-00420-2). Metadata only.
- **[PR]** Dakota Staples, Hung Cao, Saqib Hakak, Paul Cook. "Multilingual Phishing Email Detection Using Lightweight Federated Learning." IEEE PST 2025, pp. 1-6. [DOI](https://doi.org/10.1109/PST65910.2025.11268856). Metadata only.
- **[PR]** Jun Yong Yoon, Bong Jun Choi. "Privacy-Friendly Phishing Attack Detection Using Personalized Federated Learning." Lecture Notes in Computer Science, pp. 460-465, 2023. [DOI](https://doi.org/10.1007/978-3-031-27199-1_46). Groups clients to reduce data imbalance. Search snippet only.
- **[PR]** A. Elkhawas, T. M. Chen, I. Gashi. "Privacy-Preserving Federated Learning for Phishing Detection." 2025, IEEE copyright. [Repository](https://openaccess.city.ac.uk/id/eprint/35006/). The exact venue was not shown on the page I opened.
- **[PRE]** Yekai Li, Rufan Zhang, Wenxin Rong, Xianghang Mi. "SpamDam: Towards Privacy-Preserving and Adversary-Resistant SMS Spam Detection." arXiv:2404.09481, 2024. [arXiv](https://arxiv.org/abs/2404.09481). A 76K SMS spam set, federated training, and a new reverse backdoor attack.
- **[PR-claim]** Ismail Hossain, Sai Puppala, Md Jahangir Alam, Sajedul Talukder. "AI-in-the-Loop: Privacy Preserving Real-Time Scam Detection and Conversational Scambaiting by Leveraging LLMs and Federated Learning." arXiv:2509.05362, 2025; states PETS 2026. [arXiv](https://arxiv.org/abs/2509.05362). PII leakage at or below 0.0085 in federated settings.

**Intrusion detection**
- **[PRE]** Saeid Jamshidi, Omar Abdul Wahab, Foutse Khomh, Kawser Wazed Nafi. "Tri-LLM Cooperative Federated Zero-Shot Intrusion Detection with Semantic Disagreement and Trust-Aware Aggregation." arXiv:2602.00219, 2026. [arXiv](https://arxiv.org/abs/2602.00219). **Method:** GPT-4o, DeepSeek-V3 and LLaMA-3-8B create semantic attack prototypes; disagreement between them models uncertainty; aggregation weights clients by reliability. **Result:** over 80% zero-shot accuracy, more than 10% better than similarity baselines. **Limit:** the LLMs act as external encoders, not agents, and there are no signed verdicts. The same lead author requested withdrawal of a different paper (2606.10323); no such note appeared on this one when checked.
- **[PRE]** Samaresh Kumar Singh, Joyjit Roy, Martin So. "Zero-Trust Agentic Federated Learning for Secure IIoT Defense Systems." arXiv:2512.23809, 2025. [arXiv](https://arxiv.org/abs/2512.23809). **Method:** TPM attestation, SHAP-weighted aggregation and adversarial training. **Result:** 97.8% accuracy, 93.2% under 30% Byzantine clients. **Limit:** standard IDS benchmarks, including CIC-IDS2017.
- **[PRE]** Amal Alshehri, Cihan Tunc. "Federated Learning and LLM-Driven Threat Intelligence for Zero Trust IoT Architecture." arXiv:2607.17035, 2026. [arXiv](https://arxiv.org/abs/2607.17035). Raspberry Pi test with mTLS over MQTT. **Result:** F1 0.9091, ROC-AUC 1.0. **Limit:** a perfect ROC-AUC suggests a small or easy test.
- **[PR]** Beibei Li, Yuhao Wu, Jiarui Song, Rongxing Lu, Tao Li, Liang Zhao. "DeepFed: Federated Deep Learning for Intrusion Detection in Industrial Cyber-Physical Systems." *IEEE Transactions on Industrial Informatics* 17(8):5615-5624, 2021. [DOI](https://doi.org/10.1109/TII.2020.3023430). CNN and GRU with Paillier-based secure parameter exchange.
- **[PR]** Mohanad Sarhan, Siamak Layeghy, Nour Moustafa, Marius Portmann. "Cyber Threat Intelligence Sharing Scheme Based on Federated Learning for Network Intrusion Detection." *Journal of Network and Systems Management* 31(1):3, online 2022. [DOI](https://doi.org/10.1007/s10922-022-09691-3). Multiple organisations train on NetFlow-format datasets. Same group: HBFL, hierarchical blockchain FL, [arXiv:2204.04254](https://arxiv.org/abs/2204.04254).
- **[PR]** Roberto Doriguzzi-Corin, Domenico Siracusa. "FLAD: Adaptive Federated Learning for DDoS attack detection." *Computers & Security* 137:103597, 2024. [DOI](https://doi.org/10.1016/j.cose.2023.103597). Adapts computation to harder attack profiles without sharing test data.
- **[PRE]** Leonardo Henrique de Melo, Gustavo de Carvalho Bertoli, Michele Nogueira, Aldri Luiz dos Santos, Lourenço Alves Pereira Junior. "Anomaly-Flow: A Multi-domain Federated Generative Adversarial Network for Distributed Denial-of-Service Detection." arXiv:2503.14618, 2025. [arXiv](https://arxiv.org/abs/2503.14618). Multi-domain DDoS detection using synthetic flows.

**Poisoning and privacy (the evidence conflicts)**
- **[PR]** Thien Duc Nguyen, Phillip Rieger, Markus Miettinen, Ahmad-Reza Sadeghi. "Poisoning Attacks on Federated Learning-based IoT Intrusion Detection System." DISS Workshop at NDSS 2020. [DOI](https://doi.org/10.14722/diss.2020.23003). **Result:** compromised IoT devices alone can implant a backdoor, so malicious traffic is classed as benign, and this circumvents defences (three datasets from 46 devices).
- **[PR]** Minghong Fang, Xiaoyu Cao, Jinyuan Jia, Neil Gong. "Local Model Poisoning Attacks to Byzantine-Robust Federated Learning." USENIX Security 2020. [Paper page](https://www.usenix.org/conference/usenixsecurity20/presentation/fang). First systematic study of local model poisoning against methods claimed to be Byzantine-robust.
- **[PR]** Virat Shejwalkar, Amir Houmansadr, Peter Kairouz, Daniel Ramage. "Back to the Drawing Board: A Critical Evaluation of Poisoning Attacks on Production Federated Learning." IEEE S&P 2022, pp. 1354-1371. [DOI](https://doi.org/10.1109/SP46214.2022.9833647). **Result:** "FL is highly robust in practice even when using simple, low-cost defenses" under realistic threat models. This contradicts earlier alarms for untargeted attacks.
- **[PRE]** Yu Bi, Yekai Li, Xuan Feng, Xianghang Mi. "Enabling Privacy-Preserving Cyber Threat Detection with Federated Learning." arXiv:2404.05130, 2024. [arXiv](https://arxiv.org/abs/2404.05130). On SMS spam and Android malware, a practical data poisoning attack costs at most 0.14% accuracy.
- **[PR]** Sameera K.M., Vinod P., Anderson Rocha, Rafidha Rehiman K.A., Mauro Conti. "WeiDetect: Weibull distribution-based defense against poisoning attacks in federated learning for network intrusion detection systems." *Journal of Information Security and Applications* 95:104275, 2025. [DOI](https://doi.org/10.1016/j.jisa.2025.104275). Improves target-class recall by up to 70% and F1 by 1 to 14%. **Limit:** assumes a server-side validation set.
- **[PR]** Xiaoyu Cao, Minghong Fang, Jia Liu, Neil Zhenqiang Gong. "FLTrust: Byzantine-robust Federated Learning via Trust Bootstrapping." NDSS 2021. [DOI](https://doi.org/10.14722/ndss.2021.24434). Metadata only.
- **[PRE]** Ligeng Zhu, Zhijian Liu, Song Han. "Deep Leakage from Gradients." arXiv:1906.08935, 2019. [arXiv](https://arxiv.org/abs/1906.08935). Recovers pixel-accurate images and token-matching text from gradients. Publication venue not checked in this run.
- **[PRE]** Maria-Ioana-Andrea Ivan, Orhan Ermis, Ruxandra F. Olimid. "Enhanced Detective: A Dual-Stage Proactive Defense Against Internal Poisoning Attacks in Financial Fraud Detection Using Federated Learning." arXiv:2610.17523, 2026. [arXiv](https://arxiv.org/abs/2610.17523). The fraud-domain equivalent.

### Inferences
- The conflict is mostly about threat models. Backdoors from compromised devices (Nguyen) differ from untargeted poisoning by a small share of clients (Shejwalkar). STL must state which one it faces.
- Sharing verdicts instead of gradients avoids gradient leakage of the Deep Leakage kind, but it swaps that for verdict poisoning, and verdicts may reveal what an operator observed. Neither risk is measured in the work I found for verdict sharing.
- Federated learning adds a large evaluation burden. If STL's novelty lies elsewhere, it should be a side feature or future work.

### Gaps
- No work was found that runs FL across network-layer and application-layer agents together.
- Several entries above are marked metadata or snippet only and need reading before citation.
- The Crossref record "SpamDam: Enabling Privacy-Preserving Discovery and Analysis of SMS Spam" (ITNEC 2026) has a similar name. I could not confirm that it is the same work as arXiv:2404.09481.

## 6. What is the honest research gap that STL could fill, and which claims would be new versus already published?

### Takeaway
The gap is not "nobody has combined agents, semantics and signing". Most pieces exist, and the author of the paper closest to that combination has asked to withdraw it. The defensible gap is measurement: does a second layer plus evidence-carrying signed verdicts improve detection and resist attack, once compromised agents and attacker-written text are in the threat model? STL's best original idea is using one layer to check the other when the first is deceived. Two project facts shape this: STL's datasets are single-layer and unpaired, and its dependencies suggest compact models rather than LLM agents.

### Cited Findings

Closest works compared with STL's four ideas. Based on abstracts, plus full-text keyword scans for some. "Not stated" means the abstract does not claim it.

| Work | Status | Network + application | Meaning-based | Multi-agent | Signed outputs | Across organisations | Evaluation size |
|---|---|---|---|---|---|---|---|
| [Tri-LLM](https://arxiv.org/abs/2602.00219) | PRE | No, telemetry | Yes | LLM ensemble as encoders | Not stated | Federated clients | Benchmarks |
| [MALCDF](https://arxiv.org/abs/2512.14846) | PRE | No, flow schema | Yes | Yes, 4 | Encrypted messages | Not stated | 50 records |
| [MobiLLM](https://doi.org/10.1109/MILCOM64451.2025.11310651) | PR | No, RAN | Yes | Yes, 3 | Not stated | Not stated | Initial |
| [AIDA](https://arxiv.org/abs/2610.10608) | PRE | Enterprise telemetry | Yes | Yes | Append-only ledger | Not stated | 1,247 alerts, 1 scenario |
| [CORTEX](https://arxiv.org/abs/2510.00311) | PRE | Enterprise alerts | Yes | Yes | Auditable decision | Not stated | Production dataset |
| [AScope](https://arxiv.org/abs/2603.04469) | PRE | Application + OS | Yes | Supervisor LLM | Not stated | Not stated | 10 scenarios |
| [Z²-ACT](https://arxiv.org/abs/2608.21049) | PRE | RAN control | Intent checks | Agentic | ZK commitments | Multi-vendor audit | ColO-RAN traces |
| [PCM](https://arxiv.org/abs/2610.39109) | PRE | Not a detector | No | Yes | Yes, with evidence | Yes in principle | 926 messages |
| [United We Stand](https://doi.org/10.1145/3460120.3485385) | PR | Network only | No | No | No | Yes, 11 IXPs | Real IXP data |
| [Semantic Multi-Agent IDS](https://arxiv.org/abs/2606.10323) | WITHDRAWN | IoT | Yes | Yes, 4 | Not stated | Not stated | Do not use |

Supporting points:
- Fusion gains are not guaranteed: [Fard et al.](https://arxiv.org/abs/2606.22450).
- Meaning-based judgement catches what rules miss: [AgentTrust](https://arxiv.org/abs/2606.08539). Rules still stop most attacks: [DEFER](https://arxiv.org/abs/2610.07657).
- Attacker-written log fields steer LLMs: [LogInject](https://arxiv.org/abs/2607.14493), [Watchtower](https://arxiv.org/abs/2605.24421).
- Attackers cannot control all features equally: [Li 2026](https://arxiv.org/abs/2607.07739).
- Execution evidence can expose intent that input filters miss: [AScope](https://arxiv.org/abs/2603.04469).
- Channel signatures do not stop a compromised sender: [PCM](https://arxiv.org/abs/2610.39109).
- Shared intelligence is often wrong or late: [CTI-Lense](https://www.ndss-symposium.org/ndss-paper/sharing-cyber-threat-intelligence-does-it-really-help/), [Bouwman et al.](https://www.usenix.org/conference/usenixsecurity20/presentation/bouwman).
- Cooperation between operators can pay off: [United We Stand](https://doi.org/10.1145/3460120.3485385).

What the project files show (`C:/CC/Code/stl/pyproject.toml` and `C:/CC/Code/stl/training/download_data.py`):
- The project describes itself as "AI-driven fraud and attack mitigation across the OSI stack". Runtime dependencies include onnxruntime, tokenizers, lightgbm, scikit-learn, dpkt, zxing-cpp and pillow, and no LLM client. Transformers appears only in the training extras.
- Data sources: SMS spam (UCI); phishing URLs and feeds (PhiUSIIL, OpenPhish, Phishing.Database, Hugging Face); benign lists (Tranco, Common Crawl index); email corpora (Enron, SpamAssassin, CEAS_08, Nazario, Nigerian_Fraud, Ling, TREC_06); abuse text (Civil Comments, Roman Urdu hate speech, Measuring Hate Speech); traffic (corrected CICIDS2017, CTU-13); blocklists (Feodo Tracker, SSLBL JA3).
- Choosing the corrected CICIDS2017 and adding CTU-13 already avoids the worst of the problems [Engelen et al.](https://doi.org/10.1109/SPW53761.2021.00009) describe.

Side checks on two niche angles the data suggests:
- Roman Urdu fraud detection looks thin. My searches found [a 2024 SMS fraud paper in IJCDS](https://doi.org/10.12785/ijcds/150174) and [a 2015 spam study](https://doi.org/10.1109/NSEC.2015.7396343), while Roman Urdu hate speech is busy, with preprints such as [arXiv:2608.18142](https://arxiv.org/abs/2608.18142) and [arXiv:2611.04342](https://arxiv.org/abs/2611.04342). Metadata only.
- QR-code phishing is a small but active area, including a dataset ([CIC-Trap4Phish](https://arxiv.org/abs/2602.09015)), QR-based detection ([arXiv:2505.03451](https://arxiv.org/abs/2505.03451)), and signed QR codes using CBOR certificates ([arXiv:2607.08383](https://arxiv.org/abs/2607.08383)). Metadata only.

### Inferences

**Claim status (my judgement)**

| STL claim | Status | Closest prior work | What STL should do |
|---|---|---|---|
| Multi-agent LLMs beat a single LLM | Published | AIDA, CORTEX, MALCDF, MultiPhishGuard | Use as baseline, do not claim |
| Meaning catches what rules miss | Published in part | AgentTrust, Tri-LLM | Claim only for a named attack class, compared to rules |
| LLM agents can work at the network layer | Published | MobiLLM, Dayaratne et al., eX-NIDS | Not new. Report latency |
| Cross-layer data can help detection | Partly published, mixed | Fard, Chatzoglou, ALchemist, OmegaLog | New only if it measures network + application meaning-based fusion at low FPR |
| Agents can sign messages | Published | Budzyn, InterSAGE, Garzon, PCM | Not new |
| Decentralised threat sharing | Published | TRADE, TrustShare, Zhang and Miao | Not new |
| Federated phishing or IDS | Published | Thapa, FedPhishLLM, Tri-LLM, Sarhan | Not new. Keep optional |
| **Evidence-carrying signed detection verdicts, tested against a lying peer** | **Not found** | PCM (general), Zhang and Miao (reputation) | **Candidate contribution** |
| **One layer checks the other to catch prompt injection in detection agents** | **Not found** | AScope (agent actions), StateFence, Li (controllability) | **Strongest candidate contribution** |
| **Public corpus pairing network traces with abuse or fraud content** | **Not found** | TON_IoT, GUIDE (different scope) | **Candidate data contribution** |
| The full four-part system exists and works | Not found in reviewed form | Withdrawn 2606.10323 | Weak claim alone. Integration is not a result unless measured |
| It works for 6G | Vision papers only | Barua, Ferrag | Do not claim without a RAN test |
| No central authority | Hard to defend | TrustShare, Budzyn both keep anchors | Say "no single authority" and name anchors |

**The core idea worth testing.** A log field or email body is text the attacker writes. A flow record's timing, volume and peer are harder to fake, as Li's controllability split implies. So if an application agent is deceived into "benign", a network agent working from facts the attacker controls less can disagree. Cross-layer disagreement then becomes a deception detector. This links sections 1, 2 and 4 into one testable claim. It is my inference, and I did not find it published.

**First decide what an "agent" is.** The dependency list suggests small trained models, not LLMs. If that is right:
- The prompt-injection work is background, not a direct threat. The direct threat is adversarial evasion, and RQ2 below should use that instead.
- The multi-agent LLM papers become related work, not baselines to beat.
- STL gains a real selling point: fast local inference with no LLM in the path, where MALCDF reports 6.8 s per event.
- "Check by meaning" must then be justified for a compact classifier. A reviewer will ask how that differs from an ordinary text classifier. The team should have a clear answer.

**The dataset problem.** STL's sources each cover one layer, from unrelated times and networks. A CICIDS2017 flow and a Nazario email share no session, host or attack. Joining them would be an artificial pairing that reviewers will distrust, so RQ1 cannot run on these sets as they are. Three options, cheapest first:
1. Extract application content from inside one capture, such as HTTP payloads in the original CICIDS2017 PCAPs, if the corrected set or original traces allow it.
2. Build a small testbed that generates both layers together, such as a phishing page visit plus its traffic.
3. Accept that network and application agents vote on separate tasks, and drop the fusion-gain claim.
Blocklist and feed data also bring risk: feeds against Tranco can teach a model "popular domain" instead of "safe domain", and feeds change daily, so use time-based splits. This is my reading of the leakage warnings in [Arp et al.](https://www.usenix.org/conference/usenixsecurity22/presentation/arp) and [El Mahdaouy et al.](https://arxiv.org/abs/2602.05594).

**A paper shape that fits three undergraduates.** Make it a measurement study, not a system description:
1. RQ1: detection gain of each layer alone versus both, at fixed 1% FPR, using run-disjoint splits as in Fard et al. This needs paired data.
2. RQ2: attack success against a single-layer agent versus cross-layer agents. Use prompt injection from LogInject or Watchtower for LLM agents, or constrained evasion as in Li 2026 for compact models.
3. RQ3: false-verdict spread when one peer lies, comparing no signature, signature only, and signature plus evidence, with latency and message size.

Run ablations for rules alone, model alone, and rules then model. Publish code and raw outputs.

**A lower-risk fallback.** If paired data proves too hard, a narrower paper on Roman Urdu fraud or smishing detection, or on signed verdicts alone, may be easier to finish and less crowded. Roman Urdu needs a labelled fraud set, because the project's Roman Urdu data is hate speech.

**Risks to the gap**
- This area moves monthly. PCM appeared on 29 October 2026 and StateFence on 2 November 2026. Re-run these searches a week before submission.
- Absence from my searches is not proof. Say "to the best of our knowledge" and list the search terms used.
- LLM results are costly to reproduce and models change. Pin the model versions, and prefer an open-weight model for at least one arm.

### Gaps
- I did not test the core idea. It could fail if an attacker can shape both layers, for example with a compromised host that generates matching traffic.
- I know STL only from the task description, `pyproject.toml` and `download_data.py`. The README is empty, and I did not see the model code, agent design, signing code or any results. The compact-model reading is an inference from dependencies. If agents call a hosted LLM through plain HTTP, it would not show there.
- I did not check whether the corrected CICIDS2017 files include payloads, so option 1 for paired data is unconfirmed.
- The comparison table rests mostly on abstracts. A reviewer may find features that abstracts omit.

## 7. Which conferences and journals fit this paper best for undergraduate-led work, with their scope, indexing and rough acceptance difficulty? Also give their current policy on AI-assisted writing where you can confirm it.

### Takeaway
Aim first at a short paper at a focused workshop or an IEEE topical conference, then extend it into a journal such as IEEE Access or Computers & Security. Top-four conferences are a poor first target. Every venue checked permits AI assistance with conditions, but the disclosure rules differ. AISec requires a statement even when no AI was used.

### Cited Findings

**Conferences and workshops.** Ranks are from the [ICORE2026 portal](https://portal.core.edu.au/conf-ranks/), which ranks 825 venues (A* 7.52%, A 13.09%, B 30.18%). "None found" means my search returned no row, which is not proof it is unranked. Top-four mean acceptance is the five-year figure from [csconferences.org](https://csconferences.org/). "Rough difficulty" is my own judgement wherever no rate is given. I found no student track at any venue.

| Venue | Scope and fit | Rank | Publication | Dates found | Rough difficulty |
|---|---|---|---|---|---|
| [WOSOC](https://www.ndss-symposium.org/ndss2026/submissions/cfp-wosoc/) at NDSS | SOC operations. 2026 topics included "Integration of agentic AI in SOC workflows". Short papers of 4-8 pages take work in progress | Workshop | Proceedings; publisher not named on the CFP | 2026 deadline was 29 Dec 2025. 2027 CFP not confirmed. [NDSS 2027](https://www.ndss-symposium.org/ndss2027/) is 22-26 Mar 2027 in Seoul | Moderate. Acceptance rate not found |
| [AISec](https://aisec.cc/) at ACM CCS | AI and security, including LLMs. 10 pages + 2, anonymised | Workshop | ACM workshop proceedings | 2026 deadline was 24 Jul; workshop is 15 Nov 2026 in The Hague. 2027 not announced | Hard. Rate not found |
| [CAMLIS](https://camlis.org/cfp) | Applied ML for security. Full papers or extended abstracts. In-person required | None found | PMLR for full papers | 2026 CFP closed 5 Jul. 2027 not announced | Moderate. Rate not found |
| [IEEE CSR](https://www.ieee-csr.org/) | Security and resilience. The Fard et al. fusion paper states acceptance here | None found | IEEE conference; indexing not confirmed on site | 2026 was 3-5 Aug in Lisbon, deadline 9 Mar 2026 after extension. 2027 CFP not found | Moderate. Rate not found |
| [IEEE ICAIC](https://www.myhuiban.com/conference/5818) | AI in cybersecurity. Published [AgentSOC](https://doi.org/10.1109/ICAIC67076.2026.11395783) | Not checked | IEEE (DOI confirmed for 2026) | Third-party listing only: deadline 30 Dec 2026, conference 3 Mar 2027, Houston. Confirm with organisers | Moderate. Rate not found |
| [SVCC 2027](https://easychair.org/cfp/svcc2027) | Topics include AI and LLM security. Has a poster track | Not checked | The 2025 edition was IEEE, [per DOI on an arXiv record](https://arxiv.org/abs/2607.06963). 2027 publisher not confirmed | Research 16 Jan 2027, poster 20 Jan 2027, conference 21-23 Jun 2027, San Jose | Moderate. Rate not found |
| IEEE TrustCom | Trust and security in computing and communications. Published [L2M-AID](https://doi.org/10.1109/TrustCom66490.2025.00256) | B | IEEE | 2027 not checked | Moderate |
| [IEEE CNS](https://www.comsoc.org/conferences-events/ieee-conference-communications-and-network-security-2026) | Network security | None found | IEEE | 2026 was Newark, DE, [14-17 Sep](https://infosec-conferences.com/event/20260914-ieee-conference-on-communications-and-network-security-cns/) | Moderate to hard |
| GLOBECOM, [IEEE ICC](https://www.beri.net/events/ieee-icc-2027) (security symposium) | Communications security. Suits a 6G angle | GLOBECOM B; ICC none found | IEEE | ICC 2027 is 30 May-3 Jun in Washington, DC. Its [listed deadline](https://www.myhuiban.com/conference/318.md) of 2 Oct 2026 has passed | Moderate to hard |
| ARES, ACNS, DIMVA, NOMS, LCN, NetSoft, AINA, IFIP SEC | Security and networking | B | Various | Not checked | Moderate to hard |
| ICICS, SecureComm, ICISSP, SECRYPT, PST, ISC | Security | C | Various | Not checked | Moderate |
| ACSAC, ESORICS, RAID, AsiaCCS | Applied security | A | Various | Not checked | Hard |
| USENIX Security | Top security | A* | USENIX | [Cycle 2 due 26 Jan 2027](https://www.usenix.org/conference/usenixsecurity27/call-for-papers); symposium 11 Aug 2027, Denver | Very hard, mean 21% |
| [NDSS](https://www.ndss-symposium.org/ndss2027/submissions/call-for-papers/) | Top security | A* | Internet Society | Both 2027 cycles closed | Very hard, mean 17% |
| CCS, [IEEE S&P](https://sp2027.ieee-security.org/cfpapers.html) | Top security | A* | ACM, IEEE | Dates not checked | Very hard, means 19% and 15% |

**Journals**

| Journal | Fit evidence | Facts found | Notes |
|---|---|---|---|
| [IEEE Access](https://ieeeaccess.ieee.org/about/) | Published the SDN DDoS paper and TON_IoT | Average acceptance 20%, 4-6 weeks, Impact Factor 4.2, [APC $2,160](https://ieeeaccess.ieee.org/about/article-processing-charges/), broad scope | Third-party sites quote other rates. The official [about](https://ieeeaccess.ieee.org/about/) and [authors](https://ieeeaccess.ieee.org/authors/) pages both say 20% |
| Computers & Security (Elsevier) | Published FLAD, Song et al., Wagner et al. | Third-party only: [CiteScore 10.1](https://researcher.life/journal/computers-security/2593), [Impact Factor 6.8](https://www.journalmetrics.org/journal/computers-and-security). No acceptance rate found | Official pages returned 403. Check them yourself |
| Journal of Information Security and Applications (Elsevier) | Published WeiDetect | Metrics not confirmed | Reasonable journal target |
| [Cybersecurity](https://cybersecurity.springeropen.com/) (SpringerOpen) | Published Yi et al. | Impact Factor 4.1 (2025), 5-year 5.1, median first decision 15 days, Scopus indexed | Open access. APC not confirmed |
| [IEEE Open Journal of the Communications Society](https://www.comsoc.org/publications/journals/ieee-ojcoms) | Published the two agentic 6G surveys | Impact Factor 6.1 (JCR 2025, per ComSoc) | Needs a real communications angle. APC not confirmed |
| IEEE TNSM; J. Network and Systems Management | Published [Bovenzi et al.](https://doi.org/10.1109/TNSM.2025.3543022); Sarhan et al. | Metrics not checked | Network management angle |
| Future Internet, Sensors (MDPI) | Published TrustShare, Thapa et al., Chatzoglou et al. | MDPI pages returned 403. Metrics not confirmed | Check your department's view of MDPI first |

**AI-assisted writing rules**

| Venue | Current rule found | Source |
|---|---|---|
| IEEE journals | AI-generated content "shall be disclosed in the acknowledgments section". Name the system and the sections. For grammar editing, disclosure is "not required, but recommended". Exclude the reference section from AI editing | [IEEE](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/) |
| IEEE S&P 2027 | Follows IEEE policy. Authors must complete a "Generative AI usage considerations" field on HotCRP. AI cannot be an author | [CFP](https://sp2027.ieee-security.org/cfpapers.html) |
| USENIX Security '27 | Permitted. Authors acknowledge they reviewed all AI-generated content "including text, code, experimental data, and references" | [CFP](https://www.usenix.org/conference/usenixsecurity27/call-for-papers) |
| NDSS 2027 | Permitted if it does not plagiarise, misrepresent or falsify. Must be disclosed. If whole sections were generated, name the sections, tools and versions | [CFP](https://www.ndss-symposium.org/ndss2027/submissions/call-for-papers/) |
| ACM (second-hand) | AI used in research must be described in the methods section. For writing help, "ACM no longer requires the disclosure". All authors stay accountable | [Quoted by SIGCSE TS 2027](https://2027.sigcse-ts.acm.org/info/policies-ai). acm.org returned 403 |
| AISec 2026 | Stricter than ACM. Every paper needs a paragraph on AI use, even to state that none was used. Reviewers must also declare AI use | [AISec](https://aisec.cc/) |
| Elsevier journals | A separate AI declaration at submission, which appears in the article. Name the tool, purpose and oversight. Basic grammar and spelling checks are exempt. Substantive restructuring must be disclosed | [Elsevier](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) |
| Springer Nature | Risk-based. Language polishing is permitted. Extensive writing support is permitted with oversight and disclosure. Responsibility cannot be delegated to AI | [Springer](https://www.springer.com/gp/editorial-policies/artificial-intelligence--ai-/25428500), [Nature Portfolio](https://www.nature.com/nature-portfolio/editorial-policies/ai) |
| arXiv CS | Review and position papers must already be accepted at a journal or conference, with proof. Workshop review is generally not enough | [arXiv blog](https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/) |

**Predatory and look-alike warnings**
- WASET appears on the [Beall's publisher list](https://beallslist.net/), and IJSRM appears on the [standalone journal list](https://beallslist.net/standalone-journals/). One arXiv record in this topic ([2609.28843](https://arxiv.org/abs/2609.28843)) gives IJSRM as its journal reference, so I excluded it. Treat Beall's list as a warning signal, not a verdict.
- Search results on this topic were full of unfamiliar "International Journal of..." titles, including [IJERET](https://ijeret.org/index.php/ijeret/article/download/170/157/410) and [IJSRCSEIT](https://ijsrcseit.com/home/article/view/CSEIT261213109). I did not use them. They were not on the list I checked, and that does not show quality.
- Hijacked journals copy real titles and ISSNs and may promise Scopus indexing. Check the [Retraction Watch Hijacked Journal Checker](https://retractionwatch.com/the-retraction-watch-hijacked-journal-checker/) and the [Think. Check. Submit.](https://thinkchecksubmit.org/) checklist. A journal missing from the checker is not proven safe.
- Name traps: "AISEC 2026" in [Trento](https://intelligentsystems2026.github.io/AISEC/) and [Marrakech](https://aisec.uca.ma/conference/index.html) are not ACM AISec. [AISecP 2026](https://easychair.org/cfp/AISecP26) calls itself "a course-based simulated academic conference", so it is training, not publication. A [Canadian ICAIC](https://easychair.org/cfp/ICAIC-2025) in Manitoba shares the name with the IEEE event in Houston. Confirm which one you are submitting to.
- Page trap: [usenix.org/node/316785](https://www.usenix.org/node/316785) is VehicleSec's AI policy, not USENIX Security's. NDSS paths under /ndss2027/ for [WOSOC](https://www.ndss-symposium.org/ndss2027/submissions/cfp-wosoc/) and [posters](https://www.ndss-symposium.org/ndss2027/submissions/call-for-posters/) currently show old 2023 and 2017 content.

**If the team is in Pakistan**
- HEC's HJRS sorts journals into [W, X and Y categories](https://www.hec.gov.pk/english/services/faculty/journals/Documents/Policies/Policy-Research-Journals.pdf). The [HJRS site](https://hjrs.hec.gov.pk/) was down when checked on 5 November 2026, so confirm any journal's category directly. HJRS covers journals, so a conference paper would likely be judged separately; that is my reading, not a confirmed rule.
- FIT 2026 is listed for [14-15 December 2026 at COMSTECH, Islamabad](https://www.globalexhibition.org/en/sub/exhibition_view.php?idx=21024). I found no official call for papers.

### Inferences
- **Recommended order.** First, a short paper or poster: ICAIC 2027 if its date is confirmed and results exist by late December, SVCC's research or poster track by 16-20 January 2027, or WOSOC or IEEE CSR 2027 once their calls appear. Second, extend the paper with more data into IEEE Access, Computers & Security, or JISA. Check the journal's rule on extensions of conference papers first.
- **Best topical fit:** WOSOC for agentic SOC work, AISec for the prompt-injection angle, IEEE CSR for cross-layer measurement. Avoid leading with 6G unless the team has a RAN testbed.
- **Budget.** IEEE Access costs $2,160. CAMLIS requires in-person attendance and AISec requires an author to attend and present. Ask your department about support before submitting.
- **Timing.** USENIX Security Cycle 2 on 26 January 2027 is not realistic for a first paper, and a rejection there can use up months.
- **These notes themselves are AI-assisted.** USENIX and others hold authors responsible for references. Open every link before citing, and disclose AI use under the target venue's rule. Keep a record of what tools were used and for what.

### Gaps
- Acceptance rates for AISec, WOSOC, CAMLIS, IEEE CSR, ICAIC, SVCC, TrustCom and CNS were not found. A search summary gave AsiaCCS 2025 as 114 of 558 (20.4%), but I could not tie it to one page, so it is not in the table.
- One long-running statistics page ([Guofei Gu](https://people.engr.tamu.edu/guofei/sec_conf_stat.htm)) came back with misaligned columns, so I did not use it.
- The Elsevier ScienceDirect, MDPI and acm.org pages returned 403. Their metrics, and the ACM wording, are second-hand or missing.
- IEEE ICET 2026 turned up only through LinkedIn snippets, with its deadline already passed, so I left it out. IEEE INMIC 2026 could not be confirmed.
- I could not open arXiv's endorsement page. First-time submitters should check whether they need an endorser.
- ACM DTRAP was not checked and may be worth a look.
- Scopus or Web of Science indexing was confirmed only where stated above.
