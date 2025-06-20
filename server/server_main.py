import segmenter
import socket
import os
import glob
import concurrent.futures
import subprocess
import sys
import threading
import signal
import encryptor
from sender import recv_and_send as tcp_communicate
from config import HOST, PORT, BUFFER_SIZE, SEGMENT_DIR, INPUT_DIR, OUTPUT_DIR, PROFILES, DURATION

video_names = []

shutdown_event = threading.Event()

def signal_handler(sig, frame):
    print("\n[!] Server shutting down by keyboard interrupt.")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)

def check_ffmpeg():
    try:
        subprocess.Popen(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[√] ffmpeg available.")
    except Exception:
        print("[×] ffmpeg not found. Please install ffmpeg and ensure it is in your PATH.")
        sys.exit(1)

def check_and_segment():
    segements_already_exist = True
    for video in glob.glob(os.path.join(INPUT_DIR, "*.mp4")):
        video_name = os.path.splitext(os.path.basename(video))[0]
        video_names.append(video_name)
        print(video_names)
        segment_path = os.path.join(SEGMENT_DIR, video_name)
        
        if not os.path.exists(segment_path) or not os.listdir(segment_path):
            print(f"[!] Segments for video '{video_name}' do not exist, starting segmentation.")
            segements_already_exist = False
            for res_label, res_size, bitrate in PROFILES:
                segmenter.segment_video(
                    resolution_label=res_label,
                    resolution_size=res_size,
                    bitrate_kbps=bitrate,
                    input_dir=INPUT_DIR,
                    output_dir=OUTPUT_DIR,
                    video_name=video_name,
                    duration=DURATION
                )
    if segements_already_exist:
        print("[√] Segments already exist, skipping segmentation.")
    for video_name in video_names:
        encryptor.encrypt_segment(video_name)
        print(f"[√] Encrypted segments for video '{video_name}'.")
    return video_names

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen(100)
    server_socket.settimeout(1.0)
    print(f"[+] Server started on {HOST}:{PORT}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while not shutdown_event.is_set():
                try:
                    client_socket, client_address = server_socket.accept()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[!] Unexpected error in accept(): {e}")
                    continue
                with open('./server/aes.key', 'rb') as key:
                    aes_key = key.read()
                client_socket.sendall(b"KEY:")
                client_socket.sendall(aes_key)
                names = ""
                for name in video_names:
                    names += name
                    names += " "
                client_socket.send(names.encode('utf-8'))
                executor.submit(tcp_communicate, client_socket, client_address, BUFFER_SIZE, SEGMENT_DIR)
        # except KeyboardInterrupt:
        #     print("\n[!] Server shutting down by keyboard interrupt.")
        finally:
            server_socket.close()
            print("[!] Server socket closed.")
            
if __name__ == "__main__":
    encryptor.key_generator()
    check_ffmpeg()
    check_and_segment()
    start_server()
    