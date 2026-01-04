"""
Generate HTML script tags for all converted pool files
Outputs ready-to-paste <script> tags for index.html
"""

import os
from pathlib import Path

POOLS_DIR = Path(r"C:\Projects\CoH-Planner\js\data\pools")

def generate_script_tags():
    """Generate <script> tags for all pool files"""
    
    if not POOLS_DIR.exists():
        print(f"Error: Pools directory not found: {POOLS_DIR}")
        return
    
    # Get all .js files
    pool_files = sorted([f.stem for f in POOLS_DIR.glob("*.js")])
    
    if not pool_files:
        print("No pool files found. Run batch converter first.")
        return
    
    print("="*70)
    print("POOL POWER SCRIPT TAGS FOR INDEX.HTML")
    print("="*70)
    print()
    print("Copy and paste these into index.html:")
    print()
    print("<!-- Power Pools Registry -->")
    print('<script src="js/data/power-pools.js"></script>')
    print()
    print("<!-- Individual Pool Files -->")
    
    for pool in pool_files:
        print(f'<script src="js/data/pools/{pool}.js"></script>')
    
    print()
    print("="*70)
    print(f"Total pools: {len(pool_files)}")
    print("="*70)

if __name__ == "__main__":
    generate_script_tags()
