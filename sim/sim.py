#!/usr/bin/env python3
"""Phase 1 simulations for pedal-codec, in ngspice (docs/plan.md, phase 1).

The circuit is the one in docs/design.md, with the values chosen in phase 1, restated here as
SPICE netlists. Five groups of tests:

  inputs    each input mode (Instrument, Line, Mic): gain and -3 dB corners into the codec,
            noise referred to the input over 20 Hz-20 kHz, and the swing of every op-amp at codec
            full scale against the 5 V rail
  supply    the Pi's 5 V ripple, through the board's filter and mid-rail reference, to the codec's
            input in each mode
  phantom   +48 V ramped onto a microphone input, then a charged pin shorted: what the clamps,
            the series resistors and the preamp's inputs carry, and the thump the codec sees
  outputs   the unbalanced stage and the balanced followers: level at full scale with the pad in
            and out, swing against the rail, the mute's depth
  balphant  a stage box's +48 V on a balanced output, then a charged pin shorted, after the
            pedal's own test (pedal.project schematic/balanced-output-sim.py)

The op-amps are behavioural: a single-pole open loop with the part's gain-bandwidth, an output
that stops 0.1 V from either rail, and the part's input voltage noise as an equivalent resistor
in series with the non-inverting input (R = en^2 / 4kT). Current noise is left out; it matters
only at the 1 MOhm node, where the OPA2197's is a few fA/rtHz. The models have no output current
limit, so the phantom tests report the current an op-amp would have to carry. Input common-mode
limits are checked here, in Python, against each node's swing. Swap in the makers' models when
the schematic is reviewed.

    python3 sim/sim.py [--ngspice PATH]

Writes sim/results/README.md and the decks it ran (sim/results/*.cir).
"""
import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
K = 1.380649e-23
T = 300.15  # ngspice's default 27 C


def ren(en):
    """Equivalent series resistance for an input voltage noise density in V/rtHz."""
    return en * en / (4 * K * T)


# Datasheet figures (typical, 1 kHz) for each op-amp
PARTS = {
    'OPA2197': dict(gbw=10e6, en=5.5e-9),    # instrument buffer
    'OPA1612': dict(gbw=40e6, en=1.1e-9),    # mic preamp
    'OPA1656': dict(gbw=53e6, en=2.9e-9),    # outputs, mid-rail buffer
}
FDA = dict(gbw=9e6, en=3.7e-9)               # OPA1637

RAIL = 4.95      # the analogue 5 V after the load switch and filter, nominal
SWING = 0.1      # how close an output gets to a rail
VM = RAIL / 2    # mid-rail
CODEC_FS = 2.0   # Vrms differential at the codec, default VREF
CODEC_NOISE = 2.0 / 10 ** (119 / 20)   # Vrms, A-weighted, referred to the codec's input
DBU = 0.7746

# Values chosen in phase 1 (docs/design.md, "Phase 1 values")
V = dict(
    rf=4.99e3,         # FDA feedback, each side
    cf=220e-12,        # across each rf (145 kHz)
    rg_inst=3.83e3,    # Instrument: FDA gain 1.30
    rg_line=10e3,      # Line: FDA gain 0.50; 10 kOhm per leg is the line input's impedance
    rg_mic=4.99e3,     # Mic: FDA gain 1.00
    rf_mic=249.0,      # preamp feedback, each half
    rg_preamp=49.9,    # preamp gain resistor: 1 + 2*249/49.9 = 10.98
    rb_mic=1.2e3,      # mic bias, each leg to mid-rail
    rs_cap=10.0,       # between the phantom capacitor and the clamps
    rs_in=22.0,        # between the clamps and the op-amp input
    c_ph=23.5e-6,      # 2 x 47 uF 63 V back to back
    r_ph=6.81e3,
    rd_out=7.5e3,      # unbalanced output: difference amp feedback
    ri_out=9.09e3,     # its input resistors; with the mute's 1 kOhm, gain 7.5/10.09 = 0.743
    r_mute=1e3,
    r_pad1=91e3,       # balanced pad: 91k over 10k, -20.1 dB
    r_pad2=10e3,
    rbf=1.3e3,         # balanced followers: gain 1 + 1.3/10 = 1.13, making up the mute's
    rbg=10e3,          # series resistor against the loads on the codec's output
)

