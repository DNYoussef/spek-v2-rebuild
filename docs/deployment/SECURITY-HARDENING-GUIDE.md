# Security Hardening Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Compliance**: OWASP Top 10, CWE Top 25, NIST Cybersecurity Framework

---

## Overview

This guide provides comprehensive security hardening steps for SPEK Platform v2 + Atlantis UI production deployment. Follow this guide to ensure the application meets security best practices and industry standards.

---

## Security Checklist Quick Reference

| Category | Items | Status |
|----------|-------|--------|
| **Application Security** | 12 items | □ |
| **Infrastructure Security** | 8 items | □ |
| **Data Security** | 6 items | □ |
| **Network Security** | 5 items | □ |
| **Access Control** | 7 items | □ |
| **Monitoring & Logging** | 5 items | □ |

---

## 1. Application Security 🛡️

### 1.1 Security Headers

**Configure all security headers in production**:

```typescript
// atlantis-ui/next.config.ts (already configured in Week 21)
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'X-DNS-Prefetch-Control',
          value: 'on'
        },
        {
          key: 'X-Frame-Options',
          value: 'SAMEORIGIN'  // Prevents clickjacking
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff'  // Prevents MIME sniffing
        },
        {
          key: 'X-XSS-Protection',
          value: '1; mode=block'  // XSS protection (legacy browsers)
        },
        {
          key: 'Referrer-Policy',
          value: 'strict-origin-when-cross-origin'
        },
        {
          key: 'Permissions-Policy',
          value: 'camera=(), microphone=(), geolocation=()'
        },
        {
          key: 'Strict-Transport-Security',
          value: 'max-age=31536000; includeSubDomains; preload'
        },
        {
          key: 'Content-Security-Policy',
          value: [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  // Adjust based on needs
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' https://api.spek.platform",
            "frame-ancestors 'none'"
          ].join('; ')
        }
      ]
    }
  ];
}
```

**Checklist**:
- [ ] X-Frame-Options configured (prevents clickjacking)
- [ ] X-Content-Type-Options configured (prevents MIME sniffing)
- [ ] Strict-Transport-Security configured (enforces HTTPS)
- [ ] Content-Security-Policy configured (prevents XSS)
- [ ] Referrer-Policy configured (protects user privacy)
- [ ] Permissions-Policy configured (limits browser features)

---

### 1.2 Input Validation & Sanitization

**Validate all user inputs**:

```typescript
// Example: Input validation middleware
import { z } from 'zod';

const UserInputSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email(),
  message: z.string().max(500)
});

export function validateUserInput(data: unknown) {
  return UserInputSchema.parse(data);  // Throws if invalid
}
```

**Checklist**:
- [ ] All user inputs validated on server-side
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitize HTML inputs)
- [ ] Path traversal prevention (validate file paths)
- [ ] Command injection prevention (avoid shell commands)
- [ ] LDAP injection prevention (escape special chars)

---

### 1.3 Authentication & Session Management

**Secure authentication implementation**:

```typescript
// JWT token configuration
const JWT_CONFIG = {
  secret: process.env.JWT_SECRET,  // 256-bit key minimum
  expiresIn: '24h',  // Short-lived tokens
  algorithm: 'HS256',
  issuer: 'spek-platform',
  audience: 'spek-platform-users'
};

// Session configuration
const SESSION_CONFIG = {
  secret: process.env.SESSION_SECRET,
  name: 'spek.sid',
  cookie: {
    httpOnly: true,  // Prevents JavaScript access
    secure: true,  // HTTPS only
    sameSite: 'strict',  // CSRF protection
    maxAge: 24 * 60 * 60 * 1000  // 24 hours
  }
};
```

**Checklist**:
- [ ] Strong password policy (min 12 chars, complexity requirements)
- [ ] Password hashing with bcrypt (cost factor ≥12)
- [ ] JWT tokens with short expiration (<24h)
- [ ] Refresh token rotation
- [ ] Session invalidation on logout
- [ ] Multi-factor authentication (MFA) supported
- [ ] Account lockout after failed attempts

---

### 1.4 API Security

**Secure API endpoints**:

```typescript
// Rate limiting middleware
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,  // 100 requests per window
  message: 'Too many requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

// Apply to all API routes
app.use('/api/', apiLimiter);
```

**Checklist**:
- [ ] Rate limiting configured (100 req/15min)
- [ ] API authentication required (JWT/API keys)
- [ ] Input validation on all endpoints
- [ ] Output encoding (prevent XSS)
- [ ] CORS configured (whitelist origins)
- [ ] Request size limits (prevent DoS)

