"""
ForecastPerturber Module (D5 Implementation)
Implements forecast perturbation rules F'_t = P(F_t, theta, seed) in strict compliance with the frozen D5 contract.

Enforces:
1. Multiplicative interval scaling: L' = gamma * L, P' = gamma * P, U' = gamma * U.
2. Preserves lower <= point <= upper interval ordering.
3. Strict non-negativity and finite numerical value validation.
4. Immediate rejection of invalid bundles (ValueError) without silent clamping, repair, or smoothing.
5. Causal firewall: Zero access to hidden future ground-truth actuals.
"""
import copy
import math
from typing import Dict, Any, Optional

from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast


class ForecastBundleValidationError(ValueError):
    """Raised when a forecast perturbation produces an invalid ForecastBundle."""
    pass


class ForecastPerturber:
    """
    Applies deterministic forecast perturbations to baseline ForecastBundle objects.
    """

    @staticmethod
    def scale_timeseries(forecast: TimeseriesForecast, scale_factor: float, field_name: str) -> TimeseriesForecast:
        """
        Scales all components (point, lower, upper) of a TimeseriesForecast by multiplicative factor gamma.
        Enforces gamma >= 0, finite bounds, lower <= point <= upper, and field non-negativity.
        Rejects invalid results by raising ForecastBundleValidationError.
        """
        gamma = float(scale_factor)
        if math.isnan(gamma) or math.isinf(gamma):
            raise ForecastBundleValidationError(f"Scale factor for {field_name} must be finite, got {gamma}.")
        if gamma < 0.0:
            raise ForecastBundleValidationError(f"Negative scale factor for {field_name} prohibited: {gamma}.")

        new_point = [p * gamma for p in forecast.point]
        new_lower = [l * gamma for l in forecast.lower]
        new_upper = [u * gamma for u in forecast.upper]

        # Check finite values & interval ordering explicitly before instantiating schema object
        for idx, (p, l, u) in enumerate(zip(new_point, new_lower, new_upper)):
            if math.isnan(p) or math.isinf(p) or math.isnan(l) or math.isinf(l) or math.isnan(u) or math.isinf(u):
                raise ForecastBundleValidationError(
                    f"Perturbation produced non-finite value (NaN/Inf) for {field_name} at index {idx}."
                )
            if not (l <= p <= u):
                raise ForecastBundleValidationError(
                    f"Perturbation produced interval violation for {field_name} at index {idx}: lower ({l}) <= point ({p}) <= upper ({u})."
                )
            if p < 0.0:
                raise ForecastBundleValidationError(
                    f"Perturbation produced negative power/quantity for {field_name} at index {idx}: {p}."
                )

        try:
            scaled = TimeseriesForecast(
                point=new_point,
                lower=new_lower,
                upper=new_upper,
                unit=forecast.unit
            )
            scaled.validate_non_negative(field_name)
            return scaled
        except Exception as e:
            raise ForecastBundleValidationError(f"Invalid perturbed TimeseriesForecast for {field_name}: {e}")

    @classmethod
    def apply_perturbation(
        cls,
        bundle: ForecastBundle,
        solar_scale: float = 1.0,
        wind_scale: float = 1.0,
        demand_scale: float = 1.0,
        irradiance_scale: Optional[float] = None,
        scenario_id: Optional[str] = None
    ) -> ForecastBundle:
        """
        Applies multiplicative interval scaling to baseline ForecastBundle fields.
        Returns a new validated perturbed ForecastBundle.
        Raises ForecastBundleValidationError on any validity failure without silent repair.
        """
        if irradiance_scale is None:
            irradiance_scale = solar_scale

        pert_solar_irrad = cls.scale_timeseries(bundle.solar_irradiance, irradiance_scale, "solar_irradiance")
        pert_solar_gen = cls.scale_timeseries(bundle.solar_generation, solar_scale, "solar_generation")
        pert_wind_gen = cls.scale_timeseries(bundle.wind_generation, wind_scale, "wind_generation")
        pert_demand = cls.scale_timeseries(bundle.demand, demand_scale, "demand")

        new_metadata = copy.deepcopy(bundle.metadata)
        new_metadata["d5_perturbation"] = {
            "applied": True,
            "scenario_id": scenario_id or "CUSTOM",
            "solar_scale": solar_scale,
            "wind_scale": wind_scale,
            "demand_scale": demand_scale,
            "irradiance_scale": irradiance_scale
        }

        try:
            perturbed_bundle = ForecastBundle(
                schema_version=bundle.schema_version,
                origin_timestamp=bundle.origin_timestamp,
                horizon_hours=bundle.horizon_hours,
                timestamps=list(bundle.timestamps),
                solar_irradiance=pert_solar_irrad,
                solar_generation=pert_solar_gen,
                wind_generation=pert_wind_gen,
                demand=pert_demand,
                metadata=new_metadata
            )
            return perturbed_bundle
        except Exception as e:
            raise ForecastBundleValidationError(f"Perturbed ForecastBundle schema validation failed: {e}")