OPAMP = """\
.subckt OPA inp inn out vcc vee PARAMS: gbw=10e6 ren=500
Ren inp inp2 {ren}
Rin inp2 inn 1T
Eg g0 0 inp2 inn 1e6
Rp g0 x 1
Cp x 0 {1e6/(2*3.14159265*gbw)}
Bout out 0 V = max(min(v(x), v(vcc)-%(sw)g), v(vee)+%(sw)g)
.ends OPA
.subckt FDA inp inn outp outm vocm vcc vee PARAMS: gbw=9e6 ren=800
Ren inp inp2 {ren}
Rin inp2 inn 1T
Eg g0 0 inp2 inn 1e6
Rp g0 x 1
Cp x 0 {1e6/(2*3.14159265*gbw)}
Bp outp 0 V = max(min(v(vocm)+v(x)/2, v(vcc)-%(sw)g), v(vee)+%(sw)g)
Bm outm 0 V = max(min(v(vocm)-v(x)/2, v(vcc)-%(sw)g), v(vee)+%(sw)g)
.ends FDA
.model DSCH D(Is=31.7u Rs=.051 N=1.373 Cjo=190p M=.3 Eg=.69 Xti=2 BV=40 IBV=1m)
.model SWM SW(Ron=0.1 Roff=1G Vt=0.5 Vh=0)
""" % dict(sw=SWING)


def opa(name, part, inp, inn, out):
    p = PARTS[part]
    return f'X{name} {inp} {inn} {out} a5 0 OPA gbw={p["gbw"]:g} ren={ren(p["en"]):.4g}\n'


def supply(ripple=0.0):
    """The Pi's 5 V, the load switch, the LC filter, and the buffered mid-rail."""
    return f"""\
VPI pi5 0 DC 5.0 AC {ripple:g}
Rls pi5 n1 0.08
Lf n1 n2 10u
Rdcr n2 a5 0.13
Ca5 a5 c5 100u
Resr c5 0 0.02
Cb5 a5 0 10u
Iload a5 0 DC 0.06
Rm1 a5 mr 10k
Rm2 mr 0 10k
Cmr mr 0 100u
Rm3 mr mr2 10k
Cmr2 mr2 0 100u
{opa('MR', 'OPA1656', 'mr2', 'vm', 'vm')}Cvm vm 0 10u
"""


def fda_and_codec(mism=1.0):
    """The FDA and the codec's input: 10 uF, 47 ohm and 2.2 nF, then 5 kOhm per pin."""
    rf = V['rf']
    return f"""\
XF sp sn fp fm vm a5 0 FDA gbw={FDA['gbw']:g} ren={ren(FDA['en']):.4g}
Rf1 fm sp {rf:g}
Cf1 fm sp {V['cf']:g}
Rf2 fp sn {rf * mism:g}
Cf2 fp sn {V['cf']:g}
Rk1 fp k1 47
Rk2 fm k2 47
Ck k1 k2 2.2n
Cc1 k1 cp 10u
Cc2 k2 cm 10u
Rc1 cp vcod 5k
Rc2 cm vcod 5k
Vcod vcod 0 DC 1.375
"""


def mode_inst(src='AC 1', mism=1.0):
    rg = V['rg_inst']
    return f"""\
Vs src 0 DC 0 {src}
Rpu src tip 10k
Cin tip bin 100n
Rbias bin vm 1meg
Rpi bin bin2 1k
{opa('B', 'OPA2197', 'bin2', 'bo', 'bo')}Rg1 bo sp {rg:g}
Rg2 vm sn {rg * mism:g}
""", ['bo', 'fp', 'fm']


