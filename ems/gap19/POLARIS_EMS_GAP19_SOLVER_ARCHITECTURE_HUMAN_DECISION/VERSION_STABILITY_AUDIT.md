# VERSION STABILITY AUDIT

## Long-Term API Stability & Version Coupling Risk

This document evaluates the long-term version stability risks of Option A and Option B.

---

## Stability Risk Comparison

| Option | API Target | Semantic Versioning Guarantee | Maintenance & Deprecation Risk |
| :--- | :--- | :--- | :--- |
| **Option A** | `scipy.optimize.milp` | **High (Public API)**. Covered by SciPy backward-compatibility deprecation policy (2-release deprecation warning period). | **Low**. Standard SciPy public function signature is stable across minor releases. |
| **Option B** | `scipy.optimize._highs` OR standalone `highspy` | **Low (Private API / External C++ Binding)**. `_highs` is private (`_` prefix) and subject to unannounced refactoring or deletion across SciPy releases. | **High**. Upgrading SciPy or Python could break private wrapper calls or binary wheel compatibility. |

---

## Technical Finding

Option A minimizes version-coupling risk by relying strictly on SciPy's public API contract. Option B introduces version-coupling risks if implemented via SciPy private modules or external binary wheel updates.
