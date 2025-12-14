# System Architecture

## Overview

The Clinical Audit Platform is built on a modern, cloud-native architecture designed for scalability, security, and maintainability. The system separates concerns across three primary layers: Frontend, API, and Data.

## Architectural Principles

1. **API-First Design**: All functionality exposed through versioned REST APIs
2. **Data Protection by Design**: Security and privacy embedded at every layer
3. **Separation of Concerns**: Clear boundaries between presentation, business logic, and data
4. **Analysis-Ready Data**: Structured capture eliminates downstream cleaning
5. **Auditability**: Complete traceability from data entry to published metrics

## System Layers

### Frontend Layer

**Technology**: React 18 + TypeScript + Tailwind CSS

**Components**:
- **Audit Builder**: Visual questionnaire designer with drag-and-drop interface
- **Data Entry Interface**: Auto-generated forms with real-time validation
- **Analytics Dashboards**: Interactive visualizations and benchmarking tools
- **Open Library**: Public repository browser for audits and results
- **Admin Panel**: User management and governance oversight

**Key Features**:
- Progressive Web App (PWA) for offline capability
- Responsive design for mobile/tablet use
- Accessibility compliant (WCAG 2.1 AA)
- Real-time validation feedback
- Auto-save functionality

### API Layer

**Technology**: FastAPI (Python 3.11+)

**Core Services**:

1. **Audit Management Service**
   - CRUD operations for audits
   - Questionnaire versioning
   - Metadata management
   - Lifecycle state machine

2. **Data Entry Service**
   - Form schema generation
   - Real-time validation
   - Conditional logic evaluation
   - Batch import support

3. **Analytics Service**
   - Query builder for custom extracts
   - Derived metric computation
   - Aggregation engine
   - Export pipeline (CSV, JSON, Excel)

4. **Authentication & Authorization Service**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - NHS login integration
   - Multi-factor authentication support

5. **Methodological Guidance Service**
   - Rule-based questionnaire analysis
   - Best-practice recommendations
   - Validated instrument suggestions
   - Quality score computation

6. **Reporting Service**
   - Dashboard data endpoints
   - Report generation
   - Summary statistics
   - Benchmark calculations

**API Design**:
- RESTful conventions
- OpenAPI 3.0 specification
- Versioned endpoints (/api/v1/)
- Comprehensive error handling
- Rate limiting and throttling

### Data Layer

**Primary Database**: PostgreSQL 15+

**Schema Organization**:

```
┌─────────────────────────────────────────────────────────┐
│                   AUDIT METADATA                        │
│  - audits                                               │
│  - questionnaire_versions                               │
│  - questions                                            │
│  - validation_rules                                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   CLINICAL DATA                         │
│  - audit_episodes (one row per patient encounter)       │
│  - responses (EAV for flexible storage)                 │
│  - derived_metrics                                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   ENCRYPTED PII STORE                   │
│  - patient_identifiers (encrypted)                      │
│  - pseudonym_mapping                                    │
│  - access_logs                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   ACCESS CONTROL                        │
│  - users                                                │
│  - roles                                                │
│  - permissions                                          │
│  - audit_access                                         │
└─────────────────────────────────────────────────────────┘
```

**Additional Stores**:
- **Redis**: Session management, caching, task queues
- **Object Storage (S3-compatible)**: File attachments, exports, backups
- **Elasticsearch**: Full-text search for open library

## Data Model

### Core Entities

**Audit**
```python
{
  "id": "uuid",
  "title": "National Hip Fracture Audit 2025",
  "clinical_domain": "orthopaedics",
  "population": "adults 65+ with hip fracture",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "status": "active",
  "governance_body": "Royal College of Surgeons",
  "data_protection_level": "no_pii",
  "created_by": "user_id",
  "version": 1
}
```

**Questionnaire**
```python
{
  "id": "uuid",
  "audit_id": "uuid",
  "version": 2,
  "questions": [
    {
      "id": "q1",
      "type": "categorical_single",
      "text": "Primary anaesthetic technique",
      "options": ["Spinal", "General", "Combined"],
      "required": true,
      "validation": {...},
      "guidance": "Use NHS frailty score if available"
    }
  ],
  "conditional_logic": [...],
  "published_at": "2025-01-01T00:00:00Z"
}
```

**Episode (Patient Encounter)**
```python
{
  "id": "uuid",
  "audit_id": "uuid",
  "questionnaire_version": 2,
  "site_id": "hospital_123",
  "submitted_by": "clinician_456",
  "submitted_at": "2025-06-15T14:30:00Z",
  "status": "validated",
  "responses": {
    "q1": "Spinal",
    "q2": 82,
    "q3": "2025-06-10"
  }
}
```

## Security Architecture

### Authentication Flow

```
User → NHS Login → JWT Token → API Gateway → Service Layer
                      ↓
                Session Store (Redis)
```

### Data Protection Layers

