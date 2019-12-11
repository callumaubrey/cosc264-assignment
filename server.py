import socket, sys
import os.path
import datetime

def get_8_bit_num(val):
    return format(val, '08b')

def get_16_bit_num(val):
    return format(val, '016b')

def get_32_bit_num(val):
    return format(val, '032b')

def create_file_response(file_name):
    packet = bytearray()
    
    insert = (get_16_bit_num(0x497E))
    packet.append(int(insert[0:8], 2))
    packet.append(int(insert[8:16], 2))
    
    insert = (get_8_bit_num(2))
    packet.append(int(insert[0:8], 2))
    
    if os.path.exists(file_name) or os.access(file_name, os.R_OK):
        status_code = 1
    else:
        status_code = 0
    
    insert = (get_8_bit_num(status_code))
    packet.append(int(insert[0:8], 2))
    
    if status_code == 0:
        data_len = 0
    else:
        file = open(file_name, "rb")
        byte_array = bytearray()
        for line in file.readlines():
            byte_array.extend(line)
        data_len = len(byte_array)

    insert = (get_32_bit_num(data_len))
    packet.append(int(insert[0:8], 2))
    packet.append(int(insert[8:16], 2))
    packet.append(int(insert[16:24], 2))
    packet.append(int(insert[24:32], 2))

    if status_code == 1:
        f = open(file_name, "rb")
        for line in f.readlines():
            packet.extend(line)
    return packet

def loop(sock, port):
    while True:
        conn, ip_addr = sock.accept()
        conn.settimeout(1)
        ip, host = ip_addr
        
        print("Waiting for any incoming connections on port " + str(port) + "....")
        print("Connected to ip: " + str(ip) + " on port: " + str(port) + " at: " + str(datetime.datetime.now()))
        
        try:
            first_five = conn.recv(1024)
            first_bt = bytearray(first_five)
        except socket.error:
            print("Socket time out error....exiting now")
            conn.close()
            continue

        magic_num = first_bt[0] << 8 | first_bt[1]
        types = first_bt[2]
        first_len = first_bt[3] << 8 | first_bt[4]
        file_name = first_five[5:first_len + 5].decode("utf-8")
        
        if magic_num != 0x497E:
            print("Invalid packet header: (magic number invalid), loop starting again....")
            conn.close()
            continue
        elif types != 1:
            print("Invalid packet header: (type invalid), loop starting again....")
            conn.close()
            continue
        elif first_len < 1 or first_len >
            print("Invalid packet header: (file name length invalid), loop starting again....")
            conn.close()
            continue

        packet = create_file_response(file_name)
        print("File sent....: {:.2f}".format(len(packet)))
        conn.sendall(packet)

def main():
    args = sys.argv[1:]
    if len(args) > 1:
        print("Too many arguments....exiting now")
        sys.exit()

    port = int(args[0])
    if port < 1024 or port > 64000:
        print("Invalid port number....exiting now")
        sys.exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((socket.gethostname(), port))
    except socket.error:
        print("Failed to bind to socket....exiting now")
        sys.exit()

    try:
        sock.listen(1)
    except socket.error:
        print("Failed to listen to socket....exiting now")
        sys.exit()

    print("Listening on port: " + str(port) + "....")
    loop(sock, port)


main()
