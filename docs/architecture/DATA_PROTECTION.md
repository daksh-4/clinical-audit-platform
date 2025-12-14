# Data Protection and Information Governance

## Overview

This document outlines the data protection framework for the Clinical Audit Platform, designed to comply with UK GDPR, NHS Data Security and Protection Toolkit, and Caldicott principles.

## Core Principles

1. **Privacy by Design**: Data protection embedded at system architecture level
2. **Data Minimisation**: Collect only what is necessary for audit purposes
3. **No PII by Default**: Audits configured without identifiers unless justified
4. **Transparency**: Clear data flows and purposes documented
5. **Least Privilege**: Users access only data required for their role

## Legal and Regulatory Framework

### UK GDPR Compliance

**Lawful Basis for Processing**:
- Public task (Article 6(1)(e)) for NHS audits
- Legitimate interest (Article 6(1)(f)) for quality improvement
- Explicit consent (Article 6(1)(a)) for optional patient participation

**Special Category Data** (Article 9):
- Health data requires Article 9(2)(h) - healthcare/public health purposes
- Explicit consent where appropriate
- Data processing agreements in place

### NHS Data Security Standards

**DSP Toolkit Requirements**:
- Staff training on information governance
- Incident management procedures
- Network and system security controls
- Secure data transfer mechanisms
- Access controls and authentication

### Caldicott Principles

1. **Justify purpose**: Every audit must have clear clinical need
2. **Don't use PII unless necessary**: Default to non-identifiable
3. **Use minimum necessary**: Collect fewest fields needed
4. **Access on need-to-know**: RBAC enforcement
5. **Everyone's responsibility**: All users accountable
6. **Understand and comply**: Built-in compliance guidance
7. **Duty to share**: Open library for non-identifiable outputs

## Data Classification

### Level 0: Non-Identifiable Aggregate Data
**Examples**: Total procedure count, median age, percentage outcomes
**Protection**: Public access permitted
**Storage**: Standard database, no special controls

### Level 1: Pseudonymised Clinical Data
**Examples**: Study ID, age band, diagnosis, outcomes
**Protection**: Restricted to audit team members
**Storage**: Main database with access controls

### Level 2: Indirectly Identifiable Data
**Examples**: Rare diagnosis + specific date + small hospital
**Protection**: Strict access control, export approval required
**Storage**: Main database with row-level security

### Level 3: Directly Identifiable Data (PII)
**Examples**: NHS number, full name, precise address, date of birth
**Protection**: Encrypted at rest, separate storage, full audit trail
**Storage**: Encrypted PII schema, segregated from analytics

## PII Handling

### When PII is NOT Required (Default)

Most audits can operate without PII:
- Use sequential audit IDs
- Capture age bands instead of DOB
- Use postcode sectors instead of full addresses
- Record hospital site without patient name

**Configuration**:
```json
{
  "audit_id": "hip_fracture_2025",
  "data_protection_level": "no_pii",
  "identifiers_collected": false,
  "consent_required": false
}
```

### When PII IS Required

PII should only be collected when:
- Follow-up linkage is necessary
- Regulatory requirement mandates it
- Duplicate checking cannot be done otherwise

**Mandatory Requirements**:
1. Complete Data Protection Impact Assessment (DPIA)
2. Document legal basis for processing
3. Obtain Information Governance approval
4. Implement encryption and segregation
5. Define retention and deletion schedule
6. Enable audit logging for all access

**Configuration**:
```json
{
  "audit_id": "longitudinal_outcomes_2025",
  "data_protection_level": "pii_required",
  "identifiers_collected": true,
  "pii_fields": ["nhs_number", "date_of_birth"],
  "pii_justification": "12-month follow-up outcomes via NHS Digital linkage",
  "legal_basis": "public_task",
  "dpia_reference": "DPIA-2025-001",
  "retention_days": 3650,
  "consent_required": false
}
```

