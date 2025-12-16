## **Overview**

This document describes end-to-end user flows for the platform from the perspective of two primary users:

- **Clinicians / Audit Teams** (designing, deploying, and analysing audits)
    
- **Patients** (securely submitting patient-reported data using an assigned case number)

The flows are written to illustrate how the system operates in practice for a typical clinical audit, from audit creation through to data analysis, while maintaining data protection and analytical integrity.

## **1. Clinician / Audit Team Flow**

### **1.1 Audit Conception and Setup**

1. A clinician or researcher logs into the platform with authenticated credentials.
    
2. The user selects **Create New Audit**.
    
3. The system prompts for audit-level metadata:
    
    - Audit title and clinical domain
        
    - Target population and inclusion criteria
        
    - Participating organisations
        
    - Data collection period
        
    - Governance details (audit vs research, local vs national)
        
    
4. The platform automatically generates:
    
    - A unique audit identifier
        
    - A draft data governance record linked to the audit
        
    

  

At this stage, no patient data exists.



### **1.2 Questionnaire Design**

1. The clinician enters the **Questionnaire Builder**.
    
2. Questions are added using structured types (categorical, numeric, date, validated scale).
    
3. As questions are added, the guidance layer:
    
    - Flags excessive free-text use
        
    - Suggests validated instruments where relevant
        
    - Warns about ambiguity, duplication, or poor downstream analysability
        
    
4. Conditional logic is defined (e.g. follow-up questions only appear if a criterion is met).
    
5. Mandatory vs optional fields are specified, with justifications required for missingness.
    

  

Before publication:

- The system generates a **data dictionary preview** for final validation. 
    
- Derived variables (e.g. time intervals, scores) are optionally defined
    

---

### **1.3 Audit Publication and Deployment**

1. The clinician selects **Publish Audit**.
    
2. The questionnaire is versioned and locked (e.g. v1.0).
    
3. The system generates:
    
    - Clinician data entry forms
        
    - Patient-facing forms (if patient-reported outcomes are included)
        
    
4. The audit is made live for participating sites.
    
Audit forms should also be customisable for organisations containing their logos etc. 
  

At this point, the audit can begin accepting data.

---

### **1.4 Patient Case Creation and Case Number Assignment**

1. For each eligible patient, a clinician or delegated staff member:
    
    - Creates a new patient case within the audit
        
    - Enters minimal required identifiers (if permitted by governance)
        
    
2. The platform generates:
    
    - A **unique case number** (non-identifiable)
        
    - Optional one-time access credentials for patient login
        
    
3. Identifiers (if present) are stored in a segregated, encrypted store.
    
4. The case number is used for all subsequent patient interactions and data linkage.
    

Clinicians never see patient passwords; patients never see internal identifiers.

---

### **1.5 Clinician Data Entry**

1. Clinician opens the audit dashboard and selects a patient case.
    
2. The clinician-facing form is auto-generated from the questionnaire schema.
    
3. Real-time validation ensures:
    
    - Logical consistency
        
    - Valid ranges and formats
        
    - Completion of mandatory fields
        
    
4. Data is saved continuously and stored in the structured audit database.
    

---

### **1.6 Ongoing Monitoring and Data Quality**

  

Throughout data collection:

- The platform tracks completion rates and missingness
    
- Data quality flags highlight potential issues
    
- Clinicians can view aggregate summaries without accessing identifiers
    

---

### **1.7 Analysis, Export, and Reporting**

1. The audit lead navigates to the **Analysis & Export** section.
    
2. The system offers predefined analytical views (e.g. timelines, proportions, outcomes).
    
3. On request, the platform generates:
    
    - Clean, analysis-ready CSV files
        
    - Aggregated summaries
        
    - Derived metric tables
        
    
4. All exports are:
    
    - Linked to questionnaire version
        
    - Fully documented via the data dictionary
        
    

  

These outputs can be used directly for dashboards, reports, or external statistical analysis.

---

## **2. Patient Flow**

  

### **2.1 Receiving Access to the Audit**

1. The patient is informed about the audit during routine clinical care.
    
2. They receive:
    
    - A unique case number
        
    - Instructions for accessing the audit platform
        
    - Information on data use and confidentiality
        

The case number does not reveal personal identity.

---

### **2.2 Patient Login**

1. The patient navigates to the audit portal.
    
2. They select **Enter Audit Case**.
    
3. The patient enters:
    
    - Their case number
        
    - Additional authentication if required (e.g. date of birth or one-time code)
        
    
4. The system validates access without exposing any personal data.
    

---

### **2.3 Completing the Audit Questionnaire**

1. The patient is presented with a clear, minimal interface.
    
2. Only patient-relevant questions appear (e.g. PROMs, symptom duration, quality of life).
    
3. Progress indicators show completion status.
    
4. Built-in explanations clarify clinical terms where needed.
    
5. Free-text fields are limited and optional unless strictly necessary.

	
Patients can:

- Save progress and return later
    
- Submit responses once complete
    
---

### **2.4 Submission and Confirmation**

1. Upon submission, responses are validated.
    
2. The patient receives confirmation that their data has been recorded.
    
3. No results or comparisons are shown unless explicitly permitted by the audit design.
    

  

After submission, the patient cannot view or alter data unless re-authorised.

---

## **3. Data Linkage and Protection Across Flows**

- Patient responses are linked to clinician data only via the case number
    
- Identifiable data is never exposed in analysis views
    
- All actions are logged for auditability
    
- Patients and clinicians interact with the same audit without sharing credentials or access rights
    

---

## **4. End-to-End Example Summary**

1. Clinician designs and publishes an audit
    
2. Patient cases are created and issued case numbers
    
3. Clinicians enter clinical data
    
4. Patients enter patient-reported data independently
    
5. The platform links, validates, and stores data in a clean schema
    
6. Audit leads generate analysis-ready outputs and reports
    

  

This flow ensures efficiency, safety, and analytical quality from first question to final report.