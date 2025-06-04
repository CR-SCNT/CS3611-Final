import time
from video_player import Player
import os, decryptor, aes
from config import DOWNLOAD_DIR

def filename_summon(name, resolution, ords):
    return f"{name}-{resolution[0]}-{resolution[1]}-" + str(ords).zfill(4) + ".ts"

def suggest_recv(client_socket, buffer_size, video_name, videoplayer, resolution):
    # resolution = [["480p", "1000k"], ["720p", "1500k"], ["1080p", "2500k"], ["360p", "500k"]]
    ords = 0
    while True:
        strs = filename_summon(video_name, resolution, ords)
        encrypted_strs = strs + ".aes"
        client_socket.sendall(bytes(strs, encoding="utf8"))
        time.sleep(2)
        with open(os.path.join(DOWNLOAD_DIR, encrypted_strs), 'wb') as f:
            write_data = b""
            data = client_socket.recv(buffer_size)
            if data == b"Invalid segment name format." or data == b"Segment not found.":
                #os.remove(DOWNLOAD_DIR + "/" + encrypted_strs)
                break
            elif data:
                #subprocess.Popen(["ffmpeg", "-i", "tcp://localhost:8000", "-c", "copy", "-f", ".ts", "data/download/" + strs], stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                client_socket.send(b"ACK")
                write_data += data
                while True:
                    data = client_socket.recv(buffer_size)
                    if not data or data == b"END":
                        break
                    write_data += data
                    client_socket.send(b"ACK")
                print(f"Data collect completed, total length: {len(write_data)}")
                f.write(write_data)
                decryptor.decrypt_segment(encrypted_strs)
            time.sleep(2)
            videoplayer.add_playlist(DOWNLOAD_DIR + "/" + strs)
            ords += 1

    while True:
        time.sleep(1)