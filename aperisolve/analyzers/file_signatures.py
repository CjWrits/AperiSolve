"""File signature detection analyzer."""

from pathlib import Path
from typing import Dict, List, Tuple

from .utils import update_data

# Common file signatures (magic bytes)
FILE_SIGNATURES = {
    b'\x89PNG\r\n\x1a\n': 'PNG Image',
    b'\xff\xd8\xff': 'JPEG Image',
    b'GIF87a': 'GIF Image (87a)',
    b'GIF89a': 'GIF Image (89a)',
    b'BM': 'BMP Image',
    b'RIFF': 'RIFF Container (AVI/WAV)',
    b'PK\x03\x04': 'ZIP Archive',
    b'PK\x05\x06': 'ZIP Archive (empty)',
    b'PK\x07\x08': 'ZIP Archive (spanned)',
    b'\x1f\x8b\x08': 'GZIP Archive',
    b'Rar!\x1a\x07\x00': 'RAR Archive (v1.5)',
    b'Rar!\x1a\x07\x01\x00': 'RAR Archive (v5.0)',
    b'7z\xbc\xaf\x27\x1c': '7-Zip Archive',
    b'\x50\x4b\x03\x04': 'ZIP/JAR/APK Archive',
    b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'Microsoft Office Document',
    b'%PDF': 'PDF Document',
    b'\x7fELF': 'ELF Executable',
    b'MZ': 'Windows Executable',
    b'\xca\xfe\xba\xbe': 'Java Class File',
    b'\xfe\xed\xfa\xce': 'Mach-O Binary (32-bit)',
    b'\xfe\xed\xfa\xcf': 'Mach-O Binary (64-bit)',
    b'#!/bin/sh': 'Shell Script',
    b'#!/bin/bash': 'Bash Script',
    b'<?xml': 'XML Document',
    b'<html': 'HTML Document',
    b'<!DOCTYPE html': 'HTML5 Document',
    b'\x00\x00\x01\x00': 'ICO Image',
    b'WEBP': 'WebP Image',
    b'\x49\x49\x2a\x00': 'TIFF Image (little endian)',
    b'\x4d\x4d\x00\x2a': 'TIFF Image (big endian)',
}

def scan_file_signatures(file_path: Path) -> List[Tuple[int, str, str]]:
    """Scan file for embedded file signatures."""
    signatures_found = []
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            
        for signature, file_type in FILE_SIGNATURES.items():
            offset = 0
            while True:
                pos = data.find(signature, offset)
                if pos == -1:
                    break
                signatures_found.append((pos, signature.hex(), file_type))
                offset = pos + 1
                
    except Exception as e:
        return [(-1, "", f"Error reading file: {str(e)}")]
    
    return signatures_found

def analyze_entropy(file_path: Path, chunk_size: int = 1024) -> Dict[str, float]:
    """Calculate entropy of file sections to detect encrypted/compressed data."""
    import math
    from collections import Counter
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Overall entropy
        if len(data) == 0:
            return {"overall": 0.0, "max_chunk": 0.0, "min_chunk": 0.0}
            
        counter = Counter(data)
        entropy = 0.0
        for count in counter.values():
            p = count / len(data)
            entropy -= p * math.log2(p)
        
        # Chunk-based entropy analysis
        chunk_entropies = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            if len(chunk) > 0:
                chunk_counter = Counter(chunk)
                chunk_entropy = 0.0
                for count in chunk_counter.values():
                    p = count / len(chunk)
                    chunk_entropy -= p * math.log2(p)
                chunk_entropies.append(chunk_entropy)
        
        return {
            "overall": round(entropy, 3),
            "max_chunk": round(max(chunk_entropies), 3) if chunk_entropies else 0.0,
            "min_chunk": round(min(chunk_entropies), 3) if chunk_entropies else 0.0,
            "avg_chunk": round(sum(chunk_entropies) / len(chunk_entropies), 3) if chunk_entropies else 0.0
        }
        
    except Exception as e:
        return {"error": str(e)}

def analyze_file_signatures(input_img: Path, output_dir: Path) -> None:
    """Analyze file for embedded signatures and entropy."""
    
    try:
        # Scan for file signatures
        signatures = scan_file_signatures(input_img)
        
        # Calculate entropy
        entropy_data = analyze_entropy(input_img)
        
        # Filter out the main image signature at offset 0
        embedded_signatures = [
            {"offset": offset, "signature": sig, "type": file_type}
            for offset, sig, file_type in signatures
            if offset > 0  # Skip the main file signature
        ]
        
        result = {
            "file_signatures": {
                "status": "ok",
                "output": {
                    "total_signatures": len(signatures),
                    "embedded_signatures": embedded_signatures[:20],  # Limit output
                    "entropy_analysis": entropy_data,
                    "high_entropy_warning": entropy_data.get("overall", 0) > 7.5
                }
            }
        }
        
        update_data(output_dir, result)
        
    except Exception as e:
        update_data(output_dir, {
            "file_signatures": {
                "status": "error", 
                "error": str(e)
            }
        })