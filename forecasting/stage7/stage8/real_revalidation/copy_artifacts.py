#!/usr/bin/env python3
import os
import hashlib
import json
import shutil
from pathlib import Path

brain_root = Path('/home/punith-bs/.gemini/antigravity/brain')
dest_dir = Path('/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/real_revalidation')
brain_current = Path('/home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd')

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Discover all relevant files in brain
artifacts = []
for p in brain_root.rglob('*'):
    if not p.is_file():
        continue
    rel = p.relative_to(brain_root)
    rel_str = str(rel)
    name = p.name
    
    if any(part.startswith('.') for part in rel.parts):
        continue
    if name.endswith(('.metadata.json', '.tmp', '.pyc', '.log', '.png', '.jpg', '.jpeg', '.docx', '.pdf', '.resolved', '.resolved.0', '.resolved.1', '.resolved.2', '.resolved.3')):
        continue
    if name in ['implementation_plan.md', 'walkthrough.md']:
        continue
    if 'scratch' in rel.parts or 'browser' in rel.parts:
        continue
        
    is_relevant = False
    if name.startswith(('STAGE8_', 'STAGE8.', 'STAGE8_1_', 'ENEV_', 'AI_', 'POLARIS_')):
        is_relevant = True
    elif any(k in name.upper() for k in ['AROME', 'MEPS', 'METAR', 'GNSS', 'IWV', 'CLOUD', 'FEASIBILITY', 'OROGRAPHIC', 'REVALIDATION', 'POSTMORTEM']):
        is_relevant = True
    else:
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)
                if 'POLARIS' in content or 'Stage 8' in content or 'Stage 8.1' in content:
                    is_relevant = True
        except Exception:
            pass
            
    if is_relevant:
        artifacts.append(p)

copied_cnt = 0
already_present_cnt = 0
conflicts_cnt = 0
failed_cnt = 0

inventory = []

for src_path in sorted(artifacts, key=lambda x: x.name):
    filename = src_path.name
    src_hash = compute_sha256(src_path)
    target_path = dest_dir / filename
    
    status = ''
    final_dest = target_path
    
    if target_path.exists():
        target_hash = compute_sha256(target_path)
        if target_hash == src_hash:
            status = 'ALREADY_PRESENT_IDENTICAL'
            already_present_cnt += 1
        else:
            # Hash mismatch - create conflict copy
            conflict_filename = f"{src_path.stem}_conflict_{src_path.parent.name[:8]}{src_path.suffix}"
            final_dest = dest_dir / conflict_filename
            try:
                shutil.copy2(src_path, final_dest)
                copied_hash = compute_sha256(final_dest)
                if copied_hash == src_hash:
                    status = 'COPIED_CONFLICT_RESOLVED'
                    conflicts_cnt += 1
                    copied_cnt += 1
                else:
                    status = 'COPY_HASH_MISMATCH'
                    failed_cnt += 1
            except Exception as e:
                status = f'COPY_FAILED: {str(e)}'
                failed_cnt += 1
    else:
        try:
            shutil.copy2(src_path, target_path)
            copied_hash = compute_sha256(target_path)
            if copied_hash == src_hash:
                status = 'COPIED_SUCCESS'
                copied_cnt += 1
            else:
                status = 'COPY_HASH_MISMATCH'
                failed_cnt += 1
        except Exception as e:
            status = f'COPY_FAILED: {str(e)}'
            failed_cnt += 1

    inventory.append({
        'filename': final_dest.name,
        'source_path': str(src_path),
        'destination_path': str(final_dest),
        'sha256': src_hash,
        'status': status
    })

# Save JSON inventory
inv_json_path = dest_dir / 'RESEARCH_ARTIFACT_COPY_INVENTORY.json'
inv_brain_json_path = brain_current / 'RESEARCH_ARTIFACT_COPY_INVENTORY.json'

inv_data = {
    'summary': {
        'number_of_files_found': len(artifacts),
        'number_copied': copied_cnt,
        'number_already_present_identical': already_present_cnt,
        'number_of_conflicts': conflicts_cnt,
        'number_failed': failed_cnt,
        'destination_path': str(dest_dir)
    },
    'inventory': inventory
}

with open(inv_json_path, 'w', encoding='utf-8') as f:
    json.dump(inv_data, f, indent=2)

shutil.copy2(inv_json_path, inv_brain_json_path)

# Save MD inventory
inv_md_path = dest_dir / 'RESEARCH_ARTIFACT_COPY_INVENTORY.md'
inv_brain_md_path = brain_current / 'RESEARCH_ARTIFACT_COPY_INVENTORY.md'

md_lines = [
    '# AI RESEARCH ARTIFACT COPY INVENTORY',
    '',
    f'**Destination Directory:** `{dest_dir}`  ',
    f'**Files Found:** {len(artifacts)}  ',
    f'**Files Copied:** {copied_cnt}  ',
    f'**Already Present & Identical:** {already_present_cnt}  ',
    f'**Conflicts Resolved:** {conflicts_cnt}  ',
    f'**Failed:** {failed_cnt}  ',
    '',
    '---',
    '',
    '## Inventory Table',
    '',
    '| Filename | Source Path | Destination Path | SHA256 | Status |',
    '| :--- | :--- | :--- | :--- | :---: |'
]

for item in inventory:
    md_lines.append(f"| `{item['filename']}` | `{item['source_path']}` | `{item['destination_path']}` | `{item['sha256'][:16]}...` | **{item['status']}** |")

md_lines.extend([
    '',
    '---',
    '*Inventory generated automatically by POLARIS Artifact Preservation System*'
])

with open(inv_md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

shutil.copy2(inv_md_path, inv_brain_md_path)

print('=== SUMMARY RESULTS ===')
print('Number of files found:', len(artifacts))
print('Number copied:', copied_cnt)
print('Number already present/identical:', already_present_cnt)
print('Number of conflicts:', conflicts_cnt)
print('Number failed:', failed_cnt)
print('Destination path:', str(dest_dir))