def mode_line(src='AC 1', mism=1.0):
    rg = V['rg_line']
    return f"""\
Vs hs 0 DC 0 {src}
Rsh hs hot 100
Rsc cold 0 100
Rbh hot 0 100k
Rbc cold 0 100k
Cl1 hot l1 10u
Cl2 cold l2 10u
Rg1 l1 sp {rg:g}
Rg2 l2 sn {rg * mism:g}
""", ['fp', 'fm']


def mic_front(vph='Vph vph 0 DC 48', extra='', cm=1.0, rm=1.0):
    """XLR to the preamp's inputs: phantom feed, capacitors, series resistors, clamps, bias."""
    return f"""\
{vph}
Rph1 hot vph {V['r_ph']:g}
Rph2 cold vph {V['r_ph'] * rm:g}
Cm1 hot q1 {V['c_ph']:g}
Resr1 q1 m1 0.3
Cm2 cold q2 {V['c_ph'] * cm:g}
Resr2 q2 m2 0.3
Rs1 m1 c1 {V['rs_cap']:g}
Rs2 m2 c2 {V['rs_cap']:g}
Dh1 c1 a5 DSCH
Dl1 0 c1 DSCH
Dh2 c2 a5 DSCH
Dl2 0 c2 DSCH
Ri1 c1 mi1 {V['rs_in']:g}
Ri2 c2 mi2 {V['rs_in']:g}
Rb1 mi1 vm {V['rb_mic']:g}
Rb2 mi2 vm {V['rb_mic']:g}
{extra}"""


def mode_mic(src='AC 1', mism=1.0):
    rg = V['rg_mic']
    return f"""\
Vs hs hc DC 0 {src}
Rsh hs hot 75
Rsc hc cold 75
{mic_front()}{opa('P1', 'OPA1612', 'mi1', 'f1', 'p1')}{opa('P2', 'OPA1612', 'mi2', 'f2', 'p2')}Rfa p1 f1 {V['rf_mic']:g}
Rgp f1 f2 {V['rg_preamp']:g}
Rfb p2 f2 {V['rf_mic']:g}
Rg1 p1 sp {rg:g}
Rg2 p2 sn {rg * mism:g}
""", ['p1', 'p2', 'mi1', 'mi2', 'fp', 'fm']


MODES = {
    'Instrument': (mode_inst, 'tip', 1.0),
    'Line': (mode_line, 'hot-cold', 1.0),
    'Mic': (mode_mic, 'hot-cold, 150 ohm', 1.0),
}

# ----------------------------------------------------------------------------------------------


def nodesets(body):
    """Start every op-amp's internal node where it will settle, so the operating point converges:
    single-ended op-amps at the mid-rail, the FDA's differential node at zero."""
    sets = []
    for inst in re.findall(r'^X(\w+) ', body, re.M):
        sets.append(f'v(x{inst.lower()}.x)={0 if inst == "F" else VM:g}')
    sets.append(f'v(vm)={VM:g} v(a5)={RAIL:g}')
    return '.nodeset ' + ' '.join(sets) + '\n'


def run(name, body, control, ngspice):
    deck = f'* {name}\n{OPAMP}{body}{nodesets(body)}.control\n{control}\n.endc\n.end\n'
    path = OUT / f'{name}.cir'
    path.write_text(deck)
    r = subprocess.run([ngspice, '-b', str(path)], capture_output=True, text=True)
    text = r.stdout + r.stderr
    if r.returncode != 0 or 'Error' in text and 'Error on line' in text:
        sys.exit(f'ngspice failed on {name}:\n{text[-3000:]}')
    vals = {}
    for m in re.finditer(r'^\s*([a-z_0-9]+)\s*=\s*([-+0-9.eE]+)', text, re.M):
        vals[m.group(1)] = float(m.group(2))
    return vals, text


def dbu(v):
    return 20 * math.log10(v / DBU) if v > 0 else float('-inf')


