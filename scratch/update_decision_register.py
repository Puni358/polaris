import json
from collections import OrderedDict

def update_register(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    # 1. Update version and date
    data['version'] = '1.9.11'
    data['date'] = '2026-10-19 (twenty-first pass: RT-01 final owner authorization, fuel policy approval, Option D hash-transition ratification, and formal RT-01 closure)'

    # 2. Add top-level amendment key right after date
    new_data = OrderedDict()
    for k, v in data.items():
        new_data[k] = v
        if k == 'date':
            new_data['amendment_2026_10_19_twenty_first_pass_final_owner_authorization_and_rt01_closure'] = (
                "Twenty-first pass (2026-10-19). Project Owner formally authorized three decisive actions: "
                "(1) Fuel-limit policy APPROVED: The synthetic 100 L hard limit (initial_fuel_l = 100.0) governs physical tank depletion "
                "(Layer 1: measured 81.7166 L consumed, 18.2834 L remaining in tank; zero fuel exhaustion occurred). The evaluator's "
                "startup surcharge (Layer 2: 99.72 L total, including 18.0 L economic startup penalty across 3 starts) remains a separate "
                "economic accounting metric and must not be represented as physical fuel consumption. (2) Option D hash-transition "
                "ratification APPROVED WITH PROVENANCE CAVEAT: Patched Option D (system/optimization/implementations/option_d.py) "
                "SHA-256 688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3 ratified as current operational baseline, "
                "supported by completed evidence package eliminating pre-patch high-SOC/low-demand bus-bar residuals (+6,000 W at 95% SOC, "
                "+3,826.09 W at 94% SOC down to 0.0000 W max residual). Recorded explicitly that historical baseline source hash "
                "022cc6a0aef4e61772a7274ef3b0e772abacf16fab373feb3273d6af0f653771 remains unrecoverable and no authentic historical source-level "
                "A/B comparison is claimed. (3) RT-01 closure AUTHORIZED AND SATISFIED under governing closure rules: All 5 named closure tests "
                "in system/tests/test_offline_runtime.py (test_flexible_load_constraints, test_flexible_load_no_double_counting, "
                "test_per_timestep_conservation_audit, test_cumulative_physical_conservation_168h, test_long_duration_closed_loop_endurance_168h) "
                "passed cleanly (exit code 0 in 56.52s). Companion boundary regression tests in system/tests/test_option_d_boundary.py passed (6/6, exit code 0 in 0.13s). "
                "Full system test suite system/tests/ passed (518/518, exit code 0 in 1434.44s). 168-hour simulation metrics verified (168 timesteps, "
                "100.0% reliability, 0.0 Wh unmet load, 79.98% renewable utilization, 0.0 W max bus-bar residual, 81.7166 L physical fuel consumption, "
                "zero solver failures). RT-01 is formally CLOSED and marked resolved_with_evidence. All 6 other PROTECTED_FILES hashes re-verified byte-identical; "
                "winner: null, campaign guard, DSL-01 epsilon_tol, frozen Stage 8.1/N6 assets, and blind-data restrictions all preserved untouched. Nothing staged, committed, or pushed."
            )

    # 3. Update critical_dependency_chain_to_production
    chain = new_data.get('critical_dependency_chain_to_production', [])
    updated_chain = []
    for entry in chain:
        if 'RT-01' in entry:
            updated_chain.append(
                "RT-01 (CLOSED 2026-10-19, twenty-first pass: all 5 named closure tests passed, fuel policy approved, Option D baseline hash ratified with provenance caveat)"
            )
        else:
            updated_chain.append(entry)
    new_data['critical_dependency_chain_to_production'] = updated_chain

    # 4. Update RT-01 item
    for item in new_data.get('items', []):
        if item.get('id') == 'RT-01':
            item['current_state'] = 'resolved_with_evidence'
            item['authorized_next_action'] = (
                "None. RT-01 is formally closed with verified evidence: all 5/5 named closure tests pass, "
                "6/6 boundary tests pass, 518/518 full suite tests pass, 100 L physical fuel depletion policy approved, "
                "and Option D hash 688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3 ratified with provenance caveat."
            )
            item['authorized_next_action_post_decision_2026_10_17'] = (
                "Decision recorded 2026-10-17: Retain the diagnostic findings and defer the protected GAP19 fix to a deliberate review window. "
                "Closed with verified evidence 2026-10-19 (twenty-first pass)."
            )
            odr = item.get('owner_decision_record', {})
            odr['implementation_authorized'] = True
            odr['implementation_completed'] = True
            odr['evidence_verified'] = True
            odr['pass_2026_10_19_twenty_first_pass_final_owner_authorization_and_closure'] = (
                "Twenty-first pass (2026-10-19). Project Owner formally authorized three decisive actions: "
                "(1) Fuel-limit policy APPROVED: The synthetic 100 L hard limit (initial_fuel_l = 100.0) governs physical tank depletion "
                "(Layer 1: measured 81.7166 L consumed, 18.2834 L remaining in tank; zero fuel exhaustion occurred). The evaluator's "
                "startup surcharge (Layer 2: 99.72 L total, including 18.0 L economic startup penalty across 3 starts) remains a separate "
                "economic accounting metric and must not be represented as physical fuel consumption. (2) Option D hash-transition "
                "ratification APPROVED WITH PROVENANCE CAVEAT: Patched Option D (system/optimization/implementations/option_d.py) "
                "SHA-256 688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3 ratified as current operational baseline, "
                "supported by completed evidence package eliminating pre-patch high-SOC/low-demand bus-bar residuals (+6,000 W at 95% SOC, "
                "+3,826.09 W at 94% SOC down to 0.0000 W max residual). Recorded explicitly that historical baseline source hash "
                "022cc6a0aef4e61772a7274ef3b0e772abacf16fab373feb3273d6af0f653771 remains unrecoverable and no authentic historical source-level "
                "A/B comparison is claimed. (3) RT-01 closure AUTHORIZED AND SATISFIED under governing closure rules: All 5 named closure tests "
                "in system/tests/test_offline_runtime.py (test_flexible_load_constraints, test_flexible_load_no_double_counting, "
                "test_per_timestep_conservation_audit, test_cumulative_physical_conservation_168h, test_long_duration_closed_loop_endurance_168h) "
                "passed cleanly (exit code 0 in 56.52s). Companion boundary regression tests in system/tests/test_option_d_boundary.py passed (6/6, exit code 0 in 0.13s). "
                "Full system test suite system/tests/ passed (518/518, exit code 0 in 1434.44s). 168-hour simulation metrics verified (168 timesteps, "
                "100.0% reliability, 0.0 Wh unmet load, 79.98% renewable utilization, 0.0 W max bus-bar residual, 81.7166 L physical fuel consumption, "
                "zero solver failures). RT-01 is formally CLOSED and marked resolved_with_evidence."
            )

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Updated {json_path} successfully.")

if __name__ == '__main__':
    update_register('docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.json')
    update_register('forecasting/n6/remediation_reports/POLARIS_MASTER_DECISION_REGISTER.json')
