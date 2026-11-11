# Phase 1 simulation results

Written by `sim/sim.py` (ngspice, behavioural op-amps; see the script's docstring). The decks are beside this file. Values are those in `docs/design.md`, "Phase 1 values".

## Inputs

Gain from the source to the codec's pins (differential), and noise over 20 Hz-20 kHz, unweighted, referred to the source. "Codec" is the codec's own floor (119 dB below 2 Vrms, A-weighted) referred back through the gain.

| Mode | Gain at 1 kHz | -3 dB low | -3 dB high | 20 kHz | Full scale in | Board noise | Codec, referred | Total | Dynamic range |
|---|---|---|---|---|---|---|---|---|---|
| Instrument | +2.13 dB | 3.77 Hz | 137 kHz | -0.09 dB | +6.1 dBu | -107.8 dBu | -112.9 dBu | -106.6 dBu | 112.7 dB |
| Line | -6.21 dB | 3.77 Hz | 139 kHz | -0.09 dB | +14.5 dBu | -104.2 dBu | -104.5 dBu | -101.3 dBu | 115.8 dB |
| Mic | +19.90 dB | 6.58 Hz | 138 kHz | -0.09 dB | -11.7 dBu | -124.0 dBu | -130.7 dBu | -123.1 dBu | 111.5 dB |

Swing at codec full scale (a 1 kHz sine giving 2 Vrms at the codec), against the 5 V rail (4.95 V, outputs stopping 0.1 V short):

| Mode | Node | Lowest | Highest | Room to the rail |
|---|---|---|---|---|
| Instrument | `bo` | 0.299 V | 4.682 V | +0.168 V |
| Instrument | `fp` | 1.064 V | 3.919 V | +0.931 V |
| Instrument | `fm` | 1.068 V | 3.923 V | +0.927 V |
| Line | `fp` | 1.064 V | 3.919 V | +0.931 V |
| Line | `fm` | 1.068 V | 3.923 V | +0.927 V |
| Mic | `p1` | 1.059 V | 3.915 V | +0.935 V |
| Mic | `p2` | 1.072 V | 3.928 V | +0.922 V |
| Mic | `mi1` | 2.363 V | 2.623 V | +2.227 V |
| Mic | `mi2` | 2.364 V | 2.624 V | +2.226 V |
| Mic | `fp` | 1.059 V | 3.915 V | +0.935 V |
| Mic | `fm` | 1.072 V | 3.928 V | +0.922 V |

- Instrument: 2.000 Vrms differential at the codec in the swing test (target 2.0 Vrms).
- Line: 2.000 Vrms differential at the codec in the swing test (target 2.0 Vrms).
- Mic: the preamp input mi1 spans 2.363-2.623 V at full scale; the OPA1612 needs 2.00-2.95 V: inside.
- Mic: the preamp input mi2 spans 2.364-2.624 V at full scale; the OPA1612 needs 2.00-2.95 V: inside.
- Mic: 2.000 Vrms differential at the codec in the swing test (target 2.0 Vrms).

## The Pi's 5 V, through to the codec

Gain from ripple on the Pi's 5 V to the codec's differential input, with the input stage's resistor pairs matched and 0.1 % apart.

| Mode | Resistors | 100 Hz | 1 kHz | 10 kHz |
|---|---|---|---|---|
| Instrument | matched | -109.8 dB | -149.5 dB | -201.0 dB |
| Instrument | 0.1 % mismatch | -109.8 dB | -149.5 dB | -201.0 dB |
| Line | matched | -240.0 dB | -240.0 dB | -240.0 dB |
| Line | 0.1 % mismatch | -215.4 dB | -239.1 dB | -240.0 dB |
| Mic | matched | -240.0 dB | -239.9 dB | -240.0 dB |
| Mic | 0.1 % mismatch | -210.6 dB | -170.6 dB | -142.2 dB |

## Phantom power on a microphone input

+48 V ramped on over 300 ms, then pin 2 (hot) shorted to ground 0.9 s after the ramp ends, with its capacitor charged.

- The thump at the codec while phantom ramps: -0.03 to +0.00 mV differential with the legs matched; -1414.94 to +637.96 mV with cold's capacitor 20 % larger and its 6.81 kOhm 0.1 % higher (2.2 dBu, -6.0 dBFS as a peak); with those parts and a 1.5 s ramp, -20.0 dBFS.
- On the short: the current through the 10 ohm into the clamps peaks at -4.44 A / +0.00 A; the clamp node runs -0.65 to 1.23 V.
- The preamp's input, behind 22 ohm, runs -0.62 to 1.23 V, carrying -1.4 / +0.0 mA.

## Outputs

- Unbalanced: -2.83 dB from the codec's differential output; -3 dB at 2.78 Hz and above 1 MHz.
- Balanced: -0.10 dB from the codec's differential output with the pad out, -20.19 dB with it in.
- At codec full scale: the ¼″ output gives 1.445 Vrms (+5.4 dBu) into 10 kOhm, the XLR 1.976 Vrms (+8.1 dBu) into 20 kOhm; the unbalanced stage swings 0.42-4.56 V, a follower 1.01-3.97 V.
- Muted: unbalanced -78.9 dB, balanced -78.9 dB, against unmuted.
- The Pi's 5 V ripple at the outputs: unbalanced -112.0 dB at 100 Hz and -151.8 dB at 1 kHz; balanced -233.1 dB and -214.9 dB.

## Phantom power on a balanced output

A stage box's +48 V through 6.81 kOhm onto pins 2 and 3 at 50 ms, then pin 2 shorted to ground at 1.0 s with its capacitor charged.

- Pin 2 with phantom on: 44.9 V.
- The driver side of the capacitor runs -0.63 to 1.62 V.
- The op-amp carries -6.6 / +13.4 mA at most.
- On the short, the current through the 10 ohm peaks at 0.00 A / +4.25 A.
