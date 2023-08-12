import socket # low level socket programming in Python
import struct # pack and unpack datagrams

# Function to calculate checksum using Internet Checksum algorithm
def calculate_checksum(data):
    checksum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            checksum += (data[i] << 8) + data[i + 1]
        elif i < len(data):
            checksum += data[i]
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += (checksum >> 16)
    return ~checksum & 0xffff

def send_packet(socket, packet):
    socket.sendto(packet, ("127.0.0.1", 8001))

def receive_packet(socket):
    data, addr = socket.recvfrom(1024)
    return data, addr

def server_handshake(socket):
    # Receive SYN from client
    data, addr = receive_packet(socket)
    syn_packet = struct.unpack("!50si", data)
    syn, seq_num = syn_packet

    # Verify checksum
    checksum = calculate_checksum(data)
    if checksum != 0:
        print("Invalid packet received. Discarding.")
        return

    print("Received SYN from client")

    # Send SYN-ACK to client
    syn_ack_packet = struct.pack("!50si", b"SYN-ACK", seq_num)
    send_packet(socket, syn_ack_packet)
    print("Sent SYN-ACK to client")

    # Receive ACK from client
    data, addr = receive_packet(socket)
    ack_packet = struct.unpack("!50si", data)
    ack, seq_num = ack_packet

    # Verify checksum
    checksum = calculate_checksum(data)
    if checksum != 0:
        print("Invalid packet received. Discarding.")
        return

    print("Received ACK from client")

    # Server connection established
    print("Server connection established with client")

def client_handshake(socket):
    seq_num = 1

    # Send SYN to server
    syn_packet = struct.pack("!50si", b"SYN", seq_num)
    send_packet(socket, syn_packet)
    print("Sent SYN to server")

    # Receive SYN-ACK from server
    data, addr = receive_packet(socket)
    syn_ack_packet = struct.unpack("!50si", data)
    syn_ack, seq_num = syn_ack_packet

    # Verify checksum
    checksum = calculate_checksum(data)
    if checksum != 0:
        print("Invalid packet received. Discarding.")
        return

    print("Received SYN-ACK from server")

    # Send ACK to server
    ack_packet = struct.pack("!50si", b"ACK", seq_num)
    send_packet(socket, ack_packet)
    print("Sent ACK to server")

    # Client connection established
    print("Client connection established with server")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", 8000))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("127.0.0.1", 8001))

    server_handshake(server_socket)
    client_handshake(client_socket)

    server_socket.close()
    client_socket.close()

if __name__ == "__main__":
    main()