## Encryption Strategy

### Transport Encryption
- **TLS 1.3** for all HTTP connections
- **SSH** for administrative access
- **VPN** for NHS network connectivity (N3/HSCN)

### At-Rest Encryption

**Database Encryption**:
- **Full disk encryption**: LUKS/BitLocker on storage volumes
- **Transparent Data Encryption (TDE)**: PostgreSQL pgcrypto
- **Column-level encryption**: Fernet symmetric encryption for PII

**Example Encrypted Field**:
```python
from cryptography.fernet import Fernet

# PII is encrypted before database insertion
def encrypt_pii(plaintext: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(plaintext.encode()).decode()

# Only decrypted when explicitly needed by authorized user
def decrypt_pii(ciphertext: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(ciphertext.encode()).decode()
```

**Key Management**:
- Keys stored in **AWS KMS** or **Azure Key Vault**
- Automatic key rotation every 90 days
- Separate keys per audit
- Keys never logged or transmitted

### Pseudonymisation

For audits requiring linkage without PII in analysis tables:

```
NHS Number → SHA-256 Hash + Salt → Pseudonym
(encrypted PII store)     ↑         (analysis tables)
                          |
                    Site-specific salt
```

**Properties**:
- Irreversible without access to encrypted store
- Consistent within audit, different across audits
- Re-identification requires privileged access + decryption key

## Access Control

### Role-Based Access Control (RBAC)

**Roles**:

| Role | Permissions |
|------|-------------|
| **Public User** | View aggregated results in open library |
| **Registered User** | Create new audits, access own data |
| **Clinician** | Submit data for assigned audits/sites |
| **Audit Lead** | Full control over own audits, export data |
| **QI Team** | View dashboards for assigned sites, download reports |
| **Governance Officer** | Review DPIAs, access metadata, audit logs |
| **System Admin** | User management, system configuration |
| **Data Protection Officer** | Full audit trail access, compliance reviews |

**Permission Matrix**:

| Action | Public | Registered | Clinician | Audit Lead | QI Team | Governance | Admin |
|--------|--------|------------|-----------|------------|---------|------------|-------|
| View aggregate results | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Create audit | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| Submit data | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| View patient-level data | ✗ | ✗ | Own site | Own audit | Own sites | Metadata only | ✗ |
| Export raw data | ✗ | ✗ | ✗ | Own audit | ✗ | ✗ | ✗ |
| Access PII | ✗ | ✗ | ✗ | With justification | ✗ | ✗ | ✗ |
| View audit logs | ✗ | ✗ | ✗ | Own audit | ✗ | ✓ | ✓ |

### Row-Level Security

PostgreSQL RLS policies ensure users only see authorized data:

```sql
-- Clinicians can only view data from their assigned sites
CREATE POLICY clinician_site_access ON audit_episodes
  FOR SELECT
  TO clinician_role
  USING (
    site_id IN (
      SELECT site_id FROM user_site_assignments 
      WHERE user_id = current_user_id()
    )
  );

-- Audit leads have full access to their audits
CREATE POLICY audit_lead_access ON audit_episodes
  FOR ALL
  TO audit_lead_role
  USING (
    audit_id IN (
      SELECT audit_id FROM audit_ownership
      WHERE user_id = current_user_id()
    )
  );

-- PII is never returned in standard queries
CREATE POLICY no_pii_in_analysis ON audit_episodes
  FOR SELECT
  TO ALL
  USING (
    -- PII fields excluded at view layer
    TRUE
  );
```

### Multi-Factor Authentication

**Required For**:
- All access to PII
- Data export functions
- Administrative actions
- After 30 days of inactivity

**Supported Methods**:
- SMS/Email OTP
- Authenticator app (TOTP)
- NHS Smartcard (future)
- FIDO2 hardware tokens

## Audit Logging

All data access and modifications are logged:

