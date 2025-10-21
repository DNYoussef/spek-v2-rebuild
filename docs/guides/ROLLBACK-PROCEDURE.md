# SPEK Platform v2 - Rollback Procedure

**Version**: 1.0.0
**Date**: 2025-10-11
**Status**: Production-Ready

---

## Table of Contents

1. [When to Rollback](#when-to-rollback)
2. [Pre-Rollback Checklist](#pre-rollback-checklist)
3. [Rollback Steps](#rollback-steps)
4. [Post-Rollback Validation](#post-rollback-validation)
5. [Common Scenarios](#common-scenarios)
6. [Emergency Contacts](#emergency-contacts)

---

## When to Rollback

Execute rollback procedure if **any** of these conditions occur:

### Critical Conditions (IMMEDIATE ROLLBACK)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| **Error Rate** | >5% sustained for >5 minutes | IMMEDIATE |
| **Data Corruption** | Any confirmed data loss | IMMEDIATE |
| **Security Breach** | Unauthorized access detected | IMMEDIATE |
| **Application Crash** | Application won't start | IMMEDIATE |
| **Database Failure** | Cannot connect to database | IMMEDIATE |

### Warning Conditions (EVALUATE ROLLBACK)

| Condition | Threshold | Action |
|-----------|-----------|--------|
| **Performance Degradation** | >50% slower response times | Evaluate |
| **Memory Leak** | Memory usage grows continuously | Evaluate |
| **WebSocket Failures** | >10% connection failures | Evaluate |
| **3D Rendering Issues** | <30 FPS on desktop | Evaluate |
| **Agent Failures** | >20% agent execution failures | Evaluate |

---

## Pre-Rollback Checklist

**Before initiating rollback, complete these steps:**

### 1. Document the Issue

```powershell
# Create incident log
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = "logs/incident_$timestamp.txt"

@"
INCIDENT REPORT
===============
Date/Time: $(Get-Date)
Issue: [Describe the issue]
Error Rate: [X%]
Symptoms: [List symptoms]
Affected Components: [List components]
"@ | Out-File $logFile
```

### 2. Create Emergency Backup

```powershell
# Backup database
$backupFile = "backups/emergency_backup_$timestamp.sql"
docker exec spek-postgres pg_dump -U spek_user -d spek_db > $backupFile

# Verify backup
if (Test-Path $backupFile) {
    Write-Host "✓ Emergency backup created: $backupFile"
} else {
    Write-Error "❌ Backup failed! DO NOT PROCEED with rollback!"
    exit 1
}
```

### 3. Stop Incoming Traffic

```powershell
# Stop the application server
# Press Ctrl+C in the terminal running npm start
# OR
Stop-Process -Name "node" -Force
```

### 4. Notify Stakeholders

- [ ] Notify development team
- [ ] Notify project managers
- [ ] Document expected downtime
- [ ] Prepare status updates

---

## Rollback Steps

### Phase 1: Stop Application (30 seconds)

```powershell
# Navigate to project root
cd C:\Users\<YourUsername>\Desktop\spek-v2-rebuild

# Stop the Next.js server
# If running in terminal: Press Ctrl+C
# If running as background process:
Stop-Process -Name "node" -Force

# Verify stopped
Get-Process -Name "node" -ErrorAction SilentlyContinue
# Should return nothing
```

**Expected Output**:
```
✓ Application server stopped
```

---

### Phase 2: Database Rollback (2-5 minutes)

#### Option A: Rollback Last Migration

```powershell
cd atlantis-ui

# Rollback last migration
node scripts/migrate.js down

# Verify rollback
node scripts/migrate.js status
```

**Expected Output**:
```
🔄 Rolling back migrations...

   ⏳ Rolling back: 003_add_audit_logs.sql
   ✅ Rolled back: 003_add_audit_logs.sql

✅ Rollback completed successfully
```

#### Option B: Rollback All Migrations

```powershell
# Rollback all migrations (DANGER: resets database)
node scripts/migrate.js down --all

# Verify rollback
node scripts/migrate.js status
```

#### Option C: Restore from Backup

```powershell
# List available backups
dir backups\*.sql | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Choose backup file
$backupFile = "backups/emergency_backup_2025-10-11_14-30-00.sql"

# Drop and recreate database
docker exec spek-postgres psql -U spek_user -d postgres -c "DROP DATABASE IF EXISTS spek_db;"
docker exec spek-postgres psql -U spek_user -d postgres -c "CREATE DATABASE spek_db;"

# Restore from backup
docker exec -i spek-postgres psql -U spek_user -d spek_db < $backupFile

# Verify restoration
docker exec spek-postgres psql -U spek_user -d spek_db -c "\dt"
```

**Expected Output**:
```
                List of relations
 Schema |         Name          | Type  |   Owner
--------+-----------------------+-------+-----------
 public | projects              | table | spek_user
 public | agents                | table | spek_user
 public | tasks                 | table | spek_user
(3 rows)
```

---

### Phase 3: Application Rollback (2 minutes)

#### Option A: Rollback to Previous Build

```powershell
cd atlantis-ui

# Check git history
git log --oneline -10

# Checkout previous stable commit
git checkout <previous-commit-sha>

# Rebuild application
Remove-Item -Recurse -Force .next
npm install
npm run build
```

#### Option B: Keep Current Code, Clear Cache

```powershell
cd atlantis-ui

# Clear Next.js cache
Remove-Item -Recurse -Force .next

# Rebuild
npm run build
```

---

### Phase 4: Restart Application (1 minute)

```powershell
# Return to project root
cd ..

# Restart using launcher script
.\start-spek.ps1
```

**Expected Output**:
```
✓ Docker containers started successfully
✓ PostgreSQL is ready
✓ Redis is ready
✓ Atlantis UI is starting...

Application will be available at: http://localhost:3000
```

---

### Phase 5: Verify Rollback (2 minutes)

#### 1. Health Check

```powershell
# Check application health
Invoke-WebRequest -Uri "http://localhost:3000" -Method GET

# Expected: Status Code 200
```

#### 2. Database Connectivity

```powershell
# Connect to database
docker exec spek-postgres psql -U spek_user -d spek_db -c "SELECT COUNT(*) FROM projects;"

# Expected: Returns row count (may be 0)
```

#### 3. Functional Tests

**Manual Verification**:
- [ ] Home page loads (http://localhost:3000)
- [ ] Project selector works
- [ ] Loop 1 page renders
- [ ] Loop 2 page renders
- [ ] Loop 3 page renders
- [ ] WebSocket connection established
- [ ] 3D visualizations load (if enabled)
- [ ] No console errors

#### 4. Performance Validation

```powershell
# Run Playwright E2E tests
cd atlantis-ui
npm run test:e2e

# Expected: All tests pass
```

---

## Post-Rollback Validation

### Validation Checklist

| Check | Command | Expected Result |
|-------|---------|-----------------|
| **Application Running** | `Get-Process -Name "node"` | Process found |
| **Database Accessible** | `docker exec spek-postgres pg_isready -U spek_user` | Ready |
| **Redis Accessible** | `docker exec spek-redis redis-cli ping` | PONG |
| **HTTP Response** | `curl http://localhost:3000` | Status 200 |
| **Error Rate** | Check logs | <1% |
| **Response Time** | Browser DevTools | <200ms API |

### Monitoring Period

**Monitor for 1 hour after rollback**:

```powershell
# Monitor application logs
Get-Content atlantis-ui\logs\application.log -Wait -Tail 50

# Monitor Docker container logs
docker logs spek-postgres -f
docker logs spek-redis -f
```

**Key Metrics to Watch**:
- Error rate: Should be <1%
- Response time: Should be <200ms
- Memory usage: Should be stable (<100 MB)
- WebSocket connections: Should be stable
- Database queries: Should complete in <50ms

---

## Common Scenarios

### Scenario 1: Migration Failed During Deployment

**Symptoms**:
- Database error on application start
- "Migration failed" error in logs
- Application won't start

**Rollback**:
```powershell
# Rollback failed migration
cd atlantis-ui
node scripts/migrate.js down

# Restore from backup
docker exec -i spek-postgres psql -U spek_user -d spek_db < backups/pre-migration-backup.sql

# Restart application
cd ..
.\start-spek.ps1
```

---

### Scenario 2: High Error Rate After Deployment

**Symptoms**:
- Error rate >5%
- Application crashes frequently
- API endpoints returning 500 errors

**Rollback**:
```powershell
# Stop application
Stop-Process -Name "node" -Force

# Rollback to previous commit
cd atlantis-ui
git log --oneline -5
git checkout <previous-stable-commit>

# Rebuild and restart
Remove-Item -Recurse -Force .next
npm install
npm run build
cd ..
.\start-spek.ps1
```

---

### Scenario 3: Data Corruption Detected

**Symptoms**:
- Missing or corrupted data
- Inconsistent database state
- Foreign key constraint violations

**Rollback**:
```powershell
# IMMEDIATE ACTION: Stop application
Stop-Process -Name "node" -Force

# Drop and recreate database
docker exec spek-postgres psql -U spek_user -d postgres -c "DROP DATABASE IF EXISTS spek_db;"
docker exec spek-postgres psql -U spek_user -d postgres -c "CREATE DATABASE spek_db;"

# Restore from last known good backup
$backupFile = "backups/pre-deployment-backup.sql"
docker exec -i spek-postgres psql -U spek_user -d spek_db < $backupFile

# Verify data integrity
docker exec spek-postgres psql -U spek_user -d spek_db -c "SELECT COUNT(*) FROM projects;"

# Restart application
.\start-spek.ps1
```

---

### Scenario 4: Performance Degradation

**Symptoms**:
- Page load times >5s
- API response times >1s
- 3D rendering <15 FPS

**Rollback** (if caused by recent deployment):
```powershell
# Rollback to previous commit
cd atlantis-ui
git checkout <previous-commit>

# Clear cache and rebuild
Remove-Item -Recurse -Force .next
npm run build

# Restart
cd ..
.\start-spek.ps1
```

---

### Scenario 5: Security Breach Detected

**Symptoms**:
- Unauthorized access detected
- Suspicious database queries
- API keys compromised

**IMMEDIATE ACTIONS**:
```powershell
# 1. Stop application IMMEDIATELY
Stop-Process -Name "node" -Force

# 2. Stop Docker containers
docker compose down

# 3. Rotate all secrets
# Edit .env file and generate new secrets:
# SESSION_SECRET=$(openssl rand -base64 32)
# JWT_SECRET=$(openssl rand -base64 32)

# 4. Restore database from last known good backup
docker compose up -d
docker exec -i spek-postgres psql -U spek_user -d spek_db < backups/last-known-good.sql

# 5. Restart with new secrets
.\start-spek.ps1
```

---

## Emergency Contacts

### Development Team

| Role | Name | Contact |
|------|------|---------|
| **Lead Developer** | [Name] | [Email/Phone] |
| **Database Admin** | [Name] | [Email/Phone] |
| **DevOps Engineer** | [Name] | [Email/Phone] |
| **Project Manager** | [Name] | [Email/Phone] |

### Escalation Path

1. **Level 1**: Development Team (initial response)
2. **Level 2**: Lead Developer (if not resolved in 30 minutes)
3. **Level 3**: Project Manager (if critical business impact)
4. **Level 4**: Executive Sponsor (if extended outage)

---

## Post-Incident Review

After rollback is complete, conduct post-incident review:

### 1. Document Incident

Create incident report with:
- Root cause analysis
- Timeline of events
- Actions taken
- Lessons learned

### 2. Improve Processes

Identify improvements:
- [ ] Additional testing needed?
- [ ] Better monitoring required?
- [ ] Rollback procedure gaps?
- [ ] Communication issues?

### 3. Update Documentation

Update relevant documentation:
- [ ] This rollback procedure
- [ ] Deployment checklist
- [ ] Testing procedures
- [ ] Monitoring dashboards

---

## Appendix: Quick Reference

### One-Line Rollback Commands

```powershell
# Full rollback (database + application)
cd atlantis-ui && node scripts/migrate.js down && cd .. && .\start-spek.ps1

# Database only rollback
cd atlantis-ui && node scripts/migrate.js down

# Application cache clear
cd atlantis-ui && Remove-Item -Recurse -Force .next && npm run build

# Emergency stop
Stop-Process -Name "node" -Force && docker compose down
```

---

**Last Updated**: 2025-10-11
**Version**: 1.0.0
**Status**: Production-Ready
**Maximum Downtime**: 10 minutes (target: 5 minutes)
