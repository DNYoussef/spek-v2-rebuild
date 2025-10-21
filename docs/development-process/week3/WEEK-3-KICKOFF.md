# Week 3 Kickoff - Core System Implementation

**Week**: 3 of 26 (updated from 24 to 26 weeks)
**Date**: 2025-10-08
**Phase**: Core System Foundation
**Status**: 🚀 STARTING

---

## 📋 Week 3 Objectives

**Primary Goal**: Implement core system architecture that serves as foundation for both v6 agent system AND v8 Atlantis UI.

**Key Deliverables**:
1. AgentContract interface (unified agent API)
2. EnhancedLightweightProtocol (<100ms coordination)
3. GovernanceDecisionEngine (Constitution vs SPEK rules)
4. Platform Abstraction Layer (Gemini/Claude failover)

---

## 🎯 Success Criteria

### AgentContract Interface
- ✅ All 22 agents implement unified interface
- ✅ TypeScript strict mode compliance
- ✅ Validation logic (<5ms per task)
- ✅ Metadata extensibility
- ✅ Error handling standardized

### EnhancedLightweightProtocol
- ✅ Direct task assignment (no A2A overhead)
- ✅ <100ms coordination latency
- ✅ Optional health checks (lightweight)
- ✅ Optional task tracking (opt-in)
- ✅ Message serialization (<1KB)

### GovernanceDecisionEngine
- ✅ Constitution.md integration
- ✅ SPEK rules integration
- ✅ Automated conflict resolution
- ✅ Decision logging (audit trail)
- ✅ <50ms decision latency

### Platform Abstraction Layer
- ✅ Gemini API integration
- ✅ Claude API integration
- ✅ Automatic failover (<500ms)
- ✅ Rate limiting (per-provider)
- ✅ Cost tracking (per-request)

---

## 📅 Day-by-Day Breakdown

### Day 1: AgentContract Interface
**Objective**: Define and implement unified agent interface

**Tasks**:
1. Create `src/core/AgentContract.ts` (TypeScript interface)
2. Create `src/core/AgentBase.ts` (abstract base class)
3. Create `src/core/AgentMetadata.ts` (metadata structure)
4. Create test: `tests/unit/test_agent_contract.py`
5. Documentation: Interface specification

**Acceptance Criteria**:
- Interface compiles with TypeScript strict mode
- All 22 agents can implement interface
- Validation logic <5ms
- 100% test coverage for base class

---

### Day 2-3: EnhancedLightweightProtocol
**Objective**: Implement lightweight agent coordination protocol

**Tasks (Day 2)**:
1. Create `src/protocols/EnhancedLightweightProtocol.ts`
2. Message serialization (JSON with compression)
3. Direct task assignment (no queue overhead)
4. Latency monitoring (<100ms target)

**Tasks (Day 3)**:
5. Optional health checks (configurable)
6. Optional task tracking (opt-in debugging)
7. Error handling (retry logic, circuit breaker)
8. Create test: `tests/unit/test_enhanced_protocol.py`

**Acceptance Criteria**:
- <100ms coordination latency (p95)
- <1KB message size (compressed)
- Zero message loss (with retries)
- Graceful degradation on errors

---

### Day 4-5: GovernanceDecisionEngine
**Objective**: Automated decision resolution system

**Tasks (Day 4)**:
1. Create `src/governance/GovernanceDecisionEngine.ts`
2. Constitution.md parser
3. SPEK rules parser
4. Decision matrix logic

**Tasks (Day 5)**:
5. Conflict resolution algorithm
6. Decision logging (SQLite audit trail)
7. FSM decision matrix integration
8. Create test: `tests/unit/test_governance_engine.py`

**Acceptance Criteria**:
- <50ms decision latency
- 100% rule coverage (Constitution + SPEK)
- Audit trail for all decisions
- FSM decision matrix enforced

---

## 🏗️ Technical Architecture

### Directory Structure
```
src/
├── core/
│   ├── AgentContract.ts       # Interface definition
│   ├── AgentBase.ts            # Abstract base class
│   ├── AgentMetadata.ts        # Metadata structure
│   └── __init__.py
├── protocols/
│   ├── EnhancedLightweightProtocol.ts
│   ├── MessageSerializer.ts
│   └── __init__.py
├── governance/
│   ├── GovernanceDecisionEngine.ts
│   ├── ConstitutionParser.ts
│   ├── SPEKRulesParser.ts
│   └── __init__.py
└── platform/
    ├── PlatformAbstraction.ts
    ├── GeminiProvider.ts
    ├── ClaudeProvider.ts
    └── __init__.py
```

