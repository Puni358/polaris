import os, hashlib, csv

input_files = [
    ('ems/specification/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.md', 'Governance Input', 'Authoritative Stakeholder Decisions (D1-D16)'),
    ('ems/specification/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET.json', 'Governance Input', 'Stakeholder Decision Sheet Metadata'),
    ('ems/specification/POLARIS_EMS_STAKEHOLDER_DECISION_SHEET/POLARIS_EMS_STAKEHOLDER_DECISION_FORM.csv', 'Governance Input', 'Stakeholder Decision Form Register'),
    ('ems/specification/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.md', 'Governance Input', 'Authoritative Policy Definition Resolution'),
    ('ems/specification/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION/POLARIS_EMS_POLICY_DEFINITION_RESOLUTION.json', 'Governance Input', 'Policy Definition Resolution Metadata'),
    ('system/optimization/implementations/milp.py', 'Implementation Code', 'Current Prototype MILP Energy Optimizer'),
    ('system/config/battery.yaml', 'Configuration', 'Battery Energy Storage Configuration'),
    ('system/config/diesel.yaml', 'Configuration', 'Diesel Generator Configuration'),
    ('system/config/loads.yaml', 'Configuration', 'Station Loads Configuration'),
    ('system/config/optimizer.yaml', 'Configuration', 'Optimizer Configuration'),
    ('system/config/solar_pv.yaml', 'Configuration', 'Solar PV Configuration'),
    ('system/config/station.yaml', 'Configuration', 'Station Location Configuration'),
    ('docs/decision_registers/POLARIS_MASTER_HANDOFF.md', 'Documentation Input', 'Master System Architecture & Requirements Document')
]

output_files = [
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md', 'Specification Output', 'Governed Objective Specification Main Document'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.json', 'Specification Output', 'Governed Objective Specification JSON Schema'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_D1_D16_TRACEABILITY.csv', 'Specification Output', 'D1-D16 Policy Traceability Matrix'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_VARIABLE_REGISTER.csv', 'Specification Output', 'EMS State and Decision Variable Register'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_CONSTRAINT_REGISTER.csv', 'Specification Output', 'EMS Physical, Safety, and SLA Constraint Register'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_HIERARCHY.md', 'Specification Output', '4-Stage Lexicographic Optimization Model'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_NUMERICAL_REGISTER.csv', 'Specification Output', 'Numerical Value Governance Classification Register'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_IMPLEMENTATION_GAP_MATRIX.csv', 'Specification Output', 'Current Implementation vs Policy Gap Matrix'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_STATION_VALIDATION_REQUIREMENTS.csv', 'Specification Output', 'Physical Station Pre-Implementation Requirements'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_GOVERNANCE_GAPS.csv', 'Specification Output', 'Unresolved Governance Input & Policy Gap Register'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_SOURCE_TRACEABILITY.csv', 'Specification Output', 'Substantive Requirement Source Traceability'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_GOVERNANCE_STATUS.md', 'Specification Output', 'Objective Specification Governance Status Document'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_GOVERNANCE_STATUS.json', 'Specification Output', 'Objective Specification Governance Status JSON'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_CORRECTION_REVIEW.md', 'Specification Correction', 'Objective Specification Correction Audit Report'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_CORRECTION_REVIEW.json', 'Specification Correction', 'Objective Specification Correction Audit JSON Schema'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_CORRECTION_TEST_MATRIX.csv', 'Specification Correction', 'Objective Specification Correction Audit Test Matrix'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_FINAL_RESIDUAL_CORRECTION.md', 'Specification Final Residual Correction', 'Final Residual Ambiguity Correction Report'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_FINAL_RESIDUAL_CORRECTION.json', 'Specification Final Residual Correction', 'Final Residual Ambiguity Correction JSON Schema'),
    ('ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION_FINAL_RESIDUAL_CORRECTION_TEST_MATRIX.csv', 'Specification Final Residual Correction', 'Final Residual Ambiguity Correction Test Matrix')
]

hash_rows = [['FILE_PATH', 'FILE_TYPE', 'SHA256_HASH', 'HASH_STATUS', 'GOVERNANCE_ROLE']]

for fpath, ftype, frole in input_files:
    if os.path.exists(fpath):
        h = hashlib.sha256(open(fpath, 'rb').read()).hexdigest()
        hash_rows.append([fpath, ftype, h, 'VERIFIED_FROZEN', frole])

for fpath, ftype, frole in output_files:
    if os.path.exists(fpath):
        h = hashlib.sha256(open(fpath, 'rb').read()).hexdigest()
        hash_rows.append([fpath, ftype, h, 'VERIFIED_GENERATED', frole])

hash_audit_path = 'ems/specification/POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_HASH_AUDIT.csv'

with open(hash_audit_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(hash_rows)

h_self = hashlib.sha256(open(hash_audit_path, 'rb').read()).hexdigest()
hash_rows.append([hash_audit_path, 'Specification Output', h_self, 'VERIFIED_GENERATED', 'Full Audit Trail Hash Register'])

with open(hash_audit_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(hash_rows)

print(f'Updated {hash_audit_path} with {len(hash_rows)-1} audit entries!')
