# Complete Reference & Regulatory Framework

This repository provides the full, annotated bibliography of the 25 core regulatory statutes, judicial precedents, technical standards, and foundational academic literature referenced in the study, along with the primary clinical benchmark dataset citation:

> **Paper**: *A Computational Scenario-Risk Safe Harbor for Privacy-Preserving Health Data Governance and AI Training under China's Personal Information Protection Law*  
> **Status**: Under Revision (Target Venue: ICBAR 2026, proceedings scheduled with IOS Press *FAIA*)

All items are categorized by domain with active persistent identifiers (DOIs, official government gazettes, and official judicial bulletins) for seamless independent auditing and reproducibility.

---

## Table of Contents
- [1. Statutory & Regulatory Frameworks (China, EU, US)](#1-statutory--regulatory-frameworks)
- [2. Technical Standards & Clinical Datasets](#2-technical-standards--clinical-datasets)
- [3. Judicial Cases & Regulatory Enforcement Precedents](#3-judicial-cases--regulatory-enforcement-precedents)
- [4. Privacy Engineering, Differential Privacy & Medical Re-identification](#4-privacy-engineering-differential-privacy--medical-re-identification)
- [5. Information Jurisprudence & Legal Doctrine](#5-information-jurisprudence--legal-doctrine)

---

## 1. Statutory & Regulatory Frameworks

### `[1]` Civil Code of the People's Republic of China
- **Citation**: National People's Congress (NPC). *Civil Code of the People's Republic of China*, adopted May 28, 2020. *Official Gazette of the Standing Committee of the NPC* (2020), Arts. 496, 497, 1034, 1036, 1038, 1165, 1168, 1226.
- **Doctrinal Role**: Establishes statutory confidentiality duties for medical personnel (Art. 1226), fault-presumed tort liability (Art. 1165), and statutory data security obligations (Art. 1038).
- **Official Source**: [NPC Official Gazette](http://www.npc.gov.cn/npc/c30834/202006/c5601cd15ca94d629c5abe65e39542e8.shtml)

### `[2]` Personal Information Protection Law (PIPL) of China
- **Citation**: National People's Congress Standing Committee. *Personal Information Protection Law of the People's Republic of China*, adopted August 20, 2021. *Official Gazette of the Standing Committee of the NPC* (2021), Arts. 6, 13, 21, 28–31, 51, 55–56, 66, 69–70, 73.
- **Doctrinal Role**: Primary statutory focus; establishes the "separate consent" requirement for sensitive medical data (Arts. 28–29), processor fault presumption (Art. 69), cascading entrusted obligations (Art. 21), and the statutory definition of de-identification (Art. 73(4)).
- **Official Source**: [NPC Official Gazette](http://www.npc.gov.cn/npc/c30834/202108/a8c4e3672c74491a80b53a172bb753fe.shtml)

### `[12]` EU General Data Protection Regulation (GDPR)
- **Citation**: European Parliament and Council of the European Union. *Regulation (EU) 2016/679 on the protection of natural persons with regard to the processing of personal data*, 27 April 2016. *Official Journal of the European Union* L 119 (2016), 1–88, Arts. 9(2)(j), 17(3)(d), 89(1)–(2), Recital 33.
- **Comparative Role**: Serves as the international benchmark for the statutory scientific research exception and secondary data processing regime under Art. 89.
- **Official Source**: [EUR-Lex Official Publication](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

### `[13]` European Health Data Space (EHDS) Regulation
- **Citation**: European Parliament and Council of the European Union. *Regulation (EU) 2025/327 of 11 February 2025 on the European Health Data Space*, *Official Journal of the European Union* L 2025/327 (5 March 2025), Arts. 51, 53, 55, 57, 73, 105.
- **Comparative Role**: Benchmarks secure processing environments (sandboxes) for secondary health data reuse, centralized data permit permits, and statutory opt-out mechanisms.
- **Official Source**: [EUR-Lex Official Legislation](https://eur-lex.europa.eu/eli/reg/2025/327/oj)

### `[14]` United States HIPAA Privacy Rule
- **Citation**: U.S. Department of Health and Human Services (HHS) (2013). *Modifications to the HIPAA Privacy, Security, Enforcement, and Breach Notification Rules under the HITECH Act and the Genetic Information Nondiscrimination Act; Standards for Privacy of Individually Identifiable Health Information*, *Code of Federal Regulations* 45 C.F.R. §§ 164.512(i)(2)(ii), 164.514(b) (Omnibus Final Rule, 78 Fed. Reg. 5566, January 25, 2013).
- **Comparative Role**: Provides foundational comparative models for the 18-category Safe Harbor de-identification and statistical Expert Determination standards.
- **Official Source**: [Electronic Code of Federal Regulations (eCFR)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E)

### `[20]` Administrative Penalty Law of the People's Republic of China
- **Citation**: National People's Congress Standing Committee. *Administrative Penalty Law of the People's Republic of China (2021 Revision)*, adopted January 22, 2021. *Official Gazette of the Standing Committee of the NPC* (2021), Art. 33(2).
- **Doctrinal Role**: Provides statutory protection against administrative fines when processors demonstrate lack of subjective fault ("no fault, no penalty" rule).
- **Official Source**: [NPC Official Gazette](http://www.npc.gov.cn/npc/c30834/202101/bb65c4ec9b0f4435940c619b027419e5.shtml)

---

## 2. Technical Standards & Clinical Datasets

### `[4]` National Standard GB/T 39725-2020 (Health & Medical Data Security)
- **Citation**: National Standardization Administration of China (SAC). *GB/T 39725-2020: Information Security Technology — Guide for Health and Medical Data Security*, Standards Press of China, Beijing, 2020, Section 10.2 and Appendix G.
- **Technical Role**: Grounds Safe Harbor Element 1: details graded de-identification methods, quasi-identifier generalization intervals, and indirect identifier masking tables.
- **Official Portal**: [State Administration for Market Regulation (SAMR) Standard Info](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=8379B497B49B249117361730704B46E7)

### `[22]` MIMIC-IV Clinical Database Benchmark
- **Citation**: Johnson, A.E.W., Bulgarelli, L., Shen, L., Gayles, A., Shammout, A., Horng, S., Pollard, T.J., Hao, S., Moody, B., Gow, B., Lehman, L.H., Celi, L.A., and Mark, R.G. (2023). MIMIC-IV, a freely accessible electronic health record dataset. *Scientific Data*, 10, 1.
- **Technical Role**: Exemplary real-world clinical electronic health record database demonstrating international multi-stage de-identification and compliance protocols.
- **DOI Link**: [https://doi.org/10.1038/s41597-022-01899-x](https://doi.org/10.1038/s41597-022-01899-x)

### `[Dataset]` UCI Diabetes 130-US Hospitals Clinical Benchmark (ID=296)
- **Citation**: Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., and Clore, J.N. (2014). Impact of HbA1c measurement on hospital readmission rates: Analysis of 70,000 clinical database patient records. *BioMed Research International*, 2014, 781670.
- **Technical Role**: Open-access empirical EHR benchmark (101,766 encounters across 71,518 unique patients) used in `benchmark_uci_diabetes.py` to evaluate Mondrian $(k, l)$ generalization (E1) and DP-SGD utility/MIA defense (E2).
- **DOI Link**: [https://doi.org/10.1155/2014/781670](https://doi.org/10.1155/2014/781670) | **Dataset DOI**: [https://doi.org/10.24432/C5230J](https://doi.org/10.24432/C5230J)

---

## 3. Judicial Cases & Regulatory Enforcement Precedents

### `[5]` Wang and Lin Medical Data Civil Public Interest Litigation Case
- **Citation**: Supreme People's Procuratorate of China (SPP). *Typical cases of procuratorial organs protecting citizens' personal information in accordance with law*, SPP Official Release (2026), Case No. 8.
- **Case Significance**: Exemplifies the risk of civil public interest litigation when hospital contractors leak unmasked clinical registries (255,443 records) without enforceable cascade covenants.
- **Official Source**: [Supreme People's Procuratorate Portal](https://www.spp.gov.cn/xwfbh/wsfbt/202611/t20261102_739856.shtml)

### `[7]` Bo Software Company and He Criminal Case
- **Citation**: Supreme People's Court of China (SPC). *Typical cases of punishing crimes of infringing citizens' personal information and related crimes in accordance with law*, SPC Official Release (May 2026), Case No. 1.
- **Case Significance**: SPC landmark ruling establishing criminal liability under Criminal Law Art. 253a for unauthorized extraction of healthcare and prescription data from hospital HIS platforms.
- **Official Source**: [Supreme People's Court Portal](https://www.court.gov.cn/zixun/xiangqing/499271.html)

### Contrasting Pragmatic Surface-Masking Decisions (Tian Case & Xia Case)
- **Tian v. Property Management Co.** (Guangdong High People's Court Typical Precedent, October 2022): Held that once direct identifiers were redacted from publicized documents, residual attributes (ethnicity, litigation status) could not identify a specific natural person under ordinary inspection, dismissing PIPL claims.
- **Xia v. E-Commerce Co.** (Beijing Internet Court Typical Personal Information Precedent, October 2024): Ruled that internal operational access logs generated from asterisk-masked de-identified records fell outside actionable personal information claims, establishing a pragmatic surface-masking defense.

### `[9]` UK ICO Royal Free NHS Trust & DeepMind Enforcement Ruling
- **Citation**: Information Commissioner's Office (ICO, UK). *Royal Free NHS Foundation Trust and DeepMind Technologies Ltd investigation ruling and formal undertaking*, London, July 2017.
- **Enforcement Significance**: International precedent establishing regulatory illegality when 1.6 million patient records were transferred for AI algorithm development (Streams app) without adequate statutory legal basis and separate consent governance.
- **Official Source**: [UK Information Commissioner's Office](https://ico.org.uk/media/action-weve-taken/undertakings/2014353/royal-free-undertaking-03072017.pdf)

---

## 4. Privacy Engineering, Differential Privacy & Medical Re-identification

### `[3]` Broken Promises of Privacy (Failure of Anonymization)
- **Citation**: Ohm, P. (2010). Broken promises of privacy: Responding to the surprising failure of anonymization. *UCLA Law Review*, 57(6), 1701–1777.
- **Significance**: Foundational law & technology paper debunking the myth of absolute anonymization and demonstrating linkage vulnerabilities in public data releases.
- **SSRN Link**: [https://ssrn.com/abstract=1450006](https://ssrn.com/abstract=1450006)

### `[8]` Cohort Loss to Follow-up and Informed Consent Bias
- **Citation**: Kristman, V.L., Manno, M., and Côté, P. (2004). Loss to follow-up in cohort studies: How much is too much? *European Journal of Epidemiology*, 19(8), 751–760.
- **Significance**: Quantifies clinical cohort attrition and selection bias when retrospective re-consent fails (justifying safe harbor mechanisms for scientific validity).
- **DOI Link**: [https://doi.org/10.1023/B:EJEP.0000036568.02655.F8](https://doi.org/10.1023/B:EJEP.0000036568.02655.F8)

### `[15]` Anonymising and Sharing Individual Patient Data
- **Citation**: El Emam, K., Rodgers, S., and Malin, B. (2015). Anonymising and sharing individual patient data. *BMJ*, 350, h1139.
- **Mathematical Role**: Provides the empirical justification for the re-identification risk thresholds ($\le 0.05$ in HIPAA expert determination and $\le 0.09$ in EMA Policy 0070), supporting our calibrated $\tau_{\mathrm{safe}} \le 0.04$ threshold.
- **DOI Link**: [https://doi.org/10.1136/bmj.h1139](https://doi.org/10.1136/bmj.h1139)

### `[18]` k-Anonymity Privacy Protection Model
- **Citation**: Sweeney, L. (2002). k-anonymity: A model for protecting privacy. *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems*, 10(5), 557–570.
- **Mathematical Role**: Directly underpins Equation (1) parameter $k_{\min} \ge 10$, bounding maximum linkage probability by $p_{\mathrm{link}} = 1 / k_{\min}$.
- **DOI Link**: [https://doi.org/10.1142/S0218488502001648](https://doi.org/10.1142/S0218488502001648)

### `[19]` Deep Learning with Differential Privacy (DP-SGD)
- **Citation**: Abadi, M., Chu, A., Goodfellow, I., McMahan, H.B., Mironov, I., Talwar, K., and Zhang, L. (2016). Deep learning with differential privacy. In: *Proc. ACM SIGSAC Conf. on Computer and Communications Security (CCS)*, pp. 308–318.
- **Technical Role**: Underpins Safe Harbor Element 2 (controlled sandbox with DP-SGD gradient perturbation: $\varepsilon \le 2.0, \delta = 10^{-5}$).
- **DOI Link**: [https://doi.org/10.1145/2976749.2978318](https://doi.org/10.1145/2976749.2978318)

### `[23]` Mondrian Multidimensional K-Anonymity (Supplemental Privacy Engineering Literature)
- **Citation**: LeFevre, K., DeWitt, D.J., and Ramakrishnan, R. (2006). Mondrian multidimensional K-anonymity. In: *Proc. 22nd International Conference on Data Engineering (ICDE)*, IEEE, Atlanta, GA, pp. 25–35.
- **Technical Role**: Provides the top-down multidimensional kd-tree generalization algorithm used in Experiment E1 (`benchmark_uci_diabetes.py`) to construct quasi-identifier equivalence classes.
- **DOI Link**: [https://doi.org/10.1109/ICDE.2006.101](https://doi.org/10.1109/ICDE.2006.101)

### `[24]` l-Diversity Beyond k-Anonymity (Supplemental Privacy Engineering Literature)
- **Citation**: Machanavajjhala, A., Kifer, D., Gehrke, J., and Venkitasubramaniam, M. (2007). l-diversity: Privacy beyond k-anonymity. *ACM Transactions on Knowledge Discovery from Data (TKDD)*, 1(1), Article 3.
- **Technical Role**: Grounds the $l \ge 3$ distinct sensitive-diagnosis constraint integrated into Safe Harbor Element 1 and the Mondrian $(k, l)$ partitioning gate.
- **DOI Link**: [https://doi.org/10.1145/1217299.1217302](https://doi.org/10.1145/1217299.1217302)

### `[25]` Privacy Risk in Machine Learning & Membership Inference Attacks (Supplemental Privacy Engineering Literature)
- **Citation**: Yeom, S., Giacomelli, I., Fredrikson, M., and Jha, S. (2018). Privacy risk in machine learning: Analyzing the connection to overfitting. In: *Proc. IEEE 31st Computer Security Foundations Symposium (CSF)*, IEEE, Oxford, UK, pp. 268–282.
- **Technical Role**: Formalizes the loss-threshold membership inference attack (MIA) advantage metric ($\mathrm{TPR} - \mathrm{FPR}$) used in Experiment E2 to evaluate privacy leakage under varying $\varepsilon$.
- **DOI Link**: [https://doi.org/10.1109/CSF.2018.00027](https://doi.org/10.1109/CSF.2018.00027)

---

## 5. Information Jurisprudence & Legal Doctrine

### `[6]` Construction of Personal Information Rights and Interests
- **Citation**: Zhang, X.B. (2021). Construction of personal information rights and interests: An interpretation of the Personal Information Protection Law. *Peking University Law Journal*, 33(5), 1144–1166.
- **Doctrinal Role**: Foundational doctrinal analysis on the nature of personal information rights as actionable interests rather than absolute ownership rights.
- **DOI Link**: [https://doi.org/10.13821/j.cnki.ceq.2021.05.08](https://doi.org/10.13821/j.cnki.ceq.2021.05.08)

### `[10]` On Individual Consent in Personal Information Processing
- **Citation**: Cheng, X. (2021). On individual consent in personal information processing. *Global Law Review*, 43(6), 40–55.
- **Doctrinal Role**: Critiques the systemic limitations of "consent fatigue" and "notice-and-consent" dogma in complex data ecosystems.
- **DOI Link**: [https://doi.org/10.3969/j.issn.1002-6207.2021.06.004](https://doi.org/10.3969/j.issn.1002-6207.2021.06.004)

### `[11]` Conceptual Origins & Fundamental Principles of Personal Information
- **Citation**: Ding, X.D. (2019). Conceptual origins and fundamental principles of the legal protection of personal information: An analysis based on fair information practices. *Modern Law Science*, 41(3), 96–110.
- **Doctrinal Role**: Articulates risk-based and contextual approaches to data governance, departing from formalistic atomistic rights models.
- **DOI Link**: [https://doi.org/10.3969/j.issn.1001-2397.2019.03.07](https://doi.org/10.3969/j.issn.1001-2397.2019.03.07)

### `[16]` Contextual Integrity Theory
- **Citation**: Nissenbaum, H. (2010). *Privacy in Context: Technology, Policy, and the Integrity of Social Life*, Stanford University Press, Stanford.
- **Theoretical Role**: Foundational philosophical framework justifying the "Scenario-Risk Safe Harbor": privacy preservation depends on maintaining appropriate contextual informational norms.
- **DOI Link**: [https://doi.org/10.1515/9780804772891](https://doi.org/10.1515/9780804772891)

### `[17]` From Individual Control to Social Control
- **Citation**: Gao, F.P. (2018). Personal information protection: From individual control to social control. *Chinese Journal of Law*, 40(3), 84–101.
- **Doctrinal Role**: Chinese seminal scholarship advocating a transition from rigid individual consent hegemony to socialized risk governance and order preservation.
- **DOI Link**: [https://doi.org/10.3969/j.issn.1002-896X.2018.03.006](https://doi.org/10.3969/j.issn.1002-896X.2018.03.006)

### `[21]` Personal Information Impact Assessment System
- **Citation**: Ding, X.D. (2026). From environment and personal information to artificial intelligence: Rethinking the impact assessment system. *Studies in Law and Business*, 43(2).
- **Doctrinal Role**: Provides jurisprudential backing for institutionalized PIA-IRB coupled impact assessment mechanisms under PIPL Articles 55 and 56.
- **DOI Link**: [https://doi.org/10.16390/j.cnki.issn1672-0334.2026.02.007](https://doi.org/10.16390/j.cnki.issn1672-0334.2026.02.007)
