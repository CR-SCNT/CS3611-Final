import aes
import os
from config import DOWNLOAD_DIR

def decrypt_segment(segment_name):
    """
    Decrypts a video segment using AES encryption.
    You must have an `aes.key` file in the current directory.
    
    Args:
        video_name (str): Name of the video segment to decrypt (end with '.aes')
        
    """
    encrypted_segment_path = os.path.join(DOWNLOAD_DIR, segment_name)
    with open("./client/aes.key", "rb") as f:
        key = f.read()

    if not os.path.exists(encrypted_segment_path):
        print(f"[Error] Encrypted segment '{encrypted_segment_path}' does not exist.")
        return
    if not segment_name.endswith('.aes'):
        print(f"[Error] Segment name '{segment_name}' does not end with '.aes'.")
        return
    decrypted_segment_path = encrypted_segment_path[:-4]  # Remove '.aes'
    aes.decrypt(encrypted_segment_path, decrypted_segment_path, key)
    
def main():
    decrypt_segment("test2-360p-500k-0000.ts.aes")

if __name__ == "__main__":
    # for test
    pass

    
        

        
    

    