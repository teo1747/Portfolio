"""
diagrams.py — technical illustrations for projects that have no photo.

Each function returns an inline SVG (viewBox 640 x 400) drawn from the real
architecture of the project. Colours come from CSS classes defined in
assets/style.css (.d-*), so every diagram follows the light and dark themes.

Used by build.py: a project with  image = "diagram:<name>"  gets DIAGRAMS[<name>].
"""
from __future__ import annotations

from html import escape

W, H = 640, 400


def _svg(body: str, title: str) -> str:
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}" '
            f'xmlns="http://www.w3.org/2000/svg"><rect class="d-bg" width="{W}" height="{H}"/>{body}</svg>')


def _t(x, y, s, cls="d-ink", anchor="start", size=13):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">{escape(s)}</text>'


def _box(x, y, w, h, label="", cls="d-box", tcls="d-ink", size=13, rx=6, sub=None):
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>'
    if label:
        cy = y + h / 2 + (size * 0.35) - (7 if sub else 0)
        out += _t(x + w / 2, cy, label, tcls, "middle", size)
    if sub:
        out += _t(x + w / 2, y + h / 2 + 14, sub, "d-mut", "middle", 11)
    return out


def _arrow(x1, y1, x2, y2, cls="d-wire"):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ah)"/>'


ARROW_DEF = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             'orient="auto-start-reverse"><path class="d-arrowhead" d="M0 0 L10 5 L0 10 z"/></marker></defs>')


# ---------------------------------------------------------------------------
def tcu() -> str:
    """PWM heater output, the switched NTC divider, and mid-pulse ADC sampling."""
    b = [ARROW_DEF]
    x0, x1 = 70, 610
    period = 135                       # px per 10 ms period (100 Hz)
    duty = 0.62
    # PWM output
    b.append(_t(20, 34, "LDRV heater output (100 Hz PWM)", "d-mut", size=12))
    d = f"M{x0} 120"
    x = x0
    while x < x1 - 1:
        on = min(x + period * duty, x1)
        off = min(x + period, x1)
        d += f" L{x} 70 L{on} 70 L{on} 120 L{off} 120"
        x += period
    b.append(f'<path class="d-trace" d="{d}"/>')
    # ADC node: follows the output, with RC edges
    b.append(_t(20, 174, "NTC divider at the ADC pin (fed from the switched output)", "d-mut", size=12))
    d = f"M{x0} 260"
    x = x0
    while x < x1 - 1:
        on = min(x + period * duty, x1)
        off = min(x + period, x1)
        d += (f" L{x} 260 C{x + 6} 214 {x + 10} 208 {x + 22} 206 L{on} 206"
              f" C{on + 6} 252 {on + 10} 258 {on + 22} 260 L{off} 260")
        x += period
    b.append(f'<path class="d-line2" d="{d}"/>')
    # sample points at mid on-time
    x = x0
    k = 0
    while x + period * duty / 2 < x1:
        sx = x + period * duty / 2
        b.append(f'<line class="d-dash" x1="{sx}" y1="58" x2="{sx}" y2="290"/>')
        b.append(f'<circle class="d-dot" cx="{sx}" cy="206" r="5"/>')
        if k == 0:
            b.append(_t(sx + 8, 300, "ISR at PWM_DC / 2", "d-acc", size=12))
        x += period
        k += 1
    # pipeline to regulation
    b.append(_box(70, 322, 150, 52, "16-sample average", sub="in the ISR"))
    b.append(_arrow(220, 348, 268, 348))
    b.append(_box(270, 322, 140, 52, "NTC → °C", sub="main loop"))
    b.append(_arrow(410, 348, 458, 348))
    b.append(_box(460, 322, 150, 52, "Regulation", sub="duty update, faults", cls="d-box-acc"))
    return _svg("".join(b), "Heater PWM, switched NTC divider and ADC samples taken mid-pulse")


