import urllib.request
import re
import datetime

dates = ["20240114", "20240414", "20240714", "20241014"]

def parse_opendap_ascii_time(txt):
    if "---------------------------------------------" not in txt:
        return []
    body = txt.split("---------------------------------------------")[1]
    # locate numbers
    lines = body.split("\n")
    # find line starting with time[
    num_str = ""
    start_collecting = False
    for line in lines:
        if "time[" in line:
            start_collecting = True
            continue
        if start_collecting:
            num_str += " " + line
    vals = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', num_str)
    return [float(v) for v in vals]

print("==================================================")
print("TASK 2: ACTUAL ARCHIVE VERIFICATION (4 SEASONS)")
print("==================================================")

for date_str in dates:
    yyyy = date_str[:4]
    mm = date_str[4:6]
    dd = date_str[6:8]
    init_time = datetime.datetime.strptime(f"{date_str}1800", "%Y%m%d%H%M").replace(tzinfo=datetime.timezone.utc)
    target_origin = datetime.datetime.strptime(f"{yyyy}-{mm}-{int(dd)+1:02d} 00:00", "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)
    
    print(f"\n--- Model Init: {date_str} 18:00 UTC | Target POLARIS Origin: {target_origin.strftime('%Y-%m-%d %H:%M')} UTC ---")
    
    # 1. AROME-Arctic
    arome_url = f"https://thredds.met.no/thredds/dodsC/aromearcticarchive/{yyyy}/{mm}/{dd}/arome_arctic_det_2_5km_{date_str}T18Z.nc.ascii?time"
    try:
        req = urllib.request.Request(arome_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            txt = resp.read().decode('utf-8')
            ts_list = parse_opendap_ascii_time(txt)
            valid_times = [datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc) for ts in ts_list]
            leads = [(vt - init_time).total_seconds() / 3600.0 for vt in valid_times]
            
            # Check POLARIS horizons H1 (00:00) through H24 (23:00)
            h1_valid = target_origin
            h24_valid = target_origin + datetime.timedelta(hours=23)
            
            has_h1 = h1_valid in valid_times
            has_h24 = h24_valid in valid_times
            
            h1_lead = (h1_valid - init_time).total_seconds() / 3600.0
            h24_lead = (h24_valid - init_time).total_seconds() / 3600.0
            
            print(f"  [AROME-Arctic 18Z] Total Steps: {len(ts_list)} | Lead Range: +{min(leads):.0f}h to +{max(leads):.0f}h")
            print(f"    H1 ({h1_valid.strftime('%Y-%m-%d %H:%M')} UTC, lead +{h1_lead:.0f}h) present: {has_h1}")
            print(f"    H24 ({h24_valid.strftime('%Y-%m-%d %H:%M')} UTC, lead +{h24_lead:.0f}h) present: {has_h24}")
    except Exception as e:
        print(f"  [AROME-Arctic 18Z] ERROR: {e}")

    # 2. MEPS Surface, PL, HL
    for file_type in ["sfc", "pl", "hl"]:
        meps_url = f"https://thredds.met.no/thredds/dodsC/meps25epsarchive/{yyyy}/{mm}/{dd}/meps_det_{file_type}_{date_str}T18Z.ncml.ascii?time"
        try:
            req = urllib.request.Request(meps_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                txt = resp.read().decode('utf-8')
                ts_list = parse_opendap_ascii_time(txt)
                valid_times = [datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc) for ts in ts_list]
                leads = [(vt - init_time).total_seconds() / 3600.0 for vt in valid_times]
                
                h1_valid = target_origin
                h24_valid = target_origin + datetime.timedelta(hours=23)
                
                has_h1 = h1_valid in valid_times
                has_h24 = h24_valid in valid_times
                
                h1_lead = (h1_valid - init_time).total_seconds() / 3600.0
                h24_lead = (h24_valid - init_time).total_seconds() / 3600.0
                
                print(f"  [MEPS {file_type.upper()} 18Z] Total Steps: {len(ts_list)} | Lead Range: +{min(leads):.0f}h to +{max(leads):.0f}h")
                print(f"    H1 ({h1_valid.strftime('%Y-%m-%d %H:%M')} UTC, lead +{h1_lead:.0f}h) present: {has_h1}")
                print(f"    H24 ({h24_valid.strftime('%Y-%m-%d %H:%M')} UTC, lead +{h24_lead:.0f}h) present: {has_h24}")
        except Exception as e:
            print(f"  [MEPS {file_type.upper()} 18Z] ERROR: {e}")

