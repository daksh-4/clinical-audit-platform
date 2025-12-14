# Getting Started Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (v20.10+) - [Download](https://www.docker.com/products/docker-desktop)
- **Node.js** (v18+) - [Download](https://nodejs.org/) (for local frontend development)
- **Python** (v3.11+) - [Download](https://www.python.org/) (for local backend development)
- **Git** - [Download](https://git-scm.com/)

## Quick Start with Docker

The fastest way to get the platform running is using Docker Compose:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd qi
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
cd backend
cp .env.example .env
```

**Important**: Edit `.env` and update these critical values:

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Generate a Fernet key for encryption
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output and set it as FERNET_KEY
```

### 3. Start All Services

From the root directory:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)
- React frontend (port 3000)

### 4. Run Database Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Create Initial Admin User

```bash
docker-compose exec backend python -c "
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='admin@example.com',
            full_name='Admin User',
            hashed_password=get_password_hash('admin123!@#'),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        await db.commit()
        print('Admin user created: admin@example.com / admin123!@#')

asyncio.run(create_admin())
"
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **API Redoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## Local Development Setup

For active development, you may want to run services locally rather than in Docker:

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will auto-reload on code changes.

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000 with hot module replacement.

## Database Setup

### Initialize Database Schema

The database schema is managed with Alembic migrations.

**Create a new migration** (after modifying models):

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply migrations**:

```bash
alembic upgrade head
```

**Rollback migrations**:

```bash
alembic downgrade -1  # Go back one version
```

### Seed Sample Data

For development, you can seed sample data:

```bash
docker-compose exec backend python scripts/seed_data.py
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_audits.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Services

```bash
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### Access Database

```bash
# Via Docker
docker-compose exec db psql -U audit_user -d clinical_audit

# Locally (if PostgreSQL client installed)
psql postgresql://audit_user:audit_password@localhost:5432/clinical_audit
```

### Access Redis

```bash
docker-compose exec redis redis-cli
```

## Configuration

### Environment Variables

Key environment variables in `backend/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | *required* |
| `FERNET_KEY` | Encryption key for PII | *required* |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |
| `REDIS_URL` | Redis connection string | Auto-generated |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `development` |

### Frontend Environment Variables

In `frontend/.env.local`:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## Troubleshooting

### Port Already in Use

If you get port conflicts:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Frontend Build Errors

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Permission Errors (macOS/Linux)

```bash
# If you get permission errors with Docker volumes
sudo chown -R $USER:$USER .
```

## Next Steps

After setup:

1. **Read the Documentation**: Check `/docs` for detailed architecture and API docs
2. **Create Your First Audit**: Navigate to http://localhost:3000/audits/new
3. **Explore the API**: Visit http://localhost:8000/api/v1/docs for interactive API documentation
4. **Review Security Settings**: Ensure encryption keys are properly set for production

## Production Deployment

For production deployment, see:
- [docs/deployment/PRODUCTION.md](../docs/deployment/PRODUCTION.md)
- [docs/deployment/NHS_DEPLOYMENT.md](../docs/deployment/NHS_DEPLOYMENT.md)

## Getting Help

- **Documentation**: `/docs` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com
