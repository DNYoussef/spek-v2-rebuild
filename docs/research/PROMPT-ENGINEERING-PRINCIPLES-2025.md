# Prompt Engineering Principles 2025: Research Summary

**Date**: 2025-10-10
**Sources**: Anthropic, OpenAI, Google, Microsoft, Lakera, PromptingGuide.ai
**Status**: ✅ **COMPREHENSIVE RESEARCH COMPLETE**

---

## Executive Summary

**2025 State of Prompt Engineering**: Models like Claude 4, GPT-4o, and Gemini 2.5 Pro have evolved significantly, requiring model-specific approaches. **No universal best practice exists**—different models respond better to different formatting patterns.

**Key Finding**: **Specificity trumps brevity, context drives relevance, format specification improves usability, persona assignment guides tone and depth, and iterative refinement enhances initial outputs.**

**Critical Insight**: Clear structure and context matter more than clever wording—most prompt failures come from ambiguity, not model limitations.

---

## Universal Principles (All LLMs)

### 1. **Clarity & Specificity**
- Be explicit about desired output format
- Use concrete examples over abstract descriptions
- Specify constraints numerically ("3 bullets", "<50 words")

### 2. **Context Engineering**
- Provide all necessary background information
- Include relevant domain knowledge
- Reference specific frameworks or methodologies

### 3. **Output Format Specification**
- Define desired structure explicitly (JSON, XML, Markdown)
- Use formatting hints ("in JSON", "as a table")
- Specify length constraints

### 4. **Persona Assignment**
- Assign expert roles ("You are an expert software architect...")
- Guide tone and depth through persona
- Use domain-specific language

### 5. **Iterative Refinement**
- Test prompts systematically
- A/B test variations
- Continuously improve based on results

---

## Model-Specific Techniques

### Claude 4 (Anthropic)

**Primary Technique**: **XML Tag Structure**
```xml
<document>
  {LONG_CONTEXT}
</document>

<instruction>
  {TASK_DESCRIPTION}
</instruction>

<examples>
  <example>
    <input>{INPUT_1}</input>
    <output>{OUTPUT_1}</output>
  </example>
</examples>
```

**Best Practices**:
1. **XML Tags**: Use XML tags for structured prompts (Claude parses them accurately)
2. **Document Placement**: Put long documents **BEFORE** instructions (top of prompt)
3. **Chain-of-Thought**: Use "Let's think step by step" or "Think through this carefully"
4. **Boundary Definition**: Claude over-explains unless boundaries are clearly defined
5. **Explicit Goals**: State explicit goals and tone cues

**Example Claude 4 Prompt**:
```xml
<system>
You are an expert Python developer with 10+ years of experience.
You write clean, maintainable code following PEP 8 standards.
</system>

<document>
{CODE_TO_REVIEW}
</document>

<instruction>
Review the code above and identify:
1. Security vulnerabilities
2. Performance issues
3. Code quality problems

For each issue:
- Describe the problem clearly
- Explain why it's problematic
- Provide a specific fix

Output format: JSON with keys "issues" (array)
</instruction>

<examples>
  <example>
    <input>def login(user, pwd): return user == pwd</input>
    <output>
    {
      "issues": [
        {
          "type": "security",
          "severity": "critical",
          "description": "Plain text password comparison",
          "fix": "Use bcrypt.checkpw(pwd.encode(), user.password_hash)"
        }
      ]
    }
    </output>
  </example>
</examples>
```

---

### GPT-4/GPT-4o (OpenAI)

**Primary Technique**: **Six-Strategy Framework**

