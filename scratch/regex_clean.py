import re

filepath = r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\termly_report_generator.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to matches lines that are only = characters (at least 5) and optional whitespace
# This matches lines within triple quoted strings as well
new_content = re.sub(r'^[ \t]*=+[ \t]*$', '', content, flags=re.MULTILINE)

# Also remove them if they are followed by a newline to avoid empty lines
new_content = re.sub(r'^[ \t]*=+[ \t]*\n', '', new_content, flags=re.MULTILINE)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("regex cleanup complete")