---

### 1.5 Dependency Security

**Keep dependencies secure and up-to-date**:

```bash
# Run security audits
npm audit --production
pip-audit

# Fix vulnerabilities
npm audit fix
pip install --upgrade <package>

# Check for outdated packages
npm outdated
pip list --outdated
```

**Checklist**:
- [ ] No critical vulnerabilities (npm audit, pip-audit)
- [ ] Dependencies updated monthly
- [ ] Security advisories monitored (GitHub Dependabot)
- [ ] Lock files committed (package-lock.json, requirements.txt)
- [ ] Unused dependencies removed

---

## 2. Infrastructure Security 🏗️

### 2.1 Server Hardening

**Secure server configuration**:

```yaml
# Example: Kubernetes security context
securityContext:
  runAsNonRoot: true  # Never run as root
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
      - ALL  # Drop all Linux capabilities
    add:
      - NET_BIND_SERVICE  # Only add what's needed
  readOnlyRootFilesystem: true  # Immutable container
```

**Checklist**:
- [ ] Containers run as non-root user
- [ ] Read-only root filesystem
- [ ] Minimal base image (Alpine, distroless)
- [ ] No unnecessary packages installed
- [ ] Firewall configured (allow only required ports)
- [ ] SSH disabled or key-only authentication
- [ ] Security patches applied automatically

---

### 2.2 Network Segmentation

**Isolate services by network**:

```yaml
# Example: Kubernetes network policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: spek-platform-network-policy
spec:
  podSelector:
    matchLabels:
      app: spek-platform
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nginx-ingress
      ports:
        - protocol: TCP
          port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

**Checklist**:
- [ ] Network policies configured
- [ ] Database not publicly accessible
- [ ] Internal services isolated
- [ ] DMZ for public-facing services
- [ ] VPN for remote access

---

### 2.3 TLS/SSL Configuration

**Enforce strong encryption**:

```nginx
# Nginx TLS configuration
ssl_protocols TLSv1.2 TLSv1.3;  # Only modern protocols
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;

# HSTS header
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
```

**Checklist**:
- [ ] TLS 1.2+ enforced (TLS 1.0/1.1 disabled)
- [ ] Strong cipher suites configured
- [ ] Valid SSL certificate (not self-signed)
- [ ] Certificate auto-renewal configured
- [ ] HSTS header enabled

---

## 3. Data Security 🔐

### 3.1 Encryption at Rest

**Encrypt sensitive data**:

```python
# Example: Encrypt sensitive fields
from cryptography.fernet import Fernet
import os

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()
```

**Checklist**:
- [ ] Database encryption enabled (TDE/encryption at rest)
- [ ] File system encryption (LUKS, BitLocker)
- [ ] Backup encryption enabled
- [ ] Encryption keys rotated annually
- [ ] Key management service (KMS) used

---

### 3.2 Secrets Management

**Never hardcode secrets**:

```bash
# Use environment variables
export DATABASE_URL="postgresql://..."
export JWT_SECRET="..."
export API_KEY="..."

# Or use secrets management service
aws secretsmanager get-secret-value --secret-id prod/spek/database
```

**Checklist**:
- [ ] No secrets in code (use environment variables)
- [ ] Secrets stored in vault (AWS Secrets Manager, Azure Key Vault)
- [ ] Secret rotation policy (quarterly)
- [ ] `.env` files in `.gitignore`
- [ ] Secrets encrypted in transit and at rest

---

### 3.3 Data Retention & Deletion

**Implement data lifecycle policies**:

```sql
-- Example: Automatic data deletion
DELETE FROM logs
WHERE created_at < NOW() - INTERVAL '90 days';