---

## 📊 Performance Targets

| Component | Target | Measurement |
|-----------|--------|-------------|
| **AgentContract validation** | <5ms | Per task validation |
| **Protocol coordination** | <100ms | Task assignment latency |
| **Governance decision** | <50ms | Decision resolution |
| **Platform failover** | <500ms | Provider switch time |
| **Message serialization** | <1KB | Compressed JSON |

---

## 🔗 Integration Points

### v6 Core System
- AgentContract → 22 agents (Phase 1)
- EnhancedLightweightProtocol → Queen/Princess/Drone communication
- GovernanceDecisionEngine → FSM decision matrix

### v8 Atlantis UI
- AgentContract → Agent metadata API (`/api/agents/metadata`)
- EnhancedLightweightProtocol → WebSocket event stream
- GovernanceDecisionEngine → Real-time decision display

---

## 🧪 Testing Strategy

### Unit Tests (60 tests)
- `test_agent_contract.py` (15 tests)
  - Interface compliance
  - Validation logic
  - Metadata extensibility
  - Error handling

- `test_enhanced_protocol.py` (20 tests)
  - Message serialization
  - Latency measurement
  - Retry logic
  - Circuit breaker

- `test_governance_engine.py` (15 tests)
  - Constitution parsing
  - SPEK rules parsing
  - Decision resolution
  - Audit logging

- `test_platform_abstraction.py` (10 tests)
  - Gemini integration
  - Claude integration
  - Failover logic
  - Cost tracking

### Integration Tests (10 tests)
- End-to-end agent task flow
- Multi-agent coordination
- Governance + protocol integration
- Platform failover under load

---

## 📈 Success Metrics

**Week 3 Progress**: 0% → 100%

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Components Created** | 12 | 0 | 0% ⏳ |
| **Unit Tests** | 60 | 0 | 0% ⏳ |
| **Integration Tests** | 10 | 0 | 0% ⏳ |
| **Performance Validated** | 5 targets | 0 | 0% ⏳ |
| **Documentation** | 4 specs | 0 | 0% ⏳ |

---

## 🚧 Known Challenges

### Challenge 1: TypeScript + Python Integration
- **Issue**: AgentContract in TypeScript, agents in Python
- **Solution**: Use JSON schema validation, generate Python types from TS
- **Timeline**: Day 1

### Challenge 2: Protocol Latency
- **Issue**: <100ms target may be tight with network overhead
- **Solution**: Local-first design, WebSocket for remote, measure p95 not p50
- **Timeline**: Day 2-3

### Challenge 3: Governance Rule Complexity
- **Issue**: Constitution + SPEK may have conflicting rules
- **Solution**: Clear precedence hierarchy (Constitution > SPEK), explicit conflict resolution
- **Timeline**: Day 4-5

---

## 🎨 Visual Design (Atlantis UI)

**Week 3 UI Preview** (implemented in Week 5-6):
- `/dashboard` page will show:
  - AgentContract metadata cards (22 agents)
  - Protocol latency gauge (<100ms real-time)
  - Governance decision log (audit trail)
  - Platform status (Gemini/Claude health)

---

## 📝 Documentation Deliverables

1. **AgentContract Specification** (`docs/specs/AgentContract.md`)
   - Interface definition
   - Validation rules
   - Error handling
   - Usage examples

2. **EnhancedLightweightProtocol Specification** (`docs/specs/EnhancedLightweightProtocol.md`)
   - Message format
   - Latency targets
   - Retry logic
   - Circuit breaker patterns

3. **GovernanceDecisionEngine Specification** (`docs/specs/GovernanceDecisionEngine.md`)
   - Decision matrix
   - Constitution parsing
   - SPEK rules integration
   - Audit trail format

4. **Platform Abstraction Specification** (`docs/specs/PlatformAbstraction.md`)
   - Provider interfaces
   - Failover strategy
   - Cost tracking
   - Rate limiting

---

## 🚀 Next Steps (Week 4)

**Week 4 Preview**: Atlantis Backend + Critical Gates (NON-NEGOTIABLE)
- tRPC API routes (9 pages)
- WebSocket server with Redis adapter (CRITICAL)
- Project vectorization with parallel processing (CRITICAL)
- Docker sandbox with resource limits (CRITICAL)

**Week 4 is CRITICAL**: All 3 non-negotiables MUST complete or Week 5+ blocks.

---

**Prepared By**: Claude Sonnet 4
**Date**: 2025-10-08
**Status**: Week 3 Ready to Begin
**Next Review**: End of Week 3 (Core System Audit)
