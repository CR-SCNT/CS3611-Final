from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

BLOCK_SIZE = 16

def pad(data):
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt(input_path, output_path, key):
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        f_out.write(iv)  # 写入IV作为文件前缀
        while True:
            chunk = f_in.read(1024 * BLOCK_SIZE)
            if not chunk:
                break
            if len(chunk) < 1024 * BLOCK_SIZE:
                chunk = pad(chunk)
                f_out.write(cipher.encrypt(chunk))
                break
            else:
                f_out.write(cipher.encrypt(chunk))
                
def decrypt(input_path, output_path, key):
    with open(input_path, 'rb') as f_in:
        iv = f_in.read(BLOCK_SIZE)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        with open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(1024 * BLOCK_SIZE)
                if len(chunk) == 0:
                    break
                decrypted = cipher.decrypt(chunk)
                if len(chunk) < 1024 * BLOCK_SIZE:
                    decrypted = unpad(decrypted)
                f_out.write(decrypted)