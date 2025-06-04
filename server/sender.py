import socket
import os
import concurrent.futures
from datetime import datetime
import re
from logger import Logger

logger = Logger()

HOST = '0.0.0.0'
PORT = 9000
SEGMENT_DIR = 'data/segments'
BUFFER_SIZE = 4096

def parse_segment_filename(filename):
    """
    Extracts video name, resolution, bitrate, and segment index from the filename.
    
    Filename format: `<videoName>-<resolution>-<bitrate>k-<segmentIndex>.ts`
    
    Returns a tuple (video_name, resolution, bitrate_kbps, segment_index). 
    If the filename does not match the expected format, returns (None, None, 0, -1).
    
    Example:
    - Input: "example-1080p-2500k-0001.ts"
    - Output: ("example", "1080p", 2500, 1)
    """
    base = os.path.basename(filename)
    match = re.match(r'^([a-zA-Z0-9_]+)-(\d+p)-(\d+)k-(\d+)\.ts$', base)
    if match:
        video_name = match.group(1)
        resolution = match.group(2)
        bitrate_kbps = int(match.group(3))
        segment_index = int(match.group(4))
        return video_name, resolution, bitrate_kbps, segment_index
    return None, None, 0, -1

def recv_and_send(client_socket, client_address, buffer_size, segment_dir):
    
    print(f"[+] Connection established with {client_address}")
    client_socket.settimeout(30)
    with open('./server/aes.key', 'rb') as key:
        aes_key = key.read()
    
    try:
        # Send AES key to client
        client_socket.sendall(b"KEY:" + aes_key)
        
        while True:
            data = client_socket.recv(buffer_size)
            if not data:
                break
            segment_name = data.decode().strip()
            parsed_data = parse_segment_filename(segment_name)
            '''
            #if not data == b"Successfully Received Data Chunk":
                if parsed_data[0] is None:
                    print(f"[!] Invalid segment name format: {segment_name}")
                    client_socket.sendall(b"Invalid segment name format.")
                    continue
                segment_path = os.path.join(segment_dir, parsed_data[0], segment_name)
            
                if not os.path.exists(segment_path):
                    print(f"[!] Segment {segment_name} not found.")
                    client_socket.sendall(b"Segment not found.")
                    continue
            
                sendtime = datetime.now()
                total_size = os.path.getsize(segment_path)
                with open(segment_path, 'rb') as f:
                    while True:
                        file_data = f.read(buffer_size)
                        if not file_data:
                            break
                        client_socket.sendall(file_data)
                    print("Segment sending completed")
            '''
            if parsed_data[0] is None:
                print(f"[!] Invalid segment name format: {segment_name}")
                client_socket.sendall(b"Invalid segment name format.")
                continue
            segment_path = os.path.join(segment_dir, parsed_data[0], segment_name) + '.aes'
            
            if not os.path.exists(segment_path):
                print(f"[!] Segment {segment_name} not found.")
                client_socket.sendall(b"Segment not found.")
                continue
            
            sendtime = datetime.now()
            total_size = os.path.getsize(segment_path)
            with open(segment_path, 'rb') as f:
                while True:
                    file_data = f.read(buffer_size)
                    if not file_data:
                        break
                    client_socket.sendall(file_data)
                    print("send filedata")
                    try:
                        ack = client_socket.recv(3)
                        print("ACK")
                        if ack != b"ACK":
                            raise Exception("ACK missing")
                        else:
                            print("ACK received")
                    except Exception as e:
                        print(e)
                    finally:
                        pass
                print("Segment sending completed")
                client_socket.sendall(b"END")
            
            try:   
                logger.log(
                    role="server",
                    segment_name=segment_name,
                    send_time=sendtime,
                    bitrate=parsed_data[2],
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
                client_addr=str(client_address[0]) + ':' + str(client_address[1])
            )
        except Exception as log_error:
            print(f"[Logger] Failed to log: {log_error}")
    finally:
        client_socket.close()
        print(f"[-] Connection closed with {client_address}")

def test_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen(100)
    print(f"[+] Server started on {HOST}:{PORT}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while True:
                client_socket, client_address = server_socket.accept()
                executor.submit(recv_and_send, client_socket, client_address, BUFFER_SIZE, SEGMENT_DIR)
        except KeyboardInterrupt:
            print("\n[!] Server shutting down by keyboard interrupt.")
        finally:
            server_socket.close()
            print("[!] Server socket closed.")
            
if __name__ == "__main__":
    test_server()