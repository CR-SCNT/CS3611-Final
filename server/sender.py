import socket
import os
import concurrent.futures
from datetime import datetime
import threading
from server.logger import Logger

logger = Logger()

HOST = '0.0.0.0'
PORT = 9000
SEGMENT_DIR = 'data/segments'  # 视频片段目录
BUFFER_SIZE = 4096

def extract_bitrate(segment_name):
    # segment name format "xxxx-<resolution>-<bitrate>k-<segmentID>.ts"
    try:
        parts = segment_name.split('-')
        for part in parts:
            if part.endswith('k'):
                return int(part[:-1])
    except:
        pass
    return None

def recv_and_send(client_socket, client_address):
    
    print(f"[+] Connection established with {client_address}")
    client_socket.settimeout(30)
    
    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            segment_name = data.decode().strip()
            segment_path = f"{SEGMENT_DIR}/{segment_name}"
            
            if not os.path.exists(segment_path):
                print(f"[!] Segment {segment_name} not found.")
                client_socket.sendall(b"Segment not found.")
                continue
            
            bitrate = extract_bitrate(segment_name)
            if bitrate is None:
                print(f"Could not extract bitrate from segment name: {segment_name}")
                client_socket.sendall(b"Invalid segment name format.")
                continue
            
            sendtime = datetime.now()
            total_size = os.path.getsize(segment_path)
            with open(segment_path, 'rb') as f:
                while True:
                    file_data = f.read(BUFFER_SIZE)
                    if not file_data:
                        break
                    client_socket.sendall(file_data)
    
            try:   
                logger.log(
                    role="server",
                    segment_name=segment_name,
                    send_time=sendtime,
                    bitrate=bitrate,
                    client_addr=str(client_address[0]) + ':' + str(client_address[1])
                )
            except Exception as log_error:
                print(f"[Logger] Failed to log: {log_error}")
                
            print(f"[+] Sent segment {segment_name} {total_size} bytes -> {client_address[0]}:{client_address[1]}")
    except socket.timeout:
        print(f"[!] Timeout while communicating with {client_address}.")
        try:
            logger.log(
                role="server",
                segment_name=segment_name if 'segment_name' in locals() else 'unknown',
                send_time=datetime.now(),
                bitrate=0,
                client_addr=str(client_address[0]) + ':' + str(client_address[1])
            )
        except Exception as log_error:
            print(f"[Logger] Failed to log: {log_error}")     
    except Exception as e:
        print(f"[!] Error during communication with {client_address}: {e}")
        try:
            logger.log(
                role="server",
                segment_name=segment_name if 'segment_name' in locals() else 'unknown',
                send_time=datetime.now(),
                bitrate=0,
                client_id=str(client_address[0]) + ':' + str(client_address[1])
            )
        except Exception as log_error:
            print(f"[Logger] Failed to log: {log_error}")
    finally:
        client_socket.close()
        print(f"[-] Connection closed with {client_address}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen(100)
    print(f"[+] Server started on {HOST}:{PORT}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                executor.submit(recv_and_send, client_socket, client_address)
        except KeyboardInterrupt:
            print("\n[!] Server shutting down by keyboard interrupt.")
        finally:
            server_socket.close()
            print("[!] Server socket closed.")