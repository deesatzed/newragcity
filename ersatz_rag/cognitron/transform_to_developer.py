#!/usr/bin/env python3
"""
Transform Cognitron from medical focus to developer workspace tool
Removes all medical/clinical/HIPAA references and rebrands appropriately
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

class CognitronTransformer:
    """Transforms medical Cognitron to developer-focused tool"""
    
    def __init__(self):
        self.medical_terms = [
            "medical", "clinical", "hipaa", "patient", "clinical-grade", 
            "medical-grade", "clinical-level", "patient safety"
        ]
        
        self.replacements = {
            # Core concept replacements
            "medical-grade": "enterprise-grade",
            "medical AI": "developer AI",
            "clinical-level": "production-level",
            "clinical": "production",
            "medical": "developer",
            "HIPAA": "privacy",
            "patient": "user",
            "patient safety": "data safety",
            
            # Threshold replacements  
            "medical_threshold": "accuracy_threshold",
            "meets_medical_threshold": "meets_accuracy_threshold",
            "medical threshold": "accuracy threshold",
            
            # Description replacements
            "Medical-grade confidence": "Enterprise-grade confidence",
            "medical-grade": "enterprise-grade", 
            "clinical decision": "development decision",
            "medical decision": "development decision",
            
            # Purpose rebranding
            "medical document processing": "developer documentation processing",
            "medical AI quality": "development AI quality",
            "clinical validation": "accuracy validation"
        }
        
        self.files_modified = []
        
    def transform_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Transform a single file, return count of changes and change list"""
        
        if not file_path.exists() or file_path.suffix != '.py':
            return 0, []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        content = original_content
        changes = []
        
        # Apply replacements
        for old, new in self.replacements.items():
            if old in content:
                # Case-sensitive replacement
                content = content.replace(old, new)
                changes.append(f"'{old}' → '{new}'")
                
                # Also handle title case
                old_title = old.title()
                new_title = new.title()
                if old_title in content:
                    content = content.replace(old_title, new_title)
                    
        # Special handling for docstrings and comments
        content = self._transform_descriptions(content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_modified.append(str(file_path))
            
        return len(changes), changes
    
    def _transform_descriptions(self, content: str) -> str:
        """Transform medical descriptions to developer focus"""
        
        # Transform docstring descriptions
        transformations = [
            (r"medical-grade ([^\"]*)", r"enterprise-grade \1"),
            (r"Clinical ([^\"]*)", r"Production \1"),
            (r"Medical ([^\"]*)", r"Developer \1"),
            (r"HIPAA-compliant ([^\"]*)", r"Privacy-focused \1"),
            (r"patient ([^\"]*)", r"user \1"),
        ]
        
        for pattern, replacement in transformations:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
        return content
    
    def transform_directory(self, directory: Path) -> dict:
        """Transform all Python files in directory"""
        
        results = {
            "files_processed": 0,
            "files_modified": 0,
            "total_changes": 0,
            "changes_by_file": {}
        }
        
        for py_file in directory.rglob("*.py"):
            results["files_processed"] += 1
            
            change_count, changes = self.transform_file(py_file)
            
            if change_count > 0:
                results["files_modified"] += 1
                results["total_changes"] += change_count
                results["changes_by_file"][str(py_file)] = changes
                
        return results
    
    def verify_transformation(self) -> dict:
        """Verify medical terms have been removed"""
        
        cognitron_dir = Path("cognitron")
        remaining_medical = []
        
        for py_file in cognitron_dir.rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
            for term in self.medical_terms:
                if term.lower() in content:
                    # Find line numbers
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if term.lower() in line:
                            remaining_medical.append(f"{py_file}:{i} - {line.strip()}")
                            
        return {
            "remaining_medical_references": len(remaining_medical),
            "references": remaining_medical[:10]  # Show first 10
        }


def main():
    print("🔄 COGNITRON TRANSFORMATION: Medical → Developer")
    print("="*60)
    
    transformer = CognitronTransformer()
    
    # Transform all files
    print("📝 Transforming Python files...")
    results = transformer.transform_directory(Path("cognitron"))
    
    print(f"\n📊 TRANSFORMATION RESULTS:")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Files modified: {results['files_modified']}")
    print(f"   Total changes: {results['total_changes']}")
    
    if results['changes_by_file']:
        print(f"\n📋 Changes by file:")
        for file_path, changes in results['changes_by_file'].items():
            print(f"   {file_path}: {len(changes)} changes")
            for change in changes[:3]:  # Show first 3 changes per file
                print(f"      • {change}")
            if len(changes) > 3:
                print(f"      • ... and {len(changes)-3} more")
    
    # Verify transformation
    print(f"\n🔍 VERIFICATION:")
    verification = transformer.verify_transformation()
    
    if verification['remaining_medical_references'] == 0:
        print("✅ SUCCESS: All medical references removed!")
    else:
        print(f"⚠️  WARNING: {verification['remaining_medical_references']} medical references remain")
        print("First few remaining references:")
        for ref in verification['references']:
            print(f"   • {ref}")
    
    # Update main descriptions
    print(f"\n🏷️  REBRANDING COMPLETE")
    print("   Cognitron is now focused on developer workspace unification")
    print("   Medical components extracted to Thalamus")
    
    return verification['remaining_medical_references'] == 0

if __name__ == "__main__":
    success = main()