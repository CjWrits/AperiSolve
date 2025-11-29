"""Generate test images with hidden data for AperiSolve testing."""

from PIL import Image, ImageDraw, ImageFont
import os
import zipfile
import struct

# Create test_images directory
os.makedirs("test_images", exist_ok=True)

# 1. Simple PNG with text in metadata
print("Creating test1_metadata.png...")
img1 = Image.new('RGB', (400, 300), color='blue')
draw = ImageDraw.Draw(img1)
draw.text((50, 100), "Test Image 1", fill='white')
from PIL import PngImagePlugin
metadata = PngImagePlugin.PngInfo()
metadata.add_text("Comment", "flag{hidden_in_metadata_12345}")
metadata.add_text("Author", "TestUser")
img1.save("test_images/test1_metadata.png", pnginfo=metadata)

# 2. Image with embedded text strings
print("Creating test2_strings.png...")
img2 = Image.new('RGB', (400, 300), color='green')
draw2 = ImageDraw.Draw(img2)
draw2.text((50, 100), "Test Image 2", fill='white')
img2.save("test_images/test2_strings.png")

# Append hidden strings to the image
with open("test_images/test2_strings.png", "ab") as f:
    f.write(b"\n\nHIDDEN_DATA_START\n")
    f.write(b"Email: test@example.com\n")
    f.write(b"URL: https://github.com/secret/repo\n")
    f.write(b"IP: 192.168.1.100\n")
    f.write(b"Flag: CTF{strings_are_easy_to_find}\n")
    f.write(b"Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n")
    f.write(b"Base64Data: VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdlIGhpZGRlbiBpbiBiYXNlNjQ=\n")

# 3. Image with embedded ZIP file
print("Creating test3_embedded_zip.png...")
img3 = Image.new('RGB', (400, 300), color='red')
draw3 = ImageDraw.Draw(img3)
draw3.text((50, 100), "Test Image 3", fill='white')
img3.save("test_images/test3_embedded_zip.png")

# Create a small text file and zip it
with open("test_images/secret.txt", "w") as f:
    f.write("This is a secret file hidden inside the image!\n")
    f.write("Flag: flag{found_the_hidden_zip}\n")

with zipfile.ZipFile("test_images/hidden.zip", "w") as zf:
    zf.write("test_images/secret.txt", "secret.txt")

# Append ZIP to image
with open("test_images/test3_embedded_zip.png", "ab") as img_file:
    with open("test_images/hidden.zip", "rb") as zip_file:
        img_file.write(zip_file.read())

os.remove("test_images/secret.txt")
os.remove("test_images/hidden.zip")

# 4. Image with LSB steganography simulation
print("Creating test4_lsb.png...")
img4 = Image.new('RGB', (200, 200), color='white')
pixels = img4.load()

# Modify LSB of some pixels to create patterns
message = "SECRET"
for i, char in enumerate(message):
    x, y = i % 200, i // 200
    r, g, b = pixels[x, y]
    # Modify LSB of red channel
    pixels[x, y] = ((r & 0xFE) | (ord(char) & 1), g, b)

img4.save("test_images/test4_lsb.png")

# 5. Image with high entropy data (simulating encryption)
print("Creating test5_entropy.png...")
img5 = Image.new('RGB', (300, 300), color='purple')
img5.save("test_images/test5_entropy.png")

# Append random-looking data
with open("test_images/test5_entropy.png", "ab") as f:
    # Add some high-entropy data
    f.write(b"\xFF" * 100)
    f.write(bytes(range(256)) * 10)

# 6. Simple image for password cracking test
print("Creating test6_password.png...")
img6 = Image.new('RGB', (400, 300), color='orange')
draw6 = ImageDraw.Draw(img6)
draw6.text((50, 100), "Password Protected", fill='white')
draw6.text((50, 150), "Try: password, secret, or hidden", fill='white')
img6.save("test_images/test6_password.png")

# 7. Image with multiple file signatures
print("Creating test7_signatures.png...")
img7 = Image.new('RGB', (400, 300), color='cyan')
draw7 = ImageDraw.Draw(img7)
draw7.text((50, 100), "Multiple Signatures", fill='black')
img7.save("test_images/test7_signatures.png")

# Append various file signatures
with open("test_images/test7_signatures.png", "ab") as f:
    f.write(b"\n\n")
    f.write(b"PK\x03\x04")  # ZIP signature
    f.write(b"\x00" * 50)
    f.write(b"\x1f\x8b\x08")  # GZIP signature
    f.write(b"\x00" * 50)
    f.write(b"%PDF-1.4")  # PDF signature
    f.write(b"\x00" * 50)

print("\n[SUCCESS] Test images created successfully in 'test_images/' folder!")
print("\nTest Images:")
print("1. test1_metadata.png - Hidden flag in PNG metadata")
print("2. test2_strings.png - URLs, emails, IPs, crypto addresses, flags")
print("3. test3_embedded_zip.png - ZIP file embedded in image")
print("4. test4_lsb.png - LSB steganography pattern")
print("5. test5_entropy.png - High entropy data (simulated encryption)")
print("6. test6_password.png - For password cracking test")
print("7. test7_signatures.png - Multiple file signatures embedded")
print("\nUpload these to http://localhost:5000 to test all features!")
