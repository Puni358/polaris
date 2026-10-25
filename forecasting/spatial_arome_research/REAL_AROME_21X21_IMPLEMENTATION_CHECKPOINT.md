# POLARIS — REAL-AROME 21×21 IMPLEMENTATION CHECKPOINT (EVEN ONLY)

## Final Classification
**C — INVALID IMPLEMENTATION**

Verdict: 2 implementation defect(s). No scientific interpretation of model performance. Defects: ['Section14: independent reconstruction mismatch 9/11 channels', 'G6 FAILED: control not reproduced (MAE diff=22.4189)']...

## Validity Defects (if classification C)
1. Section14: independent reconstruction mismatch 9/11 channels
2. G6 FAILED: control not reproduced (MAE diff=22.4189)

## M. ODD Firewall
- ODD_data_loaded: `False`
- ODD_targets_accessed: `False`
- ODD_predictions_generated: `False`
- ODD_metrics_computed: `False`
- compliance_statement: `Only EVEN origins (173) processed. ODD firewall (174 origins) unbreached.`

## A. Data Provenance
{
  "csv_path": "/home/punith-bs/01polaris (Copy)/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv",
  "csv_shape": [
    8328,
    45
  ],
  "even_origins_count": 173,
  "even_rows_count": 4152,
  "odd_rows_present_in_even_subset": false,
  "odd_accessed": false
}

## B. Causal Run Provenance
{
  "rule": "ONLY D-1 18Z AROME-Arctic deterministic runs used",
  "example_origins": [
    {
      "origin_id": 2,
      "t0_utc": "2024-01-21 00:00:00+00:00",
      "arome_init_utc": "2024-01-20 18:00:00+00:00",
      "arome_filename": "arome_arctic_det_2_5km_20240120T18Z.nc",
      "arome_url": "dap2://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/20/arome_arctic_det_2_5km_20240120T18Z.nc",
      "month": 1
    },
    {
      "origin_id": 4,
      "t0_utc": "2024-01-23 00:00:00+00:00",
      "arome_init_utc": "2024-01-22 18:00:00+00:00",
      "arome_filename": "arome_arctic_det_2_5km_20240122T18Z.nc",
      "arome_url": "dap2://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/22/arome_arctic_det_2_5km_20240122T18Z.nc",
      "month": 1
    },
    {
      "origin_id": 6,
      "t0_utc": "2024-01-25 00:00:00+00:00",
      "arome_init_utc": "2024-01-24 18:00:00+00:00",
      "arome_filename": "arome_arctic_det_2_5km_20240124T18Z.nc",
      "arome_url": "dap2://thredds.met.no/thredds/dodsC/aromearcticarchive/2024/01/24/arome_arctic_det_2_5km_20240124T18Z.nc",
      "month": 1
    }
  ]
}

## C. Tensor Extraction Path
{
  "source": "AROME-Arctic deterministic 2.5km D-1 18Z runs on thredds.met.no",
  "opendap_protocol": "dap2:// via pydap engine (xarray)",
  "anchor_grid_point_AROME": [
    209,
    548
  ],
  "footprint_21x21_center_to_center_km": 50.0,
  "y_slice": [
    199,
    219
  ],
  "x_slice": [
    538,
    558
  ],
  "patch_shape": [
    21,
    21
  ],
  "tensor_shape_per_origin": [
    24,
    11,
    21,
    21
  ],
  "cache_dir": "/home/punith-bs/01polaris (Copy)/arome_cache_21x21"
}

## D. Exact 11-Channel Provenance
{
  "channel_count": 11,
  "channel_order": [
    "surface_downwelling_shortwave_flux_in_air",
    "cloud_area_fraction",
    "high_type_cloud_area_fraction",
    "medium_type_cloud_area_fraction",
    "low_type_cloud_area_fraction",
    "mass_fraction_of_cloud_condensed_water_in_air_pl",
    "mass_fraction_of_cloud_ice_in_air_pl",
    "x_wind_10m",
    "y_wind_10m",
    "x_wind_pl",
    "y_wind_pl"
  ],
  "all_channels_from_real_arome_netcdf": true,
  "no_synthetic_channels": true,
  "no_scalar_duplication_channels": true
}