# ---------------------------------------------------------------------------
def melibu() -> str:
    """RP2040 master on the MeLiBu bus; 11 MLX81143 nodes x 14 LEDs = 22 x 7 panel."""
    b = [ARROW_DEF]
    b.append(_box(20, 150, 112, 100, "RP2040", sub="PIO TX + RX"))
    b.append(_t(76, 272, "MeLiBu 1.x master", "d-mut", "middle", 11))
    gx, gy, cell = 178, 84, 19.5
    # bus line
    b.append(f'<line class="d-wire" x1="132" y1="200" x2="{gx - 8}" y2="200"/>')
    b.append(f'<line class="d-wire" x1="{gx - 8}" y1="60" x2="{gx - 8}" y2="340"/>')
    hues = ["d-led1", "d-led2", "d-led3"]
    for node in range(11):
        nx = gx + node * 2 * cell
        b.append(f'<rect class="d-node" x="{nx - 2}" y="{gy - 26}" width="{2 * cell}" height="{7 * cell + 30}" rx="5"/>')
        for col in range(2):
            for row in range(7):
                cx = nx + col * cell + cell / 2 - 1
                cy = gy + row * cell + cell / 2
                b.append(f'<circle class="{hues[(node + row) % 3]}" cx="{cx}" cy="{cy}" r="6.2"/>')
    b.append(_t(gx, 268, "11 MLX81143 nodes × 14 RGB LEDs = 22 × 7 panel (154 LEDs)", "d-ink", size=12))
    b.append(_t(gx, 288, "Extended-mode sub-address: subAdr = (data_len − 2) / 2", "d-mut", size=12))
    b.append(_t(gx, 306, "PWM: 15-bit linear, R G B, high byte first", "d-mut", size=12))
    b.append(_t(gx, 324, "Wiring scramble fixed in the hardware-mapping layer", "d-mut", size=12))
    return _svg("".join(b), "RP2040 driving eleven MLX81143 LED nodes over MeLiBu")


# ---------------------------------------------------------------------------
def lighting() -> str:
    """Tablet → Bluetooth → PC; one thread per gateway behind a barrier; 9 STM32 gateways."""
    b = [ARROW_DEF]
    b.append(_box(18, 40, 108, 70, "Tablet", sub="Kotlin, Compose"))
    b.append(_arrow(126, 75, 174, 75))
    b.append(_t(150, 66, "BT", "d-mut", "middle", 10))
    b.append(_t(150, 96, "JSON", "d-mut", "middle", 10))
    b.append(_box(176, 22, 196, 368, "", cls="d-box"))
    b.append(_t(274, 44, "PC application (Python)", "d-ink", "middle", 13))
    b.append(_box(192, 58, 164, 40, "MP4 decode (OpenCV)", size=11))
    b.append(_box(192, 106, 164, 40, "LED ID → frame pixel", size=11))
    # 9 thread lanes
    for i in range(9):
        y = 160 + i * 23
        b.append(f'<rect class="d-lane" x="192" y="{y}" width="164" height="17" rx="3"/>')
        b.append(_t(200, y + 12.5, f"thread {i + 1}", "d-mut", size=10))
        b.append(_arrow(356, y + 8.5, 420, y + 8.5, "d-wire-thin"))
        b.append(_box(422, y - 1, 92, 19, f"STM32 GW {i + 1}", size=10, rx=4))
        cls = "d-strip" if i < 7 else "d-strip-static"
        b.append(f'<rect class="{cls}" x="526" y="{y + 4}" width="{70 + (i * 13) % 40}" height="8" rx="4"/>')
    b.append(f'<line class="d-barrier" x1="300" y1="152" x2="300" y2="370"/>')
    b.append(_t(200, 381, "barrier: same frame on all 9", "d-acc", size=10))
    b.append(_t(468, 150, "UART 921 600 Bd", "d-mut", "middle", 10))
    b.append(_t(570, 150, "WS2812", "d-mut", "middle", 10))
    b.append(_t(422, 384, "GW 8–9: static colour zones", "d-mut", size=10))
    return _svg("".join(b), "Tablet and PC application driving nine STM32 LED gateways in lockstep")


# ---------------------------------------------------------------------------
def fruit() -> str:
    """VGG16 transfer learning pipeline."""
    b = [ARROW_DEF]
    b.append(_box(24, 150, 84, 84, "224×224", sub="RGB"))
    x = 130
    sizes = [(26, 150), (26, 130), (22, 110), (22, 90), (18, 70)]
    for i, (w, h) in enumerate(sizes):
        for k in range(2):
            b.append(f'<rect class="d-conv" x="{x + k * 7}" y="{200 - h / 2 + k * 4}" width="{w}" height="{h}" rx="3"/>')
        x += w + 26
    b.append(_t(240, 296, "VGG16 convolutional base (ImageNet weights)", "d-mut", "middle", 11))
    b.append(_arrow(x, 200, x + 26, 200))
    x += 28
    for lbl, h in (("512", 120), ("256", 90)):
        b.append(f'<rect class="d-dense" x="{x}" y="{200 - h / 2}" width="22" height="{h}" rx="4"/>')
        b.append(_t(x + 11, 200 + h / 2 + 16, lbl, "d-mut", "middle", 11))
        x += 46
    b.append(_box(x, 168, 92, 64, "softmax", sub="131 classes", cls="d-box-acc"))
    b.append(_t(320, 350, "Fruits-360 test set: 98.4 % accuracy, macro F1 0.983 (4,599 images)", "d-ink", "middle", 13))
    return _svg("".join(b), "VGG16 transfer-learning pipeline for fruit classification")


