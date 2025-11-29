"""Enhanced Strings Analyzer with pattern detection."""

import re
import subprocess
from pathlib import Path
from typing import Dict, List

from .utils import MAX_PENDING_TIME, update_data

# Patterns to detect in strings
PATTERNS = {
    "urls": r"https?://[^\s]+",
    "emails": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "ip_addresses": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "base64": r"[A-Za-z0-9+/]{20,}={0,2}",
    "hex_strings": r"[0-9a-fA-F]{16,}",
    "file_paths": r"[A-Za-z]:\\[^\s]+|/[^\s]+\.[a-zA-Z0-9]+",
    "crypto_addresses": r"[13][a-km-zA-HJ-NP-Z1-9]{25,34}|0x[a-fA-F0-9]{40}",
    "flags": r"flag\{[^}]+\}|CTF\{[^}]+\}|[A-Z0-9]{5,}_\{[^}]+\}"
}

def extract_patterns(text_lines: List[str]) -> Dict[str, List[str]]:
    """Extract interesting patterns from strings output."""
    patterns_found = {}
    full_text = "\n".join(text_lines)
    
    for pattern_name, pattern_regex in PATTERNS.items():
        matches = re.findall(pattern_regex, full_text, re.IGNORECASE)
        if matches:
            patterns_found[pattern_name] = list(set(matches))  # Remove duplicates
    
    return patterns_found

def analyze_strings(input_img: Path, output_dir: Path) -> None:
    """Analyze an image submission using enhanced strings analysis."""

    try:
        # Run strings command
        data = subprocess.run(
            ["strings", "-n", "4", input_img],  # Minimum 4 chars
            capture_output=True,
            text=True,
            check=False,
            timeout=MAX_PENDING_TIME,
        )
        
        if data.stderr:
            update_data(output_dir, {"strings": {"status": "error", "error": data.stderr}})
            return

        strings_output = data.stdout.split("\n") if data.stdout else []
        
        # Extract interesting patterns
        patterns = extract_patterns(strings_output)
        
        # Filter out very short or common strings for cleaner output
        filtered_strings = [
            s for s in strings_output 
            if len(s.strip()) >= 4 and not s.strip().isdigit()
        ][:500]  # Limit to first 500 strings
        
        result = {
            "strings": {
                "status": "ok",
                "output": filtered_strings,
            }
        }
        
        # Add patterns if found
        if patterns:
            result["strings"]["patterns"] = patterns
            
        update_data(output_dir, result)
        
    except Exception as e:
        update_data(output_dir, {"strings": {"status": "error", "error": str(e)}})
