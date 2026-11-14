# Deferred SCL fault campaign

**Physical electrical qualification and faulted PTT timing: not run; deferred
because the user cannot fit the proposed wiring change on the breadboard.**
Do not treat this as a DUT failure or substitute offline checks for physical
fault acceptance. No clamp stimulus is authorized on uncertain wiring. Confirm
the original encoder-A endpoint and board power state before further UI drive.

The following describes the prepared procedure, not a completed setup:
The fixture was STOPped and read back armed=0, drive=0 before requesting the
wiring change. The user is to reconnect only NUCLEO CN1 after moving the
existing encoder-A drive endpoint D4→D3/SCL and placing the DCV meter across
SCL/GND. Keep Arduino USB unplugged until the fixture is checked again.

Use the [illustrated procedure](../../../../../implementation/display-bus-fault-test.md).
The meter helper is an unchanged project copy of the tested inventory helper;
no inventory data was changed. New qualifier/evaluator preparation has seven
offline tests, all passing: [log](offline-tests.txt). These mock both serial
devices and the meter; they do not establish an electrical LOW or real fault
recovery. Cases include valid qualification, ineffective clamp, incorrect lead
level, failure to detect a display fault, failed recovery, relative mode and
unexpected saved-setting change. Fixture release is checked in every case.

No firmware change, upload, display fault stimulus or PSU command has been
performed for this stage. The previous display-enabled PTT/bypass and UI
results remain tied to their archived tool snapshots and verified Grove HEX.
