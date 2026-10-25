# Objective Vector Forensics

Support analysis of $c_1, c_2, c_3, c_4 \in \mathbb{R}^{409}$:

- $\text{supp}(c_1) = \{360 .. 383\}$ (24 nonzeros)
- $\text{supp}(c_2) = \{384 .. 408\}$ (25 nonzeros)
- $\text{supp}(c_3) = \bigcup_{t=0}^{23} \{15t + 7, 15t + 13, 15t + 14\}$ (72 nonzeros)
- $\text{supp}(c_4) = \bigcup_{t=0}^{23} \{15t + 2, 15t + 3\}$ (48 nonzeros)

Pairwise intersections:
$$\text{supp}(c_i) \cap \text{supp}(c_j) = \emptyset \quad \forall i \neq j$$

Objective support vectors are strictly disjoint.

`OBJECTIVE_VECTOR_MAPPING = PASS`
