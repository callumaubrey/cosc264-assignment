import sys
import os.path
import socket

def create_file_request(file_name):
    file_name_encoded = file_name.encode()
    header = (0x497E << 24 | 1 << 16 | len(file_name)).to_bytes(5, 'big')
    return header, file_name_encoded

def main():
    args = sys.argv[1:]
    if len(args) > 3:
        print("Not enough arguments")
        sys.exit()

    ip = args[0]
    port = int(args[1])
    file_name = args[2]
    if port < 1024 or port > 64000:
        print("Port number invalid....exiting now")
        sys.exit()
    elif os.path.exists(file_name):
        print("File already exists....exiting now")
        sys.exit()
    else:
        try:
            ip = socket.getaddrinfo(ip, None, family=socket.AF_INET,proto=socket.IPPROTO_TCP)[0][4][0]
        except socket.error:
            print("Failed to convert ip address....exiting now")
            sys.exit()

    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(1)
    try:
        conn.connect((ip, port))
    except socket.error:
        print("Failed to connect to socket or timeout error....exiting now")
        sys.exit()
    
    header, file_name_encoded = create_file_request(file_name)
    conn.sendall(header+file_name_encoded)
    print("File Request has been sent....")

    try:
        first_eight = conn.recv(8)
        first_eight_bt = bytearray(first_eight)
        # Check if we get an empty response and exit
        if first_eight == b'':
            print("No response recieved....exiting now")
            sys.exit()
    except socket.error:
        print("Socket out of time error....exiting now")
        sys.exit()

    magic_num = first_eight_bt[0] << 8 | first_eight_bt[1]
    types = first_eight_bt[2]
    status_code = first_eight_bt[3]
    total_len = first_eight_bt[4] << 24 | first_eight_bt[5] << 16 | first_eight_bt[6] << 8 | first_eight_bt[7]

    invalid_header_msg = None
    if magic_num != 0x497E:
        invalid_header_msg = "Magic number is wrong....exiting now"
    elif types != 2:
        invalid_header_msg = "Header type is not equal to 2....exiting now"
    elif status_code != 0 and status_code != 1:
        invalid_header_msg = "File does not exist or cannot be opened(status_code=0)....exiting now"
    
    if invalid_header_msg is not None:
        print(invalid_header_msg)
        conn.close()
        sys.exit()
    else:
        file_out = open(file_name, "w+b")
        try:
            while file_out.tell() < total_len:
                bytes_recvd = conn.recv(4096)
                file_out.write(bytes_recvd)
        except socket.error:
            print("Time out error....exiting now")
            sys.exit()
        except IOError:
            print("Failed to write to file....exiting now")
            sys.exit()
        finally:
            print("Success.")

main()