1. **Transport Security**: TLS 1.3 for all connections
2. **At-Rest Encryption**: AES-256 for PII fields
3. **Access Control**: Row-level security in PostgreSQL
4. **Audit Logging**: Immutable log of all data access
5. **Data Segregation**: PII in separate encrypted schema

### PII Handling

When PII is required:
```
[PII Input] → [Encryption Service] → [Encrypted Store]
                       ↓
              [Pseudonym Generated]
                       ↓
              [Analysis Uses Pseudonym Only]
```

## Scalability Design

### Horizontal Scaling

- **API Layer**: Stateless containers behind load balancer
- **Database**: Read replicas for analytics queries
- **Task Processing**: Celery workers for async jobs
- **Caching**: Redis cluster for session/query caching

### Performance Targets

- **Data Entry**: <200ms form load, <100ms validation response
- **Exports**: 100K records in <30 seconds
- **Dashboards**: <2s initial load, <500ms interaction updates
- **Concurrent Users**: 5,000+ simultaneous sessions

### Database Optimization

- **Partitioning**: Audit episodes partitioned by audit_id and year
- **Indexing**: Composite indexes on frequently queried fields
- **Materialized Views**: Pre-computed aggregations for dashboards
- **TimescaleDB**: Optimized time-series queries for trends

## Integration Points

### External Systems

1. **NHS Login**: OpenID Connect integration
2. **EHR Systems**: HL7 FHIR API endpoints (future)
3. **ODR (Office for Data Release)**: Automated DPIA submission
4. **HSCIC**: National audit registration sync

### Internal APIs

- `/api/v1/audits` - Audit management
- `/api/v1/questionnaires` - Questionnaire CRUD
- `/api/v1/episodes` - Data entry and retrieval
- `/api/v1/analytics` - Query and export
- `/api/v1/reports` - Dashboard data
- `/api/v1/library` - Open audit repository

## Deployment Architecture

### Production Environment

```
                    ┌─────────────────┐
                    │   CloudFlare    │
                    │   (CDN + DDoS)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │  API Pod  │      │  API Pod  │     │  API Pod  │
    │ (FastAPI) │      │ (FastAPI) │     │ (FastAPI) │
    └─────┬─────┘      └─────┬─────┘     └─────┬─────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │PostgreSQL │      │   Redis   │     │  Celery   │
    │ Primary + │      │  Cluster  │     │  Workers  │
    │ Replicas  │      │           │     │           │
    └───────────┘      └───────────┘     └───────────┘
```

### NHS-Compatible Hosting

**Options**:
1. **NHS Digital Infrastructure**: N3/HSCN connected hosting
2. **Azure UK Government Cloud**: NHS-approved regions
3. **AWS UK Sovereign Cloud**: ISO 27001 certified
4. **On-Premise**: Docker Swarm or Kubernetes deployment

**Compliance Requirements**:
- Data residency: UK only
- DSP Toolkit: Standards met
- ISO 27001 certification
- Cyber Essentials Plus
- NHS data security standards

## Monitoring & Observability

### Metrics Collection
- **Prometheus**: System and application metrics
- **Grafana**: Visualization dashboards
- **AlertManager**: Threshold-based alerting

### Logging
- **Application Logs**: Structured JSON via Python logging
- **Access Logs**: Nginx format with anonymized IPs
- **Audit Logs**: Immutable security event log
- **ELK Stack**: Centralized log aggregation

### Alerting Scenarios
- API latency >2s sustained
- Database connection pool exhausted
- Failed authentication attempts >10/minute
- Disk usage >85%
- PII access outside normal hours

## Disaster Recovery

**Backup Strategy**:
- **Database**: Continuous WAL archiving + daily snapshots
- **Object Storage**: Cross-region replication
- **Configuration**: Version controlled in Git

**RTO/RPO Targets**:
- Recovery Time Objective: <4 hours
- Recovery Point Objective: <15 minutes

**Testing**:
- Quarterly DR drills
- Annual full failover test

## Development & CI/CD

### Pipeline Stages

```
[Commit] → [Lint] → [Unit Tests] → [Integration Tests] → [Build] → [Deploy Staging] → [E2E Tests] → [Deploy Production]
```

### Environments

1. **Development**: Local Docker Compose
2. **Staging**: Cloud-hosted, mirrors production
3. **Production**: High-availability cluster

### Quality Gates

- Code coverage >80%
- Zero critical security vulnerabilities (Snyk/Dependabot)
- All E2E tests passing
- Performance benchmarks met

## Future Architecture Considerations

### Microservices Evolution
As the platform scales, consider splitting into:
- **Audit Service**: Questionnaire management
- **Data Service**: Entry and storage
- **Analytics Service**: Computation and export
- **Identity Service**: Authentication and RBAC
- **Gateway Service**: API routing and rate limiting

### Federated Architecture
For cross-organizational audits:
- Distributed query coordinator
- Privacy-preserving aggregation
- Differential privacy mechanisms
- Federated learning for guidance layer