**Logged Events**:
- User authentication (success/failure)
- Data entry (create, update, delete)
- Data access (view, query, export)
- Configuration changes
- Permission modifications
- PII decryption requests
- Failed access attempts

**Log Format**:
```json
{
  "timestamp": "2025-06-15T14:32:01.234Z",
  "user_id": "clinician_789",
  "action": "export_data",
  "resource": "audit:hip_fracture_2025",
  "resource_id": "uuid-of-export",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "records_accessed": 1247,
  "contains_pii": false,
  "justification": "Monthly QI report for trust board"
}
```

**Retention**:
- Audit logs retained for **7 years**
- Immutable storage (append-only)
- Regular integrity verification
- Separate backup from main database

## Data Protection Impact Assessment (DPIA)

### Automated DPIA Generation

When creating an audit, the system generates a pre-populated DPIA template:

**Sections**:
1. **Description**: Auto-filled from audit metadata
2. **Necessity**: Template text for common audit purposes
3. **Risk Assessment**: Automated based on:
   - Data classification level
   - Number of records expected
   - Duration of storage
   - External data sharing
4. **Mitigation Measures**: Auto-documented technical controls
5. **Consultation**: Checklist for stakeholder review
6. **Approval**: Workflow for governance sign-off

**Example Risk Scoring**:
```python
def calculate_dpia_risk_score(audit_config):
    risk_score = 0
    
    if audit_config.pii_collected:
        risk_score += 30
    if audit_config.special_category_data:
        risk_score += 20
    if audit_config.expected_records > 10000:
        risk_score += 15
    if audit_config.retention_days > 2555:  # >7 years
        risk_score += 10
    if audit_config.external_sharing:
        risk_score += 25
    
    return {
        "score": risk_score,
        "level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low",
        "dpo_review_required": risk_score > 60
    }
```

### DPIA Workflow

```
[Audit Lead Creates Audit]
         ↓
[System Generates DPIA Template]
         ↓
[Audit Lead Completes Assessment]
         ↓
[Automatic Risk Scoring]
         ↓
    [High Risk?] → Yes → [DPO Review Required]
         ↓ No
[Information Governance Officer Reviews]
         ↓
    [Approved?] → No → [Revisions Requested]
         ↓ Yes
[Audit Activated for Data Collection]
```

## Consent Management

For audits requiring patient consent:

**Consent Record**:
```json
{
  "episode_id": "uuid",
  "consent_obtained": true,
  "consent_date": "2025-06-10",
  "consent_method": "written",
  "consented_purposes": [
    "data_collection",
    "local_quality_improvement",
    "national_benchmarking"
  ],
  "consented_duration": "indefinite",
  "withdrawal_allowed": true
}
```

**Withdrawal Process**:
1. Patient requests data withdrawal
2. Episode flagged in database
3. Data excluded from future analyses
4. PII deleted (if applicable)
5. Audit trail preserved

## Data Retention and Deletion

### Default Retention Periods

| Data Type | Retention | Justification |
|-----------|-----------|---------------|
| Aggregate statistics | Indefinite | Public interest, no privacy risk |
| Pseudonymised clinical data | 10 years | NHS record retention standard |
| PII (when required) | Minimum necessary | Deleted when linkage complete |
| Audit logs | 7 years | Legal and regulatory requirement |
| Exported datasets | 90 days | Temporary analysis copies |

### Automated Deletion

```python
# Scheduled job runs daily
def delete_expired_data():
    # Delete PII after retention period
    execute_sql("""
        DELETE FROM encrypted_pii_store
        WHERE audit_id IN (
            SELECT id FROM audits 
            WHERE end_date + retention_days < CURRENT_DATE
        )
    """)
    
    # Anonymize historical data
    execute_sql("""
        UPDATE audit_episodes
        SET pseudonym = NULL,
            site_id = 'historical'
        WHERE submitted_at < CURRENT_DATE - INTERVAL '10 years'
    """)
```

