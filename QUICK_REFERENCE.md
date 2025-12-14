# Clinical Audit Platform - Quick Reference

## 🚀 Quick Start Commands

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up -d --build
```

## 📍 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| API Docs | http://localhost:8000/api/v1/docs | Interactive Swagger UI |
| API ReDoc | http://localhost:8000/api/v1/redoc | Alternative API docs |
| Health Check | http://localhost:8000/health | System health |
| Database | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | Cache |

## 🔑 Default Credentials

After creating admin user (see Getting Started):
- **Email**: admin@example.com
- **Password**: admin123!@# (CHANGE THIS!)

## 📁 Key Files

### Backend
```
backend/
├── app/main.py              # Application entry point
├── app/core/config.py       # Configuration
├── app/models/              # Database models
│   ├── user.py              # User, Site, AuditLog
│   └── audit.py             # Audit, Questionnaire, Episode
├── app/api/v1/endpoints/    # API routes
│   ├── auth.py              # Authentication
│   ├── audits.py            # Audit CRUD
│   ├── questionnaires.py    # Questionnaire management
│   └── episodes.py          # Data entry
└── requirements.txt         # Python dependencies
```

### Frontend
```
frontend/
├── src/main.tsx             # Entry point
├── src/App.tsx              # Router
├── src/components/Layout.tsx # Main layout
├── src/pages/               # Page components
├── src/services/api.ts      # API client
└── src/stores/authStore.ts  # Authentication state
```

## 🔧 Development Commands

### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Create migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head

# Run tests
pytest
pytest --cov=app

# Format code
black .
ruff check .
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## 🗃️ Database

### Connect to Database

```bash
# Via Docker
docker-compose exec db psql -U audit_user -d clinical_audit

# Local PostgreSQL
psql postgresql://audit_user:audit_password@localhost:5432/clinical_audit
```

### Common SQL Commands

```sql
-- List tables
\dt

-- Describe table
\d users

-- View data
SELECT * FROM audits LIMIT 10;

-- Count records
SELECT COUNT(*) FROM audit_episodes;

-- Exit
\q
```

## 🐛 Debugging

### Check Service Status

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Restart Service

```bash
docker-compose restart backend
```

### Access Container Shell

```bash
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Clear Everything and Start Fresh

```bash
# WARNING: This deletes all data!
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## 🔐 Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| SECRET_KEY | ✅ | JWT signing key |
| FERNET_KEY | ✅ | PII encryption key |
| POSTGRES_USER | ✅ | Database user |
| POSTGRES_PASSWORD | ✅ | Database password |
| POSTGRES_DB | ✅ | Database name |
| CORS_ORIGINS | ❌ | Allowed origins |

### Generate Keys

```bash
# SECRET_KEY
openssl rand -hex 32

# FERNET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 📊 API Quick Reference

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","full_name":"John Doe","password":"SecurePass123!@#"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123!@#"

# Get current user
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Audits

```bash
# Create audit
curl -X POST http://localhost:8000/api/v1/audits \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"My Audit",
    "clinical_domain":"cardiology",
    "population":"Adult patients",
    "start_date":"2025-01-01T00:00:00Z"
  }'

# List audits
curl http://localhost:8000/api/v1/audits \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

### Run All Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Specific Module

```bash
pytest tests/test_audits.py
pytest tests/test_auth.py -v
```

## 📦 Common Tasks

### Add Python Dependency

```bash
cd backend
pip install package-name
pip freeze > requirements.txt
```

### Add Frontend Dependency

```bash
cd frontend
npm install package-name
```

### Create New API Endpoint

1. Add function to `backend/app/api/v1/endpoints/*.py`
2. Add schema to `backend/app/schemas/*.py`
3. Test at http://localhost:8000/api/v1/docs

### Create New Frontend Page

1. Create `frontend/src/pages/NewPage.tsx`
2. Add route in `frontend/src/App.tsx`
3. Add navigation link in `frontend/src/components/Layout.tsx`

## 🚨 Troubleshooting

### "Port already in use"

```bash
# Find process
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 PID
```

### "Database connection failed"

```bash
# Check database is running
docker-compose ps db

# Check logs
docker-compose logs db

# Restart
docker-compose restart db
```

### "Frontend not loading"

```bash
# Clear cache
rm -rf frontend/node_modules
rm -rf frontend/.vite
cd frontend && npm install
```

### "Migration failed"

```bash
# Rollback
alembic downgrade -1

# Check current version
alembic current

# View history
alembic history
```

## 📚 Documentation Links

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)
- [Data Protection](docs/architecture/DATA_PROTECTION.md)
- [API Reference](docs/api/API_REFERENCE.md)
- [Roadmap](docs/ROADMAP.md)

## 🆘 Getting Help

1. Check documentation in `/docs`
2. Search existing GitHub Issues
3. Ask in GitHub Discussions
4. Email: support@example.com

## 💡 Tips

- Use the interactive API docs at `/api/v1/docs` for testing
- Check logs when things go wrong: `docker-compose logs -f`
- Database changes need migrations: `alembic revision`
- Frontend changes auto-reload in dev mode
- Backend changes auto-reload with `--reload` flag
- Always use environment variables for secrets
- Test locally before deploying

## 🎯 Next Steps

1. Read [GETTING_STARTED.md](docs/GETTING_STARTED.md)
2. Explore API at http://localhost:8000/api/v1/docs
3. Review [ROADMAP.md](docs/ROADMAP.md) for what's next
4. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

---

**Need to make changes?** Read the relevant documentation first, then dive into the code!
