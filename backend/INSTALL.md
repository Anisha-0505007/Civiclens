# CivicLens Backend Installation Guide

Complete step-by-step installation instructions for the CivicLens Backend API.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Install](#quick-install)
- [Detailed Installation](#detailed-installation)
- [Troubleshooting](#troubleshooting)
- [Verification](#verification)

---

## Prerequisites

### Required Software
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **PostGIS Extension** - Comes with PostgreSQL or install separately
- **pip** - Python package manager (comes with Python)

### System Requirements
- **OS**: Linux (Ubuntu/Debian recommended), macOS, or Windows WSL2
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for dependencies + database

---

## Quick Install

For experienced developers, here's the quick version:

```bash
# 1. Install PostgreSQL & PostGIS
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib postgis

# 2. Set up database
sudo -u postgres psql -c "CREATE DATABASE civiclens;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE civiclens TO postgres;"
sudo -u postgres psql -d civiclens -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# 3. Clone/navigate to project
cd /path/to/civiclens/backend

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings

# 6. Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

---

## Detailed Installation

### Step 1: Install PostgreSQL and PostGIS

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib postgresql-15-postgis-3
```

#### macOS (using Homebrew)
```bash
brew install postgresql@15 postgis
brew services start postgresql@15
```

#### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. During installation, select PostGIS in the Stack Builder
3. Or use WSL2 and follow Ubuntu instructions

### Step 2: Configure PostgreSQL

#### Start PostgreSQL Service
```bash
# Ubuntu/Debian
sudo service postgresql start

# macOS
brew services start postgresql@15

# Check status
sudo service postgresql status
```

#### Configure Authentication (if needed)

Edit `/etc/postgresql/15/main/pg_hba.conf`:

```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

Change authentication method from `peer` to `md5` for local connections:
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo service postgresql restart
```

### Step 3: Create Database

#### Option A: Using the provided script (recommended)
```bash
cd /path/to/civiclens/backend
chmod +x init_postgres.sh
./init_postgres.sh
```

#### Option B: Manual setup
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE civiclens;
CREATE USER civiclens_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE civiclens TO civiclens_user;

# Connect to the database
\c civiclens

# Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

# Verify PostGIS installation
SELECT PostGIS_Version();

# Exit
\q
```

### Step 4: Install Python Dependencies

#### Create Virtual Environment (recommended)
```bash
cd /path/to/civiclens/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

#### Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|sqlalchemy|psycopg2|geoalchemy2"
```

Expected output:
```
fastapi                  0.110.1
geoalchemy2              0.18.0
psycopg2-binary         2.9.11
SQLAlchemy              2.0.44
```

### Step 5: Configure Environment Variables

#### Create .env file
```bash
cp .env.example .env
```

If `.env.example` doesn't exist, create `.env` manually:

```bash
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civiclens

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-abc123xyz789
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# CORS Configuration
CORS_ORIGINS=*

# Optional: MongoDB (if needed for other features)
MONGO_URL=mongodb://localhost:27017
DB_NAME=civiclens_mongo
EOF
```

#### Generate Secure JWT Secret (recommended)
```bash
# Generate a secure random secret
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy the output and replace JWT_SECRET_KEY in .env
```

#### Edit Configuration
```bash
nano .env
```

Update the following:
- `DATABASE_URL`: Your PostgreSQL connection string
- `JWT_SECRET_KEY`: A strong random secret key
- `CORS_ORIGINS`: Your frontend URL (in production)

### Step 6: Initialize Database Tables

The database tables will be created automatically on first run, but you can also initialize them manually:

```bash
python3 -c "from database import init_db; init_db()"
```

### Step 7: Run the Server

#### Development Mode (with auto-reload)
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Production Mode
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

#### Using Supervisor (production)
Create supervisor config `/etc/supervisor/conf.d/civiclens.conf`:

```ini
[program:civiclens-backend]
command=/path/to/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/path/to/civiclens/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/civiclens/backend.err.log
stdout_logfile=/var/log/civiclens/backend.out.log
```

Start with supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start civiclens-backend
```

---

## Verification

### Check Server Status

1. **Health Check**:
```bash
curl http://localhost:8001/api/health
```

Expected output:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

2. **API Root**:
```bash
curl http://localhost:8001/api/
```

Expected output:
```json
{
  "message": "CivicLens API",
  "version": "1.0.0",
  "status": "operational"
}
```

3. **Interactive API Docs**:

Open in browser:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Run Test Suite

```bash
# Make test script executable
chmod +x test_api.sh

# Run all tests
./test_api.sh
```

Expected output: All 16 tests should pass ✓

---

## Troubleshooting

### Issue 1: PostgreSQL Connection Failed

**Error**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start PostgreSQL
sudo service postgresql start

# Check if database exists
sudo -u postgres psql -l | grep civiclens

# Create database if missing
sudo -u postgres psql -c "CREATE DATABASE civiclens;"
```

### Issue 2: Password Authentication Failed

**Error**: `password authentication failed for user "postgres"`

**Solutions**:
```bash
# Option 1: Change PostgreSQL user password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Option 2: Update .env file with correct password
nano .env
# Change DATABASE_URL to match your PostgreSQL password

# Option 3: Configure pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Change 'peer' or 'scram-sha-256' to 'md5'
sudo service postgresql restart
```

### Issue 3: PostGIS Extension Not Found

**Error**: `ERROR: could not open extension control file`

**Solutions**:
```bash
# Install PostGIS
sudo apt-get install postgresql-15-postgis-3

# Enable extension in database
sudo -u postgres psql -d civiclens -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Verify installation
sudo -u postgres psql -d civiclens -c "SELECT PostGIS_Version();"
```

### Issue 4: Port Already in Use

**Error**: `[Errno 98] Address already in use`

**Solutions**:
```bash
# Find process using port 8001
sudo lsof -ti:8001

# Kill the process
sudo kill -9 $(sudo lsof -ti:8001)

# Or use a different port
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

### Issue 5: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Issue 6: Permission Denied on PostgreSQL

**Error**: `FATAL: permission denied for database "civiclens"`

**Solutions**:
```bash
# Grant privileges
sudo -u postgres psql << EOF
GRANT ALL PRIVILEGES ON DATABASE civiclens TO postgres;
\c civiclens
GRANT ALL ON SCHEMA public TO postgres;
EOF
```

### Issue 7: Import Errors

**Error**: `ImportError: cannot import name 'X' from 'Y'`

**Solutions**:
```bash
# Ensure you're in the correct directory
cd /path/to/civiclens/backend

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Reinstall with --force-reinstall
pip install -r requirements.txt --force-reinstall
```

---

## Environment-Specific Configuration

### Development
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/civiclens_dev
JWT_SECRET_KEY=dev-secret-key-not-for-production
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Staging
```env
DATABASE_URL=postgresql://user:pass@staging-db.example.com:5432/civiclens_staging
JWT_SECRET_KEY=staging-secret-key-abc123xyz789
CORS_ORIGINS=https://staging.civiclens.com
```

### Production
```env
DATABASE_URL=postgresql://user:pass@prod-db.example.com:5432/civiclens_prod
JWT_SECRET_KEY=production-secret-key-generated-securely
CORS_ORIGINS=https://civiclens.com,https://www.civiclens.com
```

---

## Next Steps

After successful installation:

1. ✅ Read [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for complete API reference
2. ✅ Check [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) for integration examples
3. ✅ Review [README.md](./README.md) for feature overview
4. ✅ Test all endpoints with `./test_api.sh`
5. ✅ Set up frontend integration

---

## Docker Installation (Alternative)

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: civiclens
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/civiclens
    depends_on:
      - postgres
    volumes:
      - .:/app

volumes:
  postgres_data:
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

Run with Docker:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

---

## Support

If you encounter issues not covered here:

1. Check the [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for endpoint details
2. Review server logs: `tail -f /var/log/civiclens/backend.err.log`
3. Verify PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-15-main.log`
4. Run the test suite: `./test_api.sh`

---

## Security Notes

⚠️ **Before deploying to production:**

1. Change `JWT_SECRET_KEY` to a strong random value
2. Use a strong database password
3. Limit `CORS_ORIGINS` to your actual domains
4. Enable HTTPS/SSL
5. Set up firewall rules
6. Enable database backups
7. Implement rate limiting
8. Monitor logs regularly

---

Happy building with CivicLens! 🏙️
