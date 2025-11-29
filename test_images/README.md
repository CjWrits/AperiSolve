# AperiSolve Test Images

These test images demonstrate various steganography techniques and hidden data.

## Test Images

### 1. **test1_metadata.png** - Metadata Analysis
- **Hidden Data**: Flag in PNG metadata
- **Tests**: `exiftool` analyzer
- **Expected**: Should find `flag{hidden_in_metadata_12345}` in metadata

### 2. **test2_strings.png** - Pattern Detection
- **Hidden Data**: 
  - Email: test@example.com
  - URL: https://github.com/secret/repo
  - IP Address: 192.168.1.100
  - CTF Flag: CTF{strings_are_easy_to_find}
  - Bitcoin Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
  - Base64 encoded message
- **Tests**: Enhanced `strings` analyzer with pattern detection
- **Expected**: Should detect all patterns in separate categories

### 3. **test3_embedded_zip.png** - File Carving
- **Hidden Data**: ZIP file with secret.txt containing flag
- **Tests**: `binwalk`, `foremost`, `file_signatures` analyzers
- **Expected**: 
  - Detect ZIP signature at end of file
  - Extract hidden.zip containing secret.txt
  - Flag: flag{found_the_hidden_zip}

### 4. **test4_lsb.png** - LSB Steganography
- **Hidden Data**: Message in Least Significant Bits
- **Tests**: `decomposer`, `zsteg` analyzers
- **Expected**: Bit plane analysis shows patterns in LSB layers

### 5. **test5_entropy.png** - Entropy Analysis
- **Hidden Data**: High entropy data (simulated encryption)
- **Tests**: `file_signatures` entropy analysis
- **Expected**: High entropy warning (>7.5)

### 6. **test6_password.png** - Password Cracking
- **Hidden Data**: Hint text suggesting common passwords
- **Tests**: `password_crack` analyzer
- **Expected**: Would work with actual steghide-embedded data
- **Note**: This is a placeholder - real steghide embedding requires command-line tools

### 7. **test7_signatures.png** - Multiple File Signatures
- **Hidden Data**: ZIP, GZIP, and PDF signatures embedded
- **Tests**: `file_signatures` analyzer
- **Expected**: Detect multiple file type signatures at different offsets

## How to Test

1. **Start AperiSolve**:
   ```bash
   docker compose up -d
   ```

2. **Open Browser**:
   - Go to http://localhost:5000

3. **Upload Images**:
   - Drag and drop any test image
   - Optionally enable "Deep Analysis" for more tools
   - Wait for analysis to complete

4. **Check Results**:
   - View bit-plane decomposition
   - Check detected patterns in strings
   - Download extracted files
   - Review entropy analysis

## API Testing

Test the REST API with curl:

```bash
# Analyze image
curl -X POST http://localhost:5000/api/v1/analyze \
  -F "image=@test2_strings.png"

# Check status (replace HASH with submission_hash from response)
curl http://localhost:5000/api/v1/status/HASH

# Get results
curl http://localhost:5000/api/v1/result/HASH
```

## Expected New Features in Results

- **password_crack**: Automated password attempts on steghide
- **file_signatures**: Embedded file detection and entropy analysis
- **strings** (enhanced): Categorized patterns (URLs, emails, crypto, flags)
- **API endpoints**: Programmatic access to all features

## Creating Your Own Test Images

Use the `create_test_images.py` script to regenerate or modify test images:

```bash
python create_test_images.py
```
