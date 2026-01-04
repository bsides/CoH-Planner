r"""
City of Heroes: Homecoming - Power Pool Converter
Extracts and converts power pool data from raw JSON to planner format

Usage:
    python convert_pool.py <pool_name>
    Example: python convert_pool.py fighting

Input:  C:\Projects\Raw Data Homecoming\powers\pool\{pool_name}\
Output: C:\Projects\CoH-Planner\js\data\pools\{pool_name}.js
"""

import json
import sys
import os
from pathlib import Path

# Paths
RAW_DATA_DIR = Path(r"C:\Projects\Raw Data Homecoming\powers\pool")
OUTPUT_DIR = Path(r"C:\Projects\CoH-Planner\js\data\pools")

# Pool powers don't need archetype-specific tables
# They use the same values for all archetypes
TABLES = {}

def get_pool_rank(index, available_levels):
    """
    Determine pool power rank based on index and available_level
    Rank 1-2: Available at level 4
    Rank 3+: Available at level 14
    """
    if index < len(available_levels):
        level = available_levels[index]
        if level <= 0:
            return index + 1  # Rank 1-2
        elif level >= 13:
            return index + 1  # Rank 3-5
    return index + 1

def extract_effects(power_data, power_name):
    """Extract power effects from raw data"""
    effects = {}
    
    # Basic power info
    if power_data.get('accuracy'):
        effects['accuracy'] = power_data['accuracy']
    
    if power_data.get('range'):
        effects['range'] = power_data['range']
    
    if power_data.get('recharge_time'):
        effects['recharge'] = power_data['recharge_time']
    
    if power_data.get('endurance_cost'):
        effects['endurance'] = power_data['endurance_cost']
    
    if power_data.get('activation_time'):
        effects['activationTime'] = power_data['activation_time']
    
    # Effect area
    if power_data.get('effect_area'):
        effects['effectArea'] = power_data['effect_area']
        if power_data.get('radius', 0) > 0:
            effects['radius'] = power_data['radius']
        if power_data.get('arc', 0) > 0:
            effects['arc'] = power_data['arc']
    
    # Extract from effects array
    if 'effects' in power_data:
        for effect_group in power_data['effects']:
            extract_effect_templates(effect_group, effects, power_name)
    
    return effects

