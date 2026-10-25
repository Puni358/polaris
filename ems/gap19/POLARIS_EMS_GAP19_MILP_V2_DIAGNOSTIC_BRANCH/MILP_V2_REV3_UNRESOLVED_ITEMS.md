# Explicit List: What Remains Unresolved After Rev. 3

No code, config, or model changed in producing this list. GAP19 remains frozen as the
control.

1. **Infeasibility → OptionD routing** — withdrawn in Rev. 3 as confirmed invalid; no
   replacement mechanism identified. Resolving this requires either a new, currently
   unspecified way to produce a genuinely `EMERGENCY`-conditioned `EmergencyAssessment` for
   an already-`NORMAL`-classified cycle, or acceptance of GAP19's existing degenerate
   zero-dispatch infeasibility fallback as the answer for this case.
2. **Tier 2 vs. Tier 3 mapping** for `curtailable_loads` — explicitly a labeled judgment
   call, not a derived fact; no document resolves which tier it belongs to.
3. **Whether `deferrable_loads`' true scheduling/deferral semantics should be modeled** in
   some future revision — out of scope for v2 as specified; not addressed.
4. **Whether the flat `essential_demand[t]` profile is adequate even for research
   purposes**, absent real circuit-level timing data (SD-01).
5. **The inherited (pre-existing, not new) tension** between GAP19's existing nonzero `J4`
   curtailment coefficient and D10's "no explicit objective penalty for necessary
   curtailment" language — now also applies to `P_unmet_essential` by extension, since both
   share the same coefficient. Not resolved by this revision; flagged as inherited.
6. **All terminal-reserve items already open from the earlier governance audits**
   (DEC-TR-03 unit, DEC-RES-03 numeric value, SD-07/SD-08 station data) — unaffected by
   anything in Rev. 1–3, since terminal reserve was deliberately left unchanged throughout.
7. **D16 named approval authorities (SD-13)** — still no real individuals named; nothing in
   this design track resolves it.

## STOP
