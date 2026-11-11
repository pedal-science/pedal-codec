# pedal-codec

A stereo audio board for the Raspberry Pi, built around Texas Instruments' TAC5242 codec (119 dB
ADC, 120 dB DAC):

- two inputs, each switchable between **Instrument** (1 MΩ) and **Line**, each with optional
  **+48 V phantom power**
- two **line outputs**
- JST XH connectors for all four, so the board can sit inside a case with the jacks on the panel
- power, I2S audio and control through the Pi's 40-pin header, with a HAT+ ID EEPROM

It is at the design stage: [docs/design.md](docs/design.md) is the design so far and its open
questions, and [docs/plan.md](docs/plan.md) is the route to boards made and tested.

Part of [pedal.science](https://pedal.science). The hardware is CERN-OHL-P-2.0 and the software
MIT; see [LICENSING.md](LICENSING.md).
