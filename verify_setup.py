#!/usr/bin/env python3
"""
Quick verification script to test path fixes
"""

from pathlib import Path
import sys
import json

APP_DIR = Path(__file__).parent

print("=" * 70)
print("PATH VERIFICATION TEST")
print("=" * 70)
print()

print(f"APP_DIR: {APP_DIR}")
print(f"APP_DIR exists: {APP_DIR.exists()}")
print()

# Test 1: Check JSON files
print("[Test 1] Checking JSON files...")
for json_file in ['banner_registry.json', 'subtitle_templates.json', 'credentials.json']:
    path = APP_DIR / json_file
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {json_file}: {path}")

    if exists and json_file == 'banner_registry.json':
        try:
            with open(path) as f:
                data = json.load(f)
                print(f"    → Contains {len(data.get('banners', []))} banners")
        except Exception as e:
            print(f"    ✗ Error loading: {e}")

print()

# Test 2: Check scripts folder
print("[Test 2] Checking scripts folder...")
scripts_dir = APP_DIR / "scripts"
print(f"  Scripts dir: {scripts_dir}")
print(f"  Exists: {scripts_dir.exists()}")

if scripts_dir.exists():
    scripts = [
        'process_streak_eligibility.py',
        'process_txn_eligibility.py',
        'process_streak_config.py',
        'process_streak_block_template.py',
        'process_scan_homepage_config.py',
        'process_ptp_streak_config.py'
    ]

    for script in scripts:
        path = scripts_dir / script
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {script}")

print()

# Test 3: Check backups folder
print("[Test 3] Checking backups folder...")
backups_dir = APP_DIR / "backups"
print(f"  Backups dir: {backups_dir}")
print(f"  Exists: {backups_dir.exists()}")

if not backups_dir.exists():
    print("  → Creating backups directory...")
    backups_dir.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ Created: {backups_dir}")

print()

# Test 4: Test imports
print("[Test 4] Testing imports...")
sys.path.insert(0, str(APP_DIR))

try:
    from setup_campaign_master import (
        load_banner_registry, load_subtitle_templates,
        determine_configs_needed
    )
    print("  ✓ setup_campaign_master imports work")

    # Test load functions
    banner_registry = load_banner_registry()
    print(f"  ✓ load_banner_registry() - {len(banner_registry['banners'])} banners")

    subtitle_templates = load_subtitle_templates()
    print(f"  ✓ load_subtitle_templates() - {len(subtitle_templates['subtitles'])} templates")

    configs = determine_configs_needed('UPI')
    print(f"  ✓ determine_configs_needed('UPI') - {len(configs)} configs")

except Exception as e:
    print(f"  ✗ Import error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print()

print("If all tests passed, the app should work correctly now!")
print()
print("To start the app:")
print("  ./start_web_app.sh")