def test_inputs(ng):
    rows, swing_rows, notes = [], [], []
    for mode, (fn, _, _) in MODES.items():
        body, nodes = fn()
        circuit = supply() + fda_and_codec() + body
        ctrl = """\
ac dec 40 1 1meg
let g = db(mag(v(cp)-v(cm))+1e-12)
meas ac g1k find g at=1k
meas ac g10 find g at=10
meas ac g20k find g at=20k
let gm = g - g1k
meas ac flo when gm=-3 cross=1
meas ac fhi when gm=-3 cross=last
noise v(cp,cm) Vs dec 50 20 20000
setplot noise2
print inoise_total onoise_total"""
        vals, _ = run(f'inputs-{mode.lower()}-ac', circuit, ctrl, ng)
        gain = 10 ** (vals['g1k'] / 20)
        n_in = vals['inoise_total']
        fs_in = CODEC_FS / gain
        codec_ref = CODEC_NOISE / gain
        total = math.sqrt(n_in ** 2 + codec_ref ** 2)
        rows.append((mode, vals['g1k'], vals['flo'], vals['fhi'], vals['g20k'] - vals['g1k'],
                     dbu(fs_in), dbu(n_in), dbu(codec_ref), dbu(total), dbu(fs_in) - dbu(total)))

        # Swing at codec full scale: a 1 kHz sine sized to give 2 Vrms at the codec
        amp = fs_in * math.sqrt(2)
        body_t, nodes = fn(src=f'SIN(0 {amp:g} 1k)')
        circuit = supply() + fda_and_codec() + body_t
        meas = '\n'.join(f'meas tran mx_{n} max v({n}) from=2m to=6m\nmeas tran mn_{n} min v({n}) from=2m to=6m'
                         for n in nodes)
        ctrl = f"""\
tran 2u 6m
let vd = v(cp)-v(cm)
meas tran vrms rms vd from=2m to=6m
{meas}"""
        vals, _ = run(f'inputs-{mode.lower()}-swing', circuit, ctrl, ng)
        for n in nodes:
            hi, lo = vals[f'mx_{n}'], vals[f'mn_{n}']
            # the room left before the output stops at the rail
            room = min(RAIL - SWING - hi, lo - SWING)
            swing_rows.append((mode, n, lo, hi, room))
        if mode == 'Mic':
            # OPA1612 inputs need 2 V from each rail
            for n in ('mi1', 'mi2'):
                hi, lo = vals[f'mx_{n}'], vals[f'mn_{n}']
                ok = lo >= 2.0 and hi <= RAIL - 2.0
                notes.append(f'Mic: the preamp input {n} spans {lo:.3f}-{hi:.3f} V at full scale; '
                             f"the OPA1612 needs 2.00-{RAIL - 2:.2f} V: {'inside' if ok else 'OUTSIDE'}.")
        notes.append(f'{mode}: {vals["vrms"]:.3f} Vrms differential at the codec in the swing test '
                     f'(target {CODEC_FS} Vrms).')
    return rows, swing_rows, notes


def test_supply(ng):
    rows = []
    for mode, (fn, _, _) in MODES.items():
        for mism, label in ((1.0, 'matched'), (1.001, '0.1 % mismatch')):
            body, _ = fn(src='AC 0', mism=mism)
            circuit = supply(ripple=1.0) + fda_and_codec(mism) + body
            ctrl = """\
ac dec 20 10 100k
let g = db(mag(v(cp)-v(cm))+1e-12)
meas ac p100 find g at=100
meas ac p1k find g at=1k
meas ac p10k find g at=10k"""
            vals, _ = run(f'supply-{mode.lower()}-{label.split()[0]}', circuit, ctrl, ng)
            rows.append((mode, label, vals['p100'], vals['p1k'], vals['p10k']))
    return rows