## E. Sample Tensor Diagnostics (Section 13)
{
  "origins_tested": [
    {
      "2": "Winter"
    },
    {
      "42": "Spring"
    },
    {
      "134": "Summer"
    },
    {
      "226": "Fall"
    }
  ],
  "all_channels_real_arome": true,
  "any_channel_has_spatial_variation": true,
  "origins_produce_different_patterns": true,
  "all_channels_directly_extracted_not_synthetic": true,
  "no_sin_cos_ramp_wave_in_pipeline": true,
  "not_reconstructable_from_csv_alone": true,
  "channel_details": [
    {
      "origin_id": 2,
      "season": "Winter",
      "channels": [
        {
          "channel_idx": 0,
          "channel_name": "surface_downwelling_shortwave_flux_in_air",
          "channel_name_arome_netcdf": "surface_downwelling_shortwave_flux_in_air",
          "source_netcdf_variable": "surface_downwelling_shortwave_flux_in_air",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 14.529297,
          "patch_mean": 7.642839,
          "patch_std": 3.97892928,
          "patch_min": 2.568359,
          "patch_max": 17.533203,
          "n_unique_values": 424,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 1,
          "channel_name": "cloud_area_fraction",
          "channel_name_arome_netcdf": "cloud_area_fraction",
          "source_netcdf_variable": "cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.999939,
          "patch_mean": 0.998192,
          "patch_std": 0.00358897,
          "patch_min": 0.980469,
          "patch_max": 1.0,
          "n_unique_values": 129,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": "fc_cloud_cover",
          "csv_equivalent_value": 90.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 2,
          "channel_name": "high_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "high_type_cloud_area_fraction",
          "source_netcdf_variable": "high_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.999939,
          "patch_mean": 0.998189,
          "patch_std": 0.00359266,
          "patch_min": 0.980469,
          "patch_max": 1.0,
          "n_unique_values": 129,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 3,
          "channel_name": "medium_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "medium_type_cloud_area_fraction",
          "source_netcdf_variable": "medium_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 3.1e-05,
          "patch_mean": 0.066201,
          "patch_std": 0.13536243,
          "patch_min": 0.0,
          "patch_max": 0.730652,
          "n_unique_values": 204,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 4,
          "channel_name": "low_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "low_type_cloud_area_fraction",
          "source_netcdf_variable": "low_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 5.8e-05,
          "patch_std": 0.00058704,
          "patch_min": 0.0,
          "patch_max": 0.011322,
          "n_unique_values": 17,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 5,
          "channel_name": "atmosphere_mass_content_of_cloud_liquid_water",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "lwp_latest",
          "csv_equivalent_value": 0.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 6,
          "channel_name": "atmosphere_mass_content_of_cloud_ice",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "iwp_latest",
          "csv_equivalent_value": 4.175841,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 7,
          "channel_name": "x_wind_10m",
          "channel_name_arome_netcdf": "x_wind_10m",
          "source_netcdf_variable": "x_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 2.490299,
          "patch_mean": -3.191536,
          "patch_std": 3.40069652,
          "patch_min": -11.751888,
          "patch_max": 4.454166,
          "n_unique_values": 432,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 8,
          "channel_name": "y_wind_10m",
          "channel_name_arome_netcdf": "y_wind_10m",
          "source_netcdf_variable": "y_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.124617,
          "patch_mean": 0.287147,
          "patch_std": 3.70054674,
          "patch_min": -9.465227,
          "patch_max": 9.228132,
          "n_unique_values": 434,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 9,
          "channel_name": "x_wind_700hPa",
          "channel_name_arome_netcdf": "x_wind_pl",
          "source_netcdf_variable": "x_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "u700",
          "csv_equivalent_value": 9.662344,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 10,
          "channel_name": "y_wind_700hPa",
          "channel_name_arome_netcdf": "y_wind_pl",
          "source_netcdf_variable": "y_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240120T18Z.nc",
          "valid_timestamp_H13": "2024-01-21 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "v700",
          "csv_equivalent_value": 5.217216,
          "reconstructable_from_csv_scalar_alone": false
        }
      ],
      "checks": {
        "n_variable_channels": 7,
        "all_11_channels_real_arome": true,
        "center_anchor_verified": true,
        "anchor_coordinates_used": true,
        "no_synthetic_wave_pattern": true,
        "no_scalar_duplication_detected": true,
        "not_reconstructable_from_38_csv": true,
        "arome_channels_without_csv_equivalent": [
          "high_type_cloud_area_fraction",
          "medium_type_cloud_area_fraction",
          "low_type_cloud_area_fraction",
          "x_wind_10m",
          "y_wind_10m"
        ]
      }
    },
    {
      "origin_id": 42,
      "season": "Spring",
      "channels": [
        {
          "channel_idx": 0,
          "channel_name": "surface_downwelling_shortwave_flux_in_air",
          "channel_name_arome_netcdf": "surface_downwelling_shortwave_flux_in_air",
          "source_netcdf_variable": "surface_downwelling_shortwave_flux_in_air",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 120.8125,
          "patch_mean": 74.322807,
          "patch_std": 38.17567825,
          "patch_min": 31.726562,
          "patch_max": 171.492188,
          "n_unique_values": 430,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 1,
          "channel_name": "cloud_area_fraction",
          "channel_name_arome_netcdf": "cloud_area_fraction",
          "source_netcdf_variable": "cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.890106,
          "patch_mean": 0.807762,
          "patch_std": 0.16876003,
          "patch_min": 0.43161,
          "patch_max": 1.0,
          "n_unique_values": 414,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": "fc_cloud_cover",
          "csv_equivalent_value": 100.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 2,
          "channel_name": "high_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "high_type_cloud_area_fraction",
          "source_netcdf_variable": "high_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.880127,
          "patch_mean": 0.781962,
          "patch_std": 0.19209473,
          "patch_min": 0.31427,
          "patch_max": 1.0,
          "n_unique_values": 414,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 3,
          "channel_name": "medium_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "medium_type_cloud_area_fraction",
          "source_netcdf_variable": "medium_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.083099,
          "patch_mean": 0.112299,
          "patch_std": 0.05687136,
          "patch_min": 0.030212,
          "patch_max": 0.38855,
          "n_unique_values": 429,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 4,
          "channel_name": "low_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "low_type_cloud_area_fraction",
          "source_netcdf_variable": "low_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 3e-06,
          "patch_std": 9.24e-06,
          "patch_min": 0.0,
          "patch_max": 3.1e-05,
          "n_unique_values": 2,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": true,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 5,
          "channel_name": "atmosphere_mass_content_of_cloud_liquid_water",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "lwp_latest",
          "csv_equivalent_value": 0.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 6,
          "channel_name": "atmosphere_mass_content_of_cloud_ice",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "iwp_latest",
          "csv_equivalent_value": 2.072776,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 7,
          "channel_name": "x_wind_10m",
          "channel_name_arome_netcdf": "x_wind_10m",
          "source_netcdf_variable": "x_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 1.236192,
          "patch_mean": -2.523428,
          "patch_std": 1.93988967,
          "patch_min": -6.366347,
          "patch_max": 3.127793,
          "n_unique_values": 433,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 8,
          "channel_name": "y_wind_10m",
          "channel_name_arome_netcdf": "y_wind_10m",
          "source_netcdf_variable": "y_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 4.205032,
          "patch_mean": 4.804327,
          "patch_std": 4.21900654,
          "patch_min": -4.721725,
          "patch_max": 12.679642,
          "n_unique_values": 429,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 9,
          "channel_name": "x_wind_700hPa",
          "channel_name_arome_netcdf": "x_wind_pl",
          "source_netcdf_variable": "x_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "u700",
          "csv_equivalent_value": 20.115448,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 10,
          "channel_name": "y_wind_700hPa",
          "channel_name_arome_netcdf": "y_wind_pl",
          "source_netcdf_variable": "y_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240229T18Z.nc",
          "valid_timestamp_H13": "2024-03-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "v700",
          "csv_equivalent_value": 12.992327,
          "reconstructable_from_csv_scalar_alone": false
        }
      ],
      "checks": {
        "n_variable_channels": 7,
        "all_11_channels_real_arome": true,
        "center_anchor_verified": true,
        "anchor_coordinates_used": true,
        "no_synthetic_wave_pattern": true,
        "no_scalar_duplication_detected": true,
        "not_reconstructable_from_38_csv": true,
        "arome_channels_without_csv_equivalent": [
          "high_type_cloud_area_fraction",
          "medium_type_cloud_area_fraction",
          "low_type_cloud_area_fraction",
          "x_wind_10m",
          "y_wind_10m"
        ]
      }
    },
    {
      "origin_id": 134,
      "season": "Summer",
      "channels": [
        {
          "channel_idx": 0,
          "channel_name": "surface_downwelling_shortwave_flux_in_air",
          "channel_name_arome_netcdf": "surface_downwelling_shortwave_flux_in_air",
          "source_netcdf_variable": "surface_downwelling_shortwave_flux_in_air",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 105.60347,
          "patch_mean": 255.511673,
          "patch_std": 102.64807129,
          "patch_min": 50.44722,
          "patch_max": 531.009705,
          "n_unique_values": 434,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 1,
          "channel_name": "cloud_area_fraction",
          "channel_name_arome_netcdf": "cloud_area_fraction",
          "source_netcdf_variable": "cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 1.0,
          "patch_mean": 0.967049,
          "patch_std": 0.10154981,
          "patch_min": 0.180267,
          "patch_max": 1.0,
          "n_unique_values": 200,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": "fc_cloud_cover",
          "csv_equivalent_value": 28.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 2,
          "channel_name": "high_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "high_type_cloud_area_fraction",
          "source_netcdf_variable": "high_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 3,
          "channel_name": "medium_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "medium_type_cloud_area_fraction",
          "source_netcdf_variable": "medium_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.05541,
          "patch_std": 0.14113817,
          "patch_min": 0.0,
          "patch_max": 0.770569,
          "n_unique_values": 165,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 4,
          "channel_name": "low_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "low_type_cloud_area_fraction",
          "source_netcdf_variable": "low_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 1.0,
          "patch_mean": 0.962961,
          "patch_std": 0.1098992,
          "patch_min": 0.162933,
          "patch_max": 1.0,
          "n_unique_values": 210,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 5,
          "channel_name": "atmosphere_mass_content_of_cloud_liquid_water",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "lwp_latest",
          "csv_equivalent_value": 31.265099,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 6,
          "channel_name": "atmosphere_mass_content_of_cloud_ice",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "iwp_latest",
          "csv_equivalent_value": 0.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 7,
          "channel_name": "x_wind_10m",
          "channel_name_arome_netcdf": "x_wind_10m",
          "source_netcdf_variable": "x_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": -1.341874,
          "patch_mean": 2.834679,
          "patch_std": 1.62080646,
          "patch_min": -1.955644,
          "patch_max": 7.13127,
          "n_unique_values": 434,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 8,
          "channel_name": "y_wind_10m",
          "channel_name_arome_netcdf": "y_wind_10m",
          "source_netcdf_variable": "y_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.303835,
          "patch_mean": 1.303298,
          "patch_std": 1.29548097,
          "patch_min": -2.286497,
          "patch_max": 4.659792,
          "n_unique_values": 432,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 9,
          "channel_name": "x_wind_700hPa",
          "channel_name_arome_netcdf": "x_wind_pl",
          "source_netcdf_variable": "x_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "u700",
          "csv_equivalent_value": 6.964571,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 10,
          "channel_name": "y_wind_700hPa",
          "channel_name_arome_netcdf": "y_wind_pl",
          "source_netcdf_variable": "y_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240531T18Z.nc",
          "valid_timestamp_H13": "2024-06-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "v700",
          "csv_equivalent_value": 6.078686,
          "reconstructable_from_csv_scalar_alone": false
        }
      ],
      "checks": {
        "n_variable_channels": 6,
        "all_11_channels_real_arome": true,
        "center_anchor_verified": true,
        "anchor_coordinates_used": true,
        "no_synthetic_wave_pattern": true,
        "no_scalar_duplication_detected": true,
        "not_reconstructable_from_38_csv": true,
        "arome_channels_without_csv_equivalent": [
          "high_type_cloud_area_fraction",
          "medium_type_cloud_area_fraction",
          "low_type_cloud_area_fraction",
          "x_wind_10m",
          "y_wind_10m"
        ]
      }
    },
    {
      "origin_id": 226,
      "season": "Fall",
      "channels": [
        {
          "channel_idx": 0,
          "channel_name": "surface_downwelling_shortwave_flux_in_air",
          "channel_name_arome_netcdf": "surface_downwelling_shortwave_flux_in_air",
          "source_netcdf_variable": "surface_downwelling_shortwave_flux_in_air",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 356.517548,
          "patch_mean": 368.4104,
          "patch_std": 43.03642654,
          "patch_min": 164.064438,
          "patch_max": 428.533173,
          "n_unique_values": 424,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 1,
          "channel_name": "cloud_area_fraction",
          "channel_name_arome_netcdf": "cloud_area_fraction",
          "source_netcdf_variable": "cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.361816,
          "patch_mean": 0.296521,
          "patch_std": 0.29342496,
          "patch_min": 0.003723,
          "patch_max": 1.0,
          "n_unique_values": 420,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": "fc_cloud_cover",
          "csv_equivalent_value": 45.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 2,
          "channel_name": "high_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "high_type_cloud_area_fraction",
          "source_netcdf_variable": "high_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.052704,
          "patch_mean": 0.101147,
          "patch_std": 0.08980107,
          "patch_min": 0.002991,
          "patch_max": 0.439545,
          "n_unique_values": 426,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 3,
          "channel_name": "medium_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "medium_type_cloud_area_fraction",
          "source_netcdf_variable": "medium_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 3.1e-05,
          "patch_mean": 0.000137,
          "patch_std": 0.00040401,
          "patch_min": 0.0,
          "patch_max": 0.002838,
          "n_unique_values": 37,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 4,
          "channel_name": "low_type_cloud_area_fraction",
          "channel_name_arome_netcdf": "low_type_cloud_area_fraction",
          "source_netcdf_variable": "low_type_cloud_area_fraction",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.326294,
          "patch_mean": 0.202302,
          "patch_std": 0.3310225,
          "patch_min": 0.0,
          "patch_max": 1.0,
          "n_unique_values": 276,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 5,
          "channel_name": "atmosphere_mass_content_of_cloud_liquid_water",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_condensed_water_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "lwp_latest",
          "csv_equivalent_value": 0.0,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 6,
          "channel_name": "atmosphere_mass_content_of_cloud_ice",
          "channel_name_arome_netcdf": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_netcdf_variable": "mass_fraction_of_cloud_ice_in_air_pl",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "iwp_latest",
          "csv_equivalent_value": 0.09117,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 7,
          "channel_name": "x_wind_10m",
          "channel_name_arome_netcdf": "x_wind_10m",
          "source_netcdf_variable": "x_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": -0.980814,
          "patch_mean": 2.818902,
          "patch_std": 1.68891525,
          "patch_min": -2.852884,
          "patch_max": 7.758444,
          "n_unique_values": 421,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 8,
          "channel_name": "y_wind_10m",
          "channel_name_arome_netcdf": "y_wind_10m",
          "source_netcdf_variable": "y_wind_10m",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": -0.707391,
          "patch_mean": 0.275297,
          "patch_std": 1.7045629,
          "patch_min": -3.478875,
          "patch_max": 5.089484,
          "n_unique_values": 421,
          "has_genuine_spatial_variation": true,
          "all_values_same_as_center": false,
          "csv_equivalent_col": null,
          "csv_equivalent_value": null,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 9,
          "channel_name": "x_wind_700hPa",
          "channel_name_arome_netcdf": "x_wind_pl",
          "source_netcdf_variable": "x_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "u700",
          "csv_equivalent_value": -0.843058,
          "reconstructable_from_csv_scalar_alone": false
        },
        {
          "channel_idx": 10,
          "channel_name": "y_wind_700hPa",
          "channel_name_arome_netcdf": "y_wind_pl",
          "source_netcdf_variable": "y_wind_pl",
          "source_file": "arome_arctic_det_2_5km_20240831T18Z.nc",
          "valid_timestamp_H13": "2024-09-01 12:00:00+00:00",
          "shape": [
            21,
            21
          ],
          "center_value": 0.0,
          "patch_mean": 0.0,
          "patch_std": 0.0,
          "patch_min": 0.0,
          "patch_max": 0.0,
          "n_unique_values": 1,
          "has_genuine_spatial_variation": false,
          "all_values_same_as_center": true,
          "csv_equivalent_col": "v700",
          "csv_equivalent_value": -4.70248,
          "reconstructable_from_csv_scalar_alone": false
        }
      ],
      "checks": {
        "n_variable_channels": 7,
        "all_11_channels_real_arome": true,
        "center_anchor_verified": true,
        "anchor_coordinates_used": true,
        "no_synthetic_wave_pattern": true,
        "no_scalar_duplication_detected": true,
        "not_reconstructable_from_38_csv": true,
        "arome_channels_without_csv_equivalent": [
          "high_type_cloud_area_fraction",
          "medium_type_cloud_area_fraction",
          "low_type_cloud_area_fraction",
          "x_wind_10m",
          "y_wind_10m"
        ]
      }
    }
  ]
}