def extract_effect_templates(effect_group, effects, power_name):
    """Extract data from effect templates"""
    templates = effect_group.get('templates', [])
    
    for template in templates:
        attribs = template.get('attribs', [])
        aspect = template.get('aspect', '')
        scale = template.get('scale', 0)
        table_name = template.get('table', '')
        duration = template.get('duration', '0 seconds')
        magnitude = template.get('magnitude', 0)
        
        # Damage
        if aspect == 'Absolute' and any(dmg in a for a in attribs for dmg in ['_Dmg']):
            if 'damage' not in effects:
                effects['damage'] = {}
            
            for attr in attribs:
                if '_Dmg' in attr:
                    dmg_type = attr.replace('_Dmg', '').lower()
                    if dmg_type == 'special': 
                        dmg_type = 'special'
                    elif dmg_type == 'negative_energy':
                        dmg_type = 'negative'
                    
                    effects['damage']['type'] = dmg_type.title()
                    effects['damage']['scale'] = scale
                    effects['damage']['table'] = table_name
                    break
        
        # Defense
        elif aspect == 'Defense' or (aspect == 'Current' and 'Base_Defense' in attribs):
            if 'defense' not in effects:
                effects['defense'] = {}
            
            # Typed defense
            defense_types = {
                'Smashing_Def': 'smashing',
                'Lethal_Def': 'lethal',
                'Fire_Def': 'fire',
                'Cold_Def': 'cold',
                'Energy_Def': 'energy',
                'Negative_Energy_Def': 'negative',
                'Psionic_Def': 'psionic',
                'Toxic_Def': 'toxic'
            }
            
            for attr in attribs:
                if attr in defense_types:
                    def_type = defense_types[attr]
                    effects['defense'][def_type] = {
                        'scale': scale,
                        'table': table_name
                    }
                elif attr == 'Base_Defense':
                    effects['defense']['all'] = {
                        'scale': scale,
                        'table': table_name
                    }
        
        # Resistance
        elif aspect == 'Resistance':
            if 'resistance' not in effects:
                effects['resistance'] = {}
            
            resistance_types = {
                'Smashing_Dmg': 'smashing',
                'Lethal_Dmg': 'lethal',
                'Fire_Dmg': 'fire',
                'Cold_Dmg': 'cold',
                'Energy_Dmg': 'energy',
                'Negative_Energy_Dmg': 'negative',
                'Psionic_Dmg': 'psionic',
                'Toxic_Dmg': 'toxic'
            }
            
            for attr in attribs:
                if attr in resistance_types:
                    res_type = resistance_types[attr]
                    effects['resistance'][res_type] = {
                        'scale': scale,
                        'table': table_name
                    }
        
        # Healing
        elif aspect == 'Absolute' and any('Heal' in a or 'HitPoints' in a for a in attribs):
            if 'healing' not in effects:
                effects['healing'] = {}
            effects['healing']['scale'] = scale
            effects['healing']['table'] = table_name
        
        # Recovery
        elif 'Recovery' in attribs:
            if 'recovery' not in effects:
                effects['recovery'] = {}
            effects['recovery']['scale'] = scale
            effects['recovery']['table'] = table_name
        
        # Regeneration
        elif 'Regeneration' in attribs:
            if 'regeneration' not in effects:
                effects['regeneration'] = {}
            effects['regeneration']['scale'] = scale
            effects['regeneration']['table'] = table_name
        
        # Movement speeds
        elif 'RunningSpeed' in attribs or 'SpeedRunning' in attribs:
            if 'runSpeed' not in effects:
                effects['runSpeed'] = {}
            effects['runSpeed']['scale'] = scale
            effects['runSpeed']['table'] = table_name
        
        elif 'FlyingSpeed' in attribs or 'SpeedFlying' in attribs:
            if 'flySpeed' not in effects:
                effects['flySpeed'] = {}
            effects['flySpeed']['scale'] = scale
            effects['flySpeed']['table'] = table_name
        
        elif 'JumpingSpeed' in attribs or 'JumpSpeed' in attribs:
            if 'jumpSpeed' not in effects:
                effects['jumpSpeed'] = {}
            effects['jumpSpeed']['scale'] = scale
            effects['jumpSpeed']['table'] = table_name
        
        elif 'JumpHeight' in attribs:
            if 'jumpHeight' not in effects:
                effects['jumpHeight'] = {}
            effects['jumpHeight']['scale'] = scale
            effects['jumpHeight']['table'] = table_name
        
        # Mez protection (magnitude-based)
        elif aspect in ['Cur', 'Current'] and magnitude > 0:
            mez_types = {
                'Held': 'hold',
                'Stunned': 'stun',
                'Sleep': 'sleep',
                'Immobilized': 'immobilize',
                'Terrorized': 'fear',
                'Confused': 'confuse',
                'Knockback': 'knockback',
                'Knockup': 'knockup',
                'Repel': 'repel'
            }
            
            for attr in attribs:
                if attr in mez_types:
                    if 'protection' not in effects:
                        effects['protection'] = {}
                    mez_type = mez_types[attr]
                    effects['protection'][mez_type] = magnitude

def get_allowed_enhancements(power_data):
    """Extract allowed enhancement types"""
    allowed = power_data.get('boosts_allowed', [])
    
    # Map to simpler names
    enhancement_map = {
        'Enhance Damage': 'Damage',
        'Enhance Accuracy': 'Accuracy',
        'Enhance Recharge Speed': 'Recharge',
        'Reduce Endurance Cost': 'EnduranceReduction',
        'Enhance Range': 'Range',
        'Enhance Damage Resistance': 'Resistance',
        'Enhance Defense Buff': 'DefenseBuff',
        'Enhance Defense Debuff': 'DefenseDebuff',
        'Enhance Heal': 'Heal',
        'Enhance Endurance Modification': 'EnduranceModification',
        'Enhance ToHit Buff': 'ToHitBuff',
        'Enhance ToHit Debuff': 'ToHitDeb',
        'Enhance Hold': 'Hold',
        'Enhance Stun': 'Stun',
        'Enhance Immobilize': 'Immobilize',
        'Enhance Sleep': 'Sleep',
        'Enhance Slow': 'Slow',
        'Enhance Confuse': 'Confuse',
        'Enhance Fear': 'Fear',
        'Enhance Fly': 'Flight',
        'Enhance Jump': 'Jump',
        'Enhance Run Speed': 'Run',
        'Enhance Knockback': 'Knockback',
        'Enhance Taunt': 'Taunt',
        'Reduce Interrupt Time': 'InterruptReduction'
    }
    
    simplified = []
    for enh in allowed:
        if enh in enhancement_map:
            simplified.append(enhancement_map[enh])
    
    return simplified

