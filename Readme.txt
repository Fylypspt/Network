Project idea: Network from Scratch

Desc: A network rebuilt in Python from the bit up. No sockets or networking libraries are used,
so every layer is written by hand and nothing stays hidden behind a function call.

Design:

Built in Python. The "wire" is a shared variable holding a single bit.
It has no memory or index, so writing a new bit destroys the previous one, like voltage on copper.
The sender and receiver run in separate threads and share only this variable.
The sender writes one bit per clock tick, while the receiver samples half a tick later,
so every sample lands in the middle of a bit instead of on a transition.

Frame structure:

preamble | length | data

* Preamble: 8 bits marking the start of a transmission
* Length: 8 bits representing the number of bytes that follow, with a maximum of 255
* Data: 8 bits per character, using ASCII

Reception System: The receiver continuously samples the wire and works through three states.
First, it slides an 8-bit window over the incoming stream until it matches the preamble.
Everything before the preamble is discarded. It then reads the next 8 bits as the payload size
and finally reads exactly that many bytes. This allows the payload to contain any byte sequence
without accidentally being cut short by an end pattern.

Idle Line: An unconnected line sits at 0. The receiver never stops sampling,
so silence appears as a continuous stream of zeros. It can therefore detect a message automatically
without knowing when, or whether, a transmission is going to happen.

What happens when a message is sent:

1. The sender converts the message into bytes
2. The sender writes each bit onto the wire one clock tick at a time
3. The receiver continuously samples the wire half a tick after each transmission
4. The receiver searches for the 8-bit preamble
5. The receiver reads the next 8 bits to determine the payload length
6. The receiver reads exactly that many bytes and reconstructs the message

---

Next steps: line noise and corruption, checksums, hardware addresses, a shared medium with
more than two nodes, collisions, IP addresses, routing between networks, ARP, ports,
and a reliable transport protocol with acknowledgements and retransmission.