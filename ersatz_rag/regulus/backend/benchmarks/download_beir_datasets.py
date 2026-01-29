#!/usr/bin/env python3
"""
Download BEIR Datasets for Benchmarking

Downloads and verifies BEIR datasets needed for comprehensive evaluation.
Can download individual datasets or all Phase 1/2/3 datasets.
"""

import os
import sys
import zipfile
import argparse
from pathlib import Path
from typing import List, Dict
import urllib.request
import json

# BEIR dataset URLs
BEIR_BASE_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets"

DATASETS = {
    # Phase 1: Small datasets
    "phase1": ["scifact", "arguana", "fiqa", "trec-covid", "scidocs"],

    # Phase 2: Medium datasets
    "phase2": ["quora", "dbpedia-entity", "robust04"],

    # Phase 3: Large datasets
    "phase3": ["msmarco", "nq", "hotpotqa", "fever", "climate-fever", "signal1m"],

    # Already completed
    "completed": ["nfcorpus"]
}

# Dataset sizes (approximate, in MB)
DATASET_SIZES = {
    "nfcorpus": 5,
    "scifact": 8,
    "arguana": 12,
    "fiqa": 30,
    "trec-covid": 120,
    "scidocs": 40,
    "quora": 250,
    "dbpedia-entity": 2000,
    "robust04": 350,
    "msmarco": 4000,
    "nq": 1500,
    "hotpotqa": 2500,
    "fever": 2500,
    "climate-fever": 2500,
    "signal1m": 1800
}


class BEIRDatasetDownloader:
    """Download and manage BEIR datasets"""

    def __init__(self, datasets_dir: str = "/Volumes/WS4TB/newragcity/UltraRAG-main/datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self, dataset_name: str, force: bool = False) -> bool:
        """Download a single BEIR dataset"""

        dataset_path = self.datasets_dir / dataset_name

        # Check if already exists
        if dataset_path.exists() and not force:
            if self._verify_dataset(dataset_name):
                print(f"✅ {dataset_name} already downloaded and verified")
                return True
            else:
                print(f"⚠️  {dataset_name} exists but verification failed, re-downloading...")

        print(f"\n📥 Downloading {dataset_name}...")
        print(f"   URL: {BEIR_BASE_URL}/{dataset_name}.zip")
        print(f"   Size: ~{DATASET_SIZES.get(dataset_name, 'unknown')} MB")

        zip_path = self.datasets_dir / f"{dataset_name}.zip"

        try:
            # Download with progress
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(downloaded * 100 / total_size, 100)
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')

            url = f"{BEIR_BASE_URL}/{dataset_name}.zip"
            urllib.request.urlretrieve(url, zip_path, reporthook=report_progress)
            print()  # New line after progress

            # Extract
            print(f"   Extracting {dataset_name}.zip...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.datasets_dir)

            # Clean up zip
            zip_path.unlink()

            # Verify
            if self._verify_dataset(dataset_name):
                print(f"✅ {dataset_name} downloaded and verified successfully")
                return True
            else:
                print(f"❌ {dataset_name} download failed verification")
                return False

        except Exception as e:
            print(f"❌ Failed to download {dataset_name}: {str(e)}")
            if zip_path.exists():
                zip_path.unlink()
            return False

    def _verify_dataset(self, dataset_name: str) -> bool:
        """Verify dataset has required files"""

        dataset_path = self.datasets_dir / dataset_name

        required_files = [
            "corpus.jsonl",
            "queries.jsonl",
            "qrels/test.tsv"
        ]

        for file_name in required_files:
            file_path = dataset_path / file_name
            if not file_path.exists():
                print(f"   Missing: {file_name}")
                return False

        return True

    def download_phase(self, phase: int) -> Dict[str, bool]:
        """Download all datasets for a specific phase"""

        phase_key = f"phase{phase}"
        if phase_key not in DATASETS:
            print(f"❌ Invalid phase: {phase}")
            return {}

        datasets = DATASETS[phase_key]

        print(f"\n{'='*70}")
        print(f"DOWNLOADING PHASE {phase} DATASETS")
        print(f"{'='*70}")
        print(f"Datasets: {', '.join(datasets)}")
        total_size = sum(DATASET_SIZES.get(d, 0) for d in datasets)
        print(f"Total size: ~{total_size} MB")
        print(f"{'='*70}\n")

        results = {}
        for dataset in datasets:
            results[dataset] = self.download_dataset(dataset)

        # Summary
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'='*70}")
        print(f"PHASE {phase} DOWNLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"Successful: {success_count}/{len(datasets)}")

        for dataset, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {dataset}")

        print(f"{'='*70}\n")

        return results

    def download_all(self) -> Dict[str, bool]:
        """Download all BEIR datasets (all phases)"""

        print(f"\n{'='*70}")
        print("DOWNLOADING ALL BEIR DATASETS")
        print(f"{'='*70}")

        all_datasets = []
        for phase in [1, 2, 3]:
            all_datasets.extend(DATASETS[f"phase{phase}"])

        total_size = sum(DATASET_SIZES.get(d, 0) for d in all_datasets)
        print(f"Total datasets: {len(all_datasets)}")
        print(f"Total size: ~{total_size} MB (~{total_size/1024:.1f} GB)")
        print(f"{'='*70}\n")

        results = {}

        for phase in [1, 2, 3]:
            phase_results = self.download_phase(phase)
            results.update(phase_results)

        # Final summary
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'='*70}")
        print("FINAL DOWNLOAD SUMMARY")
        print(f"{'='*70}")
        print(f"Total downloaded: {success_count}/{len(all_datasets)}")
        print(f"Ready for benchmarking: {'✅ YES' if success_count == len(all_datasets) else '⚠️  PARTIAL'}")
        print(f"{'='*70}\n")

        return results

    def list_downloaded(self):
        """List all downloaded datasets"""

        print(f"\n{'='*70}")
        print("DOWNLOADED BEIR DATASETS")
        print(f"{'='*70}\n")

        all_datasets = []
        for phase_datasets in DATASETS.values():
            all_datasets.extend(phase_datasets)

        for dataset in sorted(all_datasets):
            dataset_path = self.datasets_dir / dataset
            if dataset_path.exists():
                if self._verify_dataset(dataset):
                    print(f"✅ {dataset:20s} (verified)")
                else:
                    print(f"⚠️  {dataset:20s} (incomplete)")
            else:
                print(f"❌ {dataset:20s} (not downloaded)")

        print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Download BEIR datasets for benchmarking"
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3],
        help="Download specific phase (1=small, 2=medium, 3=large)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Download specific dataset"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all datasets (all phases)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List downloaded datasets"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if exists"
    )
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default="/Volumes/WS4TB/newragcity/UltraRAG-main/datasets",
        help="Path to datasets directory"
    )

    args = parser.parse_args()

    downloader = BEIRDatasetDownloader(datasets_dir=args.datasets_dir)

    if args.list:
        downloader.list_downloaded()

    elif args.dataset:
        downloader.download_dataset(args.dataset, force=args.force)

    elif args.phase:
        downloader.download_phase(args.phase)

    elif args.all:
        downloader.download_all()

    else:
        # Default: list what's available
        print("Use --help for options")
        print("\nQuick start:")
        print("  python download_beir_datasets.py --phase 1  # Download Phase 1 (small datasets)")
        print("  python download_beir_datasets.py --all      # Download all datasets")
        print("  python download_beir_datasets.py --list     # List what's downloaded")


if __name__ == "__main__":
    main()
