# HiGHS Priority Convention Toy Proof

## 1. Experimental Setup

To verify the native HiGHS multi-objective priority convention empirically without relying solely on documentation, an isolated minimal toy MILP with conflicting objectives was constructed and solved using `highspy` 1.15.1.

### Model Formulation
- **Decision Variable**: $x \in [0, 10]$
- **Objective A**: Minimize $x$ (prefers $x = 0.0$)
- **Objective B**: Minimize $-x$ (prefers $x = 10.0$)
- **Blending Mode**: `blend_multi_objectives = False`

## 2. Experimental Execution & Results

### Test Run 1: `Obj A.priority = 1`, `Obj B.priority = 4`
- **Configuration**:
  - `obj_a.priority = 1`, `coefficients = [1.0]` (minimize $x$)
  - `obj_b.priority = 4`, `coefficients = [-1.0]` (minimize $-x$)
- **Solver Status**: `HighsModelStatus.kOptimal`
- **Resulting $x$**: `10.0`
- **Analysis**: Objective B (minimize $-x$) completely dominated Objective A, driving $x$ to its upper bound ($10.0$).

### Test Run 2: `Obj A.priority = 4`, `Obj B.priority = 1`
- **Configuration**:
  - `obj_a.priority = 4`, `coefficients = [1.0]` (minimize $x$)
  - `obj_b.priority = 1`, `coefficients = [-1.0]` (minimize $-x$)
- **Solver Status**: `HighsModelStatus.kOptimal`
- **Resulting $x$**: `0.0`
- **Analysis**: Objective A (minimize $x$) completely dominated Objective B, driving $x$ to its lower bound ($0.0$).

## 3. Verified Priority Convention

```text
HIGHS_PRIORITY_CONVENTION = HIGHER_NUMBER_IS_HIGHER_PRIORITY
```

- In HiGHS (`highspy`), an objective with a **larger numeric integer priority** takes precedence over an objective with a **smaller numeric integer priority**.
- Prioritizing $P(A) > P(B)$ requires setting `obj_A.priority > obj_B.priority`.
