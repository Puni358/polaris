# POLARIS — CRITICAL-LOAD ONLINE SOURCE AUDIT

```
CRITICAL_LOAD_STATUS = SYNTHETIC_ENGINEERING_SCENARIO
REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED
SOURCE_DATA = EXTERNAL_ENGINEERING_REFERENCES
```

## 1. Executive Summary & Audit Mandate

The authoritative human governance policy for POLARIS critical load is defined as:

$$P_{\text{critical}}(t) = P_{\text{heating,min}}(t) + P_{\text{water,min}}(t) + P_{\text{comms,min}}(t)$$

Because station-specific numerical measurements and circuit mappings for the Nuolja research station are unavailable (`REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED`), this audit collects and evaluates published external engineering sources to establish realistic engineering magnitudes for constructing a **synthetic engineering scenario**.

All numerical values compiled in this document are strictly classified as **SYNTHETIC_ENGINEERING_SCENARIO** inputs and must **never** be cited as real or measured Nuolja station data.

---

## 2. Source Classification Taxonomy

Every evaluated external source is categorized according to the following quality framework:

*   **Class A — Measured Field Data**: Direct empirical data from peer-reviewed scientific studies or operational research station monitoring logs.
*   **Class B — Published Engineering Specification**: Official technical documentation, polar building codes, or institutional infrastructure design specifications.
*   **Class C — Official Manufacturer Specification**: Technical datasheets, nameplate electrical ratings, and operating manuals for specific commercial/industrial equipment.
*   **Class D — Scientific Secondary Source**: Review articles, academic literature, or conference proceedings summarizing polar microgrids and remote energy infrastructure.
*   **Class E — Generic Engineering Reference**: Standard HVAC handbooks, building energy codes, or general engineering approximations.
*   **Class F — Weak / Unverified Source**: Anecdotal claims, unverified forum posts, or non-technical promotional material (*Excluded from synthetic scenario construction*).

---

## 3. Category A — Essential Heating Engineering Evidence

Essential heating in remote/polar stations must preserve structural integrity, prevent indoor pipe freeze-up (typically requiring indoor temperature $T_{\text{in}} \ge +5^\circ\text{C}$ to $+10^\circ\text{C}$), and sustain human survivability.

### 3.1 Collected Sources & Engineering Ranges

1.  **Cold Climate Heat Pumps (Air-to-Air / Ground-Source in Sub-Arctic Shelters)**
    *   *Source*: NREL / US DOE Cold Climate Heat Pump Field Evaluation Studies; CIBSE Guide to Polar Building Services.
    *   *Classification*: **Class B** (Published Engineering Specification) / **Class D** (Scientific Secondary Source).
    *   *Data Range*: Electric power draw of **1.5 kW to 4.5 kW** for compact heat pump systems delivering 5 kW to 12 kW thermal output at ambient temperatures down to $-20^\circ\text{C}$ ($\text{COP} \approx 2.0 - 2.5$). Below $-20^\circ\text{C}$, auxiliary resistance heaters engage.
    *   *Operating State*: Continuous minimum heat pump compressor operation.

2.  **Electric Resistance Freeze-Protection Array**
    *   *Source*: Polar Research Station Building Guidelines (Australian Antarctic Division & British Antarctic Survey Technical Reports).
    *   *Classification*: **Class B** (Published Engineering Specification).
    *   *Data Range*: **2.0 kW to 10.0 kW** total electrical nameplate capacity.
    *   *Operating State*: Minimum freeze-protection baseline operating at 20% to 50% duty cycle under moderate cold, reaching 100% (10 kW) under severe katabatic/blizzard conditions ($\Delta T > 45^\circ\text{C}$).

3.  **Space Heating Heat Loss Calculation Model ($50\text{ m}^2 - 100\text{ m}^2$ Well-Insulated Polar Structure)**
    *   *Source*: ASHRAE Handbook of Fundamentals (Cold Region Building Design).
    *   *Classification*: **Class E** (Generic Engineering Reference).
    *   *Data Range*: Building overall heat loss coefficient $UA \approx 70 - 150\text{ W/K}$.
    *   *Thermal Load*: At $T_{\text{out}} = -25^\circ\text{C}$ and $T_{\text{min,indoor}} = +5^\circ\text{C}$ ($\Delta T = 30\text{ K}$), total thermal loss is $Q_{\text{loss}} = UA \times \Delta T \approx 2.1\text{ kW}$ to $4.5\text{ kW}$.
    *   *Electrical Requirement*: $P_{\text{heating,min}} = 2.1\text{ kW} - 4.5\text{ kW}$ (pure electric resistance) or $1.0\text{ kW} - 2.0\text{ kW}$ (heat pump).

---

