# Formal Data Inquiry Draft — MET Norway User Support & Data Infrastructure

**To:** MET Norway User Support / THREDDS Operations (`post@met.no`, `support@met.no`)  
**Subject:** Technical Inquiry: Operational Publication Latency & Historical Availability of MEPS 18Z `meps_det_pl` Datasets (2024–2025)  
**Date:** 2026-10-16  
**Inquirer:** POLARIS Energy System Research Project, SITES Nuolja Microgrid Research  

---

### 1. Purpose of Inquiry

The POLARIS research project is conducting an authoritative reproducibility and causality audit of solar irradiance and microgrid energy management forecasts at the SITES Nuolja research station ($68.355701^\circ\text{N}, 18.763666^\circ\text{E}$). 

Our operational dispatch controller operates under a strict day-ahead decision boundary:
$$\text{Decision Cutoff } t_0 = 00:00\text{ UTC of Day } D$$

To ensure that candidate machine-learning models do not benefit from future information or unphysical lookahead, our governance firewall requires definitive verification of whether the prior calendar day's 18:00 UTC MEPS deterministic pressure-level dataset (`meps_det_pl`) was publicly accessible via your THREDDS server prior to $00:00\text{ UTC}$ during the 2024 and 2025 operating periods.

---

### 2. Exact Dataset & Variable Reference

- **Archive Base:** `https://thredds.met.no/thredds/dodsC/meps25epsarchive/{YYYY}/{MM}/{DD}/`
- **Product Name:** MEPS Deterministic Pressure Levels (`meps_det_pl`)
- **File Pattern:** `meps_det_pl_{YYYYMMDD}T18Z.ncml`
- **Grid Coordinates:** $(y=760, x=486)$
- **Key Variables:**
  - `mass_fraction_of_cloud_condensed_water_in_air_pl` (level index 8, ~700 hPa)
  - `mass_fraction_of_cloud_ice_in_air_pl` (level index 8, ~700 hPa)
  - `x_wind_pl`, `y_wind_pl` (level index 8, ~700 hPa)
  - `forecast_reference_time` ($18:00:00\text{ UTC}$)

---

### 3. Specific Questions for MET Norway Operations

#### Question 1: Embedded NetCDF `history` Attribute Semantics
In our programmatic inspection of the `.das` metadata for representative 2024 and 2025 dates, we consistently observe the following global attribute:
```text
String history "YYYY-MM-DDTHH:MM:SS creation by fimex";
```
Examples from our audit include:
- `2024-01-19T18Z` $\to$ `2024-01-19T20:08:28 creation by fimex`
- `2024-06-20T18Z` $\to$ `2024-06-20T20:01:51 creation by fimex`
- `2025-06-14T18Z` $\to$ `2025-06-14T20:00:03 creation by fimex`

**Questions:**
1. Does this timestamp record the exact wall-clock UTC completion time of the NetCDF file creation on your operational HPC cluster?
2. Following this timestamp, what is the nominal and 99th-percentile dissemination latency before the file is synchronized to the public THREDDS Data Server (`thredds.met.no`) and accessible to external HTTP/OpenDAP clients?

#### Question 2: Retained Server-Side Access & Dissemination Logs
We note that the static THREDDS catalog metadata (`<date type="modified">`) across 2024 files reflects May/June 2026 archive maintenance dates, overwriting the original 2024/2025 HTTP publication timestamps.
**Questions:**
1. Does MET Norway retain historical HTTP server access logs (e.g. Apache/Nginx logs), dissemination queue receipts, or operational monitoring logs for 2024 and 2025?
2. Can MET Norway provide timestamped log confirmation verifying that `meps_det_pl_*T18Z.ncml` files were publicly retrievable via HTTP before 00:00 UTC on the respective dates?

#### Question 3: Historical Outages & Delays
MetCoOp documentation specifies nominal output dissemination at ~135 minutes post-analysis (~20:15 UTC).
**Question:**
Were there any system outages, network interruptions, or operational processing delays during 2024 or 2025 that caused the 18Z MEPS deterministic run to be published after 00:00 UTC or fail dissemination entirely?

#### Question 4: Temporal Step Truncation on Pressure-Level Files
Our inspection revealed that while surface files (`meps_det_sfc`) uniformly provide 67 hourly steps (leads 0 to 66), pressure-level files (`meps_det_pl`) frequently provide only 39 time steps, switching from 1-hourly steps (leads 0–24) to 3-hourly steps (leads 27, 30, ... 66).
**Questions:**
1. Is this post-lead-24 3-hourly step spacing the official archiving policy for `meps_det_pl` to conserve storage?
2. Are hourly 3D pressure-level cloud fields for leads 25, 26, 28, and 29 permanently unarchived, or do they exist in an alternative archive collection?

---

### 4. Minimum Authoritative Evidence Required to Resolve Availability

Under POLARIS scientific governance, the historical pre-cutoff availability status is currently classified as **`NOT ESTABLISHED`**. To elevate this verdict to **`ESTABLISHED`**, one of the following authoritative artifacts must be received from MET Norway:
1. **Contemporaneous Server Log Extract:** An excerpt from MET Norway's web server logs showing initial public HTTP GET / 200 OK responses for `meps_det_pl_*T18Z` occurring prior to 00:00 UTC.
2. **Official Written Confirmation from MET Norway Operations:** A formal operational statement certifying that during the 2024–2025 period, 18Z `meps_det_pl` datasets were routinely published to `thredds.met.no` within $X$ minutes of `fimex` creation (e.g., prior to 21:00 UTC), confirming a positive operational buffer before 00:00 UTC, with an explicit list of any outage dates.
