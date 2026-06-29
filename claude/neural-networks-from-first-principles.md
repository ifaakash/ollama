# Neural Networks from First Principles — Study Notes

> A DevOps-flavored walkthrough: from a single neuron up to backpropagation.
> Built intuition-first, formulas-second, with worked examples and analogies.

---

## Table of Contents
1. [The Neuron](#1-the-neuron)
2. [Matrix Multiplication & Layers](#2-matrix-multiplication--layers)
3. [Activation Functions (Sigmoid & ReLU)](#3-activation-functions-sigmoid--relu)
4. [The Loss Function](#4-the-loss-function)
5. [Gradient Descent](#5-gradient-descent)
6. [Backpropagation](#6-backpropagation)
7. [The Full Training Loop](#7-the-full-training-loop)
8. [Quick Reference Cheat Sheet](#8-quick-reference-cheat-sheet)

---

## 1. The Neuron

A neuron is the smallest decision-making unit. It takes several signals, decides how much each matters, combines them into one number, and runs that through a gate to produce an output.

**Maps onto a tiny autoscaling decision service:**

| Neuron part | DevOps equivalent |
|---|---|
| inputs | incoming metrics (CPU, request rate) |
| weights | how much each metric is trusted (weighted routing) |
| bias | default leaning / baseline threshold |
| weighted sum | aggregating metrics into one score |
| activation | the alerting rule that turns score → decision |

### Inputs
The raw numbers the neuron receives: `x₁`, `x₂`, …
*Analogy:* metrics arriving at a monitoring system — just raw readings, nobody has decided yet which matter.

### Weights
Each input gets multiplied by its own weight = its **importance**. Bigger weight pushes harder; a **negative** weight pushes the decision *down*. Weights are the part that gets **learned** during training.
*Analogy:* weighted load balancing (70/30 traffic split).

### Bias
A single number added at the end, **independent of any input**. It shifts the whole score and sets the neuron's default tendency.
- Negative bias → reluctant by default.
- Positive bias → leans toward firing by default.

**Key proof it's not tied to any input:** feed the neuron all zeros — every weighted input vanishes and only the bias remains. The bias is "what the neuron leans toward when all inputs go quiet."

> **weights decide how much each input matters; the bias decides the neuron's default baseline before any input is considered.**

### The weighted sum (pre-activation `z`)
```
z = (w₁ × x₁) + (w₂ × x₂) + b
```

**Worked example** — autoscaling decision (`x₁`=CPU=0.8, `x₂`=req rate=0.6, `w₁`=2, `w₂`=1, `b`=-1):
```
z = (2 × 0.8) + (1 × 0.6) + (-1)
  = 1.6 + 0.6 - 1
  = 1.2
```

**Full forward pass of one neuron:**
```
y = f( (w₁ × x₁) + (w₂ × x₂) + b )
```
Everything in deep learning is this, repeated and stacked.

---

## 2. Matrix Multiplication & Layers

The pattern "multiply matching pairs, then add them up" is a **dot product** — the smallest case of matrix multiplication.

### Single neuron as a dot product
```
            ⎡ x₁ ⎤
[ w₁  w₂ ] ×⎢    ⎥  + b
            ⎣ x₂ ⎦
```
- **Row** = this neuron's weights (one number per input).
- **Column** = the input values (one per input).
- Multiply matching pairs (weight i × input i), sum them → one number.
- **Output** = the single pre-activation score `z` (before bias).

### A layer = several neurons sharing the same inputs
Each neuron is its own **row** of weights. Stack the rows → a weight **matrix** `W`.

**Convention (memorize this):**
- **Rows = neurons** (one row per neuron's full weight set)
- **Columns = inputs** (one column per input)

For 3 neurons and 2 inputs, `W` is **3×2** (not 2×3) — both hold 6 numbers, but the orientation must let the multiply line up.

**The multiplication contract:** `(3×2) · (2×1) = (3×1)`. The **inner two numbers must match** (columns of `W` = number of inputs). Like an API contract: fields sent must match fields expected, or the call fails.

**Worked example** — 3 neurons, 2 inputs (`x = [0.8, 0.6]`):
```
        W (3×2)        b (3×1)
n1: [ 2    1  ]          [ -1  ]
n2: [ 0.5  3  ]          [  0  ]
n3: [ -1   1  ]          [ -0.5]
```
Step 1 — W·x (sweep each row across the input column):
```
n1: (2   × 0.8) + (1 × 0.6) = 2.2
n2: (0.5 × 0.8) + (3 × 0.6) = 2.2
n3: (-1  × 0.8) + (1 × 0.6) = -0.2
```
Step 2 — add bias → `z = [1.2, 2.2, -0.7]`
Step 3 — activation (ReLU) → `y = [1.2, 2.2, 0]` (neuron 3 shut off).

> **One matrix multiply + one bias add + one activation = an entire layer.**
> Chain layers (each output column feeds the next layer's input) → a neural network.

**Common bug — the transpose error:** reading the matrix *down the columns* instead of *across the rows*. To find a neuron's score: **grab its row and sweep across it, pairing left-to-right with the input column top-to-bottom.**

**Why matrices?** One matrix multiply computes all neurons at once instead of a `for` loop — the same instinct as batching API calls. GPUs are built for exactly this.

---

## 3. Activation Functions (Sigmoid & ReLU)

The weighted sum `z` can be any number from `-∞` to `+∞`. An activation function `f(z)` converts it into a usable, bounded decision.

**Why it's truly needed — non-linearity:** without it, stacking layers collapses mathematically into a *single* weighted sum (a linear function of a linear function is still linear). The non-linearity is what lets depth learn curves and complex patterns. *Analogy:* the activation is your alerting rule / health check that turns a raw score into an actual decision.

### Sigmoid
Squashes any number smoothly into the range **0 to 1** (read as a confidence/probability). Big positive → ~1, big negative → ~0, zero → exactly 0.5.
```
sigmoid(z) = 1 / (1 + e^(-z))
```
**Worked:** `sigmoid(1.2) = 1 / (1 + e^(-1.2)) = 1 / (1 + 0.3012) = 1 / 1.3012 ≈ 0.77`
*Analogy:* a confidence dial that never leaves 0–1.

### ReLU (Rectified Linear Unit)
If `z` is negative → output 0. If positive → output `z` unchanged.
```
ReLU(z) = max(0, z)
```
**Worked:** `ReLU(1.2) = 1.2`  /  `ReLU(-0.3) = 0`
*Analogy:* a one-way valve / circuit breaker. Cheap, fast, and avoids sigmoid's "stuck" behaviour on large inputs — which is why it's the modern default.

### Same neuron, two scenarios
| Scenario | z | sigmoid(z) | ReLU(z) | Decision |
|---|---|---|---|---|
| High load (x=[0.8, 0.6]) | 1.2 | ≈ 0.77 | 1.2 | scale up |
| Low load (x=[0.2, 0.3]) | -0.3 | ≈ 0.43 | 0 | don't scale |

The negative bias made the neuron demand real pressure before leaning "yes."

---

## 4. The Loss Function

A single number answering **"how wrong is the network right now?"** — the scalar you drive down to improve. *Analogy:* an error-budget burn rate; you can't optimize a vague feeling.

### Why a naive sum fails
Taking `Σ(predicted − actual)` lets opposite-sign errors **cancel**, making a bad model look good.
Example errors `-1, 0, +2` → naive sum `+1` (looks great), but the real magnitude of wrongness is 3.

### Mean Squared Error (MSE) — the fix
Square each error (kills the sign **and** punishes big mistakes harder), then average:
```
MSE = (1/n) × Σ (predicted − actual)²
```
**Worked** (errors -1, 0, +2):
```
(-1)² + (0)² + (2)² = 1 + 0 + 4 = 5
mean = 5 / 3 ≈ 1.67
```

### MSE vs MAE
- **MAE** (Mean Absolute Error) = average of `|predicted − actual|`. ("Modulus"/absolute value — one method, not two.)
- **MSE** punishes big errors disproportionately (off by 4 = 16× worse than off by 1) and is **smooth** (no kink at zero) — which matters for derivatives later.
- **MAE** is more robust to rare giant outliers.
- They're different tools, not a strict ranking. The naive sum is genuinely the worst.

### Loss = 0 caveat (overfitting)
Zero loss means every prediction matched — **on the data you trained on**. That can be a *warning sign*: the model may have **memorized** the training set and will fail on unseen data (overfitting). *Analogy:* a test suite that's green only because someone hardcoded the expected outputs. The real measure is low loss on data the model has **never seen**.

---

## 5. Gradient Descent

The procedure that **finds good weights automatically** by shrinking the loss.

### The landscape picture
Plot loss vs a weight → a bowl. The bottom = best weight. We start at a random spot and need to reach the bottom, but we **can't see the whole bowl** — we can only feel the slope right where we stand.

*Analogy:* a hiker descending a mountain in thick fog. Can't see the valley, but can feel which way the ground tilts, step downhill, feel again, repeat.

### The slope tells you which way (and how much)
The slope = "if I nudge this weight up a hair, does the loss go up or down, and how steeply?"
- **Positive slope** → increasing the weight increases loss → **decrease** the weight.
- **Negative slope** → increasing the weight decreases loss → **increase** the weight.
- Always move **opposite** the slope's sign (that's the "descent").
- Steeper slope → bigger step; gentle slope → smaller step → the step naturally shrinks near the bottom.

> Destination is the **bottom of the bowl** (where slope = 0), not necessarily `w = 0`.

### The update rule (universal)
```
new weight = old weight − (learning rate × slope)
```
- **slope** — direction + steepness.
- **minus sign** — go downhill.
- **learning rate (η)** — step size you choose (e.g. 0.1).

**Learning rate is a Goldilocks knob:**
- Too **big** → overshoot the valley, loss bounces/explodes (diverges).
- Too **small** → painfully slow training.

Example of the difference (weight 5, slope 4):
```
η = 0.1 → 5 − (0.1 × 4) = 4.6   (gentle, converges)
η = 1.0 → 5 − (1.0 × 4) = 1.0   (giant leap, overshoots)
```

### Worked example — loss `L = (w − 3)²`, slope `2(w − 3)`, η = 0.1
```
Step 1 @ w=0:    L=9      slope=2(0-3)=-6     w ← 0 - 0.1(-6) = 0.6
Step 2 @ w=0.6:  L=5.76   slope=2(0.6-3)=-4.8 w ← 0.6 - 0.1(-4.8) = 1.08
Step 3 @ w=1.08: L=3.69   slope=2(1.08-3)=-3.84 w ← 1.08 - 0.1(-3.84) = 1.464
```
Loss marches `9 → 5.76 → 3.69 → …` and `w` creeps toward 3.

### How general is this?
- The **update rule is universal** (vanilla gradient descent), used on networks with billions of weights.
- `(w−3)²` was a **toy** loss. Real losses (MSE, cross-entropy) depend on *all* weights at once → the single slope becomes a **gradient** (one slope per weight); the rule runs per-weight.
- Production optimizers (**Adam, momentum, RMSProp**) are refinements of the same engine. **SGD** = estimate the slope from small random batches instead of all data.
- **Hiker analogy's blind spots:**
  - **Local minima** — bumpy real landscapes have multiple valleys; a hiker can get stuck in a shallow one. (In very high dimensions, true bad local minima are rarer than feared; saddle points are the more common speed bump, and Adam handles them reasonably.)
  - **Dimensions** — real landscapes live in millions of dimensions; the logic is identical but no longer drawable.

---

## 6. Backpropagation

The efficient way to compute `∂L/∂w` for **every** weight, including ones buried in early layers that affect the loss only indirectly.

### The four math terms
| Term | Plain meaning | Analogy |
|---|---|---|
| **Derivative** (`dL/dw`) | Sensitivity / slope: "nudge input a hair → how much does output move, and which way?" | throttle responsiveness (RPM per mm of pedal) |
| **Partial derivative** (`∂L/∂w`) | Same, but with many knobs — wiggle *one* weight, hold all others still | controlled experiment changing one config value |
| **Gradient** | The full list of partial derivatives, one slope per weight | the complete "downhill on every axis" vector |
| **Chain rule** | If A→B→C, A's effect on C = `(A→B) × (B→C)`. Sensitivities **multiply** along a chain | gears: dial moves lever 2×, lever moves gauge 3× → dial moves gauge 6× |

> Off-the-shelf rule used above: the slope of *anything squared* is `2 × (that thing)`. So `L=(w−3)²` has slope `2(w−3)`.
> Clarification: `2(w−3)` is the rate of change of the **loss** with respect to the weight — not the rate of change of the weight.

### What backprop does (intuition)
It's **blame assignment flowing backward**. The output made an error; walk back through the network asking each layer "how much did *you* contribute?" Each layer scales the blame it received by its own local slope and passes it further back. The error travels backward through the same wires it came forward on → *back*-propagation.

*Analogy:* an incident surfaces at the user-facing service; you establish impact once at the edge, then trace blame backward through each upstream dependency, scaled by how much it influenced what came after.

### Worked example — chain `w → z=(w·x) → L=(z−t)²`
Inputs: `x = 2`, `w = 1`, target `t = 10`.

**Forward pass:**
```
z = w · x    = 1 · 2     = 2
L = (z − t)² = (2 − 10)² = 64
```

**Backward pass (local slopes, then multiply via chain rule):**
```
∂L/∂z = 2(z − t) = 2(2 − 10) = -16     (loss vs z)
∂z/∂w = x        = 2                    (z vs w)
∂L/∂w = ∂L/∂z × ∂z/∂w = (-16) × 2 = -32
```
Slope is `-32` (negative → increase `w` to cut loss — sensible, `z` is below target).

**Gradient step (η = 0.01):**
```
new w = 1 − (0.01 × -32) = 1 + 0.32 = 1.32
```
Sanity check: new `z = 2.64`, new `L = (2.64 − 10)² ≈ 54.2` — down from 64. ✓

### Why backward = fast
For an earlier weight the chain just has more links (one extra multiply per layer). Backprop starts at the loss end so shared pieces like `∂L/∂z` are computed **once** and **reused** for every weight feeding that stage — turning an impossibly slow calculation into a single efficient backward sweep.

---

## 7. The Full Training Loop

```
┌──────────────────────────────────────────────────────────┐
│  1. FORWARD PASS   inputs → weighted sums + bias →         │
│                    activations → output                    │
│  2. LOSS           measure how wrong the output is (MSE…)   │
│  3. BACKPROP       sweep backward, chain-rule the slopes    │
│                    → ∂L/∂w for every weight                 │
│  4. GRADIENT STEP  new w = old w − (η × slope)  for all w   │
│  5. REPEAT         until the loss stops dropping            │
└──────────────────────────────────────────────────────────┘
```
This is how every neural network is trained — built from a single neuron up.

---

## 8. Quick Reference Cheat Sheet

```
Weighted sum:     z = Σ(wᵢ · xᵢ) + b
Neuron output:    y = f(z)
Sigmoid:          σ(z) = 1 / (1 + e^(-z))          range 0..1
ReLU:             ReLU(z) = max(0, z)
Layer:            z = W·x + b   (W is neurons × inputs)
Loss (MSE):       L = (1/n) Σ(pred − actual)²
Slope of (a)²:    2 · a
Gradient step:    w ← w − (η · ∂L/∂w)
Chain rule:       ∂L/∂w = ∂L/∂z · ∂z/∂w
```

**Mental models to keep:**
- Neuron = weighted scoring + a decision gate.
- Weights = importance; bias = default baseline.
- Activation = non-linearity, the thing that makes depth worth it.
- Loss = single "wrongness" score; squaring stops cancellation & punishes big misses.
- Gradient descent = foggy hiker stepping downhill.
- Learning rate = step size (Goldilocks).
- Backprop = backward blame-assignment via the chain rule, with reuse for speed.