def test_phantom(ng, cm=1.0, rm=1.0, tag='', ramp=0.3):
    """Phantom ramped on over 300 ms, held, then hot shorted to ground with the capacitor charged.
    cm and rm scale cold's capacitor and phantom resistor, to see the thump with parts that differ."""
    vph = f'Vph vph 0 PWL(0 0 50m 0 {0.05 + ramp:g} 48 {ramp + 2:g} 48)'
    ts = ramp + 0.9
    short = f'Ssh hot 0 shc 0 SWM\nVshc shc 0 PWL(0 0 {ts:g} 0 {ts + 1e-4:g} 1)\n'
    body = f"""\
Vs hs hc DC 0
Rsh hs hot 75
Rsc hc cold 75
{mic_front(vph=vph, extra=short, cm=cm, rm=rm)}{opa('P1', 'OPA1612', 'mi1', 'f1', 'p1')}{opa('P2', 'OPA1612', 'mi2', 'f2', 'p2')}Rfa p1 f1 {V['rf_mic']:g}
Rgp f1 f2 {V['rg_preamp']:g}
Rfb p2 f2 {V['rf_mic']:g}
Rg1 p1 sp {V['rg_mic']:g}
Rg2 p2 sn {V['rg_mic']:g}
"""
    circuit = supply() + fda_and_codec() + body
    a, b, e = ts - 0.01, ts + 0.3, ts + 0.3
    ctrl = f"""\
tran 20u {e:g} 0 20u uic
let vd = v(cp)-v(cm)
meas tran thump_max max vd from=0 to={a:g}
meas tran thump_min min vd from=0 to={a:g}
meas tran c1_max max v(c1) from={a:g} to={b:g}
meas tran c1_min min v(c1) from={a:g} to={b:g}
meas tran mi1_min min v(mi1) from={a:g} to={b:g}
meas tran mi1_max max v(mi1) from={a:g} to={b:g}
meas tran ihot_max max i(vsense) from={a:g} to={b:g}
meas tran ihot_min min i(vsense) from={a:g} to={b:g}
meas tran irs_max max i(vrs) from={a:g} to={b:g}
meas tran irs_min min i(vrs) from={a:g} to={b:g}"""
    # current through the capacitor's series resistor (all of it reaches the clamps or the input)
    circuit = circuit.replace(f"Rs1 m1 c1 {V['rs_cap']:g}", f"Rs1 m1 m1s {V['rs_cap']:g}\nVsense m1s c1 DC 0")
    circuit = circuit.replace(f"Ri1 c1 mi1 {V['rs_in']:g}", f"Ri1 c1 ri1 {V['rs_in']:g}\nVrs ri1 mi1 DC 0")
    vals, text = run('phantom-mic' + tag, circuit, ctrl, ng)
    return vals


def outputs_circuit(pad=False, mute=False, src='AC 1', ripple=0.0, extra=''):
    """Codec's differential output to the unbalanced stage and to the balanced followers."""
    tap = 'xp' if not pad else 'tpp'
    tapm = 'xm' if not pad else 'tpm'
    mute_sw = ('Rmu3 xp vm 0.1\nRmu4 xm vm 0.1' if mute else '')
    return supply(ripple) + f"""\
Vo op 0 DC 1.375 {src}
Eo om 0 vcod2 op 1
Vcod2 vcod2 0 DC 2.75
Co1 op x1 10u
Co2 om x2 10u
Rmu1 x1 xp {V['r_mute']:g}
Rmu2 x2 xm {V['r_mute']:g}
{mute_sw}
Ru1 xp ua {V['ri_out']:g}
Ru2 ua vm {V['rd_out']:g}
Ru3 xm ub {V['ri_out']:g}
Ru4 uo ub {V['rd_out']:g}
{opa('U', 'OPA1656', 'ua', 'ub', 'uo')}Cuo uo uo2 10u
Ruo uo2 jack 100
Rjb jack 0 100k
Rload jack 0 10k
Rbp xp vm 100k
Rbm xm vm 100k
Rpa1 xp tpp {V['r_pad1']:g}
Rpa2 tpp vm {V['r_pad2']:g}
Rpb1 xm tpm {V['r_pad1']:g}
Rpb2 tpm vm {V['r_pad2']:g}
{opa('H', 'OPA1656', tap, 'hn', 'ho')}{opa('C', 'OPA1656', tapm, 'cn', 'co')}Rhf ho hn {V['rbf']:g}
Rhg hn vm {V['rbg']:g}
Rcf co cn {V['rbf']:g}
Rcg cn vm {V['rbg']:g}
Rh ho h 100
Rc co c 100
Dhh h a5 DSCH
Dhl 0 h DSCH
Dch c a5 DSCH
Dcl 0 c DSCH
Ch h hc {V['c_ph']:g}
Cc c cc {V['c_ph']:g}
Rh2 hc pin2 10
Rc2 cc pin3 10
Rbl2 pin2 0 100k
Rbl3 pin3 0 100k
Rrcv pin2 pin3 20k
{extra}"""


