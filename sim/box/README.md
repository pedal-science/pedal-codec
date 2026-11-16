# Simulations for the box's audio board

Decks written by hand for what the audio board changed. Phase 1's decks, and what regenerates them,
are in [`../results/`](../results/README.md) and `../sim.py`.

## bypass-unpowered.cir (2026-11-15)

`ngspice -b bypass-unpowered.cir`

At rest the bypass relay joins the guitar's tip to the output's tip, and the tip is still on the
buffer's input network (100 nF, 1 MΩ to VM, 1 kΩ into the OPA2197). With the analogue 5 V off,
that input's protection diodes go to rails at 0 V. The deck asks whether the dry signal clips.

The pickup is 3 H and 8 kΩ with 500 pF of lead, into an amplifier's 1 MΩ. The diodes are a generic
junction, because the OPA2197's own are not published as a model: read the result as the size of
the effect, not as a figure.

| Pickup, peak | At the output, peak | Distortion (ten harmonics) |
|---|---|---|
| 0.1 V | 0.099 V | 0.00004 % |
| 0.3 V | 0.297 V | 0.005 % |
| 1 V | 0.66 V | 35 % |
| 2 V | 1.05 V | 31 % |

So an unpowered bypass is clean for quiet playing and clips a loud guitar. Powered, the buffer's
input sits at the mid-rail with 2.4 V either side, and this does not happen. What follows from it
was a second relay, K2, which takes the tip off the buffer while bypassed (the owner, 2026-11-15):
[../../docs/box-board.md](../../docs/box-board.md), "Decided while drawing". The deck is the
board as it was with one relay.

## relay-release-thump.cir (2026-11-15)

`ngspice -b relay-release-thump.cir`

At power-on each output stage rises to the mid-rail, and its 22 µF coupling capacitor charges
through the bleed on the stage's side of K1. Whatever is still on the bleed when the relays are
energised steps onto the output's tip. The deck takes the stage as a follower of the mid-rail and
reads the bleed's voltage at intervals after the analogue 5 V comes up. Edit `R47` for the rows.

| Bleed | 1 s | 2 s | 3 s | 5 s | 8 s | 10 s | 15 s | 20 s |
|---|---|---|---|---|---|---|---|---|
| 100 kΩ (phase 2's) | 0.69 V | 1.01 V | 0.97 V | 0.61 V | 0.22 V | 0.10 V | 12 mV | 1.4 mV |
| 22 kΩ | 0.39 V | 0.33 V | 0.20 V | 64 mV | 11 mV | 3.4 mV | 0.2 mV | |
| 10 kΩ (fitted) | 0.21 V | 0.14 V | 77 mV | 24 mV | 4.1 mV | 1.3 mV | 0.1 mV | |
| 4.7 kΩ | 0.10 V | 60 mV | 34 mV | 10 mV | 1.8 mV | 0.6 mV | | |

Below 10 kΩ the mid-rail's own filter (two stages, 0.5 s and 1 s) is what is left, so a smaller
bleed buys little. With 10 kΩ and a wait of 10 s the step is about a millivolt.

## mic-coupling.cir (2026-11-16)

`ngspice -b mic-coupling.cir`

Phase 2 put two 47 µF 63 V capacitors back to back in each leg of the mic input (23.5 µF), which
is what phantom power needs. The box supplies none, so each leg has one 22 µF 16 V part with its
positive end toward the preamp. The deck is the network from the socket to the preamp's inputs
(100 kΩ bleeds, the capacitor, 10 Ω, 22 Ω, 1.2 kΩ to the mid-rail) with a 150 Ω microphone, and
compares the two.

| | 22 µF a leg (fitted) | 23.5 µF a leg (phase 2) |
|---|---|---|
| Level at 1 kHz, into the preamp | −0.84 dB | −0.84 dB |
| Level at 20 Hz | −1.16 dB | −1.12 dB |
| Low corner (−3 dB from that) | 5.1 Hz | 4.8 Hz |
| The network's noise, 20 Hz to 20 kHz | 0.255 µV | the same: the capacitor isn't in it |
| Hum rejection at 50 Hz with the two legs' capacitors 20 % apart each way | 27.7 dB | 28.2 dB |
| The same at 100 Hz | 33.6 dB | 34.2 dB |

So the change costs nothing that can be heard. The last two rows are the worst case the
capacitors' ±20 % tolerance allows, and are the same weakness in both: at low frequencies the
rejection of hum picked up on the cable depends on how well the two capacitors match, because
each works against only 1.2 kΩ. Parts from one reel match far better than 20 %; it is measured
on the built board (plan.md, phase 8).

What one capacitor sees: 2.5 V, positive end at the mid-rail, in use. With 48 V put on the socket
from outside through a desk's 6.8 kΩ a leg, 42 V the other way round, which a 16 V part does not
survive. That is the case the phase 2 pairs were for, and the box gives it up
([../../docs/box-board.md](../../docs/box-board.md), "Mic input").
