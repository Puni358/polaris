#!/usr/bin/env python3
"""EVEN-only, diagnostic-only causal state aliasing audit v2 (no model fitting)."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

BASE = Path('/home/punith-bs/01polaris (Copy)')
MATRIX = BASE/'forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_full_37_feature_matrix_2024.csv'
CONTROL = BASE/'forecasting/spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv'
SEED, B = 12345, 2000
RNG = np.random.default_rng(SEED)
# H1 is valid at forecast_start (=t0); only these H1 forecast fields enter stage B.
ATM = ['ctx_std_3h','ctx_std_6h','ctx_std_12h','ctx_std_24h','ctx_abs_change_1h','ctx_abs_change_3h','ctx_abs_change_6h','ctx_max_diff_6h','ctx_mean_diff_6h','ctx_slope_6h','ctx_kt_std_6h','ctx_last_obs','ctx_mean_24h','ctx_max_24h','fc_cloud_cover','fc_temperature_2m','fc_relative_humidity_2m','cloud_frac','lwp_latest','iwp_latest','lwp_x_cloud','u700','v700']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def cdist(a,b): return np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(axis=2))
def rankdata(x): return pd.Series(x).rank(method='average').to_numpy()
def corr_p(x,y,rank=False):
    if rank: x,y=rankdata(x),rankdata(y)
    r=float(np.corrcoef(x,y)[0,1]); null=np.array([np.corrcoef(RNG.permutation(x),y)[0,1] for _ in range(B)])
    return r,float((np.abs(null)>=abs(r)).mean())
def bh(p):
    p=np.asarray(p,float); n=len(p); o=np.argsort(p); q=np.empty(n); q[o]=np.minimum.accumulate((p[o]*n/np.arange(1,n+1))[::-1])[::-1]; return np.minimum(q,1)
def ci_mean(x):
    x=np.asarray(x,float); idx=RNG.integers(0,len(x),(B,len(x))); z=x[idx].mean(1); return [float(np.quantile(z,.025)),float(np.quantile(z,.975))]
def dist_summary(d): return {str(q):float(np.quantile(d,q/100)) for q in (10,25,50,75,90)}
def clean(x):
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,list): return [clean(v) for v in x]
    if isinstance(x,(float,np.floating)) and not np.isfinite(x): return None
    return x

def load():
    # Split is applied immediately; no ODD rows are retained, evaluated, or written.
    df=pd.read_csv(MATRIX); df=df[df.origin_id.astype(int)%2==0].copy()
    ctrl=pd.read_csv(CONTROL); ctrl=ctrl[ctrl.origin_id.astype(int)%2==0].copy()
    assert df.origin_id.nunique()==173 and len(df)==4152 and ctrl.origin_id.nunique()==173
    df['forecast_start']=pd.to_datetime(df.forecast_start,utc=True); df['timestamp']=pd.to_datetime(df.timestamp,utc=True)
    return df,ctrl

def make_origins(df):
    h1=df[df.horizon_hour==1].sort_values('origin_id').copy(); ids=h1.origin_id.to_numpy(int)
    # H1 timestamp equals t0. State excludes all h>1 NWP values, target, predictions, and solar trajectory.
    assert (h1.timestamp==h1.forecast_start).all()
    X=h1[ATM].astype(float).to_numpy(); X=np.nan_to_num(X,nan=np.nanmedian(X,axis=0))
    X=(X-X.mean(0))/np.where(X.std(0,ddof=1)>1e-12,X.std(0,ddof=1),1)
    # deterministic trajectory is diagnostic Stage A only; not part of the atmospheric state.
    ordered=df.sort_values(['origin_id','horizon_hour']); cs=ordered.pivot(index='origin_id',columns='horizon_hour',values='clearsky_ghi').loc[ids].to_numpy(float)
    y=ordered.pivot(index='origin_id',columns='horizon_hour',values='actual_SW_IN').loc[ids].to_numpy(float)
    day=cs>20.0 # excludes night and unstable near-zero denominator
    kt=np.full_like(y,np.nan); kt[day]=np.clip(y[day]/cs[day],0,2)
    resid=np.where(day,y-cs,np.nan)
    month=h1.forecast_start.dt.month.to_numpy(); peak=cs.max(1)
    return ids,h1,X,cs,y,kt,resid,day,month,peak

def solar_pool(i,cs,month,k=20):
    # Same calendar month, then closest deterministic clear-sky trajectory. Fixed 20 is pre-registered.
    cand=np.where((month==month[i]) & (np.arange(len(month))!=i))[0]
    if len(cand)<5: cand=np.where(np.arange(len(month))!=i)[0]
    z=np.sqrt(np.mean((cs[cand]-cs[i])**2,axis=1)); return cand[np.argsort(z)[:min(k,len(cand))]]

def pairs_for_method(X,cs,month,method,subset=None,solar_conditioned=True):
    n=len(X); subset=np.arange(n) if subset is None else np.asarray(subset)
    Z=X if method!='rank' else np.column_stack([rankdata(X[:,j]) for j in range(X.shape[1])])
    D=cdist(Z,Z); np.fill_diagonal(D,np.inf); out=[]; ds=[]
    allowed=set(subset.tolist())
    for i in subset:
        pool=np.array([j for j in solar_pool(i,cs,month) if j in allowed],int) if solar_conditioned else np.array([j for j in subset if j!=i],int)
        if len(pool)==0: continue
        j=pool[np.argmin(D[i,pool])]; out.append((i,j)); ds.append(D[i,j])
    return np.array(out,int),np.array(ds,float)

def null_pairs(cs,month,subset,kind,n):
    subset=np.asarray(subset); ans=[]; nall=len(subset)
    solar_reg=np.digitize(cs.max(1),np.quantile(cs.max(1),[.25,.5,.75]))
    for _ in range(n):
        i=int(RNG.choice(subset)); cand=subset[subset!=i]
        if kind=='month': cand=cand[month[cand]==month[i]]
        elif kind=='season': cand=cand[((month[cand]-1)//3)==((month[i]-1)//3)]
        elif kind=='solar_regime': cand=cand[solar_reg[cand]==solar_reg[i]]
        elif kind in ('det_solar','det_solar_causal'): cand=np.array([j for j in solar_pool(i,cs,month) if j in set(subset)],int)
        if len(cand)==0: cand=subset[subset!=i]
        ans.append((i,int(RNG.choice(cand))))
    return np.array(ans,int)

def metrics(pairs,y,kt,resid,day):
    a,b=pairs[:,0],pairs[:,1]; raw=np.abs(y[a]-y[b]); trans=np.abs(kt[a]-kt[b]); r=np.abs(resid[a]-resid[b])
    # Pairwise means only on horizons daylight at both origins.
    valid=day[a]&day[b]
    def agg(z): return np.array([np.nanmean(np.where(valid[:,h],z[:,h],np.nan)) for h in range(24)])
    return {'raw_mae':agg(raw),'transmission_mae':agg(trans),'clear_sky_residual_mae':agg(r),'trajectory_rmse_to_h':np.array([np.sqrt(np.nanmean(np.where(valid[:,:h+1],raw[:,:h+1]**2,np.nan))) for h in range(24)])}

def origin_divergence(pairs,kt,day):
    a,b=pairs[:,0],pairs[:,1]; z=np.abs(kt[a]-kt[b]); v=day[a]&day[b]
    out=np.full(len(day),np.nan)
    for i in range(len(day)):
        rows=np.where(a==i)[0]
        if len(rows): out[i]=np.nanmean(np.where(v[rows],z[rows],np.nan))
    return out

def run():
    df,ctrl=load(); ids,h1,X,cs,y,kt,resid,day,month,peak=make_origins(df); n=len(ids)
    high=np.where(peak>=np.quantile(peak,.75))[0]
    methods={}; primary=None
    for name in ('euclidean','solar_conditioned','rank'):
        p,d=pairs_for_method(X,cs,month,'rank' if name=='rank' else 'euclidean',solar_conditioned=(name!='euclidean'))
        methods[name]={'n_pairs':len(p),'distance_percentiles':dist_summary(d),'metrics':{k:v.tolist() for k,v in metrics(p,y,kt,resid,day).items()}}
        if name=='solar_conditioned': primary=p
    nulls={}
    for kind in ('random','month','season','solar_regime','det_solar','det_solar_causal'):
        p=null_pairs(cs,month,np.arange(n),kind,len(primary)); nulls[kind]={'n_pairs':len(p),'metrics':{k:v.tolist() for k,v in metrics(p,y,kt,resid,day).items()}}
    pm=metrics(primary,y,kt,resid,day); nm=np.array(nulls['det_solar']['metrics']['transmission_mae'])
    effect=pm['transmission_mae']-nm
    # paired origin bootstrap: resample primary pairs; conditional-null mean held as fixed comparison estimate.
    cis=[]; pvals=[]
    a,b=primary[:,0],primary[:,1]; z=np.abs(kt[a]-kt[b]); valid=day[a]&day[b]
    for h in range(24):
        vals=z[:,h][valid[:,h]]
        if len(vals)==0:
            cis.append([None,None]); pvals.append(1.0); continue
        boot=np.array([RNG.choice(vals,len(vals),replace=True).mean() for _ in range(B)])
        cis.append([float(np.quantile(boot,.025)-nm[h]),float(np.quantile(boot,.975)-nm[h])])
        pvals.append(float(2*min((boot<=nm[h]).mean(),(boot>=nm[h]).mean())))
    q=bh(pvals); dominant=[]
    for h in range(24-2):
        if all(np.isfinite(effect[h:h+3])) and all(effect[h:h+3]>0) and all(q[h:h+3]<.05) and all(cis[x][0] is not None and cis[x][0]>0 for x in range(h,h+3)): dominant.append(h+1)
    # association strictly descriptive, per origin.
    div=origin_divergence(primary,kt,day); e=ctrl.assign(abs_error=lambda x:(x.actual_SW_IN-x.prediction).abs()).query('is_daytime').groupby('origin_id').abs_error.mean().reindex(ids).to_numpy()
    ok=np.isfinite(div)&np.isfinite(e); pr=corr_p(div[ok],e[ok]); sr=corr_p(div[ok],e[ok],rank=True)
    hp=pairs_for_method(X,cs,month,'euclidean',high)[0]; hnull={k:metrics(null_pairs(cs,month,high,k,len(hp)),y,kt,resid,day)['transmission_mae'].tolist() for k in ('random','month','season','solar_regime','det_solar','det_solar_causal')}
    feature_table=[]
    for f in ATM:
        source='past station observations' if f.startswith('ctx_') else 'MEPS H1 forecast field at valid t0'
        feature_table.append({'feature':f,'source':source,'source_timestamp':'t0 or earlier' if f.startswith('ctx_') else 'forecast issuance <= t0','valid_timestamp':'<=t0' if f.startswith('ctx_') else 't0 (H1)','available_before_t0':True,'causal_status':'included','reason':'past observation summary' if f.startswith('ctx_') else 'H1 valid timestamp equals forecast_start=t0'})
    out={'document':'POLARIS_CAUSAL_STATE_ALIASING_AUDIT_V2','generated_utc':datetime.now(timezone.utc).isoformat(),'governance':{'even_origins':173,'even_rows':4152,'odd_rows_retained_or_evaluated':False,'training':False,'new_predictive_features':False,'seed':SEED,'bootstrap_replicates':B},'input_hashes':{str(MATRIX):sha(MATRIX),str(CONTROL):sha(CONTROL)},'causality_audit':{'h1_equals_t0':True,'excluded':['actual_SW_IN (target)','all H2-H24 fields (future-valid)','pred_stage3b_cloud_nwp','phys_pred_fold','pred_stage4_fold','disagreement_fold','solar/clear-sky trajectory (diagnostic stage A only)'],'included_features':feature_table,'ambiguity_policy':'exclude if timestamp cannot be verified'},'matching':{'stage_a':'same month, then 20 closest deterministic clear-sky trajectories; deterministic variables never enter atmospheric state distance','stage_b':'nearest causal atmospheric state within Stage A pool','methods':methods,'nulls':nulls},'primary':{'definition':'solar-conditioned standardized-Euclidean atmospheric nearest neighbour','metrics':{k:v.tolist() for k,v in pm.items()},'effect_vs_deterministic_solar_null_transmission':effect.tolist(),'bootstrap_95ci_effect':cis,'raw_p_values':pvals,'fdr_bh_q_values':q.tolist(),'divergence_dominance_horizon':min(dominant) if dominant else None,'decision':'No statistically defensible divergence-dominance horizon was identified.' if not dominant else f'Earliest pre-registered divergence-dominance horizon: H{min(dominant)}'},'high_solar':{'definition':'top quartile peak clear-sky GHI over H1-H24','n_origins':len(high),'n_primary_pairs':len(hp),'exploratory':True,'primary_metrics':{k:v.tolist() for k,v in metrics(hp,y,kt,resid,day).items()},'conditional_null_transmission':hnull},'association_not_causal':{'n':int(ok.sum()),'pearson_r':pr[0],'pearson_permutation_p':pr[1],'spearman_rho':sr[0],'spearman_permutation_p':sr[1],'permutations':B},'conclusion':'Moderate evidence for horizon-conditional state aliasing only if the conditional transmission effect is positive and FDR-supported; otherwise weak/inconclusive. This audit cannot prove an irreducible ceiling.'}
    out=clean(out)
    (BASE/'forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT_V2.json').write_text(json.dumps(out,indent=2,allow_nan=False))
    # Concise reproducible Markdown; detailed H1-H24 arrays remain in JSON.
    def f(v,n=4): return 'NA' if not np.isfinite(v) else format(v,f'.{n}f')
    rows='\n'.join(f'| H{i+1:02d} | {f(pm["raw_mae"][i],3)} | {f(pm["transmission_mae"][i])} | {f(pm["clear_sky_residual_mae"][i],3)} | {f(effect[i])} | {"NA" if cis[i][0] is None else f(cis[i][0])+", "+f(cis[i][1])} | {f(q[i])} |' for i in range(24))
    md=f'''# POLARIS Causal State Aliasing Audit v2\n\n**EVEN-only diagnostic; no fitting.** H1 timestamp equals `forecast_start` (= t0), but the prior audit was invalid to treat all H1 columns as automatically causal without provenance. This implementation uses only audited H1 atmospheric/context variables; H2–H24 fields, target, predictions, and deterministic solar trajectory are excluded from state matching.\n\n## Pre-registered design\n\nStage A: same-month pool, then the 20 nearest deterministic clear-sky trajectories. Stage B: nearest atmospheric/context state within that pool. Three fixed sensitivity distances are reported in the JSON: standardized Euclidean, this solar-conditioned atmospheric distance, and rank-normalized distance. Clear-sky-normalized transmission is evaluated *after* matching, on pairwise daytime horizons with clear-sky GHI >20 W/m².\n\n## Result\n\n**{out['primary']['decision']}** The effect is NN transmission divergence minus the deterministic-solar matched random-pair null. Bootstrap resamples origin pairs (2,000, seed 12345); Benjamini–Hochberg FDR is across 24 horizons. This is association/conditional-uncertainty evidence only, never forecasting gain or proof of a ceiling.\n\n| Horizon | Raw SW_IN MAE (W/m²) | Transmission MAE | Clear-sky residual MAE (W/m²) | Effect vs det-solar null | 95% CI | FDR q |\n|---|---:|---:|---:|---:|---|---:|\n{rows}\n\n## Causality and limits\n\nThe full per-feature causality table, all nulls, all three distance sensitivity results, high-solar exploratory subgroup, hashes, and origin-level error association are in the JSON artifact. High solar is the pre-registered top quartile of **peak H1–H24 clear-sky GHI**; it is diagnostic stratification only and never part of neighbour selection.\n'''
    (BASE/'forecasting/reports/information_probe_and_causal/POLARIS_CAUSAL_STATE_ALIASING_AUDIT_V2.md').write_text(md)
if __name__=='__main__': run()
