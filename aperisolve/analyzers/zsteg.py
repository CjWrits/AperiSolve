"""Zsteg Analyzer for Image Submissions with extraction."""

import shutil
import subprocess
from pathlib import Path

from .utils import MAX_PENDING_TIME, update_data


def analyze_zsteg(input_img: Path, output_dir: Path) -> None:
    """Analyze an image submission using zsteg with extraction."""

    try:
        # Run zsteg analysis
        data = subprocess.run(
            ["zsteg", "-a", input_img],  # -a for --all
            capture_output=True,
            text=True,
            check=False,
            timeout=MAX_PENDING_TIME,
        )
        
        if data.stderr or "PNG::NotSupported" in data.stdout[:100]:
            error_msg = data.stderr or data.stdout
            update_data(output_dir, {"zsteg": {"status": "error", "error": error_msg}})
            return

        # Try to extract files with zsteg -E
        zsteg_dir = output_dir / "zsteg"
        extracted_files = False
        
        # Check if there's extractable data
        if "b1,rgb,lsb,xy" in data.stdout or "b1,bgr,lsb,xy" in data.stdout:
            zsteg_dir.mkdir(parents=True, exist_ok=True)
            
            # Try common extraction patterns
            for pattern in ["b1,rgb,lsb,xy", "b1,bgr,lsb,xy", "b1,r,lsb,xy"]:
                try:
                    extract_result = subprocess.run(
                        ["zsteg", "-E", pattern, input_img],
                        capture_output=True,
                        check=False,
                        timeout=30,
                    )
                    if extract_result.returncode == 0 and len(extract_result.stdout) > 0:
                        output_file = zsteg_dir / f"extracted_{pattern.replace(',', '_')}.bin"
                        with open(output_file, "wb") as f:
                            f.write(extract_result.stdout)
                        extracted_files = True
                except Exception:
                    pass
        
        result = {
            "zsteg": {
                "status": "ok",
                "output": data.stdout.split("\n") if data else [],
            }
        }
        
        # Add download link if files were extracted
        if extracted_files:
            # Create archive
            subprocess.run(
                ["7z", "a", str(output_dir / "zsteg.7z"), "*"],
                cwd=zsteg_dir,
                capture_output=True,
                check=False,
                timeout=MAX_PENDING_TIME,
            )
            shutil.rmtree(zsteg_dir)
            result["zsteg"]["download"] = f"/download/{output_dir.name}/zsteg"
        
        update_data(output_dir, result)
        
    except Exception as e:
        update_data(output_dir, {"zsteg": {"status": "error", "error": str(e)}})
