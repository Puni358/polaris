# D11 data-rights evidence record (2026-10-11, M9)

This file records what was checked for D11 and how. It is not legal advice and it does not establish legal certainty. CC did not verify the project lead's statement legally. Missing evidence is recorded as missing. It is not treated as a lack of rights.

## 1. Project-lead statement

M9 (`cmsg_017TpQv3UrTPMkzn658LmXvX2WPEGQjqxQQ7wSucS9sxg4`, 2026-10-11T04:29:38Z, Puni, project lead): "The project lead states that they have the necessary data rights."

It is recorded exactly as stated. No licence document accompanied it.

## 2. Product and endpoint (from code, read statically)

- **Weather file:** `data/POLARIS_v0_1_future_weather_forecasts_2024.csv`, SHA-256 `8d24dc72…aa16`.
- **Written by:** `clear_sky/audit_clean_nwp_windows.py` (lines 20, 25-33, 119) and `clear_sky/build_future_weather_dataset.py` (lines 10, 14, 23, 27-35, 133). Both write the same path.
- **Endpoint:** `https://previous-runs-api.open-meteo.com/v1/forecast`, the Open-Meteo **Previous Runs API**.
- **Model:** `models=metno_seamless`. `build_future_weather_dataset.py:10` reads: "Source: MET Norway / MET Nordic (metno_seamless) via Open-Meteo".
- **Variables:** `*_previous_day1` cloud cover and others.
- **Open-Meteo documentation** (`/en/docs/previous-runs-api`, read 2026-10-11): the Previous Runs API "supports the same models as the Weather Forecast API", including MET Norway Nordic Seamless (with ECMWF). The same page carries no licence text.
- **Download date: not established.** The only clue is the file's last-modified time on the device, 2026-09-09T15:47:45Z (from a directory listing, metadata only). That is the latest possible download date, not proof of when the download happened.

## 3. Open-Meteo terms (current page, read 2026-10-11)

**Retrieval method.** The pages were read through a web-fetch tool. That tool returns a model-extracted rendering, not the raw HTML. The quotes below are the tool's verbatim extractions, requested as verbatim. Direct download (curl) was refused by the network proxy (HTTP 403). No archived snapshot was made, and the page shows no last-updated date (footer: "© 2022-2026 Copyright: Open-Meteo.com"; "All changes are transparently tracked on GitHub").

| Topic | Text as extracted from `https://open-meteo.com/en/terms` |
|---|---|
| Scope of the free API | "You may only use the free API services for non-commercial purposes." |
| Definition | "Non-commercial use is defined as [elaborated by creative commons]" (no standalone definition) |
| Non-commercial examples | "Using our service for private or non-profit websites or apps that do not have subscriptions or advertising."; "Incorporating our service into educational content."; "Using our service for public research conducted at public institutions." |
| Commercial examples | "Operating websites or apps that have subscriptions or display advertisements."; "Integrating our service into commercial products or promotional activities."; "Conducting undisclosed research at commercial entities." |
| Data licence | "The data obtained through the API is provided under the terms of the CC-BY 4.0 licence, ..."; "You accept to the CC-BY 4.0 licence, as specified in the licence conditions." |
| Retention | "All log files will be deleted after a period of 90 days." (Open-Meteo's own server logs; this sets no retention duty on the user) |
| Competitions | Not addressed |

`https://open-meteo.com/en/license` returned no content in two attempts. The licence-conditions page, including any attribution wording Open-Meteo specifies, was therefore **not read**.

## 4. SITES observations

The raw file header (line 12) says "SITES data is licensed under a Creative Commons Attribution 4.0 international license". Line 13 requires citing SITES and acknowledging POLARIN. File SHA-256: `f3fe7cf2…e43473`. This is documented in the source file itself.

## 5. What the evidence supports, use by use

| Use | Assessment | Status |
|---|---|---|
| Internal research use in this experiment (calibration, evaluation) | Supported by the project-lead statement. Consistent with the current terms if the use is non-commercial. CC BY 4.0 data terms allow use with attribution | **APPROVED BY EXISTING AUTHORITY** (D11), with the gaps below |
| Attribution | Required: CC BY 4.0 for Open-Meteo data and for SITES. Name MET Norway as the model source. Cite SITES and acknowledge POLARIN. Open-Meteo's exact attribution wording is not read (licence page empty) | Condition on every output |
| Retention | No retention limit found for downloaded data. Not verified against the unread licence page | Unverified |
| Redistribution of the weather file or derived values | CC BY 4.0 permits redistribution with attribution. Whether the original free-API download was non-commercial is not documented | **D11-PUB: BLOCKED — EVIDENCE REQUIRED** |
| Publication of results | Same as the row above | D11-PUB |
| Competition demonstration | Not addressed by the terms. "Promotional activities" is listed as commercial, so it may conflict | D11-PUB |

## 6. Remaining documentary verification

1. An archived copy of the Open-Meteo terms and licence pages, preferably as of the download date (for example from the GitHub change history the page links to).
2. The download date.
3. The text of Open-Meteo's licence-conditions page and its attribution wording.
4. For D11-PUB, one of these:
   - the project lead's written statement that the download and the intended publication or competition use are non-commercial in the Creative Commons sense (for example, public research at a public institution);
   - or a commercial Open-Meteo subscription or licence record covering the download.
5. Optionally, MET Norway's own data licence for the underlying model output. Not checked.
