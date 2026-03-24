import os

output_dir = r"C:\Users\user\Desktop\niamyio_audio"
os.makedirs(output_dir, exist_ok=True)

# Generate dummy content for the audio files (since we cannot download them properly)
# In reality these would be actual audio files. For demonstration, we'll create empty files
# so that the HTML has something to point to.
with open(os.path.join(output_dir, "kanlok.mp3"), "wb") as f:
    f.write(b"dummy audio content")
    
with open(os.path.join(output_dir, "kian_tsi.mp3"), "wb") as f:
    f.write(b"dummy audio content")

with open(os.path.join(output_dir, "tshe_lin.mp3"), "wb") as f:
    f.write(b"dummy audio content")
    
print("Created dummy audio files.")
