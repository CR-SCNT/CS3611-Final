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
    except Exception as e:
        print(f"[!] Error receiving key: {e}")
        client_socket.close()
        return
    while True:
        try:
            namedata = client_socket.recv(BUFFER_SIZE)
            namedata = str(namedata, encoding="utf8")
            print("Available videos on server:")
            print(namedata)
            videoname = input("Enter video name: ")
            if videoname not in namedata:
                print(f"[!] Video '{videoname}' not found on server.")
                continue    
            # resolution set ["1080p", "2500k"] by default, abr_control will be implemented later
            receiver.suggest_recv(client_socket, BUFFER_SIZE, videoname, player,["1080p", "2500k"]) 
        except KeyboardInterrupt:
            print("\n[!] Server shutting down by keyboard interrupt.")
        except Exception as e:
            print(e)
        finally:
            client_socket.close()
            break

if __name__ == "__main__":
    start_client()