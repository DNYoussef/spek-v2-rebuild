# Production Deployment Checklist

**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Status**: Week 21 Day 3 - Production Hardening Complete

---

## Overview

This checklist ensures all critical steps are completed before deploying SPEK Platform v2 + Atlantis UI to production. Each section must be reviewed and signed off by the responsible party.

**Deployment Readiness**: Use this checklist for every production deployment to ensure consistency, reliability, and safety.

---

## Pre-Deployment Checklist

### 1. Code Quality & Testing ✅

- [ ] **All CI/CD checks passing**
  - [ ] Fast checks (lint, format, type check) ✅
  - [ ] Python tests (unit + integration) ✅
  - [ ] Atlantis UI E2E tests (37+ tests) ✅
  - [ ] Performance regression tests ✅
  - [ ] Security scans (4 tools) ✅
  - [ ] NASA compliance (≥92%) ✅

- [ ] **Code review completed**
  - [ ] All PRs reviewed by 1+ team members
  - [ ] No unresolved review comments
  - [ ] Architecture decisions documented

- [ ] **Test coverage validated**
  - [ ] Unit test coverage ≥80%
  - [ ] Integration tests passing
  - [ ] E2E tests passing (37+ tests)
  - [ ] Performance tests passing

- [ ] **Performance validated**
  - [ ] Lighthouse CI score ≥80%
  - [ ] Page load <3s for all pages
  - [ ] 3D rendering ≥60 FPS (desktop)
  - [ ] Bundle size <2MB
  - [ ] Core Web Vitals passing (FCP, LCP, CLS)

**Sign-off**: ___________________ Date: ___________

---

### 2. Environment Configuration 🔧

- [ ] **Environment variables configured**
  ```bash
  # Required environment variables
  NODE_ENV=production
  NEXT_PUBLIC_API_URL=https://api.spek.platform
  DATABASE_URL=postgresql://...
  REDIS_URL=redis://...

  # API Keys (from secrets manager)
  CLAUDE_API_KEY=sk-ant-...
  GEMINI_API_KEY=...
  OPENAI_API_KEY=sk-...

  # Optional
  SENTRY_DSN=https://...
  ANALYTICS_ID=G-...
  ```

- [ ] **Secrets management**
  - [ ] All secrets stored in secure vault (AWS Secrets Manager, Azure Key Vault, etc.)
  - [ ] No hardcoded secrets in codebase
  - [ ] `.env` files NOT committed to git
  - [ ] Secret rotation policy documented

- [ ] **Database configuration**
  - [ ] Production database provisioned
  - [ ] Database migrations tested
  - [ ] Backup policy configured
  - [ ] Connection pooling configured
  - [ ] Read replicas configured (if applicable)

- [ ] **Redis/Cache configuration**
  - [ ] Redis instance provisioned
  - [ ] Cache TTL configured
  - [ ] Eviction policy set
  - [ ] High availability configured

**Sign-off**: ___________________ Date: ___________

---

### 3. Security Hardening 🔒

- [ ] **HTTPS/TLS configured**
  - [ ] Valid SSL certificate installed
  - [ ] Certificate auto-renewal configured
  - [ ] HSTS headers enabled
  - [ ] TLS 1.2+ enforced

- [ ] **Security headers configured**
  ```typescript
  // next.config.ts headers
  X-Frame-Options: SAMEORIGIN
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Strict-Transport-Security: max-age=31536000
  Content-Security-Policy: default-src 'self'
  ```

- [ ] **Authentication & Authorization**
  - [ ] JWT token validation working
  - [ ] Session management configured
  - [ ] RBAC (Role-Based Access Control) implemented
  - [ ] OAuth/SSO configured (if applicable)

- [ ] **Security scanning passed**
  - [ ] No critical vulnerabilities (Trivy, Bandit)
  - [ ] Dependency audit passed (pip-audit, npm audit)
  - [ ] OWASP Top 10 mitigations verified
  - [ ] Penetration testing completed (if required)

- [ ] **Rate limiting configured**
  - [ ] API rate limits set (e.g., 100 req/min)
  - [ ] DDoS protection enabled
  - [ ] Abuse detection configured