## F. Independent Reconstruction Verification (Section 14)
{
  "origin_id": 2,
  "pipeline_tensor_shape": [
    24,
    11,
    21,
    21
  ],
  "comparison_method": "Re-open same AROME URL with pydap + re-slice independently",
  "pass": false,
  "independent_tensor_shape": [
    24,
    11,
    21,
    21
  ],
  "per_channel_comparison": [
    {
      "ch": 0,
      "name": "surface_downwelling_shortwave_flux_in_air",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 1,
      "name": "cloud_area_fraction",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 2,
      "name": "high_type_cloud_area_fraction",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 3,
      "name": "medium_type_cloud_area_fraction",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 4,
      "name": "low_type_cloud_area_fraction",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 5,
      "name": "mass_fraction_of_cloud_condensed_water_in_air_pl",
      "match": true,
      "max_abs_diff": 8.073e-05
    },
    {
      "ch": 6,
      "name": "mass_fraction_of_cloud_ice_in_air_pl",
      "match": true,
      "max_abs_diff": 1.47e-06
    },
    {
      "ch": 7,
      "name": "x_wind_10m",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 8,
      "name": "y_wind_10m",
      "match": true,
      "max_abs_diff": 0.0
    },
    {
      "ch": 9,
      "name": "x_wind_pl",
      "match": false,
      "max_abs_diff": 10.254179
    },
    {
      "ch": 10,
      "name": "y_wind_pl",
      "match": false,
      "max_abs_diff": 17.31023407
    }
  ],
  "channels_matched": 9,
  "channels_total": 11,
  "max_absolute_difference": 17.31023407,
  "shape_match": true,
  "timestamp_match": true,
  "coordinate_match": true
}

