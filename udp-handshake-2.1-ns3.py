from ns import ns

# Define the UDP packet structure
class UDPPacket:
    def __init__(self, source_port, dest_port, seq_num, ack_num, flags, checksum, data):
        self.source_port = source_port
        self.dest_port = dest_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.checksum = checksum
        self.data = data

    def calculate_checksum(self):
        # Calculate the checksum based on packet fields (excluding the checksum itself)
        packet_str = f"{self.source_port}{self.dest_port}{self.seq_num}{self.ack_num}{self.flags}{self.data}"
        # Implement your checksum algorithm here
        # Example: Use CRC32
        checksum = ns.Crc32.Calculate(packet_str.encode())
        return checksum

# Initialize simulation
simulation = ns.Simulator

# Create nodes for client and server
client_node = ns.Node()
server_node = ns.Node()

# Install internet stack on the nodes
internet_stack_helper = ns.InternetStackHelper()
internet_stack_helper.Install(client_node)
internet_stack_helper.Install(server_node)

# Create network devices and install them
point_to_point_helper = ns.PointToPointHelper()
point_to_point_helper.SetDeviceAttribute("DataRate", ns.StringValue("100Mbps"))
point_to_point_helper.SetChannelAttribute("Delay", ns.StringValue("2ms"))

# Connect the client and server nodes with a point-to-point link
device = point_to_point_helper.Install(client_node, server_node)

# Assign IP addresses to the network devices
address_helper = ns.Ipv4AddressHelper()
address_helper.SetBase(ns.Ipv4Address("10.0.0.0"), ns.Ipv4Mask("255.255.255.0"))
interface = address_helper.Assign(device)

# Create UDP applications for client and server
client_app = ns.OnOffHelper("ns3::UdpSocketFactory", ns.Address(ns.InetSocketAddress(interface.GetAddress(1), 9)))
client_app.SetAttribute("PacketSize", ns.UintegerValue(1024))
client_app.SetAttribute("DataRate", ns.DataRateValue(ns.DataRate("5Mbps")))
client_app.SetAttribute("StartTime", ns.TimeValue(ns.Seconds(1.0)))
client_app.Install(client_node)

server_app = ns.PacketSinkHelper("ns3::UdpSocketFactory", ns.Address(ns.InetSocketAddress(ns.Ipv4Address.GetAny(), 9)))
server_app.Install(server_node)

# Enable logging
ns.LogComponentEnable("UdpHandshake", ns.LOG_LEVEL_INFO)

# Run the simulation
simulation.Run()

# Perform three-way handshake
seq_num = 1001
ack_num = 0
flags = "SYN"

# Generate SYN packet
syn_packet = UDPPacket(8888, 8888, seq_num, ack_num, flags, 0, "")
syn_packet.checksum = syn_packet.calculate_checksum()

# Send SYN packet from client to server
client_socket.Start(ns.Seconds(1.0))
client_socket.Stop(ns.Seconds(5.0))
client_socket = client_app.Get(0)
client_socket.SendTo(syn_packet, server_node.GetDevice(1).GetAddress(), 8888)
NS_LOG_INFO("Sent SYN to server")

# Receive SYN packet at server
server_socket = server_app.Get(0)
received_packet = server_socket.Recv()

# Verify SYN packet checksum
if received_packet.checksum == received_packet.packet.calculate_checksum():
    NS_LOG_INFO("Received SYN packet. Handshake in progress.")
    seq_num = received_packet.packet.ack_num
    ack_num = received_packet.packet.seq_num + 1
    flags = "SYN-ACK"

    # Generate SYN-ACK packet
    syn_ack_packet = UDPPacket(8888, 8888, seq_num, ack_num, flags, 0, "")
    syn_ack_packet.checksum = syn_ack_packet.calculate_checksum()

    # Send SYN-ACK packet from server to client
    server_socket.Send(syn_ack_packet, received_packet.remoteAddress)

    # Receive SYN-ACK packet at client
    received_packet = client_socket.GetPacket()

    # Verify SYN-ACK packet checksum
    if received_packet.packet.checksum == received_packet.packet.calculate_checksum():
        NS_LOG_INFO("Received SYN-ACK packet. Handshake in progress.")
        seq_num = received_packet.packet.ack_num
        ack_num = received_packet.packet.seq_num + 1
        flags = "ACK"

        # Generate ACK packet
        ack_packet = UDPPacket(8888, 8888, seq_num, ack_num, flags, 0, "")
        ack_packet.checksum = ack_packet.calculate_checksum()

        # Send ACK packet from client to server
        client_socket.Start(ns.Seconds(2.0))
        client_socket.SendTo(ack_packet, server_node.GetDevice(1).GetAddress(), 8888)
	        NS_LOG_INFO("Sent ACK to server")
        NS_LOG_INFO("Handshake complete. Connection established.")
    else:
        NS_LOG_INFO("Invalid SYN-ACK packet. Handshake failed.")

# Cleanup and shutdown the simulation
simulation.Stop()
simulation.Destroy()