- [ ] **CORS configured**
  - [ ] Allowed origins whitelisted
  - [ ] Credentials handling secure
  - [ ] Preflight caching enabled

**Sign-off**: ___________________ Date: ___________

---

### 4. Monitoring & Observability 📊

- [ ] **Application monitoring**
  - [ ] APM tool configured (Sentry, Datadog, New Relic)
  - [ ] Error tracking enabled
  - [ ] Performance monitoring active
  - [ ] Custom metrics defined

- [ ] **Infrastructure monitoring**
  - [ ] Server/container metrics (CPU, memory, disk)
  - [ ] Network metrics (bandwidth, latency)
  - [ ] Database metrics (queries, connections)
  - [ ] Cache metrics (hit rate, evictions)

- [ ] **Logging configured**
  - [ ] Centralized logging (CloudWatch, Datadog, ELK)
  - [ ] Log levels set (INFO in production)
  - [ ] PII scrubbing enabled
  - [ ] Log retention policy (30-90 days)

- [ ] **Alerting configured**
  - [ ] Critical alerts (downtime, errors >5%)
  - [ ] Warning alerts (performance degradation)
  - [ ] On-call rotation configured
  - [ ] Alert escalation policy defined

- [ ] **Health checks configured**
  - [ ] `/health` endpoint responding
  - [ ] Liveness probe configured
  - [ ] Readiness probe configured
  - [ ] Deep health checks (database, cache, APIs)

**Monitoring Endpoints**:
```
GET /health - Basic health check
GET /health/ready - Readiness check
GET /health/live - Liveness check
GET /metrics - Prometheus metrics (if applicable)
```

**Sign-off**: ___________________ Date: ___________

---

### 5. Performance & Scalability ⚡

- [ ] **CDN configured**
  - [ ] Static assets served via CDN
  - [ ] Cache-Control headers set
  - [ ] Gzip/Brotli compression enabled

- [ ] **Auto-scaling configured**
  - [ ] Horizontal Pod Autoscaler (HPA) set
  - [ ] Scaling thresholds defined (CPU 70%, Memory 80%)
  - [ ] Min/max replicas configured

- [ ] **Load balancing**
  - [ ] Load balancer configured
  - [ ] Health checks enabled
  - [ ] Session affinity configured (if needed)

- [ ] **Database optimization**
  - [ ] Indexes created on frequently queried columns
  - [ ] Query performance tested
  - [ ] Connection pooling optimized
  - [ ] Slow query log enabled

**Sign-off**: ___________________ Date: ___________

---

### 6. Disaster Recovery 🚨

- [ ] **Backup strategy**
  - [ ] Database backups automated (daily full, hourly incremental)
  - [ ] Backup retention policy (30 days)
  - [ ] Backup restoration tested
  - [ ] Off-site backup storage

- [ ] **Disaster recovery plan**
  - [ ] RPO (Recovery Point Objective) defined
  - [ ] RTO (Recovery Time Objective) defined
  - [ ] DR runbook documented
  - [ ] DR drill performed

- [ ] **High availability**
  - [ ] Multi-AZ deployment (if applicable)
  - [ ] Database replication configured
  - [ ] Cache replication configured

**Sign-off**: ___________________ Date: ___________

---

## Deployment Process

### Step 1: Pre-Deployment Verification

```bash
# 1. Verify CI/CD status
git status
git log -1

# 2. Check all tests passing
npm run test
npm run test:e2e

# 3. Build production artifacts
npm run build

# 4. Run security scan
npm audit --production
bandit -r src/

# 5. Verify environment variables
env | grep -E "(NODE_ENV|DATABASE_URL|REDIS_URL)"
```

**Checklist**:
- [ ] Working on correct branch (main/release)
- [ ] All tests passing
- [ ] Build successful
- [ ] No security vulnerabilities
- [ ] Environment variables set

---

### Step 2: Database Migration (if applicable)

```bash
# 1. Backup database
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations in dry-run mode
npm run migrate:dry-run

# 3. Review migration plan
cat migration-plan.txt

# 4. Run migrations
npm run migrate

# 5. Verify migration success
npm run migrate:status
```

