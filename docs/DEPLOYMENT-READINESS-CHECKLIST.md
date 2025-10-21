# Deployment Readiness Checklist

**Project**: SPEK Platform v2 + Atlantis UI
**Phase**: Week 26 Final Deployment
**Date**: 2025-10-11

---

## Pre-Deployment Validation

### 1. Backend (Flask + Claude Code)

- [ ] All 12 REST endpoints tested
- [ ] WebSocket connection stable (5 event types)
- [ ] Message queue system working
- [ ] Queen orchestrator processes requests correctly
- [ ] Agent registry returns correct Drones
- [ ] Existing project handling verified (no copying)
- [ ] Error handling for all endpoints
- [ ] Logging enabled

**Test Command**:
```bash
python claude_backend_server.py
```

---

### 2. Frontend (Atlantis UI)

- [ ] Production build successful
- [ ] Zero TypeScript errors
- [ ] Bundle size acceptable
- [ ] All 54 components rendering
- [ ] MonarchChat WebSocket listeners working
- [ ] Folder selection UI functional

**Test Command**:
```bash
cd atlantis-ui && npm run build
```

---

### 3. E2E Testing

- [ ] Create new project → Success
- [ ] Load existing project → Success (no copying)
- [ ] Send chat message → Queen responds
- [ ] Agent spawn → UI updates
- [ ] Task progress → UI shows progress
- [ ] Task completion → UI shows result
- [ ] Error handling → UI shows errors

---

## Environment Configuration

### Environment Variables (.env)

```bash
FLASK_PORT=5000
FLASK_DEBUG=false
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CLAUDE_API_KEY=[your-key]
```

- [ ] All environment variables set
- [ ] Secrets not committed to git
- [ ] Production values configured

---

## Performance Validation

| Metric | Target | Status |
|--------|--------|--------|
| Message latency | <50ms | [ ] |
| Queen response time | <2s | [ ] |
| WebSocket delay | <100ms | [ ] |
| File list handling | No copy | [x] |
| Bundle size | <10 MB | [ ] |

---

## Security Validation

- [ ] No secrets in codebase
- [ ] CORS configured correctly
- [ ] Input validation on all endpoints
- [ ] XSS prevention in UI
- [ ] Rate limiting enabled

**Commands**:
```bash
npm audit
pip check
```

---

## Deployment Steps

### 1. Backend Deployment

```bash
python claude_backend_server.py
```

- [ ] Backend deployed
- [ ] Health check passing
- [ ] Logs accessible

### 2. Frontend Deployment

```bash
cd atlantis-ui && vercel deploy --prod
```

- [ ] Frontend deployed
- [ ] Build successful
- [ ] Site accessible

### 3. Post-Deployment Validation

- [ ] Visit production URL
- [ ] Select existing project
- [ ] Send chat message
- [ ] Verify agent spawns
- [ ] Monitor logs for errors

---

## Rollback Plan

1. **Revert to Previous Version**
   ```bash
   git revert HEAD && git push
   ```

2. **Restart Services**
   ```bash
   sudo systemctl restart spek-backend
   ```

- [ ] Rollback procedure documented
- [ ] Rollback tested in staging

---

## Final Sign-Off

- [ ] All E2E tests passing
- [ ] Performance targets met
- [ ] Security scan passed
- [ ] Environment configured
- [ ] Monitoring enabled
- [ ] Rollback tested
- [ ] User documentation updated

---

**Status**: Pre-Production
**Next Step**: Execute E2E testing → Deploy to staging → Production launch

**Target Date**: Week 26 (2025-10-11 - 2025-10-18)
