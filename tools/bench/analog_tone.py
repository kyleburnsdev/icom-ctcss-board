"""RAW-derived analog tone characterization with explicit screening limits."""
import math


def analyze(raw, p, active, expected_hz, *, active_pp=(1,3), active_rms=(.3,1), mean_limits=(1.2,1.9), suppressed_pp=.15, suppressed_rms=.04):
    dt = p['xincrement']
    if len(raw) != p['points'] or len(raw) < 10000 or not 0 < dt <= 1e-6 or len(raw) * dt < .2:
        raise ValueError('Require complete >=0.2-second record at >=1 MS/s')
    if min(raw) == 0 or max(raw) == 255:
        raise ValueError('ADC-clipped analog record')
    # Average short bins to reduce switching noise without hiding tone shape.
    # At the selected 400 ns/sample this is a 12.8 us averaging window.
    step = 32
    samples = [sum(raw[i:i+step]) / step for i in range(0, len(raw)-step+1, step)]
    mean = sum(samples) / len(samples)
    ordered = sorted(samples)
    span_codes = ordered[99*len(samples)//100] - ordered[len(samples)//100]
    rms = math.sqrt(sum((v-mean)**2 for v in samples) / len(samples)) * p['yincrement']
    result = {'mean_v': (mean-p['yorigin']-p['yreference']) * p['yincrement'],
              'central_pp_v': span_codes * p['yincrement'], 'averaged_ac_rms_v': rms,
              'averaging_samples': step, 'averaging_window_s': step*dt,
              'points': len(raw), 'sample_interval_s': dt, 'duration_s': len(raw)*dt,
              'active_expected': active}
    if active:
        crossings = []
        armed = False
        for i in range(1, len(samples)):
            if samples[i] < mean - .15 * span_codes:
                armed = True
            if armed and samples[i-1] < mean <= samples[i]:
                crossings.append((i-1+(mean-samples[i-1])/(samples[i]-samples[i-1])) * step * dt)
                armed = False
        if len(crossings) < 20:
            raise ValueError('Insufficient resolved tone crossings')
        n = len(crossings)
        xmean = (n-1)/2
        tmean = sum(crossings)/n
        slope = sum((i-xmean)*(t-tmean) for i,t in enumerate(crossings)) / sum((i-xmean)**2 for i in range(n))
        frequency = 1/slope
        result.update(tone_hz=frequency, tone_crossings=n, expected_tone_hz=expected_hz)
        result['checks'] = {'tone_within_0_2_hz_nominal_timebase': abs(frequency-expected_hz) <= .2,
                            'central_pp_in_selected_range': active_pp[0] <= result['central_pp_v'] <= active_pp[1],
                            'rms_in_selected_range': active_rms[0] <= rms <= active_rms[1]}
    else:
        result['checks'] = {'suppressed_central_pp_below_selected_limit': result['central_pp_v'] <= suppressed_pp,
                            'suppressed_averaged_rms_below_selected_limit': rms <= suppressed_rms}
    result['checks']['dc_in_selected_range'] = mean_limits[0] <= result['mean_v'] <= mean_limits[1]
    result['limits'] = dict(active_pp_v=active_pp, active_rms_v=active_rms, mean_v=mean_limits, suppressed_pp_v=suppressed_pp, suppressed_rms_v=suppressed_rms)
    result['passed'] = all(result['checks'].values())
    return result

