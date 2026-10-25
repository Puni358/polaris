# STAGE 7.5 — LOCAL HORIZON EXTRACTION METHODOLOGY

## Geometric Horizon Ray-Marching Formulation

For each integer azimuth angle $\theta \in [0^\circ, 359^\circ]$, a horizontal ray is projected from Nuolja station coordinate $(x_0, y_0, h_0)$ along directional vector $(\sin \theta, \cos \theta)$.

Along the ray out to maximum radius $d_{\text{max}} = 25\text{ km}$, elevation $h(d)$ is sampled at $30\text{ m}$ spatial increments.

The maximum terrain elevation angle $\alpha_{\text{max}}(\theta)$ above the station's horizontal plane is computed with Earth spherical curvature correction:

$$\alpha_{\text{max}}(\theta) = \max_{0 < d \le d_{\text{max}}} \arctan \left( \frac{h(d) - h_0 - \frac{d^2}{2 R_E}}{d} \right)$$

where $R_E = 6,371,000\text{ m}$.

## Calculated Horizon Summary
- **Max Horizon Angle:** 29.80° (Azimuth 252°, Mt. Nuolja peak ridge)
- **Min Horizon Angle:** -1.80° (Azimuth 86°, Lake Torneträsk valley to ENE)
- **Mean Horizon Angle:** 9.60°