DELETE FROM sessions
WHERE expires_at < NOW();
```

**Checklist**:
- [ ] Data retention policy documented (30-90 days)
- [ ] Automated data deletion configured
- [ ] Secure data deletion (overwrite, not just delete)
- [ ] PII anonymization before deletion
- [ ] Backup retention policy (30 days)

---

## 4. Network Security 🌐

### 4.1 Firewall Configuration

**Restrict network access**:

```bash
# UFW firewall rules (Ubuntu)
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH (key-only)
ufw allow 80/tcp   # HTTP (redirect to HTTPS)
ufw allow 443/tcp  # HTTPS
ufw enable
```

**Checklist**:
- [ ] Default deny incoming
- [ ] Allow only required ports
- [ ] SSH restricted to specific IPs
- [ ] Database ports not publicly accessible
- [ ] Firewall logs enabled

---

### 4.2 DDoS Protection

**Prevent denial of service**:

```nginx
# Nginx rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
limit_req_status 429;
```

**Checklist**:
- [ ] Rate limiting configured
- [ ] CDN with DDoS protection (Cloudflare, AWS Shield)
- [ ] Connection limits set
- [ ] Request size limits enforced
- [ ] SYN flood protection enabled

---

### 4.3 VPN & Private Networks

**Secure remote access**:

**Checklist**:
- [ ] VPN required for database access
- [ ] Admin panel requires VPN
- [ ] Private subnets for internal services
- [ ] Bastion host for SSH access
- [ ] IP whitelisting for sensitive operations

---

## 5. Access Control 🔑

### 5.1 Role-Based Access Control (RBAC)

**Implement least privilege**:

```typescript
// Example: RBAC implementation
enum Role {
  ADMIN = 'admin',
  DEVELOPER = 'developer',
  VIEWER = 'viewer'
}

const permissions = {
  [Role.ADMIN]: ['read', 'write', 'delete', 'deploy'],
  [Role.DEVELOPER]: ['read', 'write'],
  [Role.VIEWER]: ['read']
};

function hasPermission(user: User, action: string): boolean {
  return permissions[user.role]?.includes(action) ?? false;
}
```

**Checklist**:
- [ ] RBAC implemented (admin, developer, viewer)
- [ ] Least privilege principle enforced
- [ ] Service accounts have minimal permissions
- [ ] Regular access review (quarterly)
- [ ] Separation of duties enforced

---

### 5.2 Multi-Factor Authentication

**Require MFA for sensitive operations**:

**Checklist**:
- [ ] MFA required for admin accounts
- [ ] MFA required for production access
- [ ] TOTP-based MFA (Google Authenticator, Authy)
- [ ] Backup codes generated
- [ ] MFA recovery process documented

---

## 6. Monitoring & Logging 📊

### 6.1 Security Logging

**Log all security events**:

```typescript
// Example: Security event logging
function logSecurityEvent(event: SecurityEvent) {
  logger.warn('Security Event', {
    type: event.type,  // 'login_failed', 'unauthorized_access', etc.
    user: event.user,
    ip: event.ip,
    timestamp: new Date().toISOString(),
    details: event.details
  });

  // Alert for critical events
  if (event.type === 'unauthorized_access') {
    alerting.send({
      severity: 'high',
      message: `Unauthorized access attempt by ${event.user}`
    });
  }
}
```

**Checklist**:
- [ ] All authentication events logged
- [ ] Failed login attempts logged
- [ ] Unauthorized access attempts logged
- [ ] Configuration changes logged
- [ ] PII scrubbed from logs
- [ ] Logs shipped to SIEM (Security Information and Event Management)

---

### 6.2 Intrusion Detection

**Monitor for suspicious activity**:

**Checklist**:
- [ ] IDS/IPS configured (Snort, Suricata)
- [ ] Failed login threshold alerting (5 attempts)
- [ ] Unusual traffic patterns detected
- [ ] Port scanning detected
- [ ] Malware scanning enabled

---

## 7. Incident Response 🚨

### 7.1 Incident Response Plan

**Prepare for security incidents**:

**Steps**:
1. **Detection**: Monitor alerts, logs, user reports
2. **Containment**: Isolate affected systems, block IPs
3. **Eradication**: Remove malware, patch vulnerabilities
4. **Recovery**: Restore from backups, verify integrity
5. **Post-Incident**: Document, analyze root cause, improve

**Checklist**:
- [ ] Incident response plan documented
- [ ] Incident response team identified
- [ ] Contact list maintained (security team, legal, PR)
- [ ] Incident playbooks created (data breach, DDoS, ransomware)
- [ ] Quarterly incident response drills

---

### 7.2 Security Breach Response

**If security breach detected**:

```bash
# 1. Immediate containment
# - Block malicious IPs
ufw deny from <malicious-ip>

# - Isolate affected systems
kubectl drain <node-name>

# 2. Evidence collection
# - Preserve logs
kubectl logs <pod-name> > incident-logs-$(date +%Y%m%d).txt

# - Take snapshots
aws ec2 create-snapshot --volume-id <vol-id>

