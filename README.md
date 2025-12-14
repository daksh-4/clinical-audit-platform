# Clinical Audit Platform

An open-source web-based platform for clinician-led clinical audits with embedded methodological guidance, data protection, and analysis-ready data capture.

## Vision

Enable transparent, robust, and reusable clinical audits by providing standardised infrastructure that reduces cost, duplication, and technical friction in national and local audit programmes.

## Key Features

- **Visual Audit Builder**: Design questionnaires with structured data capture
- **Methodological Guidance**: Embedded best-practice recommendations during audit design
- **Analysis-Ready Data**: Fully normalised, strongly-typed data model
- **Data Protection by Design**: GDPR-compliant with PII segregation and encryption
- **Real-Time Validation**: Clinical data entry with immediate feedback
- **Automated Analysis**: Export clean datasets and generate analytical views
- **Interactive Dashboards**: Benchmarking, trends, and geographic comparisons
- **Open Audit Library**: Public repository of reusable audit instruments

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Audit Builder│  │ Data Entry   │  │ Dashboards   │     │
│  │  (React)     │  │  (React)     │  │  (React)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Audit Mgmt   │  │ Data Entry   │  │ Analytics    │     │
│  │ Auth & RBAC  │  │ Export       │  │ Reporting    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PostgreSQL   │  │ Encrypted    │  │ Analytics    │     │
│  │ (Main DB)    │  │ PII Store    │  │ Cache        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with TimescaleDB for time-series
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT with NHS login integration support
- **Task Queue**: Celery with Redis
- **Encryption**: Fernet (symmetric) for PII

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Radix UI + Tailwind CSS
- **Charts**: Recharts
- **Data Grid**: TanStack Table

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Project Structure

```
qi/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Helpers
│   ├── tests/
│   ├── alembic/               # Database migrations
│   └── requirements.txt
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API clients
│   │   ├── stores/            # State management
│   │   └── utils/             # Helpers
│   ├── public/
│   └── package.json
├── docs/                       # Documentation
│   ├── architecture/
│   ├── api/
│   └── deployment/
├── scripts/                    # Utility scripts
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd qi
```

2. **Start the services**
```bash
docker-compose up -d
```

3. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

4. **Access the application**
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Admin Panel: http://localhost:3000/admin

### Local Development

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## User Roles

- **Audit Lead**: Design audits, manage questionnaires, export data
- **Clinician**: Submit patient data
- **QI Team**: View dashboards, download reports
- **Governance**: Review compliance, access metadata
- **Public**: View aggregated results (where permitted)

## Data Protection

- **GDPR Compliance**: UK GDPR, NHS DSP Toolkit principles
- **PII Segregation**: Identifiers stored separately with encryption
- **Access Control**: Role-based with least-privilege principle
- **Audit Logging**: Full traceability of data access
- **DPIA Support**: Automated templates for each audit

## Key Workflows

### Creating an Audit
1. Define audit metadata (title, domain, timeframe)
2. Build questionnaire with structured questions
3. Review methodological guidance
4. Configure data protection settings
5. Activate audit for data collection

### Data Entry
1. Authenticate and select audit
2. Complete auto-generated form
3. Real-time validation and error checking
4. Save and submit

### Analysis
1. Define analytical views
2. Export clean datasets (CSV/JSON)
3. Generate dashboards
4. Download reports

## Development Roadmap

### Phase 1: MVP (Months 1-3)
- [ ] Core audit builder
- [ ] Basic data entry forms
- [ ] PostgreSQL storage
- [ ] Simple authentication
- [ ] CSV export

### Phase 2: Production Features (Months 4-6)
- [ ] RBAC and data protection
- [ ] Methodological guidance layer
- [ ] Interactive dashboards
- [ ] NHS login integration
- [ ] Automated DPIA generation

### Phase 3: Advanced Features (Months 7-12)
- [ ] Open audit library
- [ ] Advanced analytics
- [ ] EHR integration APIs
- [ ] Federated analytics
- [ ] Multi-language support

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## Security

Report security vulnerabilities to: security@example.com

## Citation

If you use this platform in your research or audit work, please cite:

```bibtex
@software{clinical_audit_platform,
  title = {Clinical Audit Platform: Open Infrastructure for Clinician-Led Audits},
  year = {2025},
  url = {https://github.com/yourusername/qi}
}
```
