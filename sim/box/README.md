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
