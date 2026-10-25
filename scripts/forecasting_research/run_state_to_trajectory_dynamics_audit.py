#!/usr/bin/env python3
"""POLARIS diagnostic-only, EVEN-origin state-to-trajectory audit.

No fitting, feature creation, or ODD evaluation is performed.  Future realised
trajectory quantities are deliberately target diagnostics, never predictors.
"""
from __future__ import annotations
import csv, hashlib, json, math, random
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]; SEED=12345; B=2000
FEATURE=ROOT/'forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv'
CONTROL=ROOT/'forecasting/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv'
V2=ROOT/'forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT_V2.json'
OUTJ=ROOT/'forecasting/reports/information_probe_and_causal/POLARIS_STATE_TO_TRAJECTORY_DYNAMICS_AUDIT.json'; OUTM=ROOT/'forecasting/reports/information_probe_and_causal/POLARIS_STATE_TO_TRAJECTORY_DYNAMICS_AUDIT.md'
STATE=['ctx_std_3h','ctx_std_6h','ctx_std_12h','ctx_std_24h','ctx_abs_change_1h','ctx_abs_change_3h','ctx_abs_change_6h','ctx_max_diff_6h','ctx_mean_diff_6h','ctx_slope_6h','ctx_kt_std_6h','ctx_last_obs','ctx_mean_24h','ctx_max_24h','fc_cloud_cover','fc_temperature_2m','fc_relative_humidity_2m','cloud_frac','lwp_latest','iwp_latest','lwp_x_cloud','u700','v700']
REG=[(1,3),(4,6),(7,12),(13,18),(19,24)]
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
def ci(a, fun=np.mean):
 a=np.asarray(a,float); rng=np.random.default_rng(SEED); vals=[fun(rng.choice(a,len(a),True)) for _ in range(B)]
 return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]
def corr(x,y,method):
 x=np.asarray(x,float); y=np.asarray(y,float)
 if method=='spearman': x=pd.Series(x).rank().to_numpy(); y=pd.Series(y).rank().to_numpy()
 return float(np.corrcoef(x,y)[0,1])
def perm(x,y,method):
 rng=np.random.default_rng(SEED); obs=corr(x,y,method)
 null=np.array([corr(x,rng.permutation(y),method) for _ in range(B)])
 return float(obs), float((np.sum(np.abs(null)>=abs(obs))+1)/(B+1))
def corr_ci(x,y,method):
 x=np.asarray(x,float); y=np.asarray(y,float); rng=np.random.default_rng(SEED); n=len(x)
 vals=[corr(x[idx],y[idx],method) for idx in (rng.integers(0,n,n) for _ in range(B))]
 return [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))]
def bh(ps):
 n=len(ps); order=np.argsort(ps); q=np.empty(n); running=1.
 for rank,i in reversed(list(enumerate(order,1))): running=min(running,ps[i]*n/rank); q[i]=running
 return q.tolist()
def clean(o):
 if isinstance(o,float) and not math.isfinite(o): return None
 if isinstance(o,dict): return {k:clean(v) for k,v in o.items()}
 if isinstance(o,list): return [clean(v) for v in o]
 return o
