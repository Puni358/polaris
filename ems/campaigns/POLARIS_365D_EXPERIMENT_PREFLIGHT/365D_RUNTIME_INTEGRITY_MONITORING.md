# 365D RUNTIME INTEGRITY & SAFETY MONITORING

## Automated Runtime Assertions
During each closed-loop cycle $k$, the worker process enforces 4 mandatory safety assertions:

1. **Truth-Firewall Assertion**: Asserts `ForecastBundle` generated at step $k$ contains zero actual values from $t > k$.
2. **First-Action-Only Assertion**: Asserts ONLY step index $0$ of `DispatchPlan` ($P_{chg}[0], P_{dis}[0], P_{diesel}[0]$) is passed to `DigitalTwinSimulator.step()`.
3. **State Continuity Assertion**: Asserts `StationState` at step $k+1$ matches `DigitalTwinSimulator` physical step output. Zero state resets allowed.
4. **Gate-02 Option C Assertion**: Asserts MILP infeasibility triggers governed relaxation/stop without automatic Option D fallback or Digital Twin advancement.

## Violation Response
Any assertion failure immediately halts worker execution, logs error `RUNTIME_INTEGRITY_VIOLATION`, and updates run status to `FAILED_TERMINATED`.
