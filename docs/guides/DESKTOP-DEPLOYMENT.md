# SPEK Platform v2 + Atlantis UI - Desktop Deployment Guide

**Version**: 1.0.0
**Date**: 2025-10-11
**Status**: Week 25 - Production Deployment Preparation

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Docker Without Virtualization](#docker-without-virtualization)
4. [Installation Steps](#installation-steps)
5. [Configuration](#configuration)
6. [Running the Platform](#running-the-platform)
7. [Database Management](#database-management)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)

---

## Overview

SPEK Platform v2 is deployed as a **desktop application** using:
- **Docker Tools** (native Windows containers without virtualization)
- **Local PostgreSQL** and **Redis** (Docker containers)
- **Next.js Atlantis UI** (production build)
- **AI CLI integration** (Claude Code, Gemini CLI, Codex CLI)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Windows Desktop                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Atlantis UI  │  │ PostgreSQL   │  │    Redis     │     │
│  │  (Next.js)   │  │  (Docker)    │  │  (Docker)    │     │
│  │  Port: 3000  │  │  Port: 5432  │  │  Port: 6379  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        AI CLI Integration (Local)                    │  │
│  │  - Claude Code (Cursor IDE)                          │  │
│  │  - Gemini CLI (FREE)                                 │  │
│  │  - Codex CLI (GitHub Copilot)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Budget Impact

**Phase 1 Desktop Deployment: $40/month**
- Claude Pro: $20/month (existing subscription)
- Cursor IDE: $20/month (existing subscription)
- Gemini CLI: **$0/month** (FREE - 1M tokens/month)
- Codex CLI: **$0/month** (FREE with GitHub Copilot)
- Docker Tools: **$0/month** (native Windows containers)
- PostgreSQL: **$0/month** (Docker container)
- Redis: **$0/month** (Docker container)

**Total: $40/month** (vs $270/month cloud deployment = **82% savings!**)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10/11 (64-bit) |
| **CPU** | 4 cores (Intel i5 or AMD Ryzen 5) |
| **RAM** | 8 GB (16 GB recommended) |
| **Disk Space** | 20 GB free space (SSD recommended) |
| **Network** | Stable internet connection for AI CLI |

### Software Dependencies

| Software | Version | Required |
|----------|---------|----------|
| **Node.js** | 18.x or higher | ✅ Yes |
| **npm** | 8.x or higher | ✅ Yes |
| **Docker Tools** | 24.x or higher | ✅ Yes |
| **PowerShell** | 5.1 or higher | ✅ Yes |
| **Cursor IDE** | Latest | ⚠️ Optional (but recommended) |
| **Gemini CLI** | Latest | ⚠️ Optional (but recommended) |

---

## Docker Without Virtualization

### Special Configuration

**Important**: This project uses Docker Tools running **natively on Windows without hardware virtualization** (BIOS restrictions prevent enabling VT-x/AMD-V).

**How This Works**:
- Docker runs in **native Windows container mode**
- Uses **Windows kernel isolation** instead of hardware virtualization
- Compatible with Linux containers via **Windows Subsystem for Linux 2 (WSL 2)** without Hyper-V
- **No BIOS changes required**

### Docker Tools Setup

1. **Install Docker Tools**:
   ```powershell
   # Download from: https://docs.docker.com/engine/install/
   # Or use Chocolatey:
   choco install docker-cli docker-compose
   ```

2. **Verify Installation**:
   ```powershell
   docker --version
   docker compose version
   ```

3. **Start Docker Service** (if not auto-started):
   ```powershell
   # Check status
   Get-Service docker

   # Start service (if needed)
   Start-Service docker
   ```

4. **Test Docker**:
   ```powershell
   # Pull and run test container
   docker run hello-world
   ```

---

## Installation Steps

### Step 1: Clone Repository

```powershell
cd C:\Users\<YourUsername>\Desktop
git clone https://github.com/your-org/spek-v2-rebuild.git
cd spek-v2-rebuild
```

### Step 2: Install Node.js Dependencies

```powershell
cd atlantis-ui
npm install
```

### Step 3: Configure Environment

```powershell
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
notepad .env
```

**Required Variables** (minimum configuration):
```env
# Database (Docker containers will use these)
DATABASE_URL=postgresql://spek_user:your_secure_password@localhost:5432/spek_db
REDIS_URL=redis://localhost:6379

# Application
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

**Optional Variables** (AI CLI integration):
```env
# Gemini CLI (get from: https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Claude API (get from: https://console.anthropic.com/)
CLAUDE_API_KEY=your_claude_api_key_here

# OpenAI API (get from: https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 4: Validate Environment

```powershell
# Run validation script
cd ..
.\scripts\validate-environment.ps1
```

**Expected Output**:
```
✓ Docker Tools installed
✓ Docker daemon is running
✓ Docker Compose installed
✓ Node.js installed (v18+)
✓ npm installed
✓ Port 3000 is available
✓ Port 5432 is available
✓ Port 6379 is available
✓ .env file found
✓ DATABASE_URL is configured
✓ REDIS_URL is configured
✓ Sufficient disk space
✓ Sufficient memory

✓ ALL CHECKS PASSED
```

### Step 5: Start Infrastructure

```powershell
# Start PostgreSQL and Redis containers
docker compose up -d

# Verify containers are running
docker ps
```

**Expected Output**:
```
CONTAINER ID   IMAGE                  STATUS       PORTS
abc123def456   postgres:15-alpine     Up 30s       0.0.0.0:5432->5432/tcp
def456ghi789   redis:7-alpine         Up 30s       0.0.0.0:6379->6379/tcp
```

### Step 6: Run Database Migrations

```powershell
cd atlantis-ui
node scripts/migrate.js up
```

**Expected Output**:
```
🔄 Running database migrations...

📦 Found 3 pending migration(s):

   ⏳ Applying: 001_initial_schema.sql
   ✅ Applied: 001_initial_schema.sql

   ⏳ Applying: 002_add_context_dna.sql
   ✅ Applied: 002_add_context_dna.sql

   ⏳ Applying: 003_add_audit_logs.sql
   ✅ Applied: 003_add_audit_logs.sql

✅ All migrations applied successfully
```

### Step 7: Build Application

```powershell
# Build production bundle
npm run build
```

**Expected Output**:
```
✓ Compiled successfully in 4.1s
✓ Generating static pages (13/13)
✓ Finalizing page optimization

Route (app)                         Size     First Load JS
├ ○ /                             142 B         177 kB
├ ○ /loop1                       5.23 kB         182 kB
├ ○ /loop2                       5.23 kB         182 kB
├ ○ /loop3                       5.21 kB         182 kB
```

### Step 8: Launch Platform

```powershell
# Option 1: Use launcher script (recommended)
cd ..
.\start-spek.ps1

# Option 2: Manual start
cd atlantis-ui
npm run start
```

**Expected Output**:
```
✓ Docker Tools found: Docker version 24.x
✓ Docker daemon is running
✓ Docker Compose found
✓ Node.js found: v18.x
✓ npm found: v8.x
✓ .env file found
✓ Docker containers started successfully
✓ PostgreSQL is ready
✓ Redis is ready
✓ Database migrations completed
✓ npm dependencies already installed
✓ Application already built (skipping build)
✓ Atlantis UI is starting...

Application will be available at: http://localhost:3000

Press Ctrl+C to stop the server
```

### Step 9: Access Platform

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the **Atlantis UI** home page with:
- Project selector
- Loop 1, 2, 3 navigation
- Agent status monitor
- Monarch chat interface

---

## Configuration

### Environment Variables Reference

See [atlantis-ui/.env.example](../atlantis-ui/.env.example) for complete documentation.

### Docker Compose Configuration

See [docker-compose.yml](../docker-compose.yml) for infrastructure configuration.

### PostgreSQL Configuration

**Connection Details**:
- Host: `localhost`
- Port: `5432`
- Database: `spek_db`
- User: `spek_user`
- Password: (set in `.env`)

**Resource Limits** (desktop-friendly):
- CPU: 1.0 core max, 0.5 core reserved
- Memory: 512 MB max, 256 MB reserved

### Redis Configuration

**Connection Details**:
- Host: `localhost`
- Port: `6379`
- No authentication (local only)

**Resource Limits**:
- CPU: 0.5 core max, 0.25 core reserved
- Memory: 256 MB max, 128 MB reserved
- Max Memory Policy: `allkeys-lru` (Least Recently Used eviction)

---

## Database Management

### Migration Commands

```powershell
cd atlantis-ui

# Show migration status
node scripts/migrate.js status

# Apply all pending migrations
node scripts/migrate.js up

# Rollback last migration
node scripts/migrate.js down

# Rollback all migrations
node scripts/migrate.js down --all

# Create new migration template
node scripts/migrate.js create "add_new_feature"
```

### Database Backup

```powershell
# Backup database to file
docker exec spek-postgres pg_dump -U spek_user -d spek_db > backup.sql

# Restore from backup
docker exec -i spek-postgres psql -U spek_user -d spek_db < backup.sql
```

### Database Console

```powershell
# Connect to PostgreSQL console
docker exec -it spek-postgres psql -U spek_user -d spek_db

# Common commands:
\dt           # List tables
\d+ projects  # Describe projects table
\q            # Quit
```

---

## Troubleshooting

### Issue 1: Docker Daemon Not Running

**Symptom**:
```
✗ Docker daemon is not running
```

**Solution**:
```powershell
# Check service status
Get-Service docker

# Start Docker service
Start-Service docker

# Verify
docker ps
```

### Issue 2: Port Already in Use

**Symptom**:
```
Error: Port 3000 is already in use
```

**Solution**:
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process by PID
taskkill /PID <process_id> /F
```

### Issue 3: Database Connection Failed

**Symptom**:
```
❌ ERROR: DATABASE_URL environment variable not set
```

**Solution**:
```powershell
# 1. Check .env file exists
Test-Path atlantis-ui\.env

# 2. Verify DATABASE_URL is set
cat atlantis-ui\.env | Select-String "DATABASE_URL"

# 3. Restart Docker containers
docker compose down
docker compose up -d
```

### Issue 4: Migration Failed

**Symptom**:
```
❌ Migration failed: relation "projects" already exists
```

**Solution**:
```powershell
# Option 1: Reset database (DANGER: deletes all data)
docker compose down
docker volume rm spek-postgres-data
docker compose up -d
cd atlantis-ui
node scripts/migrate.js up

# Option 2: Manual rollback
node scripts/migrate.js down
node scripts/migrate.js up
```

### Issue 5: Build Failed

**Symptom**:
```
✗ Build failed
```

**Solution**:
```powershell
# Clear Next.js cache
cd atlantis-ui
Remove-Item -Recurse -Force .next

# Reinstall dependencies
Remove-Item -Recurse -Force node_modules
npm install

# Rebuild
npm run build
```

---

## Performance Optimization

### Bundle Size Monitoring

Current bundle sizes (Week 24 optimization):
- Loop1: **5.23 KB** (96.1% reduction from 281 KB)
- Loop2: **5.23 KB** (96.1% reduction)
- Loop3: **5.21 KB** (96.2% reduction)
- First Load JS: **182 KB** (9% under 200 KB target)

### Build Performance

- Compile time: **4.1s** (35% faster than Week 23)
- Tailwind CSS: **30ms**
- PostCSS: **63ms**

### Runtime Performance Targets

| Metric | Target | How to Verify |
|--------|--------|---------------|
| **Page Load** | <3s | Browser DevTools → Network tab |
| **First Contentful Paint (FCP)** | <1.8s | Lighthouse audit |
| **Largest Contentful Paint (LCP)** | <2.5s | Lighthouse audit |
| **3D Rendering** | 60 FPS desktop, 30 FPS mobile | Browser DevTools → Performance tab |
| **WebSocket Latency** | <50ms | Network tab → WS connections |

### Optimization Checklist

- [ ] Dynamic imports enabled for 3D components
- [ ] Webpack code splitting configured
- [ ] Font loading optimized (`display: "swap"`)
- [ ] Resource hints configured (dns-prefetch, preconnect)
- [ ] Image optimization enabled (Next.js Image component)

---

## Security Considerations

### Production Checklist

Before deploying to production:

#### 1. Environment Variables
- [ ] Generate secure passwords: `openssl rand -base64 32`
- [ ] Set `SESSION_SECRET` with 32+ character random string
- [ ] Set `JWT_SECRET` with 32+ character random string
- [ ] Never commit `.env` file to git

#### 2. Docker Security
- [ ] Network isolation enabled (containers on separate network)
- [ ] No exposed ports except 3000 (PostgreSQL/Redis internal only)
- [ ] Resource limits set (prevent DoS)
- [ ] Read-only rootfs where possible

#### 3. Database Security
- [ ] Strong PostgreSQL password
- [ ] Database user has minimal privileges (not superuser)
- [ ] Regular backups configured
- [ ] Connection from localhost only

#### 4. Application Security
- [ ] CORS configured for allowed origins only
- [ ] Rate limiting enabled for API endpoints
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (React escapes by default)

#### 5. Monitoring
- [ ] Error logging configured
- [ ] Performance monitoring enabled
- [ ] Database query logging enabled (for debugging)
- [ ] WebSocket connection monitoring

---

## Rollback Procedure

See [ROLLBACK-PROCEDURE.md](ROLLBACK-PROCEDURE.md) for detailed rollback instructions.

**Quick Rollback**:
```powershell
# 1. Stop application
Ctrl+C  # Or close terminal

# 2. Rollback database (if needed)
cd atlantis-ui
node scripts/migrate.js down

# 3. Restore from backup (if needed)
docker exec -i spek-postgres psql -U spek_user -d spek_db < backup.sql

# 4. Restart application
cd ..
.\start-spek.ps1
```

---

## Next Steps

After successful deployment:

1. **User Acceptance Testing**
   - Test all 9 pages (/, /project/*, /loop1, /loop2, /loop3, /settings, /history, /help)
   - Verify real-time updates (WebSocket)
   - Test 3D visualizations (if enabled)
   - Test agent execution workflows

2. **Performance Validation**
   - Run Lighthouse audit (target: 90+ score)
   - Verify page load times (<3s)
   - Monitor memory usage (<100 MB per tab)
   - Test with 10+ concurrent projects

3. **Production Monitoring** (24 hours)
   - Monitor error rates (<1%)
   - Monitor response times (<200ms API)
   - Monitor WebSocket connections
   - Monitor database performance

4. **Backup Schedule**
   - Daily database backups
   - Weekly full system backups
   - 30-day retention policy

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/your-org/spek-v2-rebuild/issues
- **Documentation**: [Week 25 Complete Summary](../docs/development-process/week25/WEEK-25-COMPLETE-SUMMARY.md)
- **Architecture**: [ARCHITECTURE-MASTER-TOC.md](../architecture/ARCHITECTURE-MASTER-TOC.md)

---

**Last Updated**: 2025-10-11
**Version**: 1.0.0
**Status**: Production-Ready
**Week**: 25 of 26 (96.2% project completion)