def test_outputs(ng):
    res = {}
    ctrl = """\
ac dec 40 1 1meg
let gu = db(mag(v(jack))+1e-12)
let gb = db(mag(v(pin2)-v(pin3))+1e-12)
meas ac gu1k find gu at=1k
meas ac gb1k find gb at=1k
let gum = gu - gu1k
meas ac fulo when gum=-3 cross=1
meas ac fuhi when gum=-3 cross=last"""
    for pad in (False, True):
        vals, _ = run(f'outputs-ac-pad{"in" if pad else "out"}', outputs_circuit(pad=pad), ctrl, ng)
        res[f'pad{pad}'] = vals
    vals, _ = run('outputs-ac-muted', outputs_circuit(mute=True), ctrl, ng)
    res['muted'] = vals
    # Full scale: 2 Vrms differential means 1 Vrms on each pin, opposite
    amp = math.sqrt(2) * CODEC_FS / 2
    ctrl = """\
tran 2u 6m
meas tran ju rms v(jack) from=2m to=6m
let vb = v(pin2)-v(pin3)
meas tran jb rms vb from=2m to=6m
meas tran uo_mx max v(uo) from=2m to=6m
meas tran uo_mn min v(uo) from=2m to=6m
meas tran ho_mx max v(ho) from=2m to=6m
meas tran ho_mn min v(ho) from=2m to=6m"""
    vals, _ = run('outputs-swing', outputs_circuit(src=f'SIN(1.375 {amp:g} 1k)'), ctrl, ng)
    res['swing'] = vals
    ctrl = """\
ac dec 20 10 100k
let gu = db(mag(v(jack))+1e-12)
let gb = db(mag(v(pin2)-v(pin3))+1e-12)
meas ac u100 find gu at=100
meas ac u1k find gu at=1k
meas ac b100 find gb at=100
meas ac b1k find gb at=1k"""
    vals, _ = run('outputs-supply', outputs_circuit(src='AC 0', ripple=1.0), ctrl, ng)
    res['supply'] = vals
    return res