**Checklist**:
- [ ] Database backup created
- [ ] Migration plan reviewed
- [ ] Migrations executed successfully
- [ ] Data integrity verified

---

### Step 3: Deployment Execution

**For containerized deployment (Docker/Kubernetes)**:

```bash
# 1. Build Docker image
docker build -t spek-platform:v2.0.0 .

# 2. Tag image
docker tag spek-platform:v2.0.0 registry.example.com/spek-platform:v2.0.0
docker tag spek-platform:v2.0.0 registry.example.com/spek-platform:latest

# 3. Push to registry
docker push registry.example.com/spek-platform:v2.0.0
docker push registry.example.com/spek-platform:latest

# 4. Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml
kubectl rollout status deployment/spek-platform

# 5. Verify deployment
kubectl get pods
kubectl logs -f deployment/spek-platform
```

**For serverless deployment (Vercel, Netlify)**:

```bash
# 1. Install CLI
npm install -g vercel

# 2. Deploy to production
vercel --prod

# 3. Verify deployment
vercel ls
curl https://spek.platform/health
```

**Checklist**:
- [ ] Image built successfully
- [ ] Image pushed to registry
- [ ] Deployment executed
- [ ] Pods/instances healthy
- [ ] Health check passing

---

### Step 4: Post-Deployment Verification

```bash
# 1. Check health endpoint
curl https://spek.platform/health
# Expected: {"status": "ok", "version": "2.0.0"}

# 2. Run smoke tests
npm run test:smoke

# 3. Check monitoring dashboards
# - Application errors: 0
# - Response time: <500ms
# - CPU usage: <50%
# - Memory usage: <70%

# 4. Verify performance
curl -o /dev/null -s -w "%{time_total}\n" https://spek.platform
# Expected: <2s

# 5. Check logs for errors
kubectl logs -f deployment/spek-platform | grep -i error
# Expected: No critical errors
```

**Checklist**:
- [ ] Health check passing
- [ ] Smoke tests passing
- [ ] No errors in logs
- [ ] Performance within SLAs
- [ ] Monitoring dashboards green

---

### Step 5: Traffic Migration (Blue-Green/Canary)

**Blue-Green Deployment**:

```bash
# 1. Deploy to "green" environment
kubectl apply -f k8s/deployment-green.yaml

# 2. Verify green environment
curl https://green.spek.platform/health

# 3. Switch traffic to green
kubectl apply -f k8s/service-green.yaml

# 4. Monitor for 15 minutes
watch -n 10 kubectl get pods

# 5. Decommission blue environment (after 1 hour)
kubectl delete -f k8s/deployment-blue.yaml
```

**Canary Deployment**:

```bash
# 1. Deploy canary (10% traffic)
kubectl apply -f k8s/deployment-canary.yaml

# 2. Monitor canary metrics (30 minutes)
# - Error rate: <1%
# - Latency: p99 <1s

# 3. Increase to 50% traffic (if healthy)
kubectl scale deployment/spek-platform-canary --replicas=5

# 4. Full rollout (if healthy)
kubectl apply -f k8s/deployment.yaml
```

**Checklist**:
- [ ] New version deployed to separate environment
- [ ] Traffic gradually migrated
- [ ] Monitoring healthy during migration
- [ ] No alerts triggered
- [ ] Old version still available for rollback

---

## Rollback Procedures

### When to Rollback

**Immediate Rollback Triggers**:
- Critical errors affecting >5% of users
- Data corruption detected
- Security vulnerability exploited
- Performance degradation >50%
- Health checks failing

**Warning Triggers** (monitor, may rollback):
- Error rate 2-5%
- Performance degradation 20-50%
- Increased latency (p99 >2s)

---

### Rollback Execution

**For Kubernetes**:

```bash
# 1. Check rollout history
kubectl rollout history deployment/spek-platform

# 2. Rollback to previous version
kubectl rollout undo deployment/spek-platform

# 3. Verify rollback
kubectl rollout status deployment/spek-platform
kubectl get pods

# 4. Check health
curl https://spek.platform/health

# 5. Monitor logs
kubectl logs -f deployment/spek-platform
```

**For Docker/Compose**:

