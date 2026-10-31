* Current KiCad-exported tone network; see README.md for mapping and limits.
* RV1 split resistances approximate ideal travel; 1mOhm prevents zero R.
R1 pwm filter1 {R1val}
R2 filter1 filter2 {R2val}
R3 filter2 divider {R3val}
R4 divider 0 {R4val}
R5 coupled audio {R5val}
C1 filter1 0 {C1val}
C2 filter2 0 {C2val}
C3 wiper coupled {C3val}
RV1upper divider wiper {max(1m, POT*(1-W))}
RV1lower wiper 0 {max(1m, POT*W)}