## G. Control Reproduction (Section 12)
- Reproduced: `False`
- MAE: `48.785662` W/m²
- nMAE: `29.3598` %
- RMSE: `76.44815` W/m²
- bias: `-3.203821` W/m²

## H. Architecture Verification
{
  "param_count_actual": 16033,
  "param_count_expected": 16033,
  "match": true
}

## I. Training Configuration
{
  "folds": 5,
  "grouping": "forecast_origin (GroupKFold)",
  "spatial_normalization": "per-channel z-score on training fold, clip [-5,+5]",
  "tabular_normalization": "StandardScaler on training fold",
  "optimizer": "AdamW",
  "lr": 0.001,
  "weight_decay": 0.0001,
  "batch_size": 8,
  "max_epochs": 300,
  "early_stopping_patience": 20,
  "loss": "L1 / day-MAE (night_mask contributes zero loss)",
  "seed": 42
}

## J. Five-Fold EVEN Results (Candidate vs Control)
**Candidate:**
- MAE_W_m2: `59.47042`
- nMAE_pct: `35.9038`
- RMSE_W_m2: `87.847515`
- bias_W_m2: `0.108168`
- night_MAE_W_m2: `0.674355`
- delta_MAE_vs_ctrl: `10.684758`
- delta_nMAE_vs_ctrl_pp: `6.544`
- delta_RMSE_vs_ctrl: `11.399365`
- folds_improved_count: `0`
- max_fold_degradation_W_m2: `24.120599`

