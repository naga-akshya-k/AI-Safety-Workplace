"""
Industrial Safety Dataset Downloader & Harmonization Ingestion Utility
Public Data Sources:
1. WHD (Workplace Hazards Dataset) — Primary hazard dataset
2. SH17 (17-Class Manufacturing & PPE Dataset) — Primary broad PPE dataset
3. SHEL5K — Person, head, and helmet disambiguation
4. SHWD (Safety Helmet Wearing Dataset) — High-density crowd and distance helmet detection
"""

import os
import sys
import json
import urllib.request
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw_datasets"

DATASET_SOURCES = {
    "SHWD": {
        "name": "Safety Helmet Wearing Dataset (SHWD)",
        "git_url": "https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset.git",
        "description": "High-density crowd and distance helmet vs. exposed head detection",
        "format": "VOC XML / YOLO",
        "primary_domain": "Helmet vs No-Helmet in dense crowds"
    },
    "SHEL5K": {
        "name": "SHEL5K: Safety Helmet & Person Dataset",
        "git_url": "https://github.com/MoyoG/SHEL5K.git",
        "description": "5,000 images with 6 classes disambiguating worker body, head, and helmet",
        "format": "YOLO / Roboflow",
        "primary_domain": "Worker, Head, and Helmet disambiguation"
    },
    "SH17": {
        "name": "SH17 Manufacturing & Human Safety PPE Dataset",
        "git_url": "https://github.com/ahmadmughees/sh17dataset.git",
        "kaggle_slug": "ahmadmughees/sh17dataset",
        "description": "8,099 images with 17 classes covering full PPE (vest, helmet, boots, gloves, goggles, earmuffs)",
        "format": "YOLO / COCO",
        "primary_domain": "Broad multi-gear PPE compliance"
    },
    "WHD": {
        "name": "Workplace Hazards Dataset (WHD)",
        "repo_url": "https://github.com/ahmadmughees/whd-dataset",
        "description": "Industrial hazard scenes: machinery pinch points, vehicle corridors, chemical spills, fire/smoke",
        "format": "YOLO / Custom",
        "primary_domain": "Industrial hazards and dynamic unsafe situations"
    }
}

def verify_public_accessibility():
    """Verifies that each dataset repository / source is publicly reachable."""
    print("=" * 70)
    print("VERIFYING PUBLIC ACCESSIBILITY OF PRIMARY DATASETS")
    print("=" * 70)
    
    results = {}
    for key, info in DATASET_SOURCES.items():
        git_url = info.get("git_url") or info.get("repo_url")
        print(f"[*] Checking {key} ({info['name']})...")
        print(f"    Source URL: {git_url}")
        try:
            cmd = ["git", "ls-remote", "--heads", git_url]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if proc.returncode == 0:
                print(f"    [OK] Publicly accessible via Git! Heads found: {len(proc.stdout.strip().splitlines())}")
                results[key] = {"accessible": True, "method": "git", "url": git_url}
            else:
                print(f"    [!] Git probe failed, trying HTTP head request...")
                req = urllib.request.Request(git_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"    [OK] Publicly accessible via HTTP (Status: {resp.status})")
                    results[key] = {"accessible": True, "method": "http", "url": git_url}
        except Exception as e:
            print(f"    [!] Note: {e}")
            results[key] = {"accessible": False, "error": str(e), "url": git_url}
    
    print("\nAccessibility Verification Summary:")
    for k, v in results.items():
        status = "ACCESSIBLE" if v.get("accessible") else "REQUIRES_AUTH_OR_MIRROR"
        print(f" - {k:8s}: {status} ({v.get('url', '')})")
    print("=" * 70)
    return results

def download_git_subsets(target_datasets=None, shallow=True):
    """Clones public Git repositories into data/raw_datasets."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if target_datasets is None:
        target_datasets = ["SHWD", "SHEL5K", "SH17"]
    
    for key in target_datasets:
        if key not in DATASET_SOURCES:
            continue
        info = DATASET_SOURCES[key]
        git_url = info.get("git_url")
        if not git_url:
            continue
        
        dest_dir = RAW_DATA_DIR / key
        if dest_dir.exists():
            print(f"[i] {key} already downloaded at {dest_dir}. Skipping clone.")
            continue
        
        print(f"[*] Downloading {key} from {git_url} into {dest_dir}...")
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1"])
        cmd.extend([git_url, str(dest_dir)])
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[OK] Successfully downloaded {key} into {dest_dir}")
        except Exception as e:
            print(f"[ERROR] Failed to clone {key}: {e}")

def print_manual_download_instructions():
    """Prints instructions for datasets requiring Kaggle CLI or Roboflow API keys."""
    print("\n" + "=" * 70)
    print("INSTRUCTIONS FOR DOWNLOADING FULL MULTI-GIGABYTE RAW ARCHIVES")
    print("=" * 70)
    print("""
1. SH17 Full Dataset (Kaggle, ~2.8 GB, 8,099 images):
   Requires Kaggle API token (~/.kaggle/kaggle.json).
   Command:
     kaggle datasets download -d ahmadmughees/sh17dataset -p data/raw_datasets/SH17_kaggle --unzip

2. SHEL5K Dataset (GitHub / Roboflow, ~500 MB, 5,000 images):
   Direct clone:
     git clone --depth 1 https://github.com/MoyoG/SHEL5K.git data/raw_datasets/SHEL5K

3. SHWD Dataset (GitHub, ~1.8 GB, 7,581 images):
   Direct clone:
     git clone --depth 1 https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset.git data/raw_datasets/SHWD

4. WHD (Workplace Hazards Dataset):
   Direct clone or download from research archive:
     git clone --depth 1 https://github.com/ahmadmughees/whd-dataset.git data/raw_datasets/WHD

Once downloaded, run:
  python scripts/curate_safety_datasets.py --ingest-raw
to automatically harmonize, deduplicate with 64-bit dHash, and integrate into data/curated_safety_dataset/.
""")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Industrial Safety Datasets Downloader")
    parser.add_argument("--verify-only", action="store_true", help="Verify public accessibility only")
    parser.add_argument("--download-git", action="store_true", help="Download public Git datasets (SHWD, SHEL5K, SH17)")
    args = parser.parse_args()

    results = verify_public_accessibility()
    if args.download_git:
        download_git_subsets()
    else:
        print_manual_download_instructions()