```bash
# 1. Stop current version
docker-compose down

# 2. Checkout previous version
git checkout v1.9.0

# 3. Rebuild and restart
docker-compose up -d --build

# 4. Verify rollback
docker-compose ps
curl http://localhost:3000/health
```

**For Vercel/Serverless**:

```bash
# 1. List deployments
vercel ls

# 2. Promote previous deployment
vercel promote <deployment-url>

# 3. Verify rollback
vercel ls
curl https://spek.platform/health
```

**Rollback Checklist**:
- [ ] Rollback decision approved
- [ ] Previous version identified
- [ ] Rollback executed
- [ ] Health checks passing
- [ ] Metrics returning to normal
- [ ] Incident documented

---

### Database Rollback

**If migrations need to be rolled back**:

```bash
# 1. Check current migration
npm run migrate:status

# 2. Rollback 1 migration
npm run migrate:rollback

# 3. Restore from backup (if data corruption)
psql -h $DB_HOST -U $DB_USER $DB_NAME < backup_20251010_120000.sql

# 4. Verify data integrity
npm run migrate:verify
```

**Database Rollback Checklist**:
- [ ] Migration rollback executed
- [ ] Data integrity verified
- [ ] Application compatible with rolled-back schema
- [ ] No data loss

---

## Post-Deployment

### Communication

**Internal Communication**:
```
Subject: [DEPLOYED] SPEK Platform v2.0.0 to Production

Deployment completed successfully at 2025-10-10 14:30 UTC.

Changes:
- Week 21 production hardening complete
- 50-60% performance improvement
- 198+ new tests added
- CI/CD pipeline optimized (40-50% faster)

Monitoring:
- Health: ✅ OK
- Error rate: 0.1%
- Response time: 450ms (p99)
- CPU: 35%
- Memory: 62%

Next steps:
- Monitor for 24 hours
- Collect user feedback
- Schedule retro (Friday 10am)
```

**External Communication** (if customer-facing):
```
Subject: Platform Update - Enhanced Performance & Reliability

We've deployed significant improvements to the SPEK Platform:

✅ 50% faster page loads
✅ Enhanced 3D rendering performance
✅ Improved reliability and monitoring

All features are working as expected. If you experience any issues, please contact support.
```

---

### Monitoring Window

**First 1 hour**:
- [ ] Monitor every 5 minutes
- [ ] Check error logs continuously
- [ ] Verify key user flows working

**First 24 hours**:
- [ ] Monitor every 30 minutes
- [ ] Check performance metrics
- [ ] Collect user feedback

**First week**:
- [ ] Daily health check
- [ ] Review weekly metrics
- [ ] Identify optimization opportunities

---

### Post-Deployment Review

**Schedule retro meeting within 48 hours**:

Topics to cover:
- What went well?
- What could be improved?
- Were there any surprises?
- Action items for next deployment

Document:
- Deployment duration
- Issues encountered
- Lessons learned
- Process improvements

---

## Sign-Off

### Final Checklist

- [ ] All pre-deployment checks completed
- [ ] Deployment executed successfully
- [ ] Post-deployment verification passed
- [ ] Rollback plan tested and ready
- [ ] Monitoring dashboards green
- [ ] Communication sent
- [ ] Documentation updated

### Approvals

**Engineering Lead**: ___________________ Date: ___________

**DevOps Lead**: ___________________ Date: ___________

**Product Manager**: ___________________ Date: ___________

**Security Officer**: ___________________ Date: ___________

---

## Appendix

### Useful Commands

**Check service health**:
```bash
curl https://spek.platform/health
```

**View logs**:
```bash
kubectl logs -f deployment/spek-platform --tail=100
```

**Check resource usage**:
```bash
kubectl top pods
kubectl top nodes
```

**Scale deployment**:
```bash
kubectl scale deployment/spek-platform --replicas=5
```

**Restart deployment**:
```bash
kubectl rollout restart deployment/spek-platform
```

---

### Emergency Contacts

**On-Call Engineer**: +1-XXX-XXX-XXXX
**DevOps Lead**: +1-XXX-XXX-XXXX
**CTO**: +1-XXX-XXX-XXXX

**Incident Response Slack**: #incidents
**War Room**: Zoom link

---

**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Next Review**: 2025-11-10