# ---------------------------------------------------------------------------
def mcu8() -> str:
    """8-bit CPU: control FSM, ALU with flags, memory map."""
    b = [ARROW_DEF]
    b.append(_box(30, 40, 250, 150, "", cls="d-box"))
    b.append(_t(155, 62, "CPU", "d-ink", "middle", 13))
    b.append(_box(46, 76, 104, 96, "Control", sub="12-state FSM"))
    b.append(_box(162, 76, 102, 54, "ALU", sub="+ − & | ++ −−"))
    for i, f in enumerate("NZVC"):
        b.append(_box(162 + i * 26, 138, 22, 30, f, size=12, rx=3, cls="d-box-acc"))
    b.append(_t(155, 214, "fetch → decode → execute", "d-acc", "middle", 12))
    # memory map
    mx, my = 400, 40
    regions = [("0x00", "ROM  128 B", 92), ("0x80", "RAM  96 B", 70), ("0xE0", "OUT ports ×16", 34), ("0xF0", "IN ports ×16", 34)]
    y = my
    for addr, name, h in regions:
        b.append(_box(mx, y, 210, h, name, size=12, rx=0))
        b.append(_t(mx - 10, y + 14, addr, "d-mut", "end", 11))
        y += h
    b.append(_t(mx + 105, y + 22, "8-bit address space", "d-mut", "middle", 11))
    b.append(_arrow(280, 90, 396, 90))
    b.append(_arrow(396, 118, 280, 118))
    b.append(_t(336, 82, "address", "d-mut", "middle", 10))
    b.append(_t(336, 134, "data", "d-mut", "middle", 10))
    b.append(_t(320, 320, "Simulated in Vivado 2024.2 / XSim · after LaMeres' reference architecture", "d-mut", "middle", 12))
    return _svg("".join(b), "Block diagram and memory map of the 8-bit microcontroller")


