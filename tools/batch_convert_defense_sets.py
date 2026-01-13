#!/usr/bin/env python3
"""
Batch convert all defensive powersets for Brute, Scrapper, Stalker, Sentinel, and Tanker
"""
import subprocess
from pathlib import Path

# Configuration
RAW_DATA_DIR = Path(r"C:\Projects\Raw Data Homecoming\powers")
TABLES_DIR = Path(r"C:\Projects\Raw Data Homecoming\tables")
OUTPUT_DIR = Path(r"C:\Projects\CoH-Planner\js\data\powersets")
CONVERT_SCRIPT = Path(__file__).parent / "convert_powerset.py"

# Define all defensive powersets to convert
DEFENSIVE_SETS = [
    # Brute secondaries (defense)
    ("brute_defense", "brute", [
        "bio_organic_armor",
        "dark_armor",
        "electric_armor",
        "energy_aura",
        "fiery_aura",
        "ice_armor",
        "invulnerability",
        "psionic_armor",
        "radiation_armor",
        "regeneration",
        "shield_defense",
        "stone_armor",
        "super_reflexes",
        "willpower"
    ]),

    # Scrapper secondaries (defense)
    ("scrapper_defense", "scrapper", [
        "bio_organic_armor",
        "dark_armor",
        "electric_armor",
        "energy_aura",
        "fiery_aura",
        "ice_armor",
        "invulnerability",
        "ninjitsu",
        "radiation_armor",
        "regeneration",
        "shield_defense",
        "super_reflexes",
        "willpower"
    ]),

    # Stalker secondaries (defense)
    ("stalker_defense", "stalker", [
        "bio_organic_armor",
        "dark_armor",
        "electric_armor",
        "energy_aura",
        "ice_armor",
        "invulnerability",
        "ninjitsu",
        "radiation_armor",
        "regeneration",
        "shield_defense",
        "super_reflexes",
        "willpower"
    ]),

    # Sentinel secondaries (defense)
    ("sentinel_defense", "sentinel", [
        "bio_organic_armor",
        "dark_armor",
        "electric_armor",
        "energy_aura",
        "fiery_aura",
        "ice_armor",
        "invulnerability",
        "ninjitsu",
        "radiation_armor",
        "regeneration",
        "super_reflexes",
        "willpower"
    ]),

    # Tanker primaries (defense)
    ("tanker_defense", "tanker", [
        "bio_organic_armor",
        "dark_armor",
        "electric_armor",
        "energy_aura",
        "fiery_aura",
        "ice_armor",
        "invulnerability",
        "psionic_armor",
        "radiation_armor",
        "regeneration",
        "shield_defense",
        "stone_armor",
        "super_reflexes",
        "willpower"
    ])
]

def convert_powerset(raw_dir, archetype, powerset_name, output_path):
    """Convert a single powerset"""
    cmd = [
        "python",
        str(CONVERT_SCRIPT),
        str(raw_dir / powerset_name),
        str(output_path),
        f"--archetype={archetype}",
        "--level=50",
        f"--tables={TABLES_DIR}"
    ]

    print(f"\n{'='*60}")
    print(f"Converting: {archetype}/{powerset_name}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode != 0:
            print(f"ERROR: Conversion failed with return code {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main conversion process"""
    total = 0
    succeeded = 0
    failed = 0

    for raw_subdir, archetype, powersets in DEFENSIVE_SETS:
        raw_dir = RAW_DATA_DIR / raw_subdir
        output_subdir = OUTPUT_DIR / archetype

        # Ensure output directory exists
        output_subdir.mkdir(parents=True, exist_ok=True)

        for powerset_name in powersets:
            total += 1

            # Convert underscores to hyphens for output filename
            output_filename = powerset_name.replace('_', '-') + '.js'
            output_path = output_subdir / output_filename

            # Convert the powerset
            if convert_powerset(raw_dir, archetype, powerset_name, output_path):
                succeeded += 1
            else:
                failed += 1
                print(f"FAILED: {archetype}/{powerset_name}")

    # Summary
    print(f"\n{'='*60}")
    print(f"CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total powersets: {total}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
