Project idea: Network Simulator

Desc: This simulation demonstrates how a network works and how data travels between devices. 
Everything is built from scratch, without sockets or networking libraries, 
so that each part of a network is understood instead of hidden behind a function call.

Design:

Built in Python. The "cable" is a shared object that devices write bytes into and read bytes out of. 
Data is sent as raw bytes, the same way it happens on a real network.

Network Components:
- Medium: The shared cable. Whatever one node sends, every node connected to it receives
- Node: A device on the network. Each one has its own unique address
- Frame: The package of bytes that gets sent. Contains destination, source, length and data
- Address: A number that identifies each node, same idea as a MAC address
- Broadcast address: A special address that every node accepts
- Checksum: An extra byte at the end used to detect if the data got corrupted

Connection System: Nodes connect to a medium. 
When a node transmits, the medium hands the raw bytes to every other node connected to it. 
Each node then reads the destination address in the frame and decides whether to keep it or throw it away. 
This is why address filtering exists: on a shared medium, everyone physically receives everything.

Frame structure:

preamble | destination | source | length | data | checksum

What happens when a message is sent:

1. The sender builds a frame and calculates the checksum
2. The frame goes onto the medium as raw bytes
3. Every other node receives those bytes
4. Each node recalculates the checksum. If it does not match, the frame is dropped
5. Each node compares the destination address to its own. If it does not match, and it is not a broadcast, the frame is ignored
6. The intended node reads the data

------------------------------------------------------------------------

Next steps: collisions, IP addresses, routing between two networks, ARP, 
ports, and a reliable transport protocol with acknowledgements and retransmission.