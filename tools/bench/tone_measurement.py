"""Decode sine frequency from a retained raw PWM record, independently of DDS code."""
import math


def evaluate_tone(raw, p, expected_hz):
    dt = p['xincrement']
    if not math.isfinite(expected_hz) or not 67 <= expected_hz <= 254.1:
        raise ValueError('Expected tone outside accepted range')
    if len(raw) != p['points'] or not 0 < dt <= 1e-6 or len(raw)*dt < 3:
        raise ValueError('Require complete >=3 second record at >=1 MS/s')
    codes = sorted(raw)
    low, high = codes[len(raw)//10], codes[9*len(raw)//10]
    if high-low < 20:
        raise ValueError('No adequately resolved two-level waveform')
    threshold = (low+high)/2
    last_rise = fall = None
    previous = None
    periods, duties, crossings = [], [], []
    armed = False
    for index in range(1, len(raw)):
        if raw[index] < threshold <= raw[index-1]:
            if fall is not None:
                raise ValueError('Extra falling edge')
            fall = index
        elif raw[index-1] < threshold <= raw[index]:
            if last_rise is not None:
                if fall is None or not last_rise < fall < index:
                    raise ValueError('Incomplete carrier cycle')
                period = (index-last_rise)*dt
                duty = (fall-last_rise)/(index-last_rise)
                periods.append(period)
                duties.append(duty)
                if duty < .45:
                    armed = True
                if armed and previous is not None and previous[1] < .5 <= duty:
                    fraction = (.5-previous[1])/(duty-previous[1])
                    crossings.append((previous[0]+fraction*(last_rise-previous[0]))*dt)
                    armed = False
                previous = (last_rise, duty)
            last_rise, fall = index, None
    if len(crossings) < 100:
        raise ValueError('Insufficient tone cycles')
    frequency = (len(crossings)-1)/(crossings[-1]-crossings[0])
    carrier = len(periods)/sum(periods)
    checks = {
        'encoded_tone_within_0_1_hz_nominal_scope_timebase': abs(frequency-expected_hz) <= .1,
        'carrier_within_selected_1_percent': abs(carrier-10000) <= 100,
        'every_period_98_to_102_us': min(periods) >= 98e-6 and max(periods) <= 102e-6,
        'modulation_reaches_both_extremes': min(duties) <= .15 and max(duties) >= .85,
        'duty_within_selected_11_to_89_percent': min(duties) >= .11 and max(duties) <= .89,
        'not_adc_clipped': min(raw) > 0 and max(raw) < 255,
    }
    return dict(passed=all(checks.values()), checks=checks,
                expected_tone_hz=expected_hz, encoded_tone_hz=frequency,
                error_hz=frequency-expected_hz, carrier_hz=carrier,
                complete_periods=len(periods), tone_crossings=len(crossings),
                duty_min_percent=100*min(duties), duty_max_percent=100*max(duties),
                period_min_us=1e6*min(periods), period_max_us=1e6*max(periods),
                duration_s=len(raw)*dt, sample_interval_s=dt,
                scope='Raw PWM encoding only; no analog audio/distortion measurement; absolute reference accuracy unqualified')
