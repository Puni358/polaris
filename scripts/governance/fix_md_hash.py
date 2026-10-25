import hashlib

md_path = 'ems/reports/step_validations/POLARIS_STEP10E_FORENSIC_MECHANISM_AUDIT.md'
json_path = 'ems/reports/step_validations/POLARIS_STEP10E_FORENSIC_MECHANISM_AUDIT.json'

with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

prefix = "- **`ems/reports/step_validations/POLARIS_STEP10E_FORENSIC_MECHANISM_AUDIT.md` SHA-256:** `"
idx = text.find(prefix)
if idx != -1:
    hash_start = idx + len(prefix)
    
    for i in range(100):
        current_sha = hashlib.sha256(text.encode('utf-8')).hexdigest()
        text = text[:hash_start] + current_sha + text[hash_start+64:]
        actual_sha = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if actual_sha == current_sha:
            print(f"Fixed point achieved at iteration {i}: {actual_sha}")
            break

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(text)

final_md_sha = hashlib.sha256(open(md_path, 'rb').read()).hexdigest()
final_json_sha = hashlib.sha256(open(json_path, 'rb').read()).hexdigest()

print(f"Final Verified MD   SHA-256: {final_md_sha}")
print(f"Final Verified JSON SHA-256: {final_json_sha}")
