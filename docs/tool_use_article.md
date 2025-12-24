# 🧪 I Tested a Free LLM on Complex Multi-Step Tool Use — Here's What I Learned

**TL;DR:** I ran NVIDIA's Nemotron-3-Nano (a free model) through LangChain's agent framework with 3 complex reasoning puzzles requiring 7-8 chained tool calls each. It got 2 right, 1 wrong. The failure reveals something important about LLM + tool interactions.

---

## The Experiment

I built a simple LangChain agent with 3 tools:
- 🧮 **Calculator** — evaluates math expressions
- 📏 **Word Length** — counts characters  
- 🔄 **Reverse Text** — flips strings

Then I threw complex, layered puzzles at it — tasks that don't explicitly say "step 1, step 2" but require the model to decompose and chain 7-8 tool calls.

---

## The Results

### ✅ Puzzle 1: PASSED (7 steps)

> *"Take 17 × 23, multiply by (45 + 55), count digits, reverse it, raise digit count to that power, reverse 'ALGORITHM', add its length..."*

**Expected:** 3,134  
**Model's answer:** 3,134 ✓

The agent:
- Smartly combined `17 * 23 * (45 + 55)` into one calculator call
- Correctly tracked 5 digits → reversed → 5^5 = 3125
- Added ALGORITHM's length (9) → **3,134**

---

### ❌ Puzzle 2: FAILED (8 steps)

> *"144÷12 × (25×4), reverse it, get length, reverse 'PYTHON', get its length, multiply lengths, square it, reverse, count digits..."*

**Expected:** 3  
**Model's answer:** 4 ✗

**What went wrong — The Decimal Bug:**

```
Step 1: 144 / 12 * 100 = 1200.0  ← Python returns float
Step 2: Reverse "1200.0" → "0.0021"  ← 6 chars (includes ".")
Step 3: Length = 6  ← Should be 4 if "1200" → "0021"
```

The decimal point in `1200.0` corrupted the entire chain:
- 6 × 6 = 36 (should have been 4 × 6 = 24)
- 36² = 1296 (should have been 576)
- Final digit count: 4 (should have been 3)

**The model executed flawlessly. The tool output format caused the error.**

---

### ✅ Puzzle 3: PASSED (7 steps)

> *"Compute (15×8)+(72÷9)+(11×11), reverse digits, get count, reverse 'CRYPTOGRAPHY', divide total by its length, reverse quotient, square that length, compare to original count..."*

**Expected:** Yes, 25 > 3  
**Model's answer:** Yes, 25 > 3 ✓

Even with a decimal quotient (20.75 → "57.02"), the model:
- Correctly identified length = 5
- Computed 5² = 25
- Made the correct comparison to 3

---

## 🔑 Key Insight: LLM vs. Framework Responsibilities

| Component | Role | What Happened |
|-----------|------|---------------|
| **LLM (Nemotron)** | Decides WHAT to do | ✅ Perfect reasoning, correct tool selection, valid arguments |
| **LangChain** | Executes HOW to do it | ✅ Flawless orchestration and streaming |
| **Tool Design** | Returns results | ⚠️ Float output (`1200.0`) caused downstream error |

**The LLM didn't fail. The tool's output format did.**

---

## 📊 What Impressed Me

1. **Zero tool confusion** — Never called the wrong tool
2. **Valid Python expressions** — `(15 * 8) + (72 / 9) + (11 * 11)` passed correctly
3. **Context across 7-8 steps** — Remembered all intermediate values
4. **System prompt adherence** — Strictly used tools, no mental math
5. **Smart optimization** — Combined operations when possible

---

## ⚠️ Limitations Discovered

| Issue | Root Cause | Fix |
|-------|------------|-----|
| **Decimal contamination** | Python division returns floats | Cast to int when appropriate in tool |
| **No self-verification** | Model trusts tool output blindly | Add validation step |
| **Cascading errors** | One bad output corrupts the chain | Error handling in tools |

---

## 🎯 Takeaways for Builders

1. **Tool output format matters as much as LLM quality**  
   A brilliant model can't recover from `1200.0` when it expects `1200`

2. **Test with edge cases that hit tool quirks**  
   Division, floating point, special characters in reversal

3. **Free models CAN do complex agentic work**  
   Nemotron-3-Nano handled 7-8 step chains — the failure wasn't reasoning

4. **LangChain is plumbing, not intelligence**  
   Same code + different LLM = different results. Same LLM + bad tools = failures.

---

## The Fix

One line in the calculator tool:

```python
# Before
result = eval(expression)

# After  
result = eval(expression)
if isinstance(result, float) and result.is_integer():
    result = int(result)
```

---

*What's the sneakiest tool-related bug you've encountered in an agent system?*

#AI #LLM #LangChain #AgenticAI #MachineLearning #Debugging #NVIDIA