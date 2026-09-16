Project idea: Network from Scratch

Desc: A network rebuilt in Python from the bit up. No sockets or networking libraries are used,
so every layer is written by hand and nothing stays hidden behind a function call.

Design:

Built in Python. The "wire" is a shared variable holding a single bit.
It has no memory or index, so writing a new bit destroys the previous one, like voltage on copper.
Every node runs in its own thread and they share only this variable and an agreed tick rate.
The sender writes one bit per clock tick, while receivers sample half a tick later,
so every sample lands in the middle of a bit instead of on a transition.

Frame structure:

preamble | destination | source | length | data

* Preamble: 8 bits marking the start of a transmission
* Destination: 4 bits, the address the frame is meant for
* Source: 4 bits, the address it came from, so the receiver can reply
* Length: 8 bits representing the number of bytes that follow, with a maximum of 255
* Data: 9 bits per character, 8 bits of ASCII plus one parity bit

Shared Medium: Every node is connected to the same wire, so every node receives every bit.
Filtering happens at the receiver, not at the sender: each node compares the destination field
against its own address and discards the frame if it does not match. An address of all ones is
reserved for broadcast and is accepted by everyone. Because delivery is physical and filtering is
only a convention, a node that skips the check reads every frame on the medium. This is how
promiscuous mode works on real hardware.

Reception System: The receiver continuously samples the wire and works through four states.
First, it slides an 8-bit window over the incoming stream until it matches the preamble, discarding
everything before it. It then reads the destination and source addresses, and stops there if the
frame is not for it. Next it reads 8 bits as the payload size, and finally reads exactly that many
bytes. Counting rather than searching for an end pattern means the payload can contain any byte
sequence without being cut short.

Idle Line: An unconnected line sits at 0. The receiver never stops sampling, so silence appears as
a continuous stream of zeros. Detection therefore depends entirely on the preamble arriving intact,
and at a 5% bit error rate it does not, in roughly a third of transmissions.

Noise and Error Detection: The wire has a configurable chance of flipping any bit in transit.
Each byte carries one parity bit, and a frame with any failing byte is dropped in full rather than
partly kept, since parity does not confirm that the remaining bytes are correct. Every reading
state has a wait limit, so a frame that stops arriving halfway is abandoned and the receiver
returns to listening.

What happens when a message is sent:

1. The sender converts the message into bytes and appends a parity bit to each one
2. The sender writes the frame onto the wire one bit per clock tick
3. Every node samples the wire half a tick after each transition
4. Each node searches for the 8-bit preamble
5. Each node reads the addresses and drops the frame unless it is the destination or broadcast
6. The accepting node reads the length, then exactly that many bytes
7. Parity is checked across the whole frame, and if any byte fails nothing is delivered

Validation:

Tick rate was measured rather than assumed. With noise disabled, 0.01s per bit already broke around
10% of frames through clock drift alone. 0.02s was the lowest value that ran clean every time.

At a 5% bit error rate, over 100 transmissions: 32 frames were never read because the preamble was
corrupted, 11 were abandoned mid-frame, 41 were dropped by the parity check, 7 arrived intact and
9 were delivered corrupted without being detected. Predictions calculated from the binomial
distribution beforehand were 11% intact and 7.8% undetected, against 8.7% undetected measured
across 300 runs.

Inspecting the undetected corruptions showed that roughly half came from the unprotected length
field rather than from the data itself, which makes the header the weakest part of the current
design.

---

Next steps: collisions when two nodes transmit at once, protecting the header fields, CRC instead
of parity, IP addresses, routing between networks, ARP, ports, and a reliable transport protocol
with acknowledgements and retransmission.