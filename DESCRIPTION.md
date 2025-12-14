DESCRIPTION

## **1. Purpose and Vision**

This document specifies the technical and functional requirements for a web-based platform designed to enable open, clinician-led clinical audits. The platform aims to reduce cost, duplication, and technical friction in national and local audits by allowing researchers and clinicians to design, deploy, analyse, and share audits using standardised, reusable infrastructure.

The core vision is to make audits _open by default_, methodologically robust, and analytically ready from the point of data capture. The system should support audits comparable in complexity and scale to large national programmes, including longitudinal data collection, performance benchmarking, and public-facing summary outputs.

## **2. Problems Addressed**

Current audit processes are characterised by:
- High financial cost due to bespoke questionnaire development by external vendors
- Iterative communication overhead between clinicians and technical teams
- Poor downstream analysability due to free-text heavy data capture
- Fragmentation between data collection, cleaning, analysis, and reporting
- Limited transparency and reuse of audit instruments and methods

The proposed platform addresses these by embedding best-practice audit design, data governance, and analysis workflows directly into a shared, open infrastructure.

  

## **3. User Groups and Roles**

- **Audit Leads / Researchers**: design questionnaires, define inclusion criteria, manage datasets, export data, generate analyses
- **Clinicians / Data Submitters**: enter patient-level audit data efficiently and safely
- **Quality Improvement Teams**: explore dashboards, benchmark performance, download reports
- **Governance & Oversight Users**: review data protection compliance, access audit metadata
- **Public / External Users** (optional): view aggregated, non-identifiable results
    
Role-based access control (RBAC) must strictly separate identifiable data access from aggregated outputs.

  

## **4. Core Functional Requirements**

### **4.1 Audit Creation and Questionnaire Design**

The platform must provide a visual audit builder that allows users to:
- Define audit metadata (title, clinical domain, population, timeframe, governance body)
- Create questionnaires using structured question types:
    - Categorical (single/multiple choice)
    - Ordinal scales (e.g. Likert, PROMs)
    - Numeric (with units, bounds, validation)
    - Dates and intervals

- Explicitly discourage unstructured free-text, with:
    - Hard limits on free-text length
    - Mandatory justification when free-text is enabled
    - Suggested structured alternatives
    
#### **Design Guidance Layer**

A key differentiator is an embedded _methodological guidance layer_ that:
- Flags questions that are difficult to analyse downstream
- Suggests validated instruments (e.g. PROMs, clinical scores)
- Encourages alignment with clinical guidelines and quality standards
- Highlights redundancy or ambiguity across questions
    
This guidance should be rule-based initially, with scope for future learning from prior audits.

  

### **4.2 Data Model and Storage**

Data must be stored in a fully normalised, analysis-ready schema:
- One row per patient per audit episode
- Explicit versioning of questionnaires
- Separation of:
    - Identifiers (stored separately, encrypted)
    - Clinical variables
    - Derived metrics
        
All variables must be:
- Strongly typed
- Machine-readable
- Fully documented via a generated data dictionary
    
### **4.3 Data Entry and Validation**

For clinicians submitting data:
- Forms should be auto-generated from the questionnaire schema
- Real-time validation (ranges, missingness, logical consistency)
- Conditional logic to minimise irrelevant fields
- Autosave and low-friction workflows suitable for clinical settings

For patients filling out online 
- Login with case IDs 
- Easy to use questionnaire platform with guidance when you hover over the questions
    
### **4.4 Data Protection and Information Governance**

Data protection is a core design constraint, not an afterthought.

The platform must:
- Support audits with _no patient identifiable information (PII)_ by default
- Where PII is required:
    - Store identifiers in a segregated, encrypted store
    - Use pseudonymisation for analysis tables
- Enforce least-privilege access
- Provide audit-specific Data Protection Impact Assessment (DPIA) templates
- Maintain full audit logs for data access and changes
Compliance targets include UK GDPR, NHS DSP Toolkit principles, and Caldicott principles.

  

### **4.5 Analysis and Export Layer**

The system must expose a backend analysis layer that:
- Automatically generates clean CSV files on demand
- Supports:
    - Patient-level datasets
    - Aggregated summaries
    - Time-series extracts
    - Also further down the line support analyses via code (python, R, stata), researcher can write code on synthetic data which is then approved and applied to real data
- Ensures exported data exactly matches the data dictionary and questionnaire version

Advanced features:
- Predefined analytical views (e.g. referral-to-treatment intervals, outcome proportions)
- Computation of derived metrics directly from raw fields
- Reproducible analysis definitions stored alongside the audit

### **4.6 Visualisation and Reporting**

The platform should support:
- Built-in dashboards for key audit metrics
- Geographic and organisational comparisons
- Longitudinal trends
- Exportable figures and tables suitable for reports
    
The system must be capable of generating outputs similar in structure and complexity to national audit summary reports, including:
- Key messages
- Infographic-ready summary statistics
- Case-study level drill-downs
### **4.7 Open Audit Library**

A public (or semi-public) repository of:
- Audit questionnaires
- Data dictionaries
- Analysis specifications
- Aggregated results (where permitted)
    
This enables reuse, peer review, and incremental improvement of audit methodologies.

## **5. Non-Functional Requirements**
### **5.1 Architecture**
- Modular, API-first backend
- Clear separation between:
    - Frontend
    - Data layer
    - Analytics layer
- Cloud-native deployment with NHS-compatible hosting
    
### **5.2 Scalability and Performance**
- Support thousands of concurrent users
- Handle multi-year, multi-site national audits
- Efficient querying for dashboards and exports

### **5.3 Security**

- Encryption at rest and in transit
- Strong authentication (NHS login-compatible where possible)
- Regular penetration testing

### **5.4 Auditability and Transparency**
- Full version history of questionnaires
- Traceability from reported metric back to raw fields
- Reproducible analysis pipelines
    
## **6. Future Extensions**

- Integration with EHR systems to reduce manual data entry
- Machine-assisted questionnaire optimisation
- Federated analytics for cross-audit comparisons
- Support for international audit standards
## **7. Success Criteria**

The platform will be considered successful if it:
- Reduces time from audit conception to deployment
- Produces datasets that require minimal manual cleaning
- Lowers financial and administrative barriers to running audits
- Enables clinicians to retain methodological and analytical ownership
- Supports transparent, reusable, and open audit practices