# 3. Notification
# - Notify security team
# - Notify legal (if data breach)
# - Notify users (if required by law)
```

**Checklist**:
- [ ] Incident declared within 1 hour
- [ ] Containment actions taken within 2 hours
- [ ] Evidence preserved
- [ ] Stakeholders notified (security, legal, management)
- [ ] Users notified (if required, within 72 hours per GDPR)

---

## 8. Compliance 📋

### 8.1 OWASP Top 10 Mitigation

**Ensure protection against OWASP Top 10**:

1. **Broken Access Control**: RBAC implemented ✅
2. **Cryptographic Failures**: Encryption at rest/transit ✅
3. **Injection**: Input validation, parameterized queries ✅
4. **Insecure Design**: Threat modeling performed ✅
5. **Security Misconfiguration**: Security hardening applied ✅
6. **Vulnerable Components**: Dependency scanning automated ✅
7. **Authentication Failures**: MFA, strong passwords ✅
8. **Data Integrity Failures**: HMAC, digital signatures ✅
9. **Logging Failures**: Comprehensive logging ✅
10. **SSRF**: Input validation, network segmentation ✅

---

### 8.2 Regulatory Compliance

**Ensure compliance with regulations**:

**GDPR (if applicable)**:
- [ ] Privacy policy published
- [ ] Cookie consent implemented
- [ ] Right to deletion implemented
- [ ] Data portability implemented
- [ ] Data breach notification process (<72 hours)

**HIPAA (if applicable)**:
- [ ] PHI encryption at rest and in transit
- [ ] Access controls implemented
- [ ] Audit trails maintained
- [ ] Business Associate Agreements (BAAs) signed

**SOC 2 (if applicable)**:
- [ ] Security controls documented
- [ ] Audit trail maintained
- [ ] Third-party audit completed

---

## 9. Security Testing 🧪

### 9.1 Automated Security Scanning

**Run security scans regularly**:

```bash
# 1. Static code analysis
bandit -r src/
semgrep --config auto src/

# 2. Dependency scanning
npm audit --production
pip-audit

# 3. Container scanning
trivy image spek-platform:latest

# 4. Secret scanning
gitleaks detect --source . --verbose
```

**Checklist**:
- [ ] SAST (Static Application Security Testing) in CI/CD
- [ ] DAST (Dynamic Application Security Testing) monthly
- [ ] Dependency scanning daily
- [ ] Container scanning on every build
- [ ] Secret scanning on every commit

---

### 9.2 Penetration Testing

**Perform regular penetration testing**:

**Checklist**:
- [ ] Penetration test performed annually
- [ ] Vulnerability assessment quarterly
- [ ] Bug bounty program considered
- [ ] Findings remediated within SLA (Critical: 7 days, High: 30 days)

---

## 10. Security Maintenance 🔧

### 10.1 Regular Updates

**Keep system updated**:

```bash
# Update packages
apt update && apt upgrade -y  # Ubuntu/Debian
yum update -y  # CentOS/RHEL

# Update Docker images
docker pull <image>:<tag>

# Update Kubernetes
kubectl version  # Check version
# Follow upgrade guide
```

**Checklist**:
- [ ] Security patches applied within 7 days
- [ ] OS updates monthly
- [ ] Dependency updates monthly
- [ ] Reboot schedule for kernel updates

---

### 10.2 Security Review

**Conduct regular security reviews**:

**Checklist**:
- [ ] Monthly security review meeting
- [ ] Quarterly vulnerability assessment
- [ ] Annual penetration test
- [ ] Continuous security training for team

---

## Security Checklist Summary

### Critical (Must Complete Before Production)

- [ ] All security headers configured
- [ ] HTTPS enforced with valid certificate
- [ ] Input validation on all endpoints
- [ ] Authentication & authorization implemented
- [ ] Secrets stored in vault (not hardcoded)
- [ ] Encryption at rest enabled
- [ ] Security scanning in CI/CD
- [ ] Monitoring & alerting configured
- [ ] Incident response plan documented

### Important (Complete Within 30 Days)

- [ ] Penetration testing performed
- [ ] Security training completed
- [ ] Compliance review completed (GDPR, etc.)
- [ ] Third-party audits scheduled
- [ ] Bug bounty program launched

### Ongoing (Continuous Improvement)

- [ ] Monthly security reviews
- [ ] Quarterly vulnerability assessments
- [ ] Annual penetration testing
- [ ] Continuous dependency updates
- [ ] Security awareness training

---

## Resources

**Tools**:
- OWASP ZAP (penetration testing)
- Burp Suite (web security testing)
- Trivy (container scanning)
- Bandit (Python security linter)
- Semgrep (SAST)

**References**:
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

---

**Version**: 1.0.0
**Last Updated**: 2025-10-10
**Next Review**: 2025-11-10
