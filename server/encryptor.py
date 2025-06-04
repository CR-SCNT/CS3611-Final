import aes
import os
from Crypto.Random import get_random_bytes
from config import SEGMENT_DIR

def key_generator():
    """
    Generates a random AES key file `aes.key` in the current directory.
    The key is 16 bytes long, suitable for AES-128 encryption.
    """
    key = get_random_bytes(16)  # AES-128 key size
    with open('./server/aes.key', 'wb') as key_file:
        key_file.write(key)
    print("[√] AES key generated and saved to 'aes.key'.")
    return key
    

def encrypt_segment(video_name):
    """
    Encrypts a video segment using AES encryption.
    You must have an `aes.key` file in the current directory.
    
    Args:
        video_name (str): Name of the video segment to encrypt.
        
    """
    with open("./server/aes.key", "rb") as f:
        key = f.read()
    encrypted_segment_path = os.path.join(SEGMENT_DIR, video_name)
    for fname in os.listdir(encrypted_segment_path):
        if fname.endswith('.ts'):
            input_path = os.path.join(encrypted_segment_path, fname)
            output_path = input_path+ '.aes'
            aes.encrypt(input_path, output_path, key)
            
def main():
    key_generator()
    # Example usage
    video_name = "test2"
    encrypt_segment(video_name)

if __name__ == "__main__":
    main()
    

    