def convert_pool(pool_name):
    """Convert a single power pool"""
    pool_dir = RAW_DATA_DIR / pool_name
    index_file = pool_dir / "index.json"
    
    if not index_file.exists():
        print(f"[FAILED] Pool not found: {pool_name}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Converting Pool: {pool_name}")
    print(f"{'='*60}")
    
    # Load pool index
    with open(index_file, 'r', encoding='utf-8') as f:
        pool_index = json.load(f)
    
    pool_data = {
        'id': pool_name,
        'name': pool_index['display_name'],
        'displayName': pool_index['display_name'],
        'description': pool_index.get('display_help', ''),
        'icon': pool_index.get('icon', f'{pool_name}_set.png'),
        'requires': pool_index.get('requires', ''),
        'powers': []
    }
    
    available_levels = pool_index.get('available_level', [])
    power_names = pool_index.get('power_names', [])
    power_display_names = pool_index.get('power_display_names', [])
    power_short_helps = pool_index.get('power_short_helps', [])
    
    print(f"Pool: {pool_data['name']}")
    print(f"Powers: {len(power_names)}")
    
    # Process each power
    for i, full_name in enumerate(power_names):
        power_file_name = full_name.split('.')[-1].lower() + '.json'
        power_file = pool_dir / power_file_name
        
        if not power_file.exists():
            print(f"  ⚠ Power file not found: {power_file_name}")
            continue
        
        with open(power_file, 'r', encoding='utf-8') as f:
            power_raw = json.load(f)
        
        display_name = power_display_names[i] if i < len(power_display_names) else power_raw['display_name']
        short_help = power_short_helps[i] if i < len(power_short_helps) else power_raw.get('display_short_help', '')
        
        power = {
            'name': display_name,
            'fullName': full_name,
            'rank': get_pool_rank(i, available_levels),
            'available': available_levels[i] if i < len(available_levels) else 0,
            'description': power_raw.get('display_help', ''),
            'shortHelp': short_help,
            'icon': power_raw.get('icon', ''),
            'powerType': power_raw.get('type', 'Click'),
            'requires': power_raw.get('requires', ''),
            'maxSlots': power_raw.get('max_boosts', 6),
            'allowedEnhancements': get_allowed_enhancements(power_raw),
            'allowedSetCategories': power_raw.get('allowed_boostset_cats', []),
            'effects': extract_effects(power_raw, display_name)
        }
        
        pool_data['powers'].append(power)
        print(f"  [OK] {display_name} (Rank {power['rank']})")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate JavaScript file
    output_file = OUTPUT_DIR / f"{pool_name}.js"
    
    js_content = f"""/**
 * City of Heroes: Homecoming - Power Pool
 * Pool: {pool_data['name']}
 * 
 * Auto-generated from game data
 * Source: {pool_dir}
 */

const POOL_{pool_name.upper().replace('-', '_')} = {json.dumps(pool_data, indent=2)};

// Register pool
if (typeof POWER_POOLS !== 'undefined') {{
    POWER_POOLS['{pool_name}'] = POOL_{pool_name.upper().replace('-', '_')};
}} else {{
    console.error('POWER_POOLS registry not found. Make sure power-pools.js is loaded first.');
}}
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\n[SUCCESS] Converted to: {output_file}")
    print(f"  Powers: {len(pool_data['powers'])}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_pool.py <pool_name>")
        print("\nAvailable pools:")
        print("  experimentation, fighting, fitness, flight, force_of_will,")
        print("  gadgetry, invisibility, leadership, leaping, manipulation,")
        print("  medicine, sorcery, speed, teleportation, utility_belt")
        return
    
    pool_name = sys.argv[1].lower().replace(' ', '_')
    
    print("City of Heroes: Homecoming - Pool Power Converter")
    print("="*60)
    
    # Convert pool
    success = convert_pool(pool_name)
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] Conversion complete!")
        print("="*60)
    else:
        print("\n[FAILED] Conversion failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
