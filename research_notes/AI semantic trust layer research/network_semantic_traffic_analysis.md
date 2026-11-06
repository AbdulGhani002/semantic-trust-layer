# Semantic and AI-Based Traffic Analysis at the Network Layer

Notes for the Semantic Trust Layer (STL) final year project. Checked on 5 November 2026.

**Status tags.** `[PR]` peer-reviewed conference or journal. `[PR-W]` peer-reviewed workshop, short or companion paper. `[PRE]` arXiv preprint, no peer-reviewed version found. `[PRE*]` preprint whose own page claims acceptance that I could not confirm in an index.

**Depth tags.** `full` = I read the paper text and matched the key numbers against the raw text. `abs` = I read the abstract or official page only. `cite` = the citation record is confirmed, but I could not read the result.

Every citation below was opened in Crossref, arXiv, OpenAlex or a publisher page. None comes from memory. A number with no `full` tag comes from the paper's abstract and is the authors' own claim. "Limit (my reading)" marks my judgement, not the authors' words.

Link check on the same date: all DOIs resolved in Crossref and all arXiv IDs resolved in the arXiv API. ResearchGate, ScienceDirect and Taylor & Francis pages returned 403 to scripts, so open those in a browser.

## What are the main transformer and LLM methods for traffic, up to 2026?

### Takeaway

The field moved from byte-level pre-training (ET-BERT, YaTC, TrafficFormer, NetMamba) to foundation models (netFound, Lens, MM4flow) and then to tuned LLMs (TrafficLLM, ETooL, MET-LLM). Reported F1 above 95% does not survive independent testing: with a per-flow split and a frozen encoder, five such models fall to 0.5–24% macro F1 on a 120-website TLS task, while LightGBM on header fields reaches 82.4% with IPs and 40.6% without them.

### Cited Findings

#### Independent re-test of the main models