# ---------------------------------------------------------------------------
def filter3() -> str:
    """3x3 window on a pixel stream with two line buffers, and the adder tree."""
    b = [ARROW_DEF]
    ox, oy, c = 30, 50, 24
    for r in range(7):
        for k in range(9):
            cls = "d-px-win" if 2 <= r <= 4 and 3 <= k <= 5 else "d-px"
            if r == 3 and k == 4:
                cls = "d-px-centre"
            b.append(f'<rect class="{cls}" x="{ox + k * c}" y="{oy + r * c}" width="{c - 2}" height="{c - 2}" rx="2"/>')
    b.append(_t(ox, oy + 7 * c + 24, "Pixel stream, 3×3 window, border copied", "d-mut", size=11))
    b.append(_box(ox, oy + 7 * c + 40, 104, 34, "line buffer 1", size=11))
    b.append(_box(ox + 112, oy + 7 * c + 40, 104, 34, "line buffer 2", size=11))
    # adder tree
    tx = 300
    lv = [(9, "8 bit"), (5, "9 bit"), (3, "10 bit"), (1, "11 bit")]
    ys = [70, 150, 230, 310]
    prev = None
    for (n, lbl), y in zip(lv, ys):
        span = 262
        pts = [tx + (i + 0.5) * span / n for i in range(n)]
        for p in pts:
            b.append(f'<circle class="{"d-dot" if n == 1 else "d-node-c"}" cx="{p}" cy="{y}" r="{9 if n > 1 else 13}"/>')
        if prev:
            for i, p in enumerate(pts):
                for q in prev[min(len(prev) - 1, i * len(prev) // n): min(len(prev), (i + 1) * len(prev) // n + 1)]:
                    b.append(f'<line class="d-wire-thin" x1="{q}" y1="{ys[lv.index((n, lbl)) - 1] + 9}" x2="{p}" y2="{y - 9}"/>')
        b.append(_t(tx + span + 8, y + 4, lbl, "d-mut", size=11))
        prev = pts
    b.append(_t(tx + 131, 350, "Pipelined adder tree, explicit bit growth", "d-ink", "middle", 12))
    return _svg("".join(b), "Three by three window over a pixel stream and the pipelined adder tree")


# ---------------------------------------------------------------------------
def tempmon() -> str:
    b = [ARROW_DEF]
    b.append(_box(24, 160, 110, 70, "ADT7420", sub="on-board sensor"))
    b.append(_arrow(134, 195, 184, 195))
    b.append(_t(159, 186, "I²C", "d-mut", "middle", 10))
    b.append(_t(159, 214, "400 kHz", "d-mut", "middle", 10))
    b.append(_box(186, 140, 150, 110, "", cls="d-box"))
    b.append(_t(261, 162, "Artix-7 (Nexys 4 DDR)", "d-ink", "middle", 12))
    b.append(_box(198, 172, 126, 30, "read every 250 ms", size=11))
    b.append(_box(198, 208, 126, 30, "raw × 625 / 10000", size=11))
    b.append(_arrow(336, 170, 400, 120))
    b.append(_arrow(336, 220, 400, 280))
    # seven segment digits
    segs = {"2": "abged", "3": "abgcd", ".": "", "5": "afgcd"}
    def digit(x, y, ch):
        s = 26
        pos = {"a": (x, y, x + s, y), "b": (x + s, y, x + s, y + s), "c": (x + s, y + s, x + s, y + 2 * s),
               "d": (x, y + 2 * s, x + s, y + 2 * s), "e": (x, y + s, x, y + 2 * s), "f": (x, y, x, y + s),
               "g": (x, y + s, x + s, y + s)}
        o = ""
        for k, (a, bb, cc, dd) in pos.items():
            cls = "d-seg-on" if k in segs.get(ch, "") else "d-seg-off"
            o += f'<line class="{cls}" x1="{a}" y1="{bb}" x2="{cc}" y2="{dd}"/>'
        return o
    b.append(_box(404, 62, 210, 104, "", cls="d-box-dark"))
    b.append(digit(426, 84, "2") + digit(470, 84, "3"))
    b.append(f'<circle class="d-dot" cx="{509}" cy="{138}" r="3.5"/>')
    b.append(digit(520, 84, "5"))
    b.append(_t(574, 112, "°C", "d-seg-label", size=18))
    b.append(_box(404, 250, 210, 62, "UART → PC", sub="115 200 Bd 8N1"))
    b.append(_t(320, 360, "100 MHz · WNS +5.42 ns · 1,936 LUTs (3.1 %)", "d-ink", "middle", 13))
    return _svg("".join(b), "Temperature monitor: sensor over I2C to FPGA, seven-segment display and UART")


# ---------------------------------------------------------------------------
def sram() -> str:
    b = [ARROW_DEF]
    states = [("IDLE", 300, 60), ("READ_ADDR", 130, 140), ("READ_DATA", 130, 230), ("BURST_RD", 130, 320),
              ("WRITE_ADDR", 470, 140), ("WRITE_DATA", 470, 230), ("BURST_WR", 470, 320)]
    pos = {}
    for name, x, y in states:
        pos[name] = (x, y)
        b.append(f'<rect class="{"d-box-acc" if name == "IDLE" else "d-box"}" x="{x - 62}" y="{y - 18}" width="124" height="36" rx="18"/>')
        b.append(_t(x, y + 4, name, "d-ink", "middle", 11))
    for a, c in (("IDLE", "READ_ADDR"), ("READ_ADDR", "READ_DATA"), ("READ_DATA", "BURST_RD"),
                 ("IDLE", "WRITE_ADDR"), ("WRITE_ADDR", "WRITE_DATA"), ("WRITE_DATA", "BURST_WR")):
        (x1, y1), (x2, y2) = pos[a], pos[c]
        b.append(_arrow(x1 + (x2 - x1) * 0.25, y1 + 18, x2 - (x2 - x1) * 0.0, y2 - 20))
    b.append(_box(250, 210, 100, 120, "", cls="d-box"))
    b.append(_t(300, 236, "IOBUF ×36", "d-ink", "middle", 12))
    b.append(_t(300, 256, "bidirectional", "d-mut", "middle", 11))
    b.append(_t(300, 272, "DQ bus", "d-mut", "middle", 11))
    b.append(_t(300, 300, "512K × 36", "d-acc", "middle", 12))
    b.append(_t(300, 316, "ZBT SRAM", "d-acc", "middle", 12))
    b.append(_t(320, 380, "Single and 4-word burst access · self-checking bench vs Micron model", "d-mut", "middle", 12))
    return _svg("".join(b), "State machine of the ZBT SRAM controller and its bidirectional data bus")


# ---------------------------------------------------------------------------
def rtos() -> str:
    """Priority inheritance timeline with PendSV switches."""
    b = [ARROW_DEF]
    lanes = [("High", 80), ("Medium", 160), ("Low", 240)]
    for name, y in lanes:
        b.append(_t(20, y + 5, name, "d-mut", size=12))
        b.append(f'<line class="d-axis" x1="90" y1="{y + 16}" x2="620" y2="{y + 16}"/>')
    def run(y, x1, x2, cls="d-run"):
        return f'<rect class="{cls}" x="{x1}" y="{y - 12}" width="{x2 - x1}" height="24" rx="3"/>'
    b.append(run(240, 90, 200))                                  # low runs, takes mutex
    b.append(_t(96, 220, "lock(M)", "d-mut", size=11))
    b.append(run(80, 200, 250))                                  # high preempts
    b.append(_t(200, 60, "lock(M) → blocks", "d-acc", size=11))
    b.append(run(240, 250, 370, "d-run-boost"))                  # low inherits
    b.append(_t(256, 220, "inherits High priority", "d-acc", size=11))
    b.append(_t(310, 140, "Medium ready, cannot preempt", "d-mut", "middle", 11))
    b.append(run(80, 370, 470))                                  # high gets mutex
    b.append(_t(374, 60, "gets M", "d-mut", size=11))
    b.append(run(160, 470, 560))
    b.append(run(240, 560, 620))
    for x in (200, 250, 370, 470, 560):
        b.append(f'<line class="d-dash" x1="{x}" y1="56" x2="{x}" y2="270"/>')
        b.append(f'<path class="d-tick" d="M{x - 5} 284 L{x + 5} 284 L{x} 292 z"/>')
    b.append(_t(90, 312, "▼ PendSV context switch: r4–r11 + EXC_RETURN, s16–s31 only for FPU threads", "d-mut", size=12))
    b.append(_t(90, 340, "Mutex with priority inheritance: no unbounded priority inversion", "d-ink", size=13))
    b.append(_t(90, 364, "Checked against a Python reference model of the scheduler", "d-mut", size=12))
    return _svg("".join(b), "RTOS timeline showing priority inheritance and PendSV context switches")


# ---------------------------------------------------------------------------
def embcc() -> str:
    b = [ARROW_DEF]
    b.append(_box(24, 160, 96, 70, "C99", sub="source"))
    b.append(_arrow(120, 195, 160, 195))
    b.append(_box(162, 150, 120, 90, "front end", sub="parse · IR · opt"))
    targets = [("Cortex-M", "Thumb-1/2"), ("RISC-V", "RV32/RV64"), ("AVR", "8-bit"), ("x86-64", "")]
    for i, (n, s) in enumerate(targets):
        y = 48 + i * 82
        b.append(_arrow(282, 195, 338, y + 30))
        b.append(_box(340, y, 120, 60, n, sub=s or None))
        b.append(_arrow(460, y + 30, 498, 195))
    b.append(_box(500, 140, 116, 110, "", cls="d-box-acc"))
    b.append(_t(558, 168, "assembler", "d-ink", "middle", 12))
    b.append(_t(558, 188, "linker (ld scripts)", "d-ink", "middle", 12))
    b.append(_t(558, 212, "ELF · HEX", "d-mut", "middle", 11))
    b.append(_t(558, 228, "S-record · UF2", "d-mut", "middle", 11))
    b.append(_t(320, 384, "Encodings checked against llvm-mc / GNU as · output run under QEMU vs GCC/Clang", "d-mut", "middle", 12))
    return _svg("".join(b), "EmbCC: one C front end, four back ends, assembler and linker")


DIAGRAMS = {
    "tcu": tcu, "melibu": melibu, "lighting": lighting, "fruit": fruit, "mcu8": mcu8,
    "filter": filter3, "tempmon": tempmon, "sram": sram, "rtos": rtos, "embcc": embcc,
}