def test_balphant(ng):
    """+48 V from a stage box onto pin 2 and pin 3, then pin 2 shorted with the capacitor charged."""
    extra = """\
Vsp sph 0 PWL(0 0 50m 0 60m 48 2 48)
Rsp2 sph pin2 6.81k
Rsp3 sph pin3 6.81k
Ssh pin2 0 shc 0 SWM
Vshc shc 0 PWL(0 0 1.0 0 1.0001 1)
"""
    circuit = outputs_circuit(src='AC 0', extra=extra)
    circuit = circuit.replace('Rh ho h 100', 'Rh ho hs 100\nVih hs h DC 0')
    ctrl = """\
tran 20u 1.3 0 20u uic
meas tran h_mx max v(h) from=0.04 to=1.3
meas tran h_mn min v(h) from=0.04 to=1.3
meas tran io_mx max i(vih) from=0.04 to=1.3
meas tran io_mn min i(vih) from=0.04 to=1.3
meas tran pin2_on find v(pin2) at=0.9"""
    vals, _ = run('balanced-phantom', circuit, ctrl, ng)
    # the clamp current: what flows through the 10 ohm into the capacitor, less the op-amp's share
    ctrl2 = """\
tran 20u 1.3 0 20u uic
meas tran ish_mx max i(vrh2) from=0.99 to=1.3
meas tran ish_mn min i(vrh2) from=0.99 to=1.3"""
    circuit2 = circuit.replace('Rh2 hc pin2 10', 'Rh2 hc hr 10\nVrh2 hr pin2 DC 0')
    vals2, _ = run('balanced-phantom-short', circuit2, ctrl2, ng)
    vals.update(vals2)
    return vals


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--ngspice', default='ngspice')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    ng = args.ngspice

    rows, swing, notes = test_inputs(ng)
    sup = test_supply(ng)
    ph = test_phantom(ng)
    phm = test_phantom(ng, cm=1.2, rm=1.001, tag='-mismatched')
    phs = test_phantom(ng, cm=1.2, rm=1.001, tag='-mismatched-slow', ramp=1.5)
    outs = test_outputs(ng)
    bp = test_balphant(ng)

    L = ['# Phase 1 simulation results', '',
         'Written by `sim/sim.py` (ngspice, behavioural op-amps; see the script\'s docstring). '
         'The decks are beside this file. Values are those in `docs/design.md`, "Phase 1 values".', '',
         '## Inputs', '',
         'Gain from the source to the codec\'s pins (differential), and noise over 20 Hz-20 kHz, '
         'unweighted, referred to the source. "Codec" is the codec\'s own floor (119 dB below 2 Vrms, '
         'A-weighted) referred back through the gain.', '',
         '| Mode | Gain at 1 kHz | -3 dB low | -3 dB high | 20 kHz | Full scale in | Board noise | Codec, referred | Total | Dynamic range |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for m, g, lo, hi, d20, fs, n, c, t, dr in rows:
        L.append(f'| {m} | {g:+.2f} dB | {lo:.2f} Hz | {hi / 1e3:.0f} kHz | {d20:+.2f} dB | {fs:+.1f} dBu | '
                 f'{n:.1f} dBu | {c:.1f} dBu | {t:.1f} dBu | {dr:.1f} dB |')
    L += ['', 'Swing at codec full scale (a 1 kHz sine giving 2 Vrms at the codec), against the 5 V '
          f'rail ({RAIL} V, outputs stopping {SWING} V short):', '',
          '| Mode | Node | Lowest | Highest | Room to the rail |', '|---|---|---|---|---|']
    for m, n, lo, hi, room in swing:
        L.append(f'| {m} | `{n}` | {lo:.3f} V | {hi:.3f} V | {room:+.3f} V |')
    L += [''] + [f'- {x}' for x in notes]
    L += ['', '## The Pi\'s 5 V, through to the codec', '',
          'Gain from ripple on the Pi\'s 5 V to the codec\'s differential input, with the input stage\'s '
          'resistor pairs matched and 0.1 % apart.', '',
          '| Mode | Resistors | 100 Hz | 1 kHz | 10 kHz |', '|---|---|---|---|---|']
    for m, lab, a, b, c in sup:
        L.append(f'| {m} | {lab} | {a:.1f} dB | {b:.1f} dB | {c:.1f} dB |')
    L += ['', '## Phantom power on a microphone input', '',
          '+48 V ramped on over 300 ms, then pin 2 (hot) shorted to ground 0.9 s after the ramp ends, with its '
          'capacitor charged.', '',
          f'- The thump at the codec while phantom ramps: {ph["thump_min"] * 1e3:+.2f} to {ph["thump_max"] * 1e3:+.2f} mV '
          f'differential with the legs matched; {phm["thump_min"] * 1e3:+.2f} to {phm["thump_max"] * 1e3:+.2f} mV with cold\'s '
          f'capacitor 20 % larger and its 6.81 kOhm 0.1 % higher ({dbu(max(abs(phm["thump_min"]), abs(phm["thump_max"])) / math.sqrt(2)):.1f} dBu, '
          f'{20 * math.log10(max(abs(phm["thump_min"]), abs(phm["thump_max"])) / (CODEC_FS * math.sqrt(2))):.1f} dBFS as a peak); '
          f'with those parts and a 1.5 s ramp, {20 * math.log10(max(abs(phs["thump_min"]), abs(phs["thump_max"])) / (CODEC_FS * math.sqrt(2))):.1f} dBFS.',
          f'- On the short: the current through the {V["rs_cap"]:g} ohm into the clamps peaks at '
          f'{ph["ihot_min"]:.2f} A / {ph["ihot_max"]:+.2f} A; the clamp node runs {ph["c1_min"]:.2f} to {ph["c1_max"]:.2f} V.',
          f'- The preamp\'s input, behind {V["rs_in"]:g} ohm, runs {ph["mi1_min"]:.2f} to {ph["mi1_max"]:.2f} V, carrying '
          f'{ph["irs_min"] * 1e3:.1f} / {ph["irs_max"] * 1e3:+.1f} mA.']
    o = outs
    L += ['', '## Outputs', '',
          f'- Unbalanced: {o["padFalse"]["gu1k"] - 6.02:+.2f} dB from the codec\'s differential output; -3 dB at '
          f'{o["padFalse"]["fulo"]:.2f} Hz and ' + (f'{o["padFalse"]["fuhi"] / 1e3:.0f} kHz.' if o["padFalse"]["fuhi"] > 1e3 else 'above 1 MHz.'),
          f'- Balanced: {o["padFalse"]["gb1k"] - 6.02:+.2f} dB from the codec\'s differential output with the pad out, {o["padTrue"]["gb1k"] - 6.02:+.2f} dB with it in.',
          f'- At codec full scale: the ¼″ output gives {o["swing"]["ju"]:.3f} Vrms ({dbu(o["swing"]["ju"]):+.1f} dBu) into 10 kOhm, '
          f'the XLR {o["swing"]["jb"]:.3f} Vrms ({dbu(o["swing"]["jb"]):+.1f} dBu) into 20 kOhm; the unbalanced stage swings '
          f'{o["swing"]["uo_mn"]:.2f}-{o["swing"]["uo_mx"]:.2f} V, a follower {o["swing"]["ho_mn"]:.2f}-{o["swing"]["ho_mx"]:.2f} V.',
          f'- Muted: unbalanced {o["muted"]["gu1k"] - o["padFalse"]["gu1k"]:.1f} dB, balanced {o["muted"]["gb1k"] - o["padFalse"]["gb1k"]:.1f} dB, against unmuted.',
          f'- The Pi\'s 5 V ripple at the outputs: unbalanced {o["supply"]["u100"]:.1f} dB at 100 Hz and {o["supply"]["u1k"]:.1f} dB at 1 kHz; '
          f'balanced {o["supply"]["b100"]:.1f} dB and {o["supply"]["b1k"]:.1f} dB.']
    L += ['', '## Phantom power on a balanced output', '',
          'A stage box\'s +48 V through 6.81 kOhm onto pins 2 and 3 at 50 ms, then pin 2 shorted to ground at 1.0 s '
          'with its capacitor charged.', '',
          f'- Pin 2 with phantom on: {bp["pin2_on"]:.1f} V.',
          f'- The driver side of the capacitor runs {bp["h_mn"]:.2f} to {bp["h_mx"]:.2f} V.',
          f'- The op-amp carries {bp["io_mn"] * 1e3:.1f} / {bp["io_mx"] * 1e3:+.1f} mA at most.',
          f'- On the short, the current through the 10 ohm peaks at {bp["ish_mn"]:.2f} A / {bp["ish_mx"]:+.2f} A.']
    (OUT / 'README.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
