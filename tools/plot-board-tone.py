"""Render a readable TP5 sequence figure from retained RAW samples; no hardware.

Usage: python tools/plot-board-tone.py RUN_DIRECTORY
Requires matplotlib/numpy. Reads existing evidence; writes tone-sequence.png.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    result = json.loads((args.run/'result.json').read_text())
    states = result['states']
    fig, axes = plt.subplots(len(states), 1, figsize=(11, 9), sharex=True, sharey=True,
                             layout='constrained')
    for ax, state in zip(axes, states):
        folder = args.run/state['name']
        meta = json.loads((folder/'capture.json').read_text())
        p = meta['preamble']
        raw = np.frombuffer((folder/'waveform.u8').read_bytes(), dtype=np.uint8)
        if len(raw) != p['points']:
            raise ValueError('Incomplete waveform')
        n = min(len(raw), int(.03/p['xincrement']))
        # Same 32-sample averaging used by the documented measurement evaluator.
        n -= n % 32
        codes = raw[:n].reshape(-1,32).mean(axis=1)
        voltage = (codes-p['yorigin']-p['yreference'])*p['yincrement']
        elapsed_ms = (np.arange(len(codes))*32+15.5)*p['xincrement']*1000
        ax.plot(elapsed_ms, voltage, color='#147b91', linewidth=1)
        measured = state['measurement']
        label = f"{state['name'].upper()}   PTT={state['ptt']}   bypass={state['bypass']}"
        if 'tone_hz' in measured:
            label += f"   {measured['tone_hz']:.3f} Hz, {measured['central_pp_v']:.3f} V central p-p"
        else:
            label += f"   tone suppressed, {1000*measured['averaged_ac_rms_v']:.1f} mV averaged AC RMS"
        ax.set_title(label, loc='left', fontsize=10)
        ax.set_ylabel('TP5 (V)')
        ax.set_ylim(.3,2.8)
        ax.grid(alpha=.25)
    axes[-1].set_xlabel('Elapsed time from start of each independent record (ms)')
    fig.suptitle('Populated PCB: physical PTT, filtered tone and bypass\n'
                 'RAW 8 V supply; each trace shows the first 30 ms of its 240 ms capture', fontsize=13)
    fig.savefig(args.run/'tone-sequence.png', dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    main()
