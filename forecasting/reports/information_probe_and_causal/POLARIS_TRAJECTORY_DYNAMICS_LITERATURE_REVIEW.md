# POLARIS Trajectory-Dynamics Literature Review

This targeted review is external context, not POLARIS evidence and not evidence that a sequence model will improve POLARIS.

- Carpentieri et al. (2023), [*Intraday probabilistic forecasts of surface solar radiation with cloud scale-dependent autoregressive advection*](https://doi.org/10.1016/j.apenergy.2023.121775), Applied Energy: frames cloud growth and dissipation, absent from simple advection, as important sources of intraday forecast uncertainty. Its scale-dependent temporal-evolution model improved probabilistic skill in a satellite setting. This is physically relevant but not a replication of a 24-hour point/NWP forecast.
- Carpentieri et al. (2024), [*Extending intraday solar forecast horizons with deep generative models*](https://doi.org/10.1016/j.apenergy.2024.124186), Applied Energy: represents SSI through a clear-sky index and explicitly models cloud formation, evolution, and dissipation probabilistically. It motivates trajectory-aware uncertainty modelling, not a deterministic point-MAE conclusion for POLARIS.
- Roy et al. (2022), [*Impact of tropical convective conditions on solar irradiance forecasting based on cloud motion vectors*](https://doi.org/10.1088/1748-9326/ac94e6), Environmental Research Letters: finds rigid cloud-motion assumptions strained when cloud systems evolve. Its climate and timescale differ from POLARIS.
- [*Skill and Skill Prediction of Cloud-Track Advection-Only Forecasting under a Cumulus-Dominated Regime*](https://journals.ametsoc.org/view/journals/apme/56/3/jamc-d-16-0224.1.xml) (2017), JAMC: reports that advection-only skill depends on cloud regime and does not decay uniformly with lead time. It supports pre-specified regime-aware diagnostics, not post-hoc subgrouping.
- Yang et al. (2016), [*Regime-Dependent Short-Range Solar Irradiance Forecasting*](https://journals.ametsoc.org/view/journals/apme/55/7/jamc-d-15-0354.1.xml), JAMC: demonstrates that short-range performance can be regime dependent, while underscoring the danger of small regime subsets and overfitting.

## Interpretation for POLARIS

The literature makes a transition/trajectory mechanism physically plausible. It does not establish that ordinary temporal autocorrelation is a predictive opportunity, that a GRU/LSTM will improve point MAE, or that an Arctic 24-hour single-site model should be changed. POLARIS’s own frozen-control analysis must carry those conclusions.

## Sources versus POLARIS evidence

External studies largely use satellite fields, short/intraday horizons, and often probabilistic objectives. POLARIS uses existing station/NWP-era artifacts, 24 forecast horizons, frozen control predictions, and no training in this audit. Consequently the literature supports hypothesis formation only; it cannot elevate an association between realised trajectory complexity and existing error into causal evidence.