1. **Write Clear Instructions**:
   - Include details in queries
   - Ask model to adopt a persona
   - Use delimiters (```, """, <>) to separate sections
   - Specify steps required
   - Provide examples
   - Specify desired output length

2. **Provide Reference Text**:
   - Instruct model to answer using reference text
   - Instruct model to cite quotes from reference

3. **Split Complex Tasks**:
   - Use intent classification
   - For long conversations, summarize previous dialogue
   - Summarize long documents piecewise

4. **Give Models Time to "Think"**:
   - Instruct model to work out own solution before concluding
   - Use inner monologue or sequence of queries
   - Ask if model missed anything on previous passes

5. **Use External Tools**:
   - Use embeddings-based search (RAG)
   - Use code execution for calculations
   - Give model access to specific functions

6. **Test Changes Systematically**:
   - Evaluate outputs with reference to gold-standard answers
   - A/B test variations

**GPT-4o Strengths**:
- Crisp numeric constraints ("3 bullets", "<50 words")
- JSON formatting hints
- System prompts with clear role definition

**Example GPT-4o Prompt**:
```
### SYSTEM
You are a senior code reviewer at a top tech company.

### INSTRUCTIONS
1. Read the code below
2. Identify security vulnerabilities (max 5)
3. For each issue, provide:
   - Severity (critical/high/medium/low)
   - Description (1 sentence)
   - Fix (code snippet)

### OUTPUT FORMAT
Return JSON:
{
  "issues": [
    {
      "severity": "critical",
      "description": "...",
      "fix": "..."
    }
  ]
}

### CODE
{CODE_HERE}

### EXAMPLES
Input: def auth(u,p): return u==p
Output:
{
  "issues": [{
    "severity": "critical",
    "description": "Plain text password comparison",
    "fix": "Use bcrypt.checkpw(p.encode(), u.hash)"
  }]
}
```

---

### Gemini (Google)

**Primary Technique**: **PTCF Framework**

**P**ersona: Define expert role
**T**ask: Clear task description
**C**ontext: Provide background
**F**ormat: Specify output structure

**Best Practices**:
1. **Optimal Prompt Length**: ~21 words average for best results
2. **Hierarchy in Structure**: Use headings, numbered lists
3. **Stepwise Formatting**: Break tasks into steps
4. **Document Placement**: Experiment with top/bottom placement

**Example Gemini Prompt**:
```
# Persona
You are an expert security auditor.

# Task
Review this Python authentication code for vulnerabilities.

# Context
This code handles user login for a financial application.
Security is critical. We use bcrypt for passwords.

# Format
Return 3 issues max:
1. Issue: [description]
   Fix: [code snippet]

# Code
{CODE_HERE}
```

---

## Advanced Techniques (2025)

### 1. Chain-of-Thought (CoT) Prompting ⭐

**Purpose**: Guide model to reason step-by-step before answering

**Technique**: Add "Let's think step by step" or provide intermediate reasoning steps

**When to Use**:
- Math problems
- Logic puzzles
- Multi-step decision-making
- Complex analysis

**Example**:
```
Problem: Calculate ROI for a $50k investment returning $65k over 2 years.

Let's think step by step:
1. Calculate profit: $65k - $50k = $15k
2. Calculate ROI: ($15k / $50k) × 100 = 30%
3. Annualize: 30% / 2 years = 15% per year

Final answer: 30% total ROI, 15% annualized
```

**Best Practice**: Combine CoT with few-shot examples for complex tasks

---

### 2. Few-Shot Prompting ⭐

**Purpose**: Teach model desired output format and style through examples

**When to Use**:
- Output formatting matters
- Need to mimic specific tone/structure
- Math or calculation tasks
- Pattern recognition

**Example (3-shot)**:
```
Task: Convert user stories to acceptance criteria.

Example 1:
Story: As a user, I want to reset my password
Criteria:
- User can request reset via email
- Reset link expires after 1 hour
- User can set new password (8+ chars)

Example 2:
Story: As an admin, I want to view user activity logs
Criteria:
- Admin can filter logs by user/date
- Logs show timestamp, action, result
- Logs export to CSV

Example 3:
Story: As a developer, I want API rate limiting
Criteria:
- Rate limit: 1000 requests/hour per API key
- Return 429 status when limit exceeded
- Rate limit resets every hour

Now convert this story:
Story: As a customer, I want to save items to wishlist
Criteria:
```

**Best Practice**: Use 3-5 high-quality examples (not more)

---

### 3. Zero-Shot CoT (Most Powerful)

**Technique**: Combine zero-shot prompting with CoT reasoning

**Magic Phrase**: "Let's think step by step"

**Example**:
```
Question: If a store has 15 apples and sells 60% of them, how many are left?

Let's think step by step:
```

**Result**: Model automatically:
1. Calculates 60% of 15 = 9 apples sold
2. Subtracts 15 - 9 = 6 apples remaining
3. Returns final answer: 6 apples

---

### 4. Hybrid Prompting (2025 Technique)

**Purpose**: Blend multiple techniques for complex tasks

**Components**:
- Few-shot examples
- Role-based instructions
- Formatting constraints
- Chain-of-thought reasoning
- Output validation

**Example Hybrid Prompt**:
```xml
<system>
You are an expert software architect with 15+ years experience.
Your specialty is secure, scalable system design.
</system>

<instruction>
Design a user authentication system for a fintech app.

Think through this step by step:
1. Identify security requirements
2. Choose appropriate technologies
3. Design data flow
4. Identify potential vulnerabilities
5. Propose mitigations

Output format: Markdown with sections for each step.
Length: 200-300 words total.
</instruction>

<examples>
  <example>
    <task>Design a payment processing system</task>
    <output>
## Security Requirements
- PCI DSS compliance
- End-to-end encryption
- Fraud detection

## Technologies
- Stripe API (PCI-compliant)
- TLS 1.3 for transport
- Redis for rate limiting

## Data Flow
1. User submits payment -> Frontend
2. Frontend sends encrypted payload -> Backend
3. Backend validates -> Stripe API
4. Stripe processes -> Response to backend
5. Backend updates DB -> Response to frontend

## Vulnerabilities
- SQL injection in payment logs
- CSRF on payment endpoints
- Insufficient rate limiting

## Mitigations
- Parameterized queries
- CSRF tokens + SameSite cookies
- Rate limit: 5 payments/min per user
    </output>
  </example>
</examples>

<task>
{YOUR_TASK_HERE}
</task>
```

---

## 26 Prompt Engineering Principles (Comprehensive)

### Category 1: Clarity & Structure
1. **Be Specific**: Use concrete examples, not abstract descriptions
2. **Avoid Ambiguity**: Define all terms and constraints
3. **Use Delimiters**: Separate sections with ```, """, or XML tags
4. **Number Steps**: Use 1, 2, 3 for sequential tasks

### Category 2: Role & Persona
5. **Assign Expert Role**: "You are an expert X with Y years experience"
6. **Define Tone**: "Be concise", "Be detailed", "Be friendly"
7. **Specify Audience**: "Explain to a beginner", "Explain to an expert"
8. **Set Constraints**: "Use simple language", "Avoid jargon"

### Category 3: Examples & Context
9. **Few-Shot Examples**: Provide 3-5 high-quality examples
10. **Provide Context**: Include background, domain knowledge
11. **Reference Standards**: "Follow PEP 8", "Use REST best practices"
12. **Include Edge Cases**: "Handle empty input", "Deal with nulls"

### Category 4: Output Format
13. **Specify Format**: "Return JSON", "Use Markdown", "Create table"
14. **Define Structure**: "Use these keys: ...", "Include these sections: ..."
15. **Set Length**: "200 words", "3 bullets", "5 steps max"
16. **Request Validation**: "Check your work", "Verify all assertions"

### Category 5: Reasoning & Logic
17. **Chain-of-Thought**: "Let's think step by step", "Reason through this"
18. **Show Work**: "Explain your reasoning", "Show intermediate steps"
19. **Validate Logic**: "Check for contradictions", "Verify assumptions"
20. **Consider Alternatives**: "What are other approaches?", "Compare options"

### Category 6: Error Prevention
21. **Anticipate Errors**: "Check for edge cases", "Handle exceptions"
22. **Request Caveats**: "What could go wrong?", "What are limitations?"
23. **Verify Accuracy**: "Double-check calculations", "Cite sources"
24. **Test Assumptions**: "Are these assumptions valid?", "What if X changes?"

### Category 7: Iteration & Refinement
25. **Iterative Improvement**: Test and refine prompts systematically
26. **A/B Testing**: Compare variations, measure performance

---

## DSPy Integration (Week 21 Context)

### How Principles Map to DSPy Signatures

**DSPy Signature Structure**:
```python
class AgentSignature(dspy.Signature):
    """
    [PERSONA + ROLE ASSIGNMENT]

    [REASONING PROCESS - Chain-of-Thought]

    [CONSTRAINTS + BOUNDARIES]

    [QUALITY CHECKLIST]

    [COMMON MISTAKES]

    [OUTPUT FORMAT]

    [EXAMPLES - handled by BootstrapFewShot]
    """

    input_field: str = dspy.InputField(desc="...")
    output_field: str = dspy.OutputField(desc="...")
```

**Principles Embedded**:
1. ✅ **Persona**: "You are an expert software architect..."
2. ✅ **CoT**: "REASONING PROCESS (think through step-by-step)"
3. ✅ **Constraints**: "Maximum 10 subtasks", "15-60 minutes per task"
4. ✅ **Error Prevention**: "COMMON MISTAKES TO AVOID"
5. ✅ **Output Format**: "Return JSON with keys..."
6. ✅ **Examples**: BootstrapFewShot adds 3-7 examples automatically

---

## Practical Recommendations for Week 21

### For Queen Agent (Task Decomposition):
```python
class TaskDecompositionSignature(dspy.Signature):
    """You are an expert project manager with 15+ years experience.

    REASONING PROCESS:
    1. Understand objective and success criteria
    2. Identify required capabilities (coding, testing, review)
    3. Determine dependencies (what must happen first)
    4. Assign tasks to appropriate agents
    5. Estimate realistic time (15-60 min per task)
    6. Validate workflow duration (<8 hours total)
    7. Check for missing steps or edge cases

    CONSTRAINTS:
    - Maximum 10 subtasks (complexity limit)
    - Each subtask 15-60 minutes (granularity)
    - Total workflow <=8 hours (resource limit)
    - Clear, measurable outcomes
    - No circular dependencies
    - NASA Rule 10: <=60 lines per implementation

    COMMON MISTAKES:
    - Too many subtasks (>10 = insufficient abstraction)
    - Missing security validation
    - Circular dependencies
    - Unrealistic time estimates

    OUTPUT FORMAT:
    JSON array with keys: agent, task_type, description, dependencies, estimated_minutes
    """

    task_description: str = dspy.InputField(desc="...")
    objective: str = dspy.InputField(desc="...")
    subtasks: list = dspy.OutputField(desc="...")
```

### For Reviewer Agent (Code Review):
```python
class CodeReviewSignature(dspy.Signature):
    """You are a senior security-focused code reviewer.

    REASONING PROCESS:
    1. Read code carefully line by line
    2. Identify security vulnerabilities (SQL injection, XSS, hardcoded secrets)
    3. Check code quality (NASA Rule 10, type hints, assertions)
    4. Evaluate error handling (try/except, validation)
    5. Assess performance (O(n) complexity, database queries)
    6. Generate actionable fixes with code examples

    CONSTRAINTS:
    - Maximum 10 issues (prioritize critical)
    - Each issue needs: severity, description, line number, fix
    - Severity levels: critical, high, medium, low
    - Fix must include actual code snippet

    QUALITY CHECKLIST:
    - Are all critical security issues identified?
    - Are fixes specific and actionable?
    - Are line numbers accurate?
    - Is severity assessment correct?

    COMMON MISTAKES:
    - Missing SQL injection vulnerabilities
    - Ignoring hardcoded secrets
    - Vague fixes without code examples
    - Incorrect severity ratings

    OUTPUT FORMAT:
    JSON: {"issues": [{"severity": "...", "type": "...", "description": "...", "line": N, "fix": "..."}]}
    """

    code_snippet: str = dspy.InputField(desc="...")
    review_type: str = dspy.InputField(desc="...")
    output: dict = dspy.OutputField(desc="...")
```

---

## Key Takeaways for SPEK Platform v8

1. **Claude 4 Best**: Use XML tags in signatures for Claude-optimized agents
2. **CoT Essential**: All agents should use "Think step by step" reasoning
3. **Few-Shot via DSPy**: BootstrapFewShot automatically generates 3-7 examples
4. **Hybrid Approach**: Combine persona + CoT + constraints + examples + format
5. **Iterative Testing**: A/B test baseline vs optimized agents (Week 21 Day 4)

---

## References

- Anthropic Claude Prompt Engineering: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
- OpenAI GPT-4 Best Practices: Six-Strategy Framework
- Google Gemini PTCF Framework: https://www.lololai.com/blog/ai-prompt-engineering-guide
- PromptingGuide.ai: https://www.promptingguide.ai/
- Lakera Prompt Engineering Guide 2025: https://www.lakera.ai/blog/prompt-engineering-guide

---

**Generated**: 2025-10-10
**Model**: Claude Sonnet 4.5 (research synthesis)
**Status**: ✅ **COMPREHENSIVE RESEARCH COMPLETE**
**Application**: Week 21 DSPy optimization (if approved)
