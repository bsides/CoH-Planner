#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Get all powerset files
powersets_dir = Path("js/data/powersets")
files_with_incomplete = {}

for file in sorted(powersets_dir.rglob("*.js")):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Look for power objects that have:
    # - allowedSetCategories: [],
    # - icon: "...", (ending with closing brace and comma)
    # - NO effects property
    
    incomplete_powers = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for start of a power object with allowedSetCategories: []
        if 'allowedSetCategories: [],' in line:
            # Start scanning for the closing brace
            start_line = i
            j = i + 1
            has_effects = False
            icon_line = None
            closing_brace_line = None
            
            brace_depth = 0
            in_effects = False
            
            while j < len(lines):
                curr_line = lines[j]
                
                # Check for effects
                if 'effects:' in curr_line:
                    has_effects = True
                
                # Check for icon (within quotes, the actual icon property)
                if re.search(r'icon:\s+"[^"]+"\s*', curr_line) and 'icon:' in curr_line:
                    icon_line = j
                
                # Check for closing brace at the start of the line or after icon
                if re.match(r'\s+},', curr_line) and not 'description:' in curr_line and not 'shortHelp' in curr_line:
                    if icon_line is not None and icon_line > start_line:
                        closing_brace_line = j
                        break
                
                j += 1
            
            # If we found an icon without effects, mark it
            if icon_line is not None and closing_brace_line is not None and not has_effects:
                # Get the power name
                power_name_match = re.search(r'name:\s+"([^"]+)"', '\n'.join(lines[start_line:icon_line+1]))
                if power_name_match:
                    power_name = power_name_match.group(1)
                    incomplete_powers.append({
                        'name': power_name,
                        'start': start_line + 1,  # 1-indexed
                        'end': closing_brace_line + 1,  # 1-indexed
                        'lines': closing_brace_line - start_line + 1
                    })
        
        i += 1
    
    if incomplete_powers:
        files_with_incomplete[str(file.relative_to(Path.cwd()))] = incomplete_powers

print(f"Found {len(files_with_incomplete)} files with incomplete powers:\n")
for filepath in sorted(files_with_incomplete.keys()):
    for power in files_with_incomplete[filepath]:
        print(f"{filepath}: Power '{power['name']}' at lines {power['start']}-{power['end']}")

# Save to file for reference
with open('incomplete_powers.txt', 'w') as f:
    for filepath in sorted(files_with_incomplete.keys()):
        f.write(f"\n{filepath}\n")
        for power in files_with_incomplete[filepath]:
            f.write(f"  Lines {power['start']}-{power['end']}: '{power['name']}'\n")

print(f"\nTotal files: {len(files_with_incomplete)}")
print(f"Total incomplete powers: {sum(len(v) for v in files_with_incomplete.values())}")