**Fold Deltas (candidate MAE − control MAE):**
- Fold 1: ΔMAE = `24.120599` W/m² (improved=`False`)
- Fold 2: ΔMAE = `11.099813` W/m² (improved=`False`)
- Fold 3: ΔMAE = `6.444831` W/m² (improved=`False`)
- Fold 4: ΔMAE = `5.207373` W/m² (improved=`False`)
- Fold 5: ΔMAE = `6.551177` W/m² (improved=`False`)

## K. G1–G6 Gate Results
- **G1_delta_MAE_le_-0_50**: FAIL  `{'value': 10.684758, 'threshold': '<= -0.50'}`
- **G2_folds_improved_ge_4**: FAIL  `{'value': 0, 'threshold': '>= 4'}`
- **G3_max_fold_degradation_le_+0_50**: FAIL  `{'value': 24.120599, 'threshold': '<= +0.50'}`
- **G4_nMAE_and_RMSE_not_worse**: FAIL  `{'nMAE_candidate_pct': 35.9038, 'nMAE_control_pct': 29.3598, 'nMAE_not_worse': False, 'RMSE_candidate': 87.847515, 'RMSE_control': 76.44815, 'RMSE_not_worse': False}`
- **G5_causal_and_parser_compliance**: FAIL  `{'all_channels_real_arome': True, 'independent_reconstruction_pass': False, 'validity_defects_count_related': 1}`
- **G6_exact_control_reproduction**: FAIL  `{'control_reproduced_flag': False}`
- **ALL_GATES_PASS**: `False`

## Summary Output (Return)
1. Files created: see top of this document.
2. Implementation validity: `INVALID`
3. Control metrics: MAE=`48.785662`, nMAE=`29.3598%`, RMSE=`76.44815`, bias=`-3.203821`, night_MAE=`0.674355`
4. Candidate metrics: MAE=`59.47042`, nMAE=`35.9038%`, RMSE=`87.847515`, bias=`0.108168`, night_MAE=`0.674355`
5. Fold deltas (W/m², cand−ctrl): F1=+24.120599, F2=+11.099813, F3=+6.444831, F4=+5.207373, F5=+6.551177
6. G1–G6 status: G1=F, G2=F, G3=F, G4=F, G5=F, G6=F  (ALL_PASS=`False`)
7. ODD accessed: `False`
8. Final verdict: **C — INVALID IMPLEMENTATION** — 2 implementation defect(s). No scientific interpretation of model performance. Defects: ['Section14: independent reconstruction mismatch 9/11 channels', 'G6 FAILED: control not reproduced (MAE diff=22.4189)']...