import socket, threading
import os
import re
import vlc
import time
import receiver
from video_player import Player
from config import HOST, PORT, BUFFER_SIZE, SEGMENT_DIR, INPUT_DIR, OUTPUT_DIR, DOWNLOAD_DIR, PROFILES, DURATION

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # player = Player(msize=30)
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
    try:
        namedata = client_socket.recv(BUFFER_SIZE)
        namedata = str(namedata, encoding="utf8")
        while True:
            print("Available videos on server:")
            print(namedata)
            videoname = input("Enter video name: ")
            if videoname not in namedata:
                print(f"[!] Video '{videoname}' not found on server.")
                continue    
            while True:
                resolution = input("Choose resolution for the chosen video(1 for 1080p, 2 for 720p, 3 for 480p and 4 for 360p): ")
                if resolution == "1" or resolution == "2" or resolution == "3" or resolution == "4":
                    break
                else:
                    print(f"[!] '{resolution}' is invalid. Please enter 1, 2, 3 or 4 for 1080p, 720p, 480p and 360p respectively.")
                    continue
            resolution_label = PROFILES[int(resolution) - 1][0]
            bitrate = str(PROFILES[int(resolution) - 1][2]) + "k"
            m3u8_filename = f"{videoname}-{resolution_label}-{bitrate}.m3u8"
            client_socket.sendall(bytes(m3u8_filename, encoding="utf8"))
            with open(os.path.join(DOWNLOAD_DIR, m3u8_filename), 'wb') as f:
                write_data = b""
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    if data == b"m3u8 end":
                        break
                    write_data += data
                    client_socket.send(b"ACK")    
                f.write(write_data)
            with open(os.path.join(DOWNLOAD_DIR, m3u8_filename), 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                last_ts_line = lines[-2]
                match = re.search(r'-(\d+)\.ts$', last_ts_line)
                last_index = int(match.group(1))
            videoplayer = receiver.suggest_recv(client_socket, BUFFER_SIZE, videoname, [resolution_label, bitrate], m3u8_filename, last_index) 
            while True:
                if videoplayer.get_state() == vlc.State.Ended:
                    videoplayer.stop()
                    del videoplayer
                    break
                client_socket.send(b"keep connecting")
                time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Client shutting down by keyboard interrupt.")
    except Exception as e:
        print(e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