## Data Sharing and Exports

### Export Approval Workflow

```
[User Requests Export]
         ↓
[System Checks: Contains PII?]
         ↓ Yes
[Requires Justification + MFA]
         ↓
[Audit Lead Approval Required]
         ↓
[Export Generated with Watermark]
         ↓
[Access Logged]
         ↓
[Email Notification to DPO]
```

### Export Security

**Technical Controls**:
- Watermarking with user ID and timestamp
- File encryption (password-protected ZIP)
- Temporary download links (expire in 24 hours)
- Download count limits
- Virus scanning before delivery

**Data Sharing Agreements**:
- Template DSA generated for each export
- Must specify: purpose, duration, deletion date
- Requires recipient signature (DocuSign integration)
- Tracked in agreements database

## Incident Response

### Data Breach Classification

**Level 1 - Low Risk**:
- Aggregate data disclosed
- No PII involved
- Small number of records
- **Action**: Log incident, notify audit lead

**Level 2 - Medium Risk**:
- Pseudonymised data disclosed
- Large number of records
- Could lead to re-identification
- **Action**: DPO notification, investigation, mitigation

**Level 3 - High Risk**:
- PII disclosed
- Special category data involved
- Risk to patient rights/freedoms
- **Action**: ICO notification (72 hours), patient notification, full investigation

### Incident Workflow

```
[Incident Detected]
       ↓
[Automatic Classification]
       ↓
[DPO Notified]
       ↓
[Investigation Team Assembled]
       ↓
[Containment Actions]
       ↓
[ICO Notification if Required]
       ↓
[Affected Users Notified]
       ↓
[Post-Incident Review]
       ↓
[System Improvements Implemented]
```

## Compliance Monitoring

### Regular Reviews

**Monthly**:
- Access log analysis for anomalies
- Failed authentication review
- Export activity summary

**Quarterly**:
- DPIA review for active audits
- Retention policy compliance check
- User permission audit

**Annually**:
- Full security assessment
- DSP Toolkit submission
- Staff training refresh
- Penetration testing

### Compliance Dashboard

Real-time monitoring for:
- Active audits requiring DPIA renewal
- Approaching data retention deadlines
- Unusual access patterns
- Failed MFA attempts
- Exports pending approval

## Patient Rights

### Subject Access Requests (SAR)

Automated SAR processing:
1. Patient submits request via web form
2. Identity verification (NHS number + DOB)
3. System searches all audits for matches
4. Data compiled into readable format
5. Delivered within 30 days (GDPR requirement)

### Right to Rectification

Patients can request corrections:
- Web form for correction requests
- Clinician reviews and approves changes
- Original data preserved in audit trail
- Correction flag added to record

### Right to Erasure

"Right to be forgotten" implementation:
- Available for consent-based audits
- Not available for legal obligation audits
- Deletion confirmed to patient
- Audit log entry preserved (without PII)

## Training and Awareness

All users must complete:
- **Information Governance Training** (annual)
- **Platform-Specific Data Protection** (at onboarding)
- **Role-Specific Modules**:
  - Clinicians: Accurate data entry, consent
  - Audit Leads: DPIA completion, safe data export
  - Admins: Security best practices

**Training Tracking**:
```json
{
  "user_id": "clinician_789",
  "training_completed": [
    {
      "module": "IG_Level_2",
      "completed_date": "2025-01-15",
      "expiry_date": "2026-01-15",
      "score": 92
    }
  ],
  "access_restricted": false
}
```

Access automatically restricted if training expires.

## Future Enhancements

1. **Differential Privacy**: Add noise to aggregates for mathematical privacy guarantees
2. **Federated Analytics**: Compute on data without centralization
3. **Blockchain Audit Trail**: Immutable, distributed logging
4. **AI-Powered Anomaly Detection**: Identify unusual access patterns
5. **Automated DPIA Risk Scoring**: Machine learning from historical DPIAs
