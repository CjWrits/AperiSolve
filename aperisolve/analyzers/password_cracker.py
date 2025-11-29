"""Automated password cracking for steghide."""

import subprocess
from pathlib import Path
from typing import Optional

from .utils import MAX_PENDING_TIME, update_data

# Common passwords for steganography
COMMON_PASSWORDS = [
    "", "password", "123456", "admin", "root", "secret", "hidden", "flag",
    "ctf", "steganography", "stego", "image", "picture", "photo", "data",
    "file", "extract", "decode", "crack", "key", "pass", "pwd", "test",
    "demo", "example", "sample", "default", "guest", "user", "anonymous"
]

def try_steghide_password(input_img: Path, password: str) -> Optional[str]:
    """Try a password with steghide and return embedded filename if successful."""
    try:
        cmd = ["steghide", "info", str(input_img), "-p", password]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=10
        )
        if result.returncode == 0 and 'embedded file "' in result.stdout:
            # Extract filename from output
            start = result.stdout.find('embedded file "') + 15
            end = result.stdout.find('"', start)
            return result.stdout[start:end] if start < end else None
    except Exception:
        pass
    return None

def analyze_password_crack(input_img: Path, output_dir: Path) -> None:
    """Attempt to crack steghide password using common passwords."""
    
    results = {"cracked_passwords": [], "failed_attempts": 0}
    
    for password in COMMON_PASSWORDS:
        embedded_file = try_steghide_password(input_img, password)
        if embedded_file:
            results["cracked_passwords"].append({
                "password": password if password else "(empty)",
                "embedded_file": embedded_file
            })
            
            # Extract the file
            try:
                extract_dir = output_dir / "password_crack"
                extract_dir.mkdir(exist_ok=True)
                
                cmd = ["steghide", "extract", "-sf", str(input_img), 
                       "-xf", str(extract_dir / embedded_file), "-p", password]
                subprocess.run(cmd, check=True, timeout=MAX_PENDING_TIME)
                
                # Create archive
                subprocess.run(
                    ["7z", "a", str(output_dir / "password_crack.7z"), "*"],
                    cwd=extract_dir, check=True, timeout=MAX_PENDING_TIME
                )
            except Exception as e:
                results["extraction_error"] = str(e)
        else:
            results["failed_attempts"] += 1
    
    if results["cracked_passwords"]:
        update_data(output_dir, {
            "password_crack": {
                "status": "ok",
                "output": results,
                "download": f"/download/{output_dir.name}/password_crack"
            }
        })
    else:
        update_data(output_dir, {
            "password_crack": {
                "status": "error",
                "error": f"No passwords cracked from {len(COMMON_PASSWORDS)} attempts"
            }
        })