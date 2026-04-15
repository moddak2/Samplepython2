"""Training-only marker file.

This file is intentionally *non-functional*.
It contains marker strings that the training Semgrep rules treat as simulated findings.

Do NOT implement real vulnerable logic here.
"""

# These are just markers for the scanner (not real vulnerabilities):
"TRAINING_VULN:SQL_INJECTION"
"TRAINING_VULN:BUFFER_OVERFLOW"
"TRAINING_VULN:BROKEN_AUTH"
"TRAINING_VULN:SENSITIVE_DATA_EXPOSURE"
"TRAINING_VULN:INSECURE_DESERIALIZATION"
"TRAINING_VULN:IDOR"
"TRAINING_VULN:PATH_TRAVERSAL"
