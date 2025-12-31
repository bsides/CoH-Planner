#!/usr/bin/env python3
import os
import re
from pathlib import Path

powersets_dir = Path("js/data/powersets")
incomplete_entries = []

for file in sorted(powersets_dir.rglob("*.js")):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find power objects that have allowedSetCategories: [] but no effects:
    # Pattern: { name: "...", ...allowedSetCategories: [],... icon: "..." },
    # without "effects:" in between
    
    # Split into potential power objects
    parts = re.split(r'(\{[^{}]*?allowedSetCategories:\s*\[\][^{}]*?\},)', content)
    
    for i, part in enumerate(parts):
        if 'allowedSetCategories: []' in part and '},\n' in part:
            # Check if this part has 'effects:' - if not, it's incomplete
            if 'effects:' not in part:
                # Extract power name
                name_match = re.search(r'name:\s+"([^"]+)"', part)
                if name_match:
                    power_name = name_match.group(1)
                    # Count which line number this is at
                    pos = sum(len(p) for p in parts[:i])
                    line_num = content[:pos].count('\n') + 1
                    incomplete_entries.append({
                        'file': str(file.relative_to(Path.cwd())),
                        'name': power_name,
                        'line': line_num,
                        'object': part.strip()
                    })

print(f"Found {len(incomplete_entries)} incomplete power entries:\n")
for entry in incomplete_entries[:20]:
    print(f"{entry['file']} (line {entry['line']}): '{entry['name']}'")

if len(incomplete_entries) > 20:
    print(f"... and {len(incomplete_entries) - 20} more")

# Save full details
with open('incomplete_powers_detailed.txt', 'w') as f:
    for entry in incomplete_entries:
        f.write(f"\n{entry['file']} (line {entry['line']}): '{entry['name']}'\n")
        f.write(f"Object:\n{entry['object'][:200]}...\n")

print(f"\nTotal: {len(incomplete_entries)} incomplete entries")
