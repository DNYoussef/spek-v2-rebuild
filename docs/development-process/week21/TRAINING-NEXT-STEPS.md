# DSPy Training - Next Steps

## Current Status

✅ **All infrastructure ready for training**:
- DSPy installed (v3.0.3)
- Training script created and tested
- 300 training examples ready
- 30 curated top demos ready
- API key provided

⚠️ **API Access Issue**: Generative Language API needs to be enabled

## Error Encountered

```
litellm.BadRequestError: VertexAIException BadRequestError
Error code: 403
Message: "Generative Language API has not been used in project 757233410069 before or it is disabled."
```

## Required Action

### Enable Generative Language API

**URL**: https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview?project=757233410069

**Steps**:
1. Visit the URL above
2. Click "Enable API"
3. Wait 2-5 minutes for propagation
4. Retry training command

## Alternative: Use Different LLM

If Gemini API continues having issues, we can use alternative LLMs:

### Option 1: Claude (Anthropic)

```python
# In scripts/train_dspy_optimizers.py, line 256
dspy.configure(lm=dspy.LM("anthropic/claude-3-5-sonnet-20241022"))
```

**Pros**: Fast, high-quality, you're already using Claude
**Cons**: Paid API (but cheap for training: ~$0.50 total)

### Option 2: OpenAI GPT-4o

```python
# In scripts/train_dspy_optimizers.py, line 256
dspy.configure(lm=dspy.LM("openai/gpt-4o"))
```

**Pros**: Fast, reliable
**Cons**: Paid API (~$1.00 total for training)

### Option 3: Local Ollama (Free)

```python
# In scripts/train_dspy_optimizers.py, line 256
dspy.configure(lm=dspy.LM("ollama/qwen2.5-coder:32b"))
```

**Pros**: Free, no API limits
**Cons**: Requires Ollama installed, slower

## Training Command

Once API is enabled (or alternative LLM configured):

```bash
# Set API key (if using Gemini)
export GEMINI_API_KEY='AIzaSyD9e1wOv39ZyHlruGgzM_i0BaZBdU-jTfg'

# OR set Claude key
export ANTHROPIC_API_KEY='your-claude-key'

# OR set OpenAI key
export OPENAI_API_KEY='your-openai-key'

# Run training
cd C:\Users\17175\Desktop\spek-v2-rebuild
python scripts/train_dspy_optimizers.py
```

## Expected Output

**Duration**: 15-90 minutes total (5-30 min per optimizer)

**Files Created**:
- `models/dspy/queen_to_princess_dev.json` (~50KB)
- `models/dspy/queen_to_princess_quality.json` (~50KB)
- `models/dspy/queen_to_princess_coordination.json` (~50KB)

**Training Summary**:
```
================================================================================
Training Summary
================================================================================
Development          ✅ SUCCESS
Quality              ✅ SUCCESS
Coordination         ✅ SUCCESS
```

## What Happens Next (Post-Training)

### Phase 2: Integration

1. **Update AgentBase.delegate_task()**:
   - Load optimizers in `__init__()`
   - Inject optimization before `protocol.send_task()`
   - Add fallback to baseline prompts

2. **Add Latency Monitoring**:
   - Track DSPy call duration
   - Alert if >250ms (p95)
   - Log to monitoring system

3. **Create Integration Tests**:
   - Test Queen→Princess-Dev delegation
   - Test Queen→Princess-Quality delegation
   - Test Queen→Princess-Coordination delegation
   - Validate latency <250ms
   - Validate quality improvement

### Phase 3: Validation (Week 21 Day 7)

1. Run 100 end-to-end workflows
2. Measure quality vs baseline
3. Generate metrics report

## Troubleshooting

### If Gemini API Continues Failing

**Recommendation**: Switch to Claude (you're already using it):

1. Edit `scripts/train_dspy_optimizers.py` line 256:
   ```python
   dspy.configure(lm=dspy.LM("anthropic/claude-3-5-sonnet-20241022"))
   ```

2. Set API key:
   ```bash
   export ANTHROPIC_API_KEY='your-key'
   ```

3. Retry training

**Cost**: ~$0.50 for 3 optimizers (100 examples × 3 rounds × 3 optimizers ≈ 900 LLM calls)

---

**Version**: 1.0
**Date**: 2025-10-10
**Status**: Waiting for API enablement or LLM switch
**Next Action**: Enable Generative Language API OR switch to Claude/GPT-4o
