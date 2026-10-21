"""Illustrative AC model, not measured IC-229H behavior. Standard Python only.

Selected RV1: 10k across DIVIDER/GND, wiper to 1uF coupling capacitor.
Input is the PWM waveform's AC fundamental, not its 5V logic swing.
Radio/microphone equivalent impedance is modeled as a resistance to AC ground.
"""
import math


def solve(matrix, rhs):
    rows = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for column in range(len(rows)):
        pivot = max(range(column, len(rows)), key=lambda i: abs(rows[i][column]))
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        if abs(scale) < 1e-30:
            raise ValueError("singular circuit")
        rows[column] = [value / scale for value in rows[column]]
        for i in range(len(rows)):
            if i != column:
                scale = rows[i][column]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[column])]
    return [row[-1] for row in rows]


def response(frequency, load, wiper=1.0):
    if not 0 < wiper <= 1:
        raise ValueError("use 0 < wiper <= 1; the grounded end is exactly zero")
    # Nodes: filter1, filter2, divider, wiper, AC side of C3, audio.
    matrix = [[0j] * 6 for _ in range(6)]
    rhs = [0j] * 6

    def branch(a, b, admittance):
        matrix[a][a] += admittance
        if b is not None:
            matrix[b][b] += admittance
            matrix[a][b] -= admittance
            matrix[b][a] -= admittance

    omega = 2 * math.pi * frequency
    matrix[0][0] += 1 / 3300
    rhs[0] = 1 / 3300  # Ideal source, 1V AC input.
    branch(0, None, 1j * omega * 100e-9)
    branch(0, 1, 1 / 3300)
    branch(1, None, 1j * omega * 100e-9)
    branch(1, 2, 1 / 10000)
    branch(2, None, 1 / 1000)
    # Near-zero upper segment approximates full clockwise end, avoiding
    # an extra special-case topology; 1mOhm is negligible in this circuit.
    branch(2, 3, 1 / max(0.001, 10000 * (1 - wiper)))
    branch(3, None, 1 / (10000 * wiper))
    branch(3, 4, 1j * omega * 1e-6)
    branch(4, 5, 1 / 100000)
    branch(5, None, 1 / load)
    return solve(matrix, rhs)[5]


if __name__ == "__main__":
    print("Illustrative 10k pot, maximum setting; 1uF coupling; ideal PWM source")
    print("Load (ohm) | Gain at 151.4 Hz | Gain at 10 kHz | Relative rejection (dB)")
    for load in (600, 1000, 2200, 10000, 100000):
        tone, carrier = (abs(response(f, load)) for f in (151.4, 10000))
        print(f"{load:11} | {tone:16.7f} | {carrier:14.9f} | {20*math.log10(carrier/tone):23.2f}")
    print("\nSelectable-tone examples: illustrative 1k load, maximum trimmer")
    reference=abs(response(151.4,1000))
    for frequency in (67,100,151.4,203.5,254.1):
        gain=abs(response(frequency,1000))
        print(f"{frequency:6.1f} Hz | {gain:.7f} V/V | {20*math.log10(gain/reference):+.2f} dB vs 151.4 Hz")
