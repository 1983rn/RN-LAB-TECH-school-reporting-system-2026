import sys

filepath = r'd:\2025-2026\PRODUCTION\USA\RN-LAB-TECH-school-reporting-system-2026-1\termly_report_generator.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.strip()
    # Check for separator lines (all = characters and at least 10 of them)
    if all(c == '=' for c in stripped) and len(stripped) >= 10:
        continue
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned separator lines.")
