"""Render synchronized loaded-PTT transitions from retained evidence; no hardware.

Usage: python tools/plot-board-ptt.py RUN_DIRECTORY
Requires matplotlib/numpy; writes loaded-ptt-transitions.png.
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
    parser.add_argument('run',type=Path)
    args = parser.parse_args()
    result = json.loads((args.run/'result.json').read_text())
    fig,axes = plt.subplots(2,2,figsize=(12,7),sharex=True,sharey=True,layout='constrained')
    for bypass in [0,1]:
        for column,pressed in enumerate([True,False]):
            ax = axes[bypass,column]
            rows = [r for r in result['transitions'] if r['bypass']==bypass and r['measurement']['pressed']==pressed]
            if not rows:
                raise ValueError('Missing transition group')
            delays = []
            for row in rows:
                folder = args.run/row['name']
                delays.append(row['measurement']['latency_ms'])
                for channel,color,label,style in [(1,'#737373','TP7 PTT sense','--'),
                                                   (2,'#067e92','TP8 collector','-')]:
                    capture = folder/f'ch{channel}'
                    p = json.loads((capture/'capture.json').read_text())['preamble']
                    raw = np.frombuffer((capture/'waveform.u8').read_bytes(),dtype=np.uint8)
                    if len(raw)!=p['points']:
                        raise ValueError('Incomplete samples')
                    i = np.arange(0,len(raw),10)
                    t = ((i-p['xreference'])*p['xincrement']+p['xorigin']-row['measurement']['input_edge_s'])*1000
                    keep = (t>=-2)&(t<=12)
                    volts = (raw[i].astype(float)-p['yorigin']-p['yreference'])*p['yincrement']
                    ax.plot(t[keep],volts[keep],color=color,linestyle=style,linewidth=1,
                            alpha=.8,label=label if row is rows[0] else None)
            ax.axvline(0,color='#999999',linewidth=.6)
            ax.set_title(f"Bypass {bypass}: {'press' if pressed else 'release'}\n"
                         f"{len(rows)} captures; delay {min(delays):.3f}–{max(delays):.3f} ms")
            ax.set_xlim(-2,12)
            ax.set_ylim(-.3,5.5)
            ax.grid(alpha=.25)
            ax.legend(loc='center right',fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel('Time relative to actual TP7 input edge (ms)')
    for ax in axes[:,0]:
        ax.set_ylabel('Voltage (V)')
    fig.suptitle('Populated PCB: Q1 PTT response with 1 kΩ pull-up to +5 V\n'
                 'Overlaid synchronized RAW captures; display decimation 10 samples, timing evaluated at full resolution',fontsize=12)
    fig.savefig(args.run/'loaded-ptt-transitions.png',dpi=170)
    plt.close(fig)


if __name__=='__main__':
    main()
