A network rebuilt in Python from the bit up. No sockets, no networking libraries,
nothing that hides a layer behind a function call. I wrote every part of it myself.

Why: I wanted to understand how a network actually works instead of calling a library that
does it for me. So I built each part only after running into the problem it solves. The receiver
had no way of finding the start of a message before I added a preamble, and the parity bit only
went in after I could watch noise break a message.

Design:

Built in Python. The "wire" is a shared variable holding a single bit.
It has no memory or index, so writing a new bit destroys the previous one, like voltage on copper.
Every node runs in its own thread and they share only this variable and an agreed tick rate.
The sender writes one bit per clock tick, and receivers sample half a tick later,
so every sample lands in the middle of a bit instead of on a transition.

Frame structure:

preamble | destination | source | length | data

* Preamble: 8 bits marking the start of a transmission
* Destination: 4 bits, the address the frame is meant for
* Source: 4 bits, the address it came from, so the receiver can reply
* Length: 8 bits for the number of bytes that follow, so 255 bytes at most
* Data: 9 bits per character, 8 bits of ASCII plus one parity bit

Shared Medium: Every node is on the same wire, so every node receives every bit. The filtering
happens at the receiver and not at the sender. Each node compares the destination field against
its own address and drops the frame if it does not match. An address of all ones is kept for
broadcast and everyone accepts it. Since the bits physically reach everyone and ignoring them is
just something the software agreed to do, a node that skips the check reads every frame on the
wire. That is what promiscuous mode is on real hardware.

Reception System: A receiver samples the wire non stop and goes through four states.
First it slides an 8-bit window over the incoming stream until it matches the preamble, throwing
away everything before that. Then it reads the destination and source addresses, and stops there
if the frame is not for it. Next it reads 8 bits as the payload size, and then reads exactly that
many bytes. Counting instead of looking for an end pattern means the data can contain any byte
without getting cut short by accident.

Idle Line: A wire with nobody talking sits at 0. The receiver never stops sampling, so silence
looks like a stream of zeros. That means detection only works if the preamble arrives intact,
and at 5% bit error it does not, in about a third of the transmissions.

Noise and Error Detection: The wire has a configurable chance of flipping any bit on its way
through. Each byte carries one parity bit. If any byte fails, the whole frame is dropped instead
of keeping the good parts, because parity does not tell me the other bytes are fine, only that
this one is wrong. Every reading state has a wait limit, so a frame that stops arriving halfway
is abandoned and the node goes back to listening.

What happens when a message is sent:

1. The sender turns the message into bytes and adds a parity bit to each one
2. The sender writes the frame onto the wire, one bit per clock tick
3. Every node samples the wire half a tick after each transition
4. Every node looks for the 8-bit preamble
5. Every node reads the addresses and drops the frame unless it is the destination or broadcast
6. The node that accepts it reads the length, then exactly that many bytes
7. Parity is checked on every byte, and if one fails nothing is delivered

I measured the tick rate instead of picking one. With noise off, 0.01s per bit was already
breaking around 10% of frames on its own, which is the two clocks drifting apart and not the
wire. 0.02s was the lowest value that ran clean every time. This number is specific to my
machine.

At 5% bit error, over 100 transmissions: 32 frames were never read because the preamble was
corrupted, 11 were abandoned halfway, 41 were dropped by the parity check, 7 arrived intact and
9 were delivered corrupted without anything noticing. I worked out the predictions from the
binomial distribution before running it and got 11% intact and 7.8% undetected, against 8.7%
undetected measured over 300 runs.

Looking at the corrupted messages one by one, about half of them came from the length field
getting hit rather than the data itself. The length field has no parity on it, so when it
changes the receiver reads the wrong number of bits and does not know. That makes the header
the weakest part of what I built.

Known limitations:

* The receiver syncs its clock once at the start and never again, so it drifts over a long
  message. Real networks resync on every transition, which is what Manchester encoding is for
* The length, destination and source fields have no error checking on them
* The preamble is a single run of eight 1s, so if it gets corrupted the receiver can lock onto
  eight 1s appearing inside the data instead. Ethernet repeats its preamble for this reason
* The node converts the data to text itself, which the data link layer should not be doing