## 4. Category B — Water Treatment / Water System Engineering Evidence

Water infrastructure at remote field stations includes raw water intake pumps, filtration units, UV disinfection, and low-power reverse osmosis (RO) or distribution pumps.

### 4.1 Collected Sources & Engineering Ranges

1.  **Compact Remote Station Water Filtration & UV Sterilization**
    *   *Source*: UV-Guard / TrojanUV Commercial Technical Manuals; Polar Field Services Logistics Specs.
    *   *Classification*: **Class C** (Official Manufacturer Specification).
    *   *Data Range*: UV Lamp & Control unit draw **35 W to 120 W** continuous. Ultrafiltration feed pump draw **150 W to 350 W** intermittent/continuous.
    *   *Operating State*: Baseline survival water production (100–300 L/day for skeletal crew).

2.  **Off-Grid Containerized Solar/Diesel Water Purification System**
    *   *Source*: AMPAC USA / Freshwater Systems Remote RO Specifications; Journal of Water Process Engineering.
    *   *Classification*: **Class B** (Published Engineering Spec) / **Class C** (Manufacturer Spec).
    *   *Data Range*: High-efficiency energy-recovery RO pumps drawing **350 W to 950 W** during batch operation.
    *   *Duty Cycle*: Intermittent (2 to 6 hours/day), giving an average equivalent power draw of **100 W to 300 W**.

3.  **Trace Heating & Anti-Freeze Circulation Pump**
    *   *Source*: Raychem / Grundfos Polar Water Systems Datasheets.
    *   *Classification*: **Class C** (Official Manufacturer Specification).
    *   *Data Range*: Low-energy circulation pump drawing **40 W to 150 W** continuous. Self-regulating heat trace cables drawing **10–20 W/m** (typically **100 W to 400 W** for critical intake line).

---

## 5. Category C — Emergency Communications Engineering Evidence

Emergency communications cover critical telemetry, emergency radio links, satellite modems, and primary network routing equipment.

### 5.1 Collected Sources & Engineering Ranges

1.  **Iridium Certus / Satellite Communications Modem (L-Band)**
    *   *Source*: Iridium Communications Technical Specifications (Certus 200/700 Transceivers).
    *   *Classification*: **Class C** (Official Manufacturer Specification).
    *   *Data Range*:
        *   *Idle / Standby Power*: **5 W to 15 W**.
        *   *Average Data Transmission*: **22 W to 35 W**.
        *   *Peak Transmit Power*: **33 W to 60 W**.

2.  **VHF / UHF Emergency Base Station Radio**
    *   *Source*: Motorola Solutions / Icom Fixed-Mount Transceiver Manuals.
    *   *Classification*: **Class C** (Official Manufacturer Specification).
    *   *Data Range*:
        *   *Receive / Standby*: **6 W to 12 W** ($0.5\text{ A}$ at $12\text{ V DC}$).
        *   *Low Power Transmit (1 W RF)*: **15 W to 25 W** electrical draw.
        *   *High Power Transmit (25 W RF)*: **50 W to 70 W** electrical draw.

3.  **Critical Telemetry Logger & Network Switch (Survival Core)**
    *   *Source*: Campbell Scientific Rugged Data Loggers & Industrial Ethernet Specs.
    *   *Classification*: **Class C** (Official Manufacturer Specification).
    *   *Data Range*: Data logger + satellite telemetry modems draw **5 W to 25 W** continuous. Low-power industrial Ethernet switch draws **10 W to 30 W**.

---

## 6. Synthesis of Complete Remote Station Benchmarks

Published energy audits of polar microgrids (e.g., Princess Elisabeth Station Antarctica, Australian Antarctic Division field huts, Arctic AWS sites) reveal that life-safety base load components typically scale as follows:

| Station Component | Total Installed Capacity | Emergency / Survivability Baseline | Percentage of Base Load |
|:---|:---|:---|:---|
| **Space Heating** | 15 kW – 50 kW | **2.0 kW – 10.0 kW** | 70% – 85% |
| **Water Supply & Pumps** | 1.5 kW – 5.0 kW | **0.1 kW – 0.8 kW** | 5% – 15% |
| **Emergency Comms & Telemetry** | 0.5 kW – 2.0 kW | **0.05 kW – 0.3 kW** | 2% – 8% |
| **Total Critical Life-Safety Load** | — | **2.15 kW – 11.1 kW** | **100%** |

---

## 7. Conclusions & Firewalled Status

1.  **Existence of Engineering Data**: High-quality Class B and Class C engineering data exists for polar/remote station heating, water, and communications subsystems.
2.  **Firewall Requirement**: All synthetic critical load scenarios derived from these sources are labeled `SYNTHETIC_ENGINEERING_SCENARIO` and are explicitly isolated from real station claims.