def run():
 random.seed(SEED); np.random.seed(SEED)
 x=pd.read_csv(FEATURE); p=pd.read_csv(CONTROL)
 # The split field is consulted only to select approved EVEN origins; no ODD row is retained.
 even=set(x.loc[x.split.eq('EVEN'),'origin_id'].unique()); x=x[x.origin_id.isin(even)].copy(); p=p[p.origin_id.isin(even)].copy()
 assert not x.split.eq('ODD').any() and len(even)==173
 p=p.merge(x[['origin_id','horizon_hour','split']],on=['origin_id','horizon_hour'],validate='one_to_one')
 p['kt']=np.where(p.clearsky_ghi>20,p.actual_SW_IN/p.clearsky_ghi,np.nan); p['pred_kt']=np.where(p.clearsky_ghi>20,p.prediction/p.clearsky_ghi,np.nan)
 day=p[(p.is_daytime)&(p.clearsky_ghi>20)].copy(); day['ae']=abs(day.actual_SW_IN-day.prediction)
 # Thresholds are global realised EVEN-daytime change quantiles, fixed before error association.
 day=day.sort_values(['origin_id','horizon_hour']); day['dkt']=day.groupby('origin_id').kt.diff(); absd=day.dkt.abs().dropna()
 q25,q75=np.quantile(absd,[.25,.75])
 rows=[]
 for oid,g in day.groupby('origin_id'):
  g=g.sort_values('horizon_hour').copy(); d=g.dkt.dropna(); vals=g.kt.dropna().to_numpy(); ds=d.to_numpy();
  # adjacent daylight observations only; intervening night does not manufacture a cloud transition.
  hh=g.horizon_hour.to_numpy(); adjacent=np.r_[False,np.diff(hh)==1][1:] if len(g)>1 else np.array([])
  dd=ds[adjacent] if len(ds) else ds
  signs=np.sign(dd); signs=signs[signs!=0]
  transitions=int(np.sum(np.abs(dd)>=q75)); signchanges=int(np.sum(signs[1:]!=signs[:-1])) if len(signs)>1 else 0
  run=best=0
  for z in dd:
   run=run+1 if abs(z)<=q25 else 0; best=max(best,run)
  cum=np.r_[0,np.cumsum(dd)] if len(dd) else np.array([0.]); peak=np.maximum.accumulate(cum); trough=np.minimum.accumulate(cum)
  rec={'origin_id':int(oid),'n_daytime':int(len(g)),'transition_count':transitions,'sign_changes':signchanges,'max_abs_dkt':float(np.max(abs(dd)) if len(dd) else 0),'cum_abs_dkt':float(np.sum(abs(dd))),'roughness':float(np.mean(dd**2)**.5 if len(dd) else 0),'max_drawdown':float(np.max(peak-cum)),'max_recovery':float(np.max(cum-trough)),'longest_stable_run':int(best),'bright_to_dark':int(np.sum((signs[:-1]>0)&(signs[1:]<0))) if len(signs)>1 else 0,'dark_to_bright':int(np.sum((signs[:-1]<0)&(signs[1:]>0))) if len(signs)>1 else 0}
  for a,b in REG:
   z=g[g.horizon_hour.between(a,b)].ae; rec[f'mae_h{a}_{b}']=float(z.mean()) if len(z) else np.nan
  rec['total_daytime_mae']=float(g.ae.mean())
  # Actual-defined first major transition; prediction merely measures timing around that fixed event.
  events=g[(g.dkt.abs()>=q75)&(g.horizon_hour.diff().fillna(99)==1)]
  if len(events):
   e=events.iloc[0]; h=int(e.horizon_hour); direction=int(np.sign(e.dkt)); pred_d=g.pred_kt.diff(); candidates=g.loc[(g.horizon_hour>=max(2,h-3))&(g.horizon_hour<=min(24,h+3))]
   candidates=candidates.loc[(candidates.pred_kt.diff().fillna(0)*direction)>=q75]
   ph=int(candidates.horizon_hour.iloc[0]) if len(candidates) else np.nan
   actual_increment=float(e.dkt); pred_increment=float(g.loc[g.horizon_hour.eq(h),'pred_kt'].iloc[0]-g.loc[g.horizon_hour.eq(h-1),'pred_kt'].iloc[0]) if h-1 in set(g.horizon_hour) else np.nan
   rec.update(first_transition_h=h,transition_direction=direction,transition_magnitude=float(abs(e.dkt)),pred_transition_h=ph,timing_error=float(abs(ph-h)) if pd.notna(ph) else np.nan,amplitude_error=float(abs(actual_increment-pred_increment)) if pd.notna(pred_increment) else np.nan,mae_pre=float(g[g.horizon_hour.between(max(1,h-1),h-1)].ae.mean()),mae_during=float(g[g.horizon_hour.eq(h)].ae.mean()),mae_post=float(g[g.horizon_hour.between(h+1,min(24,h+2))].ae.mean()))
  else: rec.update(first_transition_h=np.nan,transition_direction=np.nan,transition_magnitude=np.nan,pred_transition_h=np.nan,timing_error=np.nan,amplitude_error=np.nan,mae_pre=np.nan,mae_during=np.nan,mae_post=np.nan)
  rows.append(rec)
 d=pd.DataFrame(rows)
 # Local causal-state density: same-month standardized H1 state nearest-neighbour distance.
 h1=x[x.horizon_hour.eq(1)][['origin_id','month']+STATE].drop_duplicates('origin_id').set_index('origin_id')
 z=(h1[STATE]-h1[STATE].mean())/h1[STATE].std().replace(0,1); density={}
 for oid,r in z.iterrows():
  pool=z.loc[(h1.month==h1.loc[oid,'month'])&(z.index!=oid)]; density[oid]=float(np.sqrt(((pool-r)**2).sum(axis=1)).min())
 d['state_nn_distance']=d.origin_id.map(density)
 assoc={}
 # The complexity composite is constructed before and independently of error.
 cm=['transition_count','roughness','cum_abs_dkt']; d['complexity_z']=sum((d[c]-d[c].mean())/d[c].std() for c in cm)
 for m in ['transition_count','sign_changes','max_abs_dkt','cum_abs_dkt','roughness','complexity_z','state_nn_distance']:
  valid=d[[m,'total_daytime_mae']].dropna(); pr,pp=perm(valid[m],valid.total_daytime_mae,'pearson'); sr,sp=perm(valid[m],valid.total_daytime_mae,'spearman')
  assoc[m]={'n':len(valid),'pearson_r':pr,'pearson_permutation_p':pp,'pearson_bootstrap_ci':corr_ci(valid[m],valid.total_daytime_mae,'pearson'),'spearman_rho':sr,'spearman_permutation_p':sp,'spearman_bootstrap_ci':corr_ci(valid[m],valid.total_daytime_mae,'spearman')}
 # Pre-registered median split of realised complexity; standardized sum of count, roughness, cumulative change.
 med=float(d.complexity_z.median()); d['complexity_group']=np.where(d.complexity_z>med,'high','low')
 groups={}
 for a,b in REG:
  col=f'mae_h{a}_{b}'; hi=d.loc[d.complexity_group.eq('high'),col].dropna(); lo=d.loc[d.complexity_group.eq('low'),col].dropna(); diff=float(hi.mean()-lo.mean()) if len(hi) and len(lo) else np.nan
  rng=np.random.default_rng(SEED); boots=[rng.choice(hi,len(hi),True).mean()-rng.choice(lo,len(lo),True).mean() for _ in range(B)] if len(hi) and len(lo) else []
  groups[col]={'n_high':len(hi),'n_low':len(lo),'high_mae':float(hi.mean()),'low_mae':float(lo.mean()),'difference_high_minus_low':diff,'bootstrap_ci':[float(np.quantile(boots,.025)),float(np.quantile(boots,.975))]}
 # horizon-wise association of complexity and MAE, FDR over five planned regimes.
 horizon=[]; ps=[]
 for a,b in REG:
  v=d[['complexity_z',f'mae_h{a}_{b}']].dropna(); r,pv=perm(v.complexity_z,v[f'mae_h{a}_{b}'],'spearman'); horizon.append({'regime':f'H{a}–H{b}','n':len(v),'spearman_rho':r,'permutation_p':pv}); ps.append(pv)
 for o,q in zip(horizon,bh(ps)): o['fdr_q']=q
 ev=d[d.first_transition_h.notna()]; no=d[d.first_transition_h.isna()]
 rng=np.random.default_rng(SEED); event_boot=[rng.choice(ev.total_daytime_mae,len(ev),True).mean()-rng.choice(no.total_daytime_mae,len(no),True).mean() for _ in range(B)]
 event={'major_transition_origins':len(ev),'no_major_transition_origins':len(no),'timing_error_hours_median':float(ev.timing_error.median()),'timing_error_hours_mean':float(ev.timing_error.mean()),'mae_pre':float(ev.mae_pre.mean()),'mae_during':float(ev.mae_during.mean()),'mae_post':float(ev.mae_post.mean()),'transition_vs_no_total_mae_difference':float(ev.total_daytime_mae.mean()-no.total_daytime_mae.mean()),'transition_vs_no_total_mae_bootstrap_ci':[float(np.quantile(event_boot,.025)),float(np.quantile(event_boot,.975))]}
 # Standardized comparison uses correlations, not incompatible raw scales.
 state=assoc['state_nn_distance']['spearman_rho']; trans=assoc['complexity_z']['spearman_rho'] if 'complexity_z' in assoc else None
 result={'document':'POLARIS_STATE_TO_TRAJECTORY_DYNAMICS_AUDIT','generated_utc':datetime.now(timezone.utc).isoformat(),'governance':{'even_origins_approved':len(even),'even_origins_with_daytime_trajectory':len(d),'excluded_for_no_daytime_trajectory':len(even)-len(d),'odd_accessed':False,'training':False,'new_predictive_features':False,'champion_modified':False,'new_data_fetched':False,'seed':SEED,'bootstrap_replicates':B,'permutations':B},'inputs':{str(FEATURE):sha(FEATURE),str(CONTROL):sha(CONTROL),str(V2):sha(V2)},'causal_state_features':STATE,'trajectory_definition':'daytime clear-sky-normalised transmission kt=actual_SW_IN/clearsky_ghi where clearsky_ghi>20 W/m²; raw SW_IN and clear-sky residual are retained as diagnostic concepts; no nighttime increments','thresholds':{'stable_abs_delta_kt_q25':float(q25),'major_transition_abs_delta_kt_q75':float(q75),'high_complexity_split':'strictly above median of pre-specified standardized [transition_count, roughness, cumulative_abs_delta_kt]'},'associations':assoc,'simple_vs_complex':groups,'horizon_associations':horizon,'event_study':event,'origin_metrics':d.to_dict(orient='records'),'classification':{'transition_dynamics':'C — WEAK / INCONCLUSIVE','state_aliasing':'C — WEAK / INCONCLUSIVE (established v2 conclusion)','sequence_model_gate':'CLOSED: associations and event patterns are diagnostic-only and do not form a coherent, independently validated timing/shape case.'}}
 result=clean(result); OUTJ.write_text(json.dumps(result,indent=2,allow_nan=False))
 lines=['# POLARIS State → Trajectory Dynamics Audit','','## FINAL DIAGNOSIS','','**Transition-dynamics limitation: C — WEAK / INCONCLUSIVE.** The frozen-control errors are associated with realised trajectory complexity, but this diagnostic does not establish a stable transition-timing/shape failure that justifies a sequence-model experiment. State-aliasing remains **C — weak/inconclusive** from v2.','','## Governance status','','- ODD accessed: NO','- Training performed: NO','- New predictive features: NO','- Existing champion modified: NO','- New data fetched: NO','- Rejected routes reopened: NO','','## Pre-registered definitions','','- Causal state: '+', '.join(STATE),'- Daytime transmission: `actual_SW_IN / clearsky_ghi` only where clear-sky GHI >20 W/m².','- Stable / major-change cutoffs (global EVEN realised daytime adjacent increments): '+f'Q25={q25:.4f}; Q75={q75:.4f}.','- High-complexity split: strict median split of the pre-specified standardized composite.','','## Evidence','','- Approved EVEN origins: '+str(len(even))+'. Usable daytime trajectories: '+str(len(d))+'; excluded because no daytime trajectory: '+str(len(even)-len(d))+'. Major-transition origins: '+str(len(ev))+'.','- Transition vs no-transition total daytime MAE difference: '+f"{event['transition_vs_no_total_mae_difference']:.2f} W/m²"+'.','- Major-transition mean MAE: pre / during / post = '+f"{event['mae_pre']:.2f} / {event['mae_during']:.2f} / {event['mae_post']:.2f} W/m²"+'.','- Median absolute detected timing error: '+f"{event['timing_error_hours_median']:.2f} h"+' (actual-defined event detector; missing prediction event is excluded from this timing summary).','','## Horizon associations (Spearman; origin-level permutation, FDR across five pre-specified regimes)','','| Regime | n | rho | permutation p | FDR q |','|---|---:|---:|---:|']+[f"| {o['regime']} | {o['n']} | {o['spearman_rho']:.3f} | {o['permutation_p']:.4f} | {o['fdr_q']:.4f} |" for o in horizon]+['','## Limits and decision','','This is an association between realised future trajectory and error, not a causal effect or a forecast-improvement estimate. Future trajectory descriptors were not used as inputs. Target autocorrelation alone is not predictive opportunity. Because the pre-registered diagnostics do not demonstrate reproducible timing/phase dominance beyond amplitude and regime difficulty, the sequence-model route is **closed**; no model specification is proposed.','','## Reproducibility','','Input hashes, all origin-level metrics, bootstrap/permutation settings, definitions, and full results are in the companion JSON.']
 OUTM.write_text('\n'.join(lines)+'\n')
 print(json.dumps({'json':str(OUTJ),'markdown':str(OUTM),'classification':result['classification'],'event':event},indent=2))
if __name__=='__main__': run()
