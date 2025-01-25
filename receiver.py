# receiver.py
import os
import socket
import hashlib

# Configurations
chunk_size =  1024 * 10240  # 4MB chunks
storage_dir = os.path.expanduser("~/storage/shared")  # Default directory for Termux

def calculate_checksum(file_path):
    """Calculate the MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()

def receive_file(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            s.listen(1)
            print(f"Listening on port {port}...")

            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")

                # Receive file metadata
                metadata = conn.recv(1024).decode()
                file_name, file_size, checksum = metadata.split(",")
                file_size = int(file_size)

                # Prepare to save file
                save_path = os.path.join(storage_dir, file_name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                conn.sendall("READY".encode())

                # Receive file in chunks
                received_bytes = 0
                with open(save_path, "wb") as f:
                    while received_bytes < file_size:
                        chunk = conn.recv(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_bytes += len(chunk)
                        progress = (received_bytes / file_size) * 100
                        print(f"Progress: {progress:.2f}%", end="\r")

                print("\nFile received successfully!")

                # Verify checksum
                received_checksum = calculate_checksum(save_path)
                if received_checksum == checksum:
                    print("Checksum verified. File integrity intact.")
                else:
                    print("Checksum mismatch. File may be corrupted.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    port = int(input("Enter the port to listen on (default 5001): ") or 5001)
    receive_file(port)
