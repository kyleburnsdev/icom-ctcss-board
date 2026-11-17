"""Plot retained TP5/TP6 maximum/minimum captures; no hardware access.

Usage: python tools/plot-board-mixing.py MAX_RUN [MIN_RUN]
Requires matplotlib/numpy; writes mixing-path.png in the first run directory.
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',nargs='+',type=Path)
    args=parser.parse_args()
    fig,axes=plt.subplots(len(args.runs),2,figsize=(12,3.5*len(args.runs)),squeeze=False,layout='constrained')
    for row,run in enumerate(args.runs):
        result=json.loads((run/'result.json').read_text())
        for column,channel in enumerate([1,2]):
            folder=run/f'ch{channel}'
            p=json.loads((folder/'capture.json').read_text())['preamble']
            raw=np.frombuffer((folder/'waveform.u8').read_bytes(),dtype=np.uint8)
            if len(raw)!=p['points']:
                raise ValueError('Incomplete RAW waveform')
            n=min(len(raw),int(.03/p['xincrement']))
            n-=n%32
            codes=raw[:n].reshape(-1,32).mean(axis=1)
            volts=(codes-p['yorigin']-p['yreference'])*p['yincrement']
            t=(np.arange(len(codes))*32+15.5)*p['xincrement']*1000
            ax=axes[row,column]
            ax.plot(t,volts,color='#067e92',linewidth=1)
            measured=result['filter' if channel==1 else 'output']
            point='TP5 filter' if channel==1 else 'TP6 audio output'
            ax.set_title(f"RV1 {result['level']}: {point}\n"
                         f"{measured['central_pp_v']*1000:.1f} mV central p-p, mean {measured['mean_v']:.4f} V")
            ax.set_xlabel('Elapsed time from capture start (ms)')
            ax.set_ylabel('Voltage (V)')
            ax.set_ylim((.3,2.8) if channel==1 else (-.12,.12))
            ax.grid(alpha=.25)
    fig.suptitle('Populated PCB: divider, level control and DC-blocked audio output\n'
                 'PTT held; TP5 ×10, TP6 ×1 (nominal 1 MΩ load); RAW-derived 32-sample averages',fontsize=12)
    fig.savefig(args.runs[0]/'mixing-path.png',dpi=170)
    plt.close(fig)


if __name__=='__main__':
    main()
