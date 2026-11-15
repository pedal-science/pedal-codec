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
