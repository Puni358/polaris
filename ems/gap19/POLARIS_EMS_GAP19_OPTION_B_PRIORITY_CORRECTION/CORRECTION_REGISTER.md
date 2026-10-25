# Correction Register

| Issue | Evidence | Current State | Required Correction | Code Modified? |
| :--- | :--- | :--- | :--- | :---: |
| **HiGHS priority convention** | Toy MILP ($x=10$ vs $x=0$) | Higher number = higher priority | Use descending priorities for $J_1 \to J_4$ | **NO** |
| **$J_1$ priority** | Source trace line 316 | `obj1.priority = 1` | `obj1.priority = 4` (or `100`) | **NO** |
| **$J_2$ priority** | Source trace line 321 | `obj2.priority = 2` | `obj2.priority = 3` (or `80`) | **NO** |
| **$J_3$ priority** | Source trace line 326 | `obj3.priority = 3` | `obj3.priority = 2` (or `60`) | **NO** |
| **$J_4$ priority** | Source trace line 331 | `obj4.priority = 4` | `obj4.priority = 1` (or `40`) | **NO** |
| **Blend mode** | Source trace line 298 | `blend_multi_objectives = False` | Retain `False` | **NO** |
| **Tolerance** | Source trace lines 316-331 | `abs/rel_tolerance = 0.0` | Retain `0.0` | **NO** |
| **Objective vectors** | Source trace lines 270-293 | Unchanged ($c_1, c_2, c_3, c_4$) | Retain unchanged | **NO** |
