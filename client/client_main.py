import socket, threading
import receiver
from video_player import Player
from config import HOST, PORT, BUFFER_SIZE, SEGMENT_DIR, INPUT_DIR, OUTPUT_DIR, PROFILES, DURATION

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    player = Player(msize=30)
    try:
        prefix = client_socket.recv(4)
        if prefix == b'KEY:':
            key = client_socket.recv(16)
        with open('./client/aes.key', 'wb') as key_file:
            key_file.write(key)
        print("[√] Key received and saved as 'aes.key'.")
        
        namedata = client_socket.recv(BUFFER_SIZE)
        namedata = str(namedata, encoding='utf-8')
        print(str(namedata))
        receiver.suggest_recv(client_socket, BUFFER_SIZE, namedata, player)
    except KeyboardInterrupt:
        print("\n[!] Server shutting down by keyboard interrupt.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()