Zhao et al. re-tested the models on packet classification with a per-flow split and frozen encoders. Figures are macro F1 — [Zhao et al. 2025, Tables 3, 7, 8](https://arxiv.org/html/2507.16438v1).

| Model | Own claim | VPN-app (16 classes) | TLS-120 (120 sites) |
|---|---|---|---|
| ET-BERT | F1 97.4% on CSTNET-TLS 1.3 | 43.7 | 6.7 |
| YaTC | "outperforms by a large margin" | 44.3 | 9.6 |
| NetMamba | accuracy near 99% | 28.4 | 4.5 |
| TrafficFormer | up to +10% F1 | 54.4 | 24.0 |
| netFound (version tested in 2025) | see entry below | 15.3 | 0.5 |
| Pcap-Encoder (headers only) | introduced in this paper | 71.0 | 63.7 |
| Pcap-Encoder, no IP addresses | | 52.5 | 13.0 |
| LightGBM on header fields | baseline | 82.6 | 82.4 |
| LightGBM, no IP addresses | baseline | 74.5 | 40.6 |

Caveat: this is a packet-level task on legacy data, so it may be harsh on models built for whole flows (my reading).

#### Byte-level and pre-training models

- **[PR · abs] Lin, X., Xiong, G., Gou, G., Li, Z., Shi, J., Yu, J. (2022). ET-BERT: A Contextualized Datagram Representation with Pre-training Transformers for Encrypted Traffic Classification. Proc. ACM Web Conference (WWW '22), pp. 633–642.** [DOI](https://doi.org/10.1145/3485447.3512217) · [arXiv](https://arxiv.org/abs/2202.06335)
  - Method: BERT-style pre-training on unlabelled datagram bytes, then fine-tuning on few labels.
  - Data: five tasks, including ISCX-Tor, ISCX-VPN-Service, Cross-Platform (Android), CSTNET-TLS 1.3.
  - Result: F1 of 99.2%, 98.9%, 92.5% and 97.4% on those four.
  - Limit: randomising SeqNo, AckNo and timestamps in the test set only drops accuracy from 97.4 to 19.5, and a model with no pre-training still reaches 97.1 — [Zhao et al. 2025](https://arxiv.org/html/2507.16438v1).
- **[PR · abs] Zhao, R., Zhan, M., Deng, X., Wang, Y., Wang, Y., Gui, G., Xue, Z. (2023). Yet Another Traffic Classifier: A Masked Autoencoder Based Traffic Transformer with Multi-Level Flow Representation. Proc. AAAI 37(4), pp. 5420–5427.** [DOI](https://doi.org/10.1609/aaai.v37i4.25674)
  - Method: masked autoencoder with a traffic matrix and packet-level plus flow-level attention.
  - Data: five real-world traffic datasets.
  - Result: outperforms prior methods "by a large margin"; the abstract gives no numbers.
  - Limit: accuracy falls from 0.90 to 0.62 when MAC, IP and ports are anonymised — [Wickramasinghe et al. 2025](https://arxiv.org/html/2503.20093v4).
- **[PR · cite] Hang, Z., Lu, Y., Wang, Y., Xie, Y. (2023). Flow-MAE: Leveraging Masked AutoEncoder for Accurate, Efficient and Robust Malicious Traffic Classification. Proc. RAID 2023, pp. 297–314.** [DOI](https://doi.org/10.1145/3607199.3607206)
  - Method: masked autoencoder for malicious traffic, motivated by ET-BERT's input limit and fixed byte-pair encoding.
  - Result and data: not verified; the indexed abstract is cut short.
- **[PR · abs] Zhou, G., Guo, X., Liu, Z., Li, T., Li, Q., Xu, K. (2025). TrafficFormer: An Efficient Pre-trained Model for Traffic Data. IEEE S&P 2025, pp. 1844–1860.** [DOI](https://doi.org/10.1109/SP61157.2025.00102)
  - Method: fine-grained multi-classification pre-training; augmentation that uses the random initial values of protocol fields.
  - Data: six classification datasets plus protocol understanding tasks.
  - Result: up to 10% better F1.
  - Limit: best of the pre-trained models in the re-test table, but still only 24.0 macro F1 on TLS-120. Full text not read; the author PDF host refused the connection.
- **[PR · abs] Wang, T., Xie, X., Wang, W., Wang, C., Zhao, Y., Cui, Y. (2024). NetMamba: Efficient Network Traffic Classification via Pre-training Unidirectional Mamba. IEEE ICNP 2024, pp. 1–11.** [DOI](https://doi.org/10.1109/ICNP61940.2024.10858569) · [arXiv](https://arxiv.org/abs/2405.11449)
  - Method: linear-time unidirectional Mamba instead of a Transformer, with a traffic representation that removes biased bytes.
  - Data: six public datasets, three tasks.
  - Result: accuracy near 99%; up to 60x faster inference.
  - Limit: most anisotropic embeddings of four foundation models tested — [Beltiukov et al. 2025](https://arxiv.org/html/2509.23089).
- **[PRE · abs] Wang, T., Xie, X., Wang, W., Wang, C., Liu, J., Huang, B., Hu, Y., Zhao, Y., Cui, Y. (2026). NetMamba+: A Framework of Pre-trained Models for Efficient and Accurate Network Traffic Classification.** [arXiv](https://arxiv.org/abs/2601.21792)
  - Method: Mamba plus Flash Attention, multimodal representation, label-distribution-aware fine-tuning.
  - Result: up to 6.44% better F1, 1.7x throughput, 261.87 Mb/s online.
  - Limit (my reading): no leak-free re-test yet.
- **[PR · abs] Chen, X.-Y., Han, L., Zhan, D.-C., Ye, H.-J. (2025). MIETT: Multi-Instance Encrypted Traffic Transformer for Encrypted Traffic Classification. Proc. AAAI 39(15).** [DOI](https://doi.org/10.1609/aaai.v39i15.33748) · [arXiv](https://arxiv.org/abs/2412.15306)
  - Method: each packet is an instance in a flow bag; two-level attention; two new pre-training tasks.
  - Data: five datasets.
  - Result: reports state-of-the-art results.
  - Limit (my reading): tokens still come from bytes, the input type the re-test challenges.
- **[PR · abs] Yan, Z., Peng, L., Liu, P., Bao, Y., Yang, B. (2026). NT-Transformer: A Non-Pretrained Encrypted Network Traffic Classification Model. IEEE TNSM 23, pp. 4278–4292.** [DOI](https://doi.org/10.1109/TNSM.2026.3683410)
  - Method: no pre-training; learns byte level plus flow level (packet size, inter-arrival time) from labels.
  - Data: three public sets and three recently collected sets.
  - Result: F1 up by 0.25–2.24% — [abstract snippet](https://www.researchgate.net/publication/403782842_NT-Transformer_A_Non-Pretrained_Encrypted_Network_Traffic_Classification_Model).
  - Limit (my reading): supervised, so it depends on labels.
- **[PR · abs] Qu, J., Zhang, Y., Zhang, J., Li, J., Ma, X. (2026). Tracegram: Framing Trace-Level Traffic Analysis with Temporally-Aware Multiple Instance Learning. USENIX Security 2026.** [Page](https://www.usenix.org/conference/usenixsecurity26/presentation/qu)
  - Method: treats a whole trace as the unit; per-flow encoders with temporal aggregation; flags the key flows.
  - Data: four public datasets.
  - Result: better or comparable to prior methods, with attribution signals for analysts.
  - Limit (my reading): numbers not in the abstract. The idea fits STL's goal of judging behaviour across flows.
- **[PRE* · abs] Chen, Z., Yu, Q., Song, Z., Yang, G., Yan, W. (2026). TDDM-Melatt: A Decoupled Memory and Diffusion Framework for Generalizable Encrypted Traffic Classification.** [arXiv](https://arxiv.org/abs/2608.30745)
  - Method: memory-decoupled CG-LSTM encoder, frozen after pre-training, topology anonymisation, diffusion augmentation.
  - Data: four public benchmarks under strict flow-level splits.
  - Result: beats six basic and six representation models.
  - Limit: CCS 2026 acceptance is the arXiv comment only. Abstract gives no numbers.
- **[PRE* · abs] Lin, C., Jiang, Y., Zhang, W., Meng, X., Zuo, T., Zhang, Y. (2025). TraGe: A Generic Packet Representation for Traffic Classification Based on Header-Payload Differences.** [arXiv](https://arxiv.org/abs/2506.14151)
  - Method: treats header and payload differently in pre-training.
  - Limit: IWQoS 2025 acceptance is the arXiv comment only. Result numbers not read.
- **[PRE · abs] Liu, L., Li, R., Li, Q., Hou, M., Jiang, Y., Xu, M. (2025). FlowletFormer: Network Behavioral Semantic Aware Pre-training Model for Traffic Classification.** [arXiv](https://arxiv.org/abs/2508.19924)
  - Method: BERT model that cuts traffic into behaviour-coherent units, with protocol-layer embeddings.
  - Result: reports better classification and few-shot learning; no numbers in the abstract.
- **[PRE · abs] He, Q., Fu, X., Zhang, L. (2026). TrafficMoE: Heterogeneity-aware Mixture of Experts for Encrypted Traffic Classification.** [arXiv](https://arxiv.org/abs/2603.29520)
  - Method: separate expert branches for headers and payloads, with uncertainty filtering.
  - Data: six datasets.
  - Result: reports consistent wins; no numbers in the abstract.
- **[PRE · abs] Kulatilleke, G. K., Layeghy, S., Baktashmotlagh, M., Portmann, M. (2026). MambaNetBurst: Direct Byte-level Network Traffic Classification without Tokenization or Pretraining.** [arXiv](https://arxiv.org/abs/2605.11034)
  - Method: Mamba-2 on raw bytes of the first packets, supervised.
  - Data: six public benchmarks.
  - Result: competitive with heavier pre-trained models.
  - Limit: code and data only on request.
- **[PRE · abs] Luo, Y., Tao, J., Yu, L., Cheng, G. (2026). Treat Traffic Like Trees: A Semantic-Preserving Hierarchical Graph-Based Expert Framework for Encrypted Traffic Analysis.** [arXiv](https://arxiv.org/abs/2606.04517)
  - Method: graph built from protocol fields so the model's field preferences can be measured.
  - Limit (my reading): submitted to IEEE, not yet reviewed.
- **[PRE · abs] Lin, C., Meng, X., Zuo, T., Zhang, W., Shen, M., Zhao, R., Che, G., Meng, R., Huang, Z., Luo, H., Xu, Z., Zhang, Y. (2025, revised 2026). Versatile yet Efficient Network Traffic Analysis: Offloading Network Foundation Model to SmartNIC (Nepco).** [arXiv](https://arxiv.org/abs/2508.02001)
  - Method: convolutional byte-sequence model on a BlueField-3 SmartNIC.
  - Result: macro F1 competitive with eight foundation models; 328x lower latency.
  - Limit: arXiv says "Under review", while one [community list](https://github.com/linwhitehat/ETA-Resource) says NDSS 2027. Unconfirmed. Another [list](https://github.com/wangtz19/Awesome-NTA) shows the same ID under an older title about convolutions.
- **[PR-W · abs] Wickramasinghe, N., Shaghaghi, A., Ferrari, E., Jha, S. (2025). Less is More: Simplifying Network Traffic Classification Leveraging RFCs. WWW Companion 2025, pp. 1398–1401.** [DOI](https://doi.org/10.1145/3701716.3715492)
  - Method: NetMatrix, a small tabular view built from RFC field definitions, with plain XGBoost.
  - Result: on par with ET-BERT and YaTC at orders of magnitude lower resource use.
  - Limit (my reading): short paper.

#### Foundation models

- **[PRE · abs] Beltiukov, S., Guthula, S., Manda, H., Daneshamooz, J., Guo, W., Willinger, W., Gupta, A., Monga, I. (2023, revised 2026). netFound: Principled Design for Network Foundation Models.** [arXiv](https://arxiv.org/abs/2310.17025) · [Code](https://github.com/SNL-UCSB/netFound)
  - Method: protocol-aware tokens, context embedding, burst-flow attention. It leaves out payload and IP addresses by design.
  - Data: 4.2 billion flows, 5,000 GPU hours.
  - Result: F1 of 0.95 on exogenous context, against below 0.62 for others.
  - Limit: self-reported and not peer-reviewed. An earlier version scored 0.5 macro F1 on TLS-120 in the re-test table. Earlier title: "netFound: Foundation Model for Network Security".
- **[PRE · abs] Li, X., Qian, C., Wang, Q., Kong, J., Wang, Y., Yao, Z., Ji, B., Cheng, L., Zhou, G., Shao, H. (2024, revised 2026). Lens: A Knowledge-Guided Foundation Model for Network Traffic.** [arXiv](https://arxiv.org/abs/2402.03646) · [Code](https://github.com/V-Enzo/Lens-foundation-model-for-network-traffic)
  - Method: T5 encoder-decoder; masks whole protocol fields rather than digits; turns classification into closed-ended generation.
  - Result: 96.33% average accuracy, best on 8 of 12 tasks.
  - Limit: the code repository says TMLR (Transactions on Machine Learning Research), but I could not confirm it in an index.
- **[PR · abs] Yang, L., Liu, L., Huang, J., Liu, Z., Liang, S., Fu, S., Wang, Y. (2025). MM4flow: A Pre-trained Multi-modal Model for Versatile Network Traffic Analysis. ACM CCS 2025, pp. 1664–1678.** [DOI](https://doi.org/10.1145/3719027.3744804)
  - Method: BERT variants on two views, raw bytes and transmission patterns, fused by cross-attention.
  - Data: over 70 TB of real traffic for pre-training; six public datasets for tasks.
  - Result: 84% better accuracy for website identification in encrypted tunnels against other pre-trained models.
  - Limit (my reading): the byte view keeps the risk of shortcuts.
- **[PR-W · abs] Qian, C., Li, X., Wang, Q., Zhou, G., Shao, H. (2024). NetBench: A Large-Scale and Comprehensive Network Traffic Benchmark Dataset for Foundation Models. IEEE FMSys 2024, pp. 20–25.** [DOI](https://doi.org/10.1109/FMSys62467.2024.00008) · [arXiv](https://arxiv.org/abs/2403.10319)
  - Method: a shared benchmark that targets inconsistent datasets and leaky splits.
  - Result: result numbers not read.
- **[PR · full] Beltiukov, S. (Roman in Crossref), Guthula, S., Guo, W., Willinger, W., Gupta, A. (2025). Demystifying Network Foundation Models. NeurIPS 38 (Datasets and Benchmarks), pp. 158143–158169.** [DOI](https://doi.org/10.52202/085713-4769) · [arXiv](https://arxiv.org/abs/2509.23089)
  - Method: looks at embeddings, not task scores: geometry, alignment with expert features, sensitivity to causal changes.
  - Data: YaTC, ET-BERT, netFound, NetMamba on Android Crossmarket, CIC-IDS2017, CIC-APT-IIoT24, CAIDA, MAWI.
  - Result: mean cosine similarity 0.86 ± 0.09, meaning embeddings bunch together. Expert-feature alignment by CKA is low (netFound 0.143, ET-BERT 0.029) and lower on CAIDA (0.032) and MAWI (0.055). Decorrelating embeddings adds up to +0.35 F1.
  - Limit: authors call it an initial attempt, not exhaustive. All five authors are also netFound authors, and netFound scores best here.

#### LLM-based methods

- **[PRE · abs] Meng, X., Lin, C., Wang, Y., Zhang, Y. (2023, revised 2025). NetGPT: Generative Pretrained Transformer for Network Traffic.** [arXiv](https://arxiv.org/abs/2304.09513)
  - Method: turns traffic into unified text; shuffles header fields, segments packets, adds task prompts.
  - Data: encrypted software, DNS, private industrial protocols, crypto mining.
  - Result: "outperform state-of-the-art baselines by a wide margin"; no numbers in the abstract.
  - Limit: I found no peer-reviewed version.
- **[PRE · abs] Qu, J., Ma, X., Li, J. (2024). TrafficGPT: Breaking the Token Barrier for Efficient Long Traffic Analysis and Generation.** [arXiv](https://arxiv.org/abs/2403.05822)
  - Method: generative pre-training with linear attention.
  - Result: capacity of 12,032 tokens instead of 512; discriminator F1 near 0.5 on generated data.
  - Limit: name clash, see Ginige below. I found no peer-reviewed version.
- **[PRE · full] Cui, T., Lin, X., Li, S., Chen, M., Yin, Q., Li, Q., Xu, K. (2025). TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation.** [arXiv](https://arxiv.org/abs/2504.04222)
  - Method: traffic-domain tokeniser, dual-stage tuning (task instruction, then traffic patterns), small adapters of 7.1 MB; base models Llama2-7B and ChatGLM2-6B.
  - Data: ten scenarios, 229 traffic types; deployment at a security company.
  - Result: detection F1 0.9875, generation F1 0.9483; 98.7% malware and 99.8% web attack F1 in the enterprise test; 89.3% F1 on future APT stages.
  - Limit: a new adapter needs 23 GB GPU memory and 14 hours; inference takes 0.2 s per label on an A100. The enterprise test ran at a company selling signature-based WAF and NIDS services. No venue stated on arXiv.
- **[PR · abs] Ginige, Y., Silva, B., Dahanayaka, T., Seneviratne, S. (2026). TrafficLLM: LLMs for improved open-set encrypted traffic analysis. Computer Networks 274, 111847.** [DOI](https://doi.org/10.1016/j.comnet.2025.111847). Extends **Ginige, Y., Dahanayaka, T., Seneviratne, S. (2024). TrafficGPT: An LLM Approach for Open-Set Encrypted Traffic Classification. AINTEC 2024, pp. 26–35.** [DOI](https://doi.org/10.1145/3674213.3674217)
  - Method: pre-trained GPT-2 and LLaMA-2-7B as feature extractors on packet sizes, timing and direction, with little fine-tuning.
  - Data: seven encrypted datasets.
  - Result: open-set gains over ET-BERT of 12.7% (GPT-2) and 17.6% (LLaMA-2-7B).
  - Limit: a different paper from Cui's TrafficLLM, so always cite by author. Framed as an attack, not defence.
- **[PR · abs] Lin, X., Xiong, G., Gou, G., Dong, W., Yu, J., Li, Z., Xia, W. (2025). Respond to Change With Constancy: Instruction-Tuning With LLM for Non-I.I.D. Network Traffic Classification. IEEE TIFS 20, pp. 5758–5773.** [DOI](https://doi.org/10.1109/TIFS.2025.3574971)
  - Method: ETooL links text and traffic through self-supervised instruction tuning.
  - Data: APP53, ISCX-Botnet, and a new shift dataset, NETD.
  - Result: F1 on APP53 is 93.19% I.I.D. and 74.88% out of distribution.
  - Limit: the same model loses about 18 points under distribution shift, by its own figures.
- **[PR · cite] Huang, Y., Du, P., Li, R., Li, X., Li, L. (2026). MET-LLM: Enhancing large language models for malicious encrypted traffic detection. Expert Systems with Applications 303, 130621.** [DOI](https://doi.org/10.1016/j.eswa.2025.130621)
  - Method: domain tokenisation, pre-trained LLM, adaptive tuning adaptor — [publisher page snippet](https://www.sciencedirect.com/science/article/abs/pii/S0957417425042368).
  - Result: not verified.
- **[PR-W · abs] Chen, Y., Li, R., Li, X., Zhao, Z., Zhang, H. (2025). MERLOT: A Distilled LLM-based Mixture-of-Experts Framework for Scalable Encrypted Traffic Classification. IEEE Globecom Workshops 2025, pp. 98–103.** [DOI](https://doi.org/10.1109/GCWkshps68340.2025.11591188) · [arXiv](https://arxiv.org/abs/2411.13004)
  - Method: small models distilled from GPT-2, used as experts behind a gating network.
  - Data: ten datasets.
  - Result: competitive, at lower resource use.
- **[PRE* · abs] Li, H., Kang, H., Liu, C., Wang, R., Li, J., Sun, G., Wang, J., Liang, S., Mao, S. (2025). Encrypted Traffic Detection in Resource Constrained IoT Networks: A Diffusion Model and LLM Integrated Framework.** [arXiv](https://arxiv.org/abs/2512.21144)
  - Method: DMLITE, diffusion features with LLM-guided feature selection.
  - Result: accuracy 98.87% (USTC-TFC), 92.61% (ISCX-VPN), 99.83% (Edge-IIoTset).
  - Limit: USTC-TFC2016 is 94.7% unencrypted and ISCXVPN2016 is 98.9% unencrypted — [Wickramasinghe et al. 2025](https://arxiv.org/html/2503.20093v4).
- **[PR · abs] Zhao, X., Deng, X., Cui, T., Zhang, Y., Xu, K., Li, Q. (2026). Robust LLM-Based Website Fingerprinting under Dynamic Real-World Conditions. WWW 2026, pp. 2800–2811.** [DOI](https://doi.org/10.1145/3774904.3792288)
  - Method: TraVerse, LLM representation learning for Tor website fingerprinting.
  - Result: Accuracy@3 up 176.3% on average, stable over a three-month test on real-user traffic.
  - Limit (my reading): an attack on Tor users, but a rare LLM result with a long time window.
- **[PR · cite] Wu, D., Wang, X., Qiao, Y., Wang, Z., Jiang, J., Cui, S., Wang, F. (2024). NetLLM: Adapting Large Language Models for Networking. ACM SIGCOMM 2024, pp. 661–678.** [DOI](https://doi.org/10.1145/3651890.3672268)
  - Method: adapts LLMs to reduce manual DNN design for networking tasks. This is network control, not traffic classification (my reading).
- **[PR · abs] He, D., Naz, F., Wang, Y., Naz, L. (2026). Toward Deployable LLM-Based Encrypted Traffic Classification: Opportunities, Bottlenecks, and a Roadmap. IEEE Network (early access).** [DOI](https://doi.org/10.1109/MNET.2026.3733495)
  - Method: design space of traffic representation, model family, adaptation strategy, deployment target.
  - Limit: the paper says its gates are not empirically validated.
- **[PR · abs] Pérez-Jove, R., Munteanu, C. R., Dorado, J., Pazos, A., Vázquez-Naya, J. (2026). Network traffic foundation models: A systematic review. Computer Networks 276, 111998.** [DOI](https://doi.org/10.1016/j.comnet.2026.111998)
  - Method: review of 51 primary studies, 2017–2025.
  - Result: cross-task transfer remains limited; terabyte-scale corpora are scarce.

### Inferences

- "Semantic" means different things in these papers: learned relations between byte tokens (ET-BERT), protocol-aware structure (Lens, FlowletFormer, Treat Traffic Like Trees), and behaviour across packets (Exosphere, under the next question). STL should define its own meaning and test it.
- The Demystifying checks (embedding spread, match to expert features, reaction to causal changes) give STL a way to test whether a network agent understands behaviour, not only whether it scores well.
- netFound's design choice of leaving out payload and IP matches STL's constraint, so it is the closest foundation model. Its claims need independent confirmation before STL relies on them.
- Tuned LLMs are too costly for line-rate use on commodity hardware. TrafficLLM's own figure of 0.2 s per label on an A100 is about 5 labels per second.

### Gaps

- I could not read the TrafficFormer, Flow-MAE or MET-LLM full texts.
- I found no independent, leak-free re-test of Cui's TrafficLLM, ETooL, MM4flow or netFound v5.
- Venue claims I could not confirm: Lens (TMLR), Nepco (NDSS 2027), TDDM-Melatt (CCS 2026), TraGe (IWQoS 2025).
- Semantic Scholar rate-limited me and DBLP blocked scripts, so venue checks rest on Crossref, OpenAlex and arXiv.

## What works on encrypted traffic with metadata only?

### Takeaway

The evidence favours metadata. Ciphertext adds almost nothing beyond its length, and what works is packet sizes, directions and timing over the first packets, flow statistics, and links between flows and hosts. Simple models on these features often match deep ones, but plain header fields such as IP addresses are shortcuts, and the coming loss of SNI through ECH also removes a common source of labels.

### Cited Findings

#### Evidence on what carries signal

- **[PR · full] Wickramasinghe, N., Shaghaghi, A., Tsudik, G., Jha, S. (2025). SoK: Decoding the Enigma of Encrypted Network Traffic Classifiers. IEEE S&P 2025, pp. 1825–1843.** [DOI](https://doi.org/10.1109/SP61157.2025.00165) · [arXiv](https://arxiv.org/abs/2503.20093)
  - Method: 348 feature-occlusion experiments on ET-BERT and YaTC.
  - Data: CipherSpectrum and CSTNET-TLS1.3.
  - Result: ISCXVPN2016 is 98.9% unencrypted, USTC-TFC2016 94.7%, ISCXTor2016 89.3%. Anonymising MAC, IP and ports drops ET-BERT from 0.96 to 0.51. Payload alone gives ET-BERT about 0.12. Guideline 6 says classifiers rely on payload length, not patterns in ciphertext; Guideline 9 says header data remains crucial.
  - Limit: two classifiers tested. CipherSpectrum was collected by scripts, not people.
- **[PR · full] Zhao, Y., Dettori, G., Boffa, M., Vassio, L., Mellia, M. (2025). The Sweet Danger of Sugar: Debunking Representation Learning for Encrypted Traffic Classification. ACM SIGCOMM 2025, pp. 296–310.** [DOI](https://doi.org/10.1145/3718958.3750498) · [arXiv](https://arxiv.org/abs/2507.16438)
  - Method: re-tests ET-BERT, YaTC, NetMamba, TrafficFormer and netFound, and adds Pcap-Encoder, a language model on headers.
  - Data: ISCX-VPN, USTC-TFC, CSTN-TLS1.3. Pre-training for Pcap-Encoder used MAWI, UNSW-NB15 and a campus trace.
  - Result: results up to 80% lower than reported. For Pcap-Encoder, removing payload barely matters (71.0 to 66.7 on VPN-app; 63.7 to 63.6 on TLS-120), but removing headers is fatal (16.4; 1.5).
  - Limit: Pcap-Encoder is the second slowest model and a shallow baseline still does as well or better.
- **[PRE · full] Jerabek, K., Luxemburk, J., Plny, R., Koumar, J., Pesek, J., Hynek, K. (2025). When Simple Model Just Works: Is Network Traffic Classification in Crisis?** [arXiv](https://arxiv.org/abs/2506.08655)
  - Method: k-NN on packet sequence metadata (sizes, times, directions).
  - Data: 12 datasets, 15 tasks.
  - Result: on average only 2.88% behind the state of the art. CESNET-TLS22: 92.34 against 97.2. CESNET-QUIC22: 72.91 against 80.87.
  - Limit: the same paper warns that much of this strength comes from duplicates, see the next question.
- **[PRE · abs] Huang, S., Yang, S. (2026). SoK: Where Do Flow Labels Come From? Auditing Label Provenance in Encrypted Traffic Benchmarks.** [arXiv](https://arxiv.org/abs/2609.02140)
  - Method: audits 14 benchmark entries.
  - Result: under strict side-channel features, the ceiling on balanced accuracy is 0.56–0.76 on public benchmarks that inherit labels. Only 24.95% of connections in their corpus carry an observable SNI of their own.
  - Limit: new and unreviewed.

#### Metadata features and models

- **[PR · abs] Liu, C., He, L., Xiong, G., Cao, Z., Li, Z. (2019). FS-Net: A Flow Sequence Network For Encrypted Traffic Classification. IEEE INFOCOM 2019, pp. 1171–1179.** [DOI](https://doi.org/10.1109/INFOCOM.2019.8737507)
  - Method: recurrent encoder-decoder on flow sequences.
  - Data: real-world traffic of 18 applications.
  - Result: 99.14% TPR, 0.05% FPR.
  - Limit (my reading): closed-set, known applications.
- **[PR · abs] Shapira, T., Shavitt, Y. (2021). FlowPic: A Generic Representation for Encrypted Traffic Classification and Applications Identification. IEEE TNSM 18(2), pp. 1218–1232.** [DOI](https://doi.org/10.1109/TNSM.2021.3071441)
  - Method: turns basic flow data into a picture for a CNN.
  - Result: high accuracy even on VPN and Tor.
  - Limit: a replication found a 20% accuracy drop in some scenarios from a data shift in a follow-up study's original dataset — [Finamore et al. 2023](https://doi.org/10.1145/3618257.3624820).
- **[PR · abs] Akbari, I., Salahuddin, M. A., Aniva, L., Limam, N., Boutaba, R., Mathieu, B., Moteau, S., Tuffin, S. (2021). A Look Behind the Curtain: Traffic Classification in an Increasingly Encrypted Web. POMACS 5(1), pp. 1–26.** [DOI](https://doi.org/10.1145/3447382)
  - Method: stacked LSTM and CNN on engineered features.
  - Data: traffic from a major ISP and mobile network operator.
  - Result: 95% service accuracy. Shows that deep models often apply simple logic on TLS handshake fields.
  - Limit: that reliance limits robustness to future protocols.
- **[PR · abs] Koumar, J., Hynek, K., Čejka, T. (2023). Network Traffic Classification Based on Single Flow Time Series Analysis. CNSM 2023, pp. 1–7.** [DOI](https://doi.org/10.23919/CNSM59352.2023.10327876) · [arXiv](https://arxiv.org/abs/2307.13434)
  - Method: 69 features from the time series of packet sizes.
  - Data: 15 public datasets.
  - Result: up to 5% better in more than half of the tasks.
- **[PR · abs] Koumar, J., Hynek, K., Pešek, J., Čejka, T. (2024). NetTiSA: Extended IP flow with time-series features for universal bandwidth-constrained high-speed network traffic classification. Computer Networks 240, 110147.** [DOI](https://doi.org/10.1016/j.comnet.2023.110147) · [arXiv](https://arxiv.org/abs/2310.05530)
  - Method: compact extended IP flow.
  - Data: 25 classification tasks.
  - Result: deployable on 100 Gbps ISP lines.
  - Limit (my reading): tested on classification, not unknown attacks.
- **[PR · abs] Fu, C., Li, Q., Shen, M., Xu, K. (2024). Detecting Tunneled Flooding Traffic via Deep Semantic Analysis of Packet Length Patterns. ACM CCS 2024, pp. 3659–3673.** [DOI](https://doi.org/10.1145/3658644.3670353)
  - Method: Exosphere learns the semantics of packet length patterns, with no packet contents; FPGA prototype.
  - Data: real institutional network and existing datasets.
  - Result: 0.967 F1 on unseen attacks and misconfigurations; 0.996 AUC on existing datasets.
  - Limit (my reading): flooding only.
- **[PR · abs] Fu, C., Li, Q., Xu, K. (2023). Detecting Unknown Encrypted Malicious Traffic in Real Time via Flow Interaction Graph Analysis. NDSS 2023.** [DOI](https://doi.org/10.14722/ndss.2023.23080) · [arXiv](https://arxiv.org/abs/2301.13686). Journal version: **Fu, C., Li, Q., Xu, K. (2024). Flow Interaction Graph Analysis: Unknown Encrypted Malicious Traffic Detection. IEEE/ACM ToN 32(4), pp. 2972–2987.** [DOI](https://doi.org/10.1109/TNET.2024.3370851). Details under the next question.
- **[PR · abs] Qing, Y., Yin, Q., Deng, X., Chen, Y., Liu, Z., Sun, K., Xu, K., Zhang, J., Li, Q. (2024). Low-Quality Training Data Only? A Robust Framework for Detecting Encrypted Malicious Network Traffic. NDSS 2024.** [DOI](https://doi.org/10.14722/ndss.2024.23081). Journal version: **(2026) IEEE ToN 34, pp. 5223–5238.** [DOI](https://doi.org/10.1109/TON.2026.3690471)
  - Method: RAPIER augments data using the tight spread of normal traffic and corrects label noise.
  - Data: two public sets, one combined, one from a security firm.
  - Result: with 1,000 samples and 45% noise, F1 of 0.770–0.855; 0.773 on the real-world set.
  - Limit: F1 tops out at 0.855 (0.87 in the journal version), so noisy small datasets remain hard.
- **[PR · abs] Qing, Y., Yin, Q., Deng, X., Zhang, X., Li, P., Liu, Z., Sun, K., Xu, K., Li, Q. (2025). Training Robust Classifiers for Classifying Encrypted Traffic under Dynamic Network Conditions. ACM CCS 2025, pp. 3564–3578.** [DOI](https://doi.org/10.1145/3719027.3765073)
  - Method: MetaTraffic, meta-learning for stable representations across conditions.
  - Data: three public and three new large sets.
  - Result: +8.94% accuracy and +12.55% F1-Macro under changing conditions.
- **[PR · abs] Cui, S., Han, X., Han, D., Wang, Z., Wang, W., Jiang, B., Liu, B., Lu, Z. (2025). FG-SAT: Efficient Flow Graph for Encrypted Traffic Classification Under Environment Shifts. IEEE TIFS 20, pp. 5326–5339.** [DOI](https://doi.org/10.1109/TIFS.2025.3571663)
  - Method: flow graph of internal structure; features chosen by Jensen-Shannon divergence.
  - Result: outperforms prior methods on encrypted attack detection and application classification under shifts.
- **[PRE* · abs] Wan, G., Liu, S., Bronzino, F., Feamster, N., Durumeric, Z. (2024, revised 2025). CATO: End-to-End Optimization of ML-Based Traffic Analysis Pipelines.** [arXiv](https://arxiv.org/abs/2402.06099)
  - Method: multi-objective Bayesian search over features and serving costs.
  - Result: up to 3600x lower inference latency and 3.7x higher zero-loss throughput.
  - Limit: arXiv says NSDI 2025, while a [community list](https://github.com/wangtz19/Awesome-NTA) says S&P 2025. Crossref showed neither, so the venue is unresolved.
- **[PR · abs] Lin, C., Zhang, W., Shen, M., Jiang, Y., Zuo, T., Luo, H., Wang, Y., Meng, X., Zhang, Y. (2026). Is the Data Really Noisy? Rethinking Traffic Filtering for Encrypted Traffic Classification. IEEE TDSC (early access), pp. 1–18.** [DOI](https://doi.org/10.1109/TDSC.2026.3725472)
  - Method: studies common filtering and proposes TraCare, a filter-free framework.
  - Result: filtering harms more than 35% of traffic categories. TraCare gives up to 11.37% relative gain.
  - Limit (my reading): classification, not attack detection.

#### Encrypted Client Hello and DNS

- **[IETF standard · abs] Rescorla, E., Oku, K., Sullivan, N., Wood, C. A. (2026). TLS Encrypted Client Hello. RFC 9849, Standards Track.** [RFC](https://www.rfc-editor.org/info/rfc9849)
  - It encrypts the ClientHello under a server public key. It is now a formal IETF standard.
- **[PR · abs] Merlach, G., Trevisan, M., Giordano, D. (2025). Encrypted Client Hello Is Coming: A View from Passive Measurements. Network 5(3), 29.** [DOI](https://doi.org/10.3390/network5030029)
  - Data: one month from an operational network.
  - Result: 59% of QUIC flows include ECH, but almost all are GREASE values, and only a negligible share reach servers that support it.
  - Limit: one network, before wide adoption.
- **[PR · abs] Shamsimukhametov, D., Kurapov, A., Liubogoshchev, M., Khorov, E. (2022). Is Encrypted ClientHello a Challenge for Traffic Classification? IEEE Access 10, pp. 77883–77897.** [DOI](https://doi.org/10.1109/ACCESS.2022.3191431). Follow-up: **(2024). Early Traffic Classification With Encrypted ClientHello: A Multi-Country Study. IEEE Access 12, pp. 142979–142993.** [DOI](https://doi.org/10.1109/ACCESS.2024.3469730)
  - Method: Random Forest on open TLS metadata plus early flow statistics (hRFTC).
  - Data: collected across North America, Europe and Asia; the dataset is available online.
  - Result: TLS-only classifiers fall to 38.4% F-score; hRFTC reaches up to 94.6%.
  - Limit: a 2026 review snippet says one 2022 study modelled ECH conditions and did not evaluate native ECH deployment — [Electronics 2026 review](https://doi.org/10.3390/electronics15173846). I could not confirm that this refers to the 2022 paper here, or whether the 2024 data is native ECH.
- **[PR · abs] Kahana, Y., Stein, Y. J., Glickman, O. (2026). Fast Real-World Classification of ECH-Enabled Applications. IEEE TMLCN 4, pp. 337–350.** [DOI](https://doi.org/10.1109/TMLCN.2026.3655328)
  - Method: hierarchical classifier on short per-packet information.
  - Data: new dataset from operational traffic.
  - Result: classifies within one second; Random Forest matches deep variants.
- **[PRE · abs] Akbari, E., Zhou, Z., Salahuddin, M. A., Limam, N., Boutaba, R., Mathieu, B., Moteau, S., Tuffin, S. (2025). One task to rule them all: A closer look at traffic classification generalizability.** [arXiv](https://arxiv.org/abs/2507.06430)
  - Method: simulates SNIs hidden in one network and labelled in another.
  - Data: two real TLS datasets from large networks.
  - Result: best models reach only 30–40%, and 1-NN is not far behind.
- **[PR · abs] Siby, S., Juarez, M., Diaz, C., Vallina-Rodriguez, N., Troncoso, C. (2020). Encrypted DNS --> Privacy? A Traffic Analysis Perspective. NDSS 2020.** [DOI](https://doi.org/10.14722/ndss.2020.24301)
  - Method: traffic analysis of DoT and DoH.
  - Result: identifies domains from encrypted DNS with high accuracy; standard padding is not effective.
- **[PR · abs] MontazeriShatoori, M., Davidson, L., Kaur, G., Lashkari, A. H. (2020). Detection of DoH Tunnels using Time-series Classification of Encrypted Traffic. IEEE DASC/PiCom/CBDCom/CyberSciTech 2020.** [DOI](https://doi.org/10.1109/DASC-PICom-CBDCom-CyberSciTech49142.2020.00026)
  - Method: two-layer time-series detection of DoH tunnels.
  - Limit: k-NN on CIC-DoHBrw falls from 98.66 to 79.61 with IP-disjoint splits — [Jerabek et al. 2025](https://arxiv.org/html/2506.08655v1).
- **[PR · cite] Menon, R. M., Praveen, K., Das, A. R., Ambili, K. N. (2026). Enhancing DoH Traffic Classification Using LLM Embeddings: Evaluation of Traditional, LLM-Based, and Hybrid Models. LNNS, pp. 1–12.** [DOI](https://doi.org/10.1007/978-3-032-18135-0_1)
  - Result: F1 above 99% for an LSTM+LLM hybrid, seen only in a [publisher snippet](https://link.springer.com/chapter/10.1007/978-3-032-18135-0_1). Full paper not read.

### Inferences

- STL's split between a network agent (behaviour) and an application agent (content) matches this evidence. The network agent loses little by ignoring ciphertext.
- A good feature set for the network agent is the first 30 packets' sizes, directions and timing (the CESNET format), plus flow statistics, DNS timing and host-level graph links. Plaintext TLS fields should be optional, because ECH will remove some of them.
- STL should not label by SNI alone, since ECH will remove it and only about a quarter of connections had their own SNI in one corpus.
- Results on ISCXVPN2016, USTC-TFC2016 or ISCXTor2016 say little about encrypted traffic, because those sets are mostly unencrypted.

### Gaps

- I found no peer-reviewed test on native ECH traffic at scale. The 2026 Electronics review notes dependence on TLS-specific features, but I read only its abstract.
- I found little peer-reviewed work that combines DNS and TLS metadata with deep models for attack detection. This needs a focused search.
- [Theofanous et al. 2024](https://doi.org/10.1145/3589334.3645719) on TLS fingerprints of malicious servers was found, but only part of its abstract could be read.

## What are the strongest flow-based intrusion and anomaly detection methods, and what do they report on unseen attacks?

### Takeaway

Near-perfect scores come from attack classes seen in training. With a whole attack family held out at 1% FPR, one recent preprint on corrected CICIDS2017 finds mean detection of 76.2% for Random Forest, 40.2% for XGBoost, 25.8% for a 1D-CNN and 22.8% for FT-Transformer. The best peer-reviewed unsupervised systems report F1 of at least 0.86 on unknown attacks, but mostly with attacks replayed over real background or in one institution's network.

### Cited Findings

#### Held-out and cross-dataset tests

- **[PRE · full] Zaro, A. (2026). Adversarial Robustness Is Not Zero-Day Generalization: A Controlled Evaluation of Flow-Based Intrusion Detectors on Corrected CIC-IDS2017.** [arXiv](https://arxiv.org/abs/2611.00713)
  - Method: Random Forest, XGBoost, 1D-CNN and FT-Transformer at fixed 1% FPR over five seeds, leaving out one attack family at a time.
  - Data: corrected CIC-IDS2017, also CSE-CIC-IDS2018.
  - Result: detection under the strongest perturbation stays at 90.9–99.7%, yet held-out family detection is 76.2 / 40.2 / 25.8 / 22.8%. Benign-only anomaly detectors did not close the gap.
  - Limit: single-author preprint, five days old on the check date. Code is public.
- **[PRE · full] Moczkodan, Z., Ragab, H. (2026). Do Transformers Actually Help Intrusion Detection? A Temporal Sequence Evaluation on CIC-IDS2017.** [arXiv](https://arxiv.org/abs/2606.11098)
  - Method: nine models on ordered flow sequences, with a random split, two leakage-free splits and a padding test.
  - Result: padding, not architecture, decides Transformer results. The Transformer's best macro-F1 is 0.89, but a padding cue hides a 67x rise in its false alarm rate. A class-balanced Random Forest is the most robust model.
  - Limit: I found no sign that it uses a corrected CIC-IDS2017 release.
- **[PRE · abs] Atif, M. E., Ali, M. H. (2026). A Three-Axis Stress Test of LLM vs Classical ML for Network Intrusion Detection under Distribution Shift and Adversarial Evasion.** [arXiv](https://arxiv.org/abs/2609.13511)
  - Method: XGBoost against RoBERTa-LoRA on two NetFlow v2 networks.
  - Result: tied on the same dataset. XGBoost wins on transfer by 15 F1 points; RoBERTa-LoRA's FPR reaches 0.78 on the target network. RoBERTa-LoRA wins under evasion by about 17 points.
  - Limit: only two networks, and transfer was directional.
- **[PR · abs] Cantone, M., Marrocco, C., Bria, A. (2024). On the Cross-Dataset Generalization of Machine Learning for Network Intrusion Detection. IEEE Access 12, pp. 144489–144508.** [DOI](https://doi.org/10.1109/ACCESS.2024.3472907) · [arXiv](https://arxiv.org/abs/2402.10974)
  - Method: four classifiers, train on one dataset and test on another.
  - Data: CIC-IDS-2017, CSE-CIC-IDS2018, LycoS-IDS2017, LycoS-Unicas-IDS2018.
  - Result: near-perfect within a dataset, close to random chance across datasets for most combinations.
  - Limit: anomalies in the data themselves block generalisation.
- **[PR · full] Apruzzese, G., Laskov, P., Schneider, J. (2023). SoK: Pragmatic Assessment of Machine Learning for Network Intrusion Detection. IEEE EuroS&P 2023, pp. 592–614.** [DOI](https://doi.org/10.1109/EuroSP57164.2023.00042) · [arXiv](https://arxiv.org/abs/2305.00550)
  - Method: reviews 30 papers and re-assesses ML across hundreds of settings and four hardware platforms.
  - Data: CTU13, NB15, UF-NB15, CICIDS17, GTCS.
  - Result: a survey of 12 practitioners: 92% are uncertain whether papers help them judge real value; 90% call missing statistical comparison "very problematic".
  - Limit: assessments took weeks of computing; concept drift can only be fully judged after deployment.
- **[PR · abs] Sarhan, M., Layeghy, S., Gallagher, M., Portmann, M. (2023). From zero-shot machine learning to zero-day attack detection. International Journal of Information Security 22(4), pp. 947–959.** [DOI](https://doi.org/10.1007/s10207-023-00676-0)
  - Method: maps features to semantic attributes, measured by a Zero-day Detection Rate.
  - Data: two NIDS datasets.
  - Result: some attack groups are not detected as malicious. These have a higher Wasserstein distance from known attacks.
- **[PR · abs] Wilkie, J., Hindy, H., Michie, C., Tachtatzis, C., Irvine, J., Atkinson, R. (2026). A Novel Contrastive Loss for Zero-Day Network Intrusion Detection. IEEE TNSM 23, pp. 2064–2076.** [DOI](https://doi.org/10.1109/TNSM.2026.3652529) · [arXiv](https://arxiv.org/abs/2601.09902)
  - Method: contrastive loss that uses benign and known attack samples.
  - Data: Lycos2017.
  - Result: AUROC gain of 0.060883 on zero-day detection; OpenAUC gain of 0.170883.
  - Limit: one dataset.
- **[PR · abs] Nayak, S. (2026). ThreatFormer-IDS: Robust Transformer Intrusion Detection with Zero-Day Generalization and Explainable Attribution. AICCONF 2026, pp. 1–8.** [DOI](https://doi.org/10.1109/AICCONF69182.2026.11600642) · [arXiv](https://arxiv.org/abs/2603.00185)
  - Method: time-ordered flow windows, masked self-supervision, adversarial training, Integrated Gradients.
  - Data: ToN IoT, chronological split.
  - Result: on held-out families, AUC-PR 0.721 and Recall@1%FPR 0.783.
  - Limit: one dataset. Authors of Bad Design Smells flag problems in ToN IoT, see the next question.

#### Unsupervised and graph-based detectors

- **HyperVision (citation under the previous question) [PR · full].**
  - Method: unsupervised learning on an in-memory graph of flow interactions.
  - Data: 92 datasets, 48 with encrypted attacks, replayed over MAWI backbone traffic from January to June 2020, plus Kitsune, CIC-DDoS2019 and CIC-IDS2017 sets.
  - Result: at least 0.92 AUC and 0.86 F1, at least 80.6 Gb/s, 0.83 s mean latency. Over 50% of the attacks evaded all prior methods.
  - Limit: covers active attacks only. Attacks are injected into MAWI, which has no ground truth.
- **[PR · abs] Fu, C., Li, Q., Bertino, E., Xu, K. (2025). Training with Only 1.0 ‰ Samples: Malicious Traffic Detection via Cross-Modality Feature Fusion. ACM CCS 2025, pp. 3930–3944.** [DOI](https://doi.org/10.1145/3719027.3765143)
  - Method: tFusion, cross-modal attention over packet, flow and host features; topology-driven contrastive pre-training.
  - Data: five days in an institutional network, plus 11 existing datasets.
  - Result: labels only 1.0‰ of traffic and reaches 99.82% accuracy.
  - Limit (my reading): accuracy on rare attacks can hide false alarm load.
- **[PR · abs] Fu, C., Li, Q., Shen, M., Xu, K. (2021). Realtime Robust Malicious Traffic Detection via Frequency Domain Analysis. ACM CCS 2021, pp. 3431–3446.** [DOI](https://doi.org/10.1145/3460120.3484585)
  - Method: Whisper, frequency-domain features.
  - Data: 42 attack types.
  - Result: up to 18.36% AUC gain and about 90% accuracy under evasion attacks.
- **[PR · abs] Hsieh, K., Wong, M., Segarra, S., Mani, S. K., Eberl, T., Panasyuk, A., Netravali, R., Chandra, R., Kandula, S. (2024). NetVigil: Robust and Low-Cost Anomaly Detection for East-West Data Center Security. USENIX NSDI 2024.** [Page](https://www.usenix.org/conference/nsdi24/presentation/hsieh)
  - Method: graph neural network and contrastive learning on flow logs.
  - Data: traces from production clusters.
  - Result: better accuracy, cost and latency than prior anomaly detectors.
  - Limit (my reading): built for data centres, not backbone links.
- **[PR · abs] Mirsky, Y., Doitshman, T., Elovici, Y., Shabtai, A. (2018). Kitsune: An Ensemble of Autoencoders for Online Network Intrusion Detection. NDSS 2018.** [DOI](https://doi.org/10.14722/ndss.2018.23204) · [arXiv](https://arxiv.org/abs/1802.09089)
  - Method: online autoencoder ensemble. A baseline before the requested date range.
  - Limit: did not finish within 90 minutes on some HyperVision datasets — [Fu et al. 2023](https://ar5iv.labs.arxiv.org/html/2301.13686).
- **[PR · abs] Caville, E., Lo, W. W., Layeghy, S., Portmann, M. (2022). Anomal-E: A self-supervised network intrusion detection system based on graph neural networks. Knowledge-Based Systems 258, 110030.** [DOI](https://doi.org/10.1016/j.knosys.2022.110030) · [arXiv](https://arxiv.org/abs/2207.06819)
  - Method: self-supervised edge GNN on flows.
  - Data: two benchmarks.
  - Result: embeddings beat raw features; no numbers in the abstract.
- **[PR · abs] Lo, W. W., Layeghy, S., Sarhan, M., Gallagher, M., Portmann, M. (2022). E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT. IEEE/IFIP NOMS 2022, pp. 1–9.** [DOI](https://doi.org/10.1109/NOMS54207.2022.9789878) · [arXiv](https://arxiv.org/abs/2103.16329)
  - Method: GNN using edge features and topology of flows.
  - Data: four NIDS benchmarks.
  - Result: beats prior work on classification metrics.
  - Limit (my reading): no unseen attack test in the abstract.
- **[PR · abs] Wu, C., Sun, J., Chen, J., Alazab, M., Liu, Y., Xiang, Y. (2025). TCG-IDS: Robust Network Intrusion Detection via Temporal Contrastive Graph Learning. IEEE TIFS 20, pp. 1475–1486.** [DOI](https://doi.org/10.1109/TIFS.2025.3530702)
  - Method: self-supervised temporal contrastive GNN.
  - Data: NF-CSE-CIC-IDS2018-V2, NF-UNSW-NB15-V2.
  - Result: balanced accuracy 99.48% and 91.48%; mean FPR of 4.15% and 3.34% in multi-class detection.
  - Limit (my reading): FPRs that size mean heavy alert load on real traffic.

#### Transformers on flow records

- **[PR · full] Manocchio, L. D., Layeghy, S., Lo, W. W., Kulatilleke, G. K., Sarhan, M., Portmann, M. (2024). FlowTransformer: A transformer framework for flow-based network intrusion detection systems. Expert Systems with Applications 241, 122564.** [DOI](https://doi.org/10.1016/j.eswa.2023.122564) · [arXiv](https://arxiv.org/abs/2304.14746)
  - Method: modular comparison of input encodings, transformer bodies and classification heads, including GPT 2.0 and BERT.
  - Data: NSL-KDD, UNSW-NB15, CSE-CIC-IDS2018.
  - Result: on CSE-CIC-IDS2018, a shallow encoder reaches F1 97.05% with 0.10% false alarm rate; GPT 96.93%; BERT 95.80%. On UNSW-NB15, 90.45%. Global Average Pooling and CLS heads collapse F1 to about 0.33. Model size can fall by over 50% with no loss.
  - Limit: no held-out attack test in the sections I read. It reports the best of at least three repeats and uses NSL-KDD.
- **[PR · abs] Ferrag, M. A., Ndhlovu, M., Tihanyi, N., Cordeiro, L. C., Debbah, M., Lestable, T., Thandi, N. S. (2024). Revolutionizing Cyber Threat Detection With Large Language Models: A Privacy-Preserving BERT-Based Lightweight Model for IoT/IIoT Devices. IEEE Access 12, pp. 23733–23750.** [DOI](https://doi.org/10.1109/ACCESS.2024.3363469) · [arXiv](https://arxiv.org/abs/2306.14263)
  - Method: SecurityBERT, fixed-length encoding of flow fields plus a byte-level tokeniser.
  - Data: Edge-IIoTset.
  - Result: 98.2% accuracy on 14 attack types; 16.7 MB model.
  - Limit: Edge-IIoTset's gap to the theoretical maximum is under 0.15%, so it is unsuitable for benchmarking — [Jerabek et al. 2025](https://arxiv.org/html/2506.08655v1).

#### Unknown class detection and adaptation

- **[PR · abs] Zhao, Z., Li, Z., Song, Z., Li, W., Zhang, F. (2024). Trident: A Universal Framework for Fine-Grained and Class-Incremental Unknown Traffic Detection. WWW 2024, pp. 1608–1619.** [DOI](https://doi.org/10.1145/3589334.3645407)
  - Method: splits known and new class detection into one-class tasks.
  - Data: four datasets.
  - Result: beats 16 prior methods.
- **[PR · abs] Meng, Q., Tao, J., Yuan, Q., Li, G., Wang, Y., Gao, B., Lu, S. (2025). Detection of Unknown Attacks Through Encrypted Traffic: A Gaussian Prototype-Aided Variational Autoencoder Framework. IEEE TIFS 20, pp. 10652–10667.** [DOI](https://doi.org/10.1109/TIFS.2025.3612141)
  - Method: Open-Detect maps each class to a Gaussian prototype and flags far samples.
  - Limit: abstract gives no numbers; flows become grayscale images.
- **[PR · abs] Meng, Q., Yuan, Q., Shen, M., Lu, S., Li, G., Tao, J., Yu, Y., Wang, Y. (2026). Fine-Grained Detection and Analysis of Unknown Encrypted Malicious Traffic From Mixed Noisy Labels. IEEE TDSC 23(5), pp. 10035–10052.** [DOI](https://doi.org/10.1109/TDSC.2026.3697849)
  - Method: Sieve corrects labels, uses Mahalanobis distance and clusters the unknowns.
  - Result: above 94% accuracy and F1 on Mal_TLS2023 with 50% noise.
- **[PR · abs] Yang, L., Finamore, A., Jun, F., Rossi, D. (2021). Deep Learning and Zero-Day Traffic Classification: Lessons Learned From a Commercial-Grade Dataset. IEEE TNSM 18(4), pp. 4103–4118.** [DOI](https://doi.org/10.1109/TNSM.2021.3122940)
  - Method: GradBP, gradient backpropagation for zero-day application detection.
  - Data: commercial dataset with hundreds of application labels.
  - Result: DL and ML tie on known traffic, but DL's learned features help on unknown classes.
- **[PR · abs] Han, D., Wang, Z., Chen, W., Wang, K., Yu, R., Wang, S., Zhang, H., Wang, Z., Jin, M., Yang, J., Shi, X., Yin, X. (2023). Anomaly Detection in the Open World: Normality Shift Detection, Explanation, and Adaptation. NDSS 2023.** [DOI](https://doi.org/10.14722/ndss.2023.24830)
  - Method: OWAD detects, explains and adapts to shift in normal traffic, unsupervised.
  - Data: three applications with long-term data; a SCADA deployment.
  - Result: better adaptation with less labelling.
- **[PR · abs] Yang, S., Zheng, X., Li, J., Xu, J., Wang, X., Ngai, E. C. H. (2024). ReCDA: Concept Drift Adaptation with Representation Enhancement for Network Intrusion Detection. ACM KDD 2024, pp. 3818–3828.** [DOI](https://doi.org/10.1145/3637528.3672007)
  - Method: self-supervised representation stage, then weakly supervised tuning.
- **[PR · abs] Alotaibi, F., Maffeis, S. (2024). Mateen: Adaptive Ensemble Learning for Network Anomaly Detection. RAID 2024, pp. 215–234.** [DOI](https://doi.org/10.1145/3678890.3678901)
  - Method: adaptive autoencoder ensemble, aimed at false alarms from benign change.
- **[PR · cite] Amalapuram, S. K., Tamma, B. R., Channappayya, S. S. (2024). SPIDER: A Semi-Supervised Continual Learning-based Network Intrusion Detection System. IEEE INFOCOM 2024, pp. 571–580.** [DOI](https://doi.org/10.1109/INFOCOM52122.2024.10621428)
- **[PR · abs] Zhang, X., Zhao, R., Jiang, Z., Sun, Z., Ding, Y., Ngai, E. C. H., Yang, S.-H. (2024). AOC-IDS: Autonomous Online Framework with Contrastive Learning for Intrusion Detection. IEEE INFOCOM 2024, pp. 581–590.** [DOI](https://doi.org/10.1109/INFOCOM52122.2024.10621346) · [arXiv](https://arxiv.org/abs/2402.01807)
  - Method: online pseudo-labels for updates, no human labelling.
  - Data: NSL-KDD, UNSW-NB15.
  - Limit (my reading): NSL-KDD is an old benchmark, and neither set shows current traffic.

### Inferences

- STL should report leave-one-family-out detection at a fixed low FPR as a main result, with Random Forest and XGBoost as baselines. Random Forest beating FT-Transformer in the Zaro result is plausible but needs reproduction.
- STL's result on unseen attacks may be well below its seen-attack score. The project plan should treat this as expected, not as failure.
- HyperVision, Exosphere and tFusion suggest that flow interaction graphs and host context may carry more signal for unknown attacks than per-flow sequences. A hybrid network agent is worth testing.
- Replaying attacks over MAWI is an accepted method (HyperVision) and is a practical way to use MAWI in STL.

### Gaps

- Most zero-day numbers above are on lab datasets. I found no peer-reviewed comparison of transformer and tree models under family holdout on real traffic.
- The two leading held-out studies (Zaro; Moczkodan and Ragab) are preprints and need reproduction.
- I did not find per-family results for HyperVision or tFusion in the sections I read.

## What is known about dataset flaws and evaluation pitfalls?

### Takeaway

This is the best-supported part of the topic. Published scores are inflated by flow-construction bugs, wrong labels, leakage through same-flow packets or duplicates, identifying fields, random splits and ignoring the base rate. On real networks true attacks are extremely rare, so false alarm rate is the limiting factor.

### Cited Findings

#### General pitfalls

- **[PR · full] Arp, D., Quiring, E., Pendlebury, F., Warnecke, A., Pierazzi, F., Wressnegger, C., Cavallaro, L., Rieck, K. (2022). Dos and Don'ts of Machine Learning in Computer Security. USENIX Security 2022 (Distinguished Paper).** [Page](https://www.usenix.org/conference/usenixsecurity22/presentation/arp) · [arXiv](https://arxiv.org/abs/2010.09470). Shorter version: **(2024). Pitfalls in Machine Learning for Computer Security. Communications of the ACM 67(11), pp. 104–112.** [DOI](https://doi.org/10.1145/3643456)
  - Method: ten pitfalls, checked by two reviewers each across 30 top-tier papers.
  - Result: P1 Sampling Bias 60% present, P2 Label Inaccuracy 10%, P3 Data Snooping 57%, P4 Spurious Correlations 20%, P5 Biased Parameter Selection 10%, P6 Inappropriate Baseline 20%, P7 Inappropriate Performance Measures 33%, P8 Base Rate Fallacy 10%, P9 Lab-Only Evaluation 47%, P10 Inappropriate Threat Model 17%. Counting partial cases, sampling bias reaches 90% and data snooping 73%. Every paper had at least three pitfalls, and only 22% of instances were discussed.
  - Limit: authors agreed with the findings 63% of the time on average. The sample is security in general, not only NIDS.
  - Recommended fixes: split test data early and respect time order; use explanations to find shortcut features; compare against simple models; report precision and recall, and FPR against the base rate — [Arp et al.](https://ar5iv.labs.arxiv.org/html/2010.09470).
- **[PR · abs] Pendlebury, F., Pierazzi, F., Jordaney, R., Kinder, J., Cavallaro, L. (2019). TESSERACT: Eliminating Experimental Bias in Malware Classification across Space and Time. USENIX Security 2019.** [Page](https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury)
  - Method: space and time constraints for evaluation.
  - Result: published scores near 0.99 are inflated by spatial and temporal bias.
  - Limit: Android malware, but the split logic carries over (my reading).
- **[PR · abs] Jacobs, A. S., Beltiukov, R., Willinger, W., Ferreira, R. A., Gupta, A., Granville, L. Z. (2022). AI/ML for Network Security: The Emperor has no Clothes. ACM CCS 2022, pp. 1537–1551.** [DOI](https://doi.org/10.1145/3548606.3560609)
  - Method: studies underspecification by building explainable surrogates of black-box models.
- **[PR · abs] Thirumuruganathan, S., Deniz, F., Khalil, I., Yu, T., Nabeel, M., Ouzzani, M. (2024). Detecting and Mitigating Sampling Bias in Cybersecurity with Unlabeled Data. USENIX Security 2024.** [Page](https://www.usenix.org/conference/usenixsecurity24/presentation/thirumuruganathan)
  - Method: detects and reduces sampling bias using unlabelled production data.

#### CICIDS2017 and related datasets

- **[PR-W · full] Engelen, G., Rimmer, V., Joosen, W. (2021). Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study. IEEE Security and Privacy Workshops (WTMC 2021), pp. 7–12.** [DOI](https://doi.org/10.1109/SPW53761.2021.00009) · [Site](https://intrusion-detection.distrinet-research.be/WTMC2021/)
  - Method: audits the data pipeline, fixes CICFlowMeter and regenerates the data.
  - Result: 25.9% of the dataset is "TCP appendices" from a flow-ending bug (one FIN packet ended a flow, RST was ignored). More than 20% of traces were rebuilt or relabelled. DoS Hulk was misused and ineffective. From Table I as extracted: Web Brute Force 1,507 to 151 flows, XSS 652 to 27, Slowhttptest 5,499 to 1,742. Overall accuracy stayed 0.99 in all three versions while Bot F1 went from 0.60 to 0.99. Bot detection had learned RST packets, meaning failed TCP connections, not botnet traffic.
  - Limit: Web SQL Injection ends with 12 flows, too few to test.
- **[PR · abs] Liu, L., Engelen, G., Lynar, T., Essam, D., Joosen, W. (2022). Error Prevalence in NIDS datasets: A Case Study on CIC-IDS-2017 and CSE-CIC-IDS-2018. IEEE CNS 2022, pp. 254–262.** [DOI](https://doi.org/10.1109/CNS56114.2022.9947235) · [Site](https://intrusion-detection.distrinet-research.be/CNS2022/)
  - Method: documents errors in attack setup, features, documentation and labels; rebuilds both datasets.
  - Result: fully recreated datasets with open labelling logic.
  - Limit: authors advise relabelling "Attempted" flows as Benign when unsure, and never treating them as a separate class — [download page](https://intrusion-detection.distrinet-research.be/CNS2022/Dataset_Download.html).
- **[PR · abs] Lanvin, M., Gimenez, P.-F., Han, Y., Majorczyk, F., Mé, L., Totel, E. (2023). Errors in the CICIDS2017 Dataset and the Significant Differences in Detection Performances It Makes. CRiSIS 2022, LNCS, pp. 18–33.** [DOI](https://doi.org/10.1007/978-3-031-31108-6_2) · [HAL](https://hal.science/hal-03775466)
  - Method: finds packet misorder, duplication and attacks performed but not labelled, then measures the effect on supervised detectors.
  - Limit: abstract only. The full text and any label download sit behind a bot wall; I could not read the figures.
- **[PR · cite] Rosay, A., Cheval, E., Carlier, F., Leroux, P. (2022). Network Intrusion Detection: A Comprehensive Analysis of CIC-IDS2017. ICISSP 2022, pp. 25–36.** [DOI](https://doi.org/10.5220/0010774000003120) · [LYCOS-IDS2017](https://lycos-ids.univ-lemans.fr/)
  - Method: new flow tool, LycoSTand, and a rebuilt dataset.
- **[PRE · abs] Xin, Y., Goseland, B., Rahouti, M. (2026). Multi-Class, Multi-Tier Network Intrusion Detection: A Comprehensive and Reproducible Benchmark.** [arXiv](https://arxiv.org/abs/2609.36039)
  - Method: corrected PCAP-level labels; eleven tabular models.
  - Result: voting ensemble reaches macro-F1 0.999 binary, 0.955 on 15 classes.
  - Limit: corrected labels do not make the dataset hard. Seen-attack scores stay near perfect.
- **[PR · full] Flood, R., Engelen, G., Aspinall, D., Desmet, L. (2024). Bad Design Smells in Benchmark NIDS Datasets. IEEE EuroS&P 2024, pp. 658–675.** [DOI](https://doi.org/10.1109/EuroSP60621.2024.00042) · [Draft](https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf)
  - Method: manual analysis of seven datasets (CIC 2017, CIC 2018, ISCX 2012, UNSW-NB15, ToN IoT, Bot-IoT, CTU-13) and 38 papers using them.
  - Result: six smells: poor data diversity, highly dependent features, unclear ground truth, wrong labels, traffic collapse, artificial diversity. 97.8% of malicious flows in CTU-13 Scenario 5 relate to a basic nmap scan. UNSW-NB15 TTL values appear to fingerprint operating systems. ToN IoT treats DNS traffic as malicious.
  - Limit: authors note a smell is not always harmful, for example Timestamp where data is periodic.
- **[PR-W · abs] Bönninghausen, P., Uetz, R., Henze, M. (2024). Introducing a Comprehensive, Continuous, and Collaborative Survey of Intrusion Detection Datasets. CSET 2024, pp. 34–40.** [DOI](https://doi.org/10.1145/3675741.3675754) · [arXiv](https://arxiv.org/abs/2408.02521)
  - Method: COMIDDS, a living website and GitHub survey of IDS datasets.
- **[PRE · abs] Youssef, M. A. (2026). Stream Assembly Is an Uncontrolled Treatment in Streaming Intrusion-Detection Benchmarks.** [arXiv](https://arxiv.org/abs/2605.24696)
  - Result: on CICIDS2017, reordering identical records yields test sets sharing only 32.5% of records, with prevalence of 68.2% against 25.2%.
  - Limit: the author corrected and rebuilt v3 after v1 and v2 reported wrong results.

#### Leakage and duplicates in encrypted traffic work

- **Zhao et al. 2025 and Wickramasinghe et al. 2025 (citations under the previous sections).** Packets of the same flow in train and test create a data leak; TCP SeqNo, AckNo and timestamps act as implicit flow IDs — [Zhao et al.](https://arxiv.org/html/2507.16438v1). Twelve guidelines include avoiding MAC, IP, ports, IP ID, checksums and TCP timestamps — [Wickramasinghe et al.](https://arxiv.org/html/2503.20093v4).
- **Jerabek et al. 2025 [PRE · full].** Most datasets have over 50% redundant samples, shared between train and test. Time split on CESNET-QUIC22 drops k-NN from 79.41 to 70.99 by week 47. IP-disjoint split on CIC-DoHBrw drops it from 98.66 to 79.61. CIC-IDS-2017's gap to the theoretical maximum is under 0.15%, so it is called unsuitable for benchmarking. Their advice: do not use random splits, deduplicate, and report a simple baseline — [Jerabek et al.](https://arxiv.org/html/2506.08655v1).
- **[PR · abs] Finamore, A., Wang, C., Krolikowski, J., Navarro, J. M., Chen, F., Rossi, D. (2023). Replication: Contrastive Learning and Data Augmentation in Traffic Classification Using a Flowpic Input Representation. ACM IMC 2023, pp. 36–51.** [DOI](https://doi.org/10.1145/3618257.3624820) · [arXiv](https://arxiv.org/abs/2309.09733)
  - Result: confirms most findings of the original, but finds a 20% accuracy drop in some scenarios from a data shift in the original dataset.
- **[PRE · abs] Roy, U. S., Minu, M. J. (2026). Unmasking Shortcut Learning in IoT Intrusion Detection.** [arXiv](https://arxiv.org/abs/2609.28725)
  - Data: CyberFlowIoT-GICAP, 3.6 million flows, PCAP-disjoint splits.
  - Result: with behaviour features only, LightGBM, Random Forest and an MLP all reach about 92.6% macro-F1. DNS Beaconing recall falls from 27.78% to 0% once context features are removed.

#### Concept drift

- **[PR · abs] Yang, L., Guo, W., Hao, Q., Ciptadi, A., Ahmadzadeh, A., Xing, X., Wang, G. (2021). CADE: Detecting and Explaining Concept Drift Samples for Security Applications. USENIX Security 2021.** [Page](https://www.usenix.org/conference/usenixsecurity21/presentation/yang-limin)
  - Method: contrastive learning maps samples to a space where distance flags drift, and explains it.
  - Limit: CADE's evaluation keeps the Timestamp feature, a possible highly dependent feature — [Flood et al.](https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf).
- **[PR · cite] Malekghaini, N., Akbari, E., Salahuddin, M. A., Limam, N., Boutaba, R., Mathieu, B., Moteau, S., Tuffin, S. (2023). Deep learning for encrypted traffic classification in the face of data drift: An empirical study. Computer Networks 225, 109648.** [DOI](https://doi.org/10.1016/j.comnet.2023.109648)
  - Result: not read; no abstract in the index.
- **[PR · abs] Hynek, K., Luxemburk, J., Pešek, J., Čejka, T., Šiška, P. (2024). CESNET-TLS-Year22: A year-spanning TLS network traffic dataset from backbone lines. Scientific Data 11.** [DOI](https://doi.org/10.1038/s41597-024-03927-4)
  - Method: a year of real TLS traffic designed to test robustness over time. See the dataset table under the next question.
- OWAD, ReCDA and Mateen, under the previous question, address drift directly.

#### False alarms on real traffic

- **[PR · abs] Yang, L., Chen, Z., Wang, C., Zhang, Z., Booma, S., Cao, P., Adam, C., Withers, A., Kalbarczyk, Z., Iyer, R. K., Wang, G. (2024). True Attacks, Attack Attempts, or Benign Triggers? An Empirical Measurement of Network Alerts in a Security Operations Center. USENIX Security 2024.** [Page](https://www.usenix.org/conference/usenixsecurity24/presentation/yang-limin)
  - Data: 115 million alerts over four years from a real SOC, with ground truth of 227 attacks.
  - Result: 24K–134K alerts per day, and only 0.01% tied to true attacks. 27% are attack attempts and 49% are benign triggers.
  - Limit: one SOC, and rule-based alerts, not ML.
- **[PR · abs] Alahmadi, B. A., Axon, L., Martinovic, I. (2022). 99% False Positives: A Qualitative Study of SOC Analysts' Perspectives on Security Alarms. USENIX Security 2022.** [Page](https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi)
  - Data: survey (n=20) and interviews (n=21).
  - Result: most perceived false positives are benign triggers. Five properties for good alarms: Reliable, Explainable, Analytical, Contextual, Transferable.
- **[PR · abs] Axelsson, S. (2000). The base-rate fallacy and the difficulty of intrusion detection. ACM TISSEC 3(3), pp. 186–205.** [DOI](https://doi.org/10.1145/357830.357849)
  - Result: the false alarm rate is the limiting factor for an IDS. Before the requested date range, but still the core argument.
- **[PR · abs] Fu, C., Li, Q., Xu, K., Wu, J. (2023). Point Cloud Analysis for ML-Based Malicious Traffic Detection: Reducing Majorities of False Positive Alarms. ACM CCS 2023, pp. 1005–1019.** [DOI](https://doi.org/10.1145/3576915.3616631)
  - Method: pVoxel groups alarm feature vectors into voxels and uses density to spot false positives, unsupervised.
  - Data: 75 real-world datasets and 11 detectors.
  - Result: removes 95.55% of false positives, at 201.10K alarms per second — [abstract on Thinkst Citation](https://citation.thinkst.com/talk/86985).
- **[PR · abs] Vermeer, M., Kadenko, N., van Eeten, M., Gañán, C., Parkin, S. (2023). Alert Alchemy: SOC Workflows and Decisions in the Management of NIDS Rules. ACM CCS 2023, pp. 2770–2784.** [DOI](https://doi.org/10.1145/3576915.3616581)
  - Data: interviews with 17 professionals.
  - Result: rule specificity and alert volume drive SOC decisions.
- **[PR · cite] Guerra, J. L., Catania, C., Veas, E. (2022). Datasets are not enough: Challenges in labeling network traffic. Computers & Security 120, 102810.** [DOI](https://doi.org/10.1016/j.cose.2022.102810)
  - Result: not read; no abstract in the index.

### Inferences

- A worked base-rate example (my arithmetic, not from a source): if 1 flow in 10,000 is malicious and recall is perfect, a 1% FPR gives precision of about 1%. Reaching 50% precision needs FPR of about 0.01%. So STL should report precision at realistic prevalence, not only F1.
- The 0.01% from Yang et al. is a share of alerts, not flows, so real flow-level prevalence may be lower.
- STL checklist drawn from these sources:
  - Split by flow at minimum; better by time and by host or network.
  - Remove or test without IP, MAC, ports, TTL, IP ID, checksums, SeqNo, AckNo and raw timestamps.
  - Deduplicate, and report the maximum achievable accuracy.
  - Report per-class results. Aggregate accuracy hid the whole CICIDS2017 problem.
  - Include k-NN, Random Forest and LightGBM or XGBoost baselines.
  - Report leave-one-family-out, cross-dataset and fixed-FPR results.
  - Run feature importance to find shortcuts.
  - Handle "attempted" attacks explicitly, since they are label noise in real alerts as well.

### Gaps

- I could not obtain Lanvin's performance figures or the Liu et al. error counts per class.
- I found no peer-reviewed, multi-month study of deep NIDS false alarm rates on real backbone traffic. One [drift paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13517801/) states that longer real-deployment evaluation is still needed.
- Preprint-only claims here should be cited as such.

## Which real traffic datasets are recommended today, and how can each be obtained?

### Takeaway

No source names one best dataset, and the 2025 survey of 89 datasets stresses that the community lacks best practice, not data. For STL the sources support a mix: CESNET sets for real labelled metadata and drift, MAWI as unlabelled real background, CTU-13 for real malware with caution, and the improved CIC-IDS-2017 only for family-holdout tests. MAWILab labels stopped in December 2024.

### Cited Findings

| Dataset | What it is | Labels | How to get it | Main caveat |
|---|---|---|---|---|
| [CESNET DataZoo](https://cesnet.github.io/cesnet-datazoo/datasets_overview/) | Real ISP traffic. CESNET-TLS22: 141M samples, 2 weeks, 191 classes. CESNET-QUIC22: 153M, 4 weeks. CESNET-TLS-Year22: 507M, 1 year, 180 classes. CESNET-QUICEXT-25: 194M, 12 months | Web service or app, not attacks | Python package `cesnet-datazoo` ([docs](https://cesnet.github.io/cesnet-datazoo/)) | Sizes, directions and times for the first 30 packets; no attack labels |
| [MAWI archive](https://mawi.wide.ad.jp/mawi/) | Real backbone. Samplepoint-F daily since 2006, BBIX link added August 2023. IPs scrambled with tcpdpriv | None | Free download by date. Research use only, no privacy violations | No ground truth. A [sampled trace](https://mawi.wide.ad.jp/mawi/samplepoint-F/2026/202604011400.html) (1 April 2026) has 96-byte capture length, 15 minutes, 339.5M packets, 2.85 Gbps. Gap from 4 November to 15 December 2022; duplicates from 28 May to 3 September 2015 |
| [MAWILab](http://www.fukuda-lab.org/mawilab/) | Anomaly labels for MAWI from combined detectors ([Fontugne et al. 2010](https://doi.org/10.1145/1921168.1921179)) | Automated, not verified attacks | Web site | Site says updates stopped December 2024 because quality fell. [Goldschmidt and Chudá](https://arxiv.org/html/2502.06688v3) say inactive since 2015; I treat the site as authoritative |
| [CTU-13](https://www.stratosphereips.org/datasets-ctu13) | 13 botnet scenarios, real network, 2011 ([Garcia et al. 2014](https://doi.org/10.1016/j.cose.2014.05.011)) | Botnet, C&C, Normal, Background on NetFlows | Archive of about 1.9 GB, or per-scenario folders | Full pcaps with background are withheld for privacy. Use bidirectional NetFlows. Scenario 5 is mostly an nmap scan ([Flood et al.](https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf)). Old, so it cannot test modern encryption (my reading) |
| [Improved CIC-IDS-2017](https://intrusion-detection.distrinet-research.be/CNS2022/Dataset_Download.html) | Lab, 5 days, July 2017. Rebuilt with fixed [CICFlowMeter](https://github.com/GintsEngelen/CICFlowMeter) | Corrected, with "Attempted" flag | Direct download; docs per attack on the [CNS 2022 site](https://intrusion-detection.distrinet-research.be/CNS2022/CICIDS2017.html) | Latest version of the two from this group. Still synthetic: 25 synthetic employees, per [Jerabek et al.](https://arxiv.org/html/2506.08655v1) |
| [Original CIC-IDS-2017](https://www.unb.ca/cic/datasets/ids-2017.html) ([Sharafaldin et al. 2018](https://doi.org/10.5220/0006639801080116)) | Same lab capture, pcaps and CSV | Original, flawed | Direct link from UNB | Use only to reproduce old results |
| [LYCOS-IDS2017](https://lycos-ids.univ-lemans.fr/) | Rebuilt from CIC-IDS2017 with LycoSTand | Rebuilt | Code and data on the site | Used by Wilkie et al. and Cantone et al. |
| [CAIDA Anonymized Traces](https://www.caida.org/catalog/datasets/passive_dataset/) | Real backbone, April 2008 to January 2019 | None | Request form and Acceptable Use Agreement; must report publications | Restricted. No payload. CryptoPan IPs. No longer collected. A separate 100G set runs from April 2024 and is restricted |
| [CipherSpectrum](https://cspectrum.web.cse.unsw.edu.au) | TLS 1.3, 120,000 sessions, 40 domains, January to March 2024 | Domain | Short form, links shown at once | Scripted browsers; no attacks |
| [IoT-23](https://www.stratosphereips.org/datasets-iot23) | 20 malware and 3 benign IoT captures, 2018–2019 | Yes | 21 GB full, 8.8 GB flows only; Zenodo DOI 10.5281/zenodo.4743746 | IoT scope |
| [HIKARI-2021](https://zenodo.org/records/6463389) ([Ferriyan et al. 2021](https://doi.org/10.3390/app11177868)) | Encrypted synthetic attacks and benign traffic | Yes | Zenodo, CC-BY-4.0, pcaps and CSV | Attacks are synthetic |
| [UQ NetFlow datasets](https://staff.itee.uq.edu.au/marius/NIDS_datasets/) | V2 has 43 features, five datasets. V3 adds 10 temporal features, four datasets ([Luay et al. 2026](https://doi.org/10.1109/ACCESS.2026.3688204); [Sarhan et al. 2022](https://doi.org/10.1007/s11036-021-01843-0)) | Inherited from source sets | CSV from the UQ page | Flows only, and source dataset flaws carry over (my reading) |
| [CIC-IoT2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html) ([Neto et al. 2023](https://doi.org/10.3390/s23135941)) | Large IoT attack benchmark | Yes | UNB page | Lab. Page not opened; DOI confirmed |
| [CIRA-CIC-DoHBrw-2020](https://www.unb.ca/cic/datasets/dohbrw-2020.html) | DoH traffic and tunnels | Yes | UNB page | k-NN drops from 98.66 to 79.61 on IP-disjoint split. Page not opened |
| [UNSW-NB15](https://doi.org/10.1109/MilCIS.2015.7348942) | Lab, 2015 (Moustafa and Slay) | Yes | Not checked | TTL fingerprints operating systems ([Flood et al.](https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf)) |
| [UGR'16](https://doi.org/10.1016/j.cose.2017.11.004) | Maciá-Fernández et al. 2018, Computers & Security 73, pp. 411–424 | Not read | Not checked | Citation only |

- **[PR · abs] Goldschmidt, P., Chudá, D. (2025). Network intrusion datasets: A survey, limitations, and recommendations. Computers & Security 156, 104510.** [DOI](https://doi.org/10.1016/j.cose.2025.104510) · [arXiv](https://arxiv.org/abs/2502.06688)
  - Method: compares 89 public datasets on 13 properties.
  - Result: DARPA and KDD sets are no longer recommended. Random or time-ignoring splits can inflate results. CTU-13 counts as real, not emulated, traffic.
  - Limit: I read about 37% of the text, not its recommendations section.
- MAWI and CAIDA are used by [Beltiukov et al. 2025](https://arxiv.org/html/2509.23089) as the real-world sets. MAWI is used as background in [HyperVision](https://ar5iv.labs.arxiv.org/html/2301.13686) and for pre-training in [Pcap-Encoder](https://arxiv.org/html/2507.16438v1).
- The netFound authors claim to release a 4.2-billion-flow pre-training dataset — [arXiv](https://arxiv.org/abs/2310.17025). I did not confirm the download.
- NETD, a dataset for distribution shift from the ETooL authors, is [listed here](https://github.com/linwhitehat/ETA-Resource). Not opened.

### Inferences

- The three datasets named in the project brief are complementary:
  - CTU-13 gives real botnet flows, but in NetFlow form only for background, so packet-sequence models cannot run over it.
  - Corrected CICIDS2017 gives attack variety with known labels.
  - MAWI gives real scale and false alarm load but no truth.
- MAWI's 96-byte capture length leaves about 30–42 bytes after Ethernet, IP and TCP headers. Most TLS SNI fields will be cut off, while short DNS queries may fit. This should be measured on samples before design decisions rest on it.
- Since MAWI has no labels, STL can use it to measure alert volume on presumed-mostly-benign traffic and to inject attacks, as HyperVision did. It should not be reported as a detection accuracy test.
- CESNET-TLS-Year22 is the strongest option for a real drift test, though for application identity, not attacks. It would be a useful fourth dataset.

### Gaps

- The Goldschmidt and Chudá recommendations section was not read; the page was too long for one fetch.
- I could not confirm that the Lanvin corrected labels are still online. HAL and Inria GitLab returned bot checks.
- UNB dataset pages other than CIC-IDS-2017 were listed but not opened.
- I did not confirm licences for CTU-13, MAWI or the improved CIC-IDS-2017; their pages state no licence or only research-use terms.

## Can LLMs reason about traffic and explain alerts?

### Takeaway

As detectors on raw flow values, LLMs are close to chance: zero-shot GPT-4 and Llama 3 score about 50% macro precision and recall, at around 7,000 times the inference time of light models. As explainers fed by a separate detector they are more useful, with GPT-4 reaching 80% fully correct explanations on 50 flows once context was added. They still invent details, and tool-using triage agents in a 2026 preprint missed at least 40.4% of attack alerts until stricter evidence rules were forced.

### Cited Findings

#### LLMs as detectors and explainers of flows

- **[PR · full] Houssel, P. R. B., Singh, P., Layeghy, S., Portmann, M. (2024). Towards Explainable Network Intrusion Detection using Large Language Models. IEEE/ACM BDCAT 2024, pp. 67–72.** [DOI](https://doi.org/10.1109/BDCAT63179.2024.00021) · [arXiv](https://arxiv.org/abs/2408.04342)
  - Method: zero-shot GPT-4 and Llama 3 on NetFlows, plus fine-tuning of Llama 3.
  - Data: NF-UNSW-NB15-v2, NF-CSE-CIC-IDS2018-v2.
  - Result: GPT-4 macro precision and recall 50.85% and 53.47% on UNSW; Llama 3 48.56% and 40.56%. Llama 3 takes about 14,000 µs per sample against 2.03 µs for Random Forest.
  - Limit: small test sets; explanation review was manual. Explanations held factual errors, and the LLM failed to explain a SYN flood.
- **[PR · full] Houssel, P. R. B., Layeghy, S., Singh, P., Portmann, M. (2026). eX-NIDS: A framework for explainable network intrusion detection leveraging Large Language Models. Computers and Electrical Engineering 129, 110826.** [DOI](https://doi.org/10.1016/j.compeleceng.2025.110826) · [arXiv](https://arxiv.org/abs/2507.16241)
  - Method: Prompt Augmenter adds threat intelligence and context to flows flagged by a NIDS.
  - Data: 50 malicious flows from NF-CSE-CIC-IDS2018-v2.
  - Result (explanation correctness, feature consistency, factual consistency): GPT-4 basic 40 / 96 / 78; GPT-4 eX-NIDS 80 / 100 / 92; Llama 3 basic 26 / 84 / 42; Llama 3 eX-NIDS 36 / 100 / 90.
  - Limit: 50 malicious flows only, one dataset, manual marking, no user study. Cost about $10.37 per 1,000 queries.
- **[PR-W · abs] Ziems, N., Liu, G., Flanagan, J., Jiang, M. (2023). Explaining Tree Model Decisions in Natural Language for Network Intrusion Detection. NeurIPS XAIA Workshop 2023.** [arXiv](https://arxiv.org/abs/2310.19658)
  - Method: LLM explains decision trees, tested with auto-generated quiz questions for humans.
  - Result: explanations correlate with human ratings and improve understanding of decision boundaries.
- **[PR · abs] Ali, T., Kostakos, P., Sheikhi, S. (2026). HuntGPT: Integrating Machine Learning-Based Anomaly Detection and Explainable AI with Large Language Models (LLMs). Telecom 7(3), 73.** [DOI](https://doi.org/10.3390/telecom7030073) · [2023 arXiv](https://arxiv.org/abs/2309.16021)
  - Method: Random Forest with SHAP and LIME, narrated by GPT-3.5 Turbo in a dashboard.
  - Limit: uses KDD99 in the arXiv version.
- **[PR-W · abs] Li, Y., Xiang, Z., Bastian, N. D., Song, D., Li, B. (2024). IDS-Agent: An LLM Agent for Explainable Intrusion Detection in IoT Networks. NeurIPS 2024 Workshops.** [Page](https://neurips.cc/virtual/2024/100920)
  - Method: LLM agent that calls specialised IDS tools, with memory and a knowledge base.
  - Data: ACI-IoT, CIC-IoT.
  - Result: F1 0.97 and 0.75; zero-day recall 0.61.
  - Limit (my reading): IoT benchmarks. The detector is mostly the tools, not the LLM.
- **[PR-W · abs] Wang, T., Xie, X., Zhang, L., Wang, C., Zhang, L., Cui, Y. (2024). ShieldGPT: An LLM-based Framework for DDoS Mitigation. APNet 2024, pp. 108–114.** [DOI](https://doi.org/10.1145/3663408.3663424)
  - Method: represents global and local traffic features for an LLM, with domain knowledge and role prompts.
  - Result: preliminary experiments and case studies only.
- **[PRE · abs] Jamshidi, S., Wahab, O. A., Khomh, F., Nafi, K. W. (2026). Tri-LLM Cooperative Federated Zero-Shot Intrusion Detection with Semantic Disagreement and Trust-Aware Aggregation.** [arXiv](https://arxiv.org/abs/2602.00219)
  - Method: GPT-4o, DeepSeek-V3 and LLaMA-3-8B build attack prototypes; disagreement between them is treated as uncertainty.
  - Result: over 80% zero-shot detection accuracy on unseen patterns.
  - Limit (my reading): unreviewed. The idea of model disagreement as a trust signal may suit STL.
- **[PRE · abs] Antari, A., Abo-Aisheh, Y., Shamasneh, J., Ashqar, H. I. (2025). Network Traffic Classification Using Machine Learning, Transformer, and Large Language Models.** [arXiv](https://arxiv.org/abs/2503.02141)
  - Data: 30,959 observations with 19 features from Arbor Edge Defender devices.
  - Result: Transformer 98.95%, XGBoost 97.56%; GPT-4o and Gemini improve with few-shot examples but confuse IPSec and Backup.
- **Atif and Ali 2026 [PRE · abs]**, under the previous question: tuned RoBERTa has an FPR of 0.78 on a new network.
- **[PRE · abs] Li, Z. (2026). Traffic-Aware Randomized Smoothing for LLM-Based Network Intrusion Detection.** [arXiv](https://arxiv.org/abs/2607.13801)
  - Method: certified defence that adds noise only to attacker-controllable features.
  - Data: CIC-IDS-2018, HIKARI-2021.
  - Result: 55–100% certified accuracy at their threshold.
  - Limit: submitted for review.

#### LLMs on packets and captures

- **[PR · abs] Paukkeri, S.-P., Frantti, T. (2026). Evaluation of local LLMs for network traffic packet analysis. Journal of Cyber Security Technology 10(1).** [DOI](https://doi.org/10.1080/23742917.2026.2671738)
  - Method: Llama 3.1 and four other local LLMs on IoT traffic.
  - Result: local LLMs are not reliable at detecting attacks, cannot process hexadecimal packets, and encrypted traffic causes hallucinations.
  - Limit: publisher page blocked my fetch. A [search snippet](https://www.tandfonline.com/doi/full/10.1080/23742917.2026.2671738) gave 56% and 38% figures that I could not confirm.
- **[PRE · full] Zhang, L., Fu, X., Huang, F., Zhang, L. (2026). Multimodal Reasoning with LLM for Encrypted Traffic Interpretation: A Benchmark.** [arXiv](https://arxiv.org/abs/2604.08140)
  - Method: BGTD benchmark links bytes to structured text; mmTraffic joins a NetMamba encoder to Qwen3-1.7B.
  - Data: about 310,000 samples from six public datasets.
  - Result: JSON validity 100%; accuracy below NetMamba, for example 0.6448 against 0.8474 on CSTNet-TLS1.3. The paper calls the gap an "alignment tax".
  - Limit: reference reports are generated by Claude Opus, not by humans. The LLM cannot yet express uncertainty, and I found no hallucination rate in the text.
- **[PRE · abs] Marjou, X., Tamic, L., Jaffeux-Cheniout, I. (2026). PCAP-LM: An LLM-Native Text Representation for TLS Bulk Traffic Analysis.** [arXiv](https://arxiv.org/abs/2607.28100)
  - Method: lossy flow summaries using an ASCII alphabet for direction, TCP/TLS state, log size and delay.
  - Data: 5G and 4G TLS 1.3 bulk downloads, 30 held-out files.
  - Result: 99.3% forensic question accuracy against 51.0% from a matched tshark -V prefix; 812x smaller.
  - Limit: 24% false negatives for TCP retransmissions; a narrow corpus.
- **[PRE · abs] Henry, J., Pradhan, S., Popovic, M. (2026). Evidence-Grounded Ensemble Diagnosis of 802.11 Packet Captures: A Multi-Stage Pipeline with Deterministic Reliability Scoring.** [arXiv](https://arxiv.org/abs/2606.06871)
  - Method: PROBE, deterministic capture-to-text, ensembles, and a reliability score with no LLM self-assessment.
  - Data: 87 enterprise Wi-Fi captures.
  - Result: single-pass LLM misses critical frames in 35% of cases; naive majority voting drops below the expert baseline.
  - Limit: Wi-Fi diagnosis, not security.
- **[PRE · abs] Masukawa, R., Yun, S., Jeong, S., Huang, W., Ni, Y., Bryant, I., Bastian, N. D., Imani, M. (2025). PacketCLIP: Multi-Modal Embedding of Network Traffic and Language for Cybersecurity Reasoning.** [arXiv](https://arxiv.org/abs/2503.03747)
  - Result: 95% mean AUC, 11.6% better than baselines, 92% smaller.
  - Limit: abstract read only in part.

#### Alert triage and rule work

- **[PRE · abs] Tsegai, S. A., Kantchelian, A., Yao, D., Gao, P. (2026). From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage.** [arXiv](https://arxiv.org/abs/2610.10608)
  - Method: ALERT-BENCH replays enterprise telemetry through a live SIEM; AIDA adds a separate challenger and judge.
  - Data: 1,247 alerts from one multi-stage attack scenario.
  - Result: every studied approach missed at least 40.4% of attack alerts, with F1 of 0.371–0.744. AIDA reaches F1 0.958 and 3.1% false negatives while escalating 18.4% of alerts.
  - Limit: one scenario. Alerts were more likely to be dismissed when a search returned no records.
- **[PRE · abs] Liu, Z., Wang, Z. (2026). HESP: Separating What to Probe from When to Stop in Local LLM Alert-Triage Agents.** [arXiv](https://arxiv.org/abs/2609.33446)
  - Method: a controller outside the model selects probes and accepts only verdicts backed by evidence.
  - Data: 7,272 audited episodes, five open-weight models.
  - Result: Qwen2.5-7B verified completion rises from 0.125 to 1.000.
  - Limit: a controlled triage environment. Local models suit STL's privacy needs.
- **[PRE · abs] Daniel, N., Kaiser, F. K., Giladi, S., Sharabi, S., Moyal, R., Shpolyansky, S., Murillo, A., Elyashar, A., Puzis, R. (2024). Labeling NIDS Rules with MITRE ATT&CK Techniques: Machine Learning vs. Large Language Models.** [arXiv](https://arxiv.org/abs/2412.10978)
  - Data: 973 Snort rules, ChatGPT, Claude, Gemini.
  - Result: ML beats LLMs on precision, recall and F1; LLMs are explainable and scalable as a first pass.
- **[PRE · abs] Li, J., Chai, Y., Du, L., Duan, C., Yan, H., Gu, Z. (2025). GRIDAI: Generating and Repairing Intrusion Detection Rules via Collaboration among Multiple LLM-based Agents.** [arXiv](https://arxiv.org/abs/2510.13257)
  - Method: agents generate or repair rules, with tool-based validation against hallucinations.
  - Data: a public set with seven attack types; a private set with 43.
- **[PRE · abs] Yoon, H.-J., Kiran, M., Ebling, D., Breen, J. (2025). OFCnetLLM: Large Language Model for Network Monitoring and Alertness.** [arXiv](https://arxiv.org/abs/2507.22711)
  - Method: multi-agent LLM for anomaly detection and root-cause analysis at a conference network.
  - Limit: "still evolving", early results.
- **[PRE · abs] Feng, Y., Sakurai, K. (2025). Network Intrusion Detection: Evolution from Conventional Approaches to LLM Collaboration and Emerging Risks.** [arXiv](https://arxiv.org/abs/2510.23313)
  - Method: survey with 213 references.

#### Explanation without LLMs, and what analysts want

- **[PR · abs] Wei, F., Li, H., Zhao, Z., Hu, H. (2023). xNIDS: Explaining Deep Learning-based Network Intrusion Detection Systems for Active Intrusion Responses. USENIX Security 2023.** [Page](https://www.usenix.org/conference/usenixsecurity23/presentation/wei-feng)
  - Method: approximates history inputs and captures feature dependencies, then produces defence rules.
  - Data: four DL-NIDS.
  - Result: better fidelity, sparsity, completeness and stability than prior explainers.
- **[PR · abs] Lanvin, M., Gimenez, P.-F., Han, Y., Majorczyk, F., Mé, L., Totel, E. (2023). Towards Understanding Alerts raised by Unsupervised Network Intrusion Detection Systems. RAID 2023, pp. 135–150.** [DOI](https://doi.org/10.1145/3607199.3607247)
  - Method: AE-pvalues, p-values of autoencoder reconstruction errors.
  - Data: CICIDS2017.
  - Result: finds the abnormal features and helps identify attack type.
- **[PR · abs] Ponraj, R., Durairajan, R., Wang, Y. (2026). Building Transparency in Deep Learning-Powered Network Traffic Classification: A Traffic-Explainer Framework. ACM KDD 2026, pp. 2368–2379.** [DOI](https://doi.org/10.1145/3770854.3783939)
  - Method: masks inputs and maximises mutual information with predictions.
  - Result: about 42% better than prior explanation methods.
- **[PR · abs] Mink, J., Benkraouda, H., Yang, L., Ciptadi, A., Ahmadzadeh, A., Votipka, D., Wang, G. (2023). Everybody's Got ML, Tell Me What Else You Have: Practitioners' Perception of ML-Based Security Tools and Explanations. IEEE S&P 2023, pp. 2068–2085.** [DOI](https://doi.org/10.1109/SP46215.2023.10179321)
  - Data: 18 security practitioners.
  - Result: ML should work with rule-based methods, not replace them. Current explanations do not fit downstream tasks.

### Inferences

- The evidence does not support an LLM as STL's network detector. Its likely role is second-stage: a fast classical or sequence model raises the alert, then the LLM turns structured evidence into an explanation.
- STL should give the LLM computed features and context, not raw hex or raw NetFlow numbers. PCAP-LM, eX-NIDS and Paukkeri and Frantti all point the same way.
- A deterministic verifier should check every factual claim in an LLM explanation against the flow record. PROBE, HESP and AIDA all add control outside the model, and that is where their gains come from.
- An empty search result must not count as evidence of benign behaviour, since that is a failure pattern in ALERT-BENCH.
- STL can adopt eX-NIDS's three metrics, but should test benign flows too. eX-NIDS covered only malicious flows.
- Disagreement between the network agent and the application agent could act as a trust signal. The Tri-LLM preprint offers a weak precedent. This is an idea to test, not a finding.

### Gaps

- I found no peer-reviewed study that measures whether LLM explanations help real analysts decide faster or better on network alerts.
- I found no LLM evaluation on CTU-13 or MAWI.
- I saw a Hugging Face [agentic PCAP dataset](https://huggingface.co/datasets/maureille/agentic-pcap) in search results, with 44 captures, but did not open or verify it.
- Most 2026 agent work here is preprint and very recent, so it should be treated as provisional.
