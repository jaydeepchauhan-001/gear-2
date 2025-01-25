# sender.py
import os
import socket
import hashlib

# Configurations
chunk_size = 1024 * 10240  # 4MB chunks

def calculate_checksum(file_path):
    """Calculate the MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()

def send_file(file_path, ip, port):
    try:
        file_size = os.path.getsize(file_path)
        checksum = calculate_checksum(file_path)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            print(f"Connected to {ip}:{port}")

            # Send file metadata
            file_name = os.path.basename(file_path)
            s.sendall(f"{file_name},{file_size},{checksum}".encode())

            # Wait for acknowledgment
            ack = s.recv(1024).decode()
            if ack != "READY":
                print("Receiver not ready. Aborting.")
                return

            # Send file in chunks
            with open(file_path, "rb") as f:
                sent_bytes = 0
                while chunk := f.read(chunk_size):
                    s.sendall(chunk)
                    sent_bytes += len(chunk)
                    progress = (sent_bytes / file_size) * 100
                    print(f"Progress: {progress:.2f}%", end="\r")

            print("\nFile sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    file_path = input("Enter the file name to send: ").strip()
    ip = input("Enter the receiver's IP address: ").strip()
    port = int(input("Enter the receiver's port (default 5001): ") or 5001)

    if os.path.exists(file_path):
        send_file(file_path, ip, port)
    else:
        print("File not found!")
