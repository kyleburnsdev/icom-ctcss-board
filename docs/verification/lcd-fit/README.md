# LCD interface L1 — current digital checks, physical retest pending

The [original coupon failed](failed-coupon-2026-11-17.json). L1 fixes the ear-radius
interpretation, window datum and support depth using the user's **9.13 mm** front
projection. It uses **9.43 mm seats** with a selected 0.30 mm bezel gap.

- [Shared drawing-coordinate review](xy-review.json): independent front/rear coordinates, row pitch, window origin and unused-ear clearance.
- [Native checks](native-checks.json): actual saved sketch centers/depths, empty viewing-window volume, fully constrained sketches, unchanged non-LCD C1 parts and B2 thumb screw, C1 clip/PCB contact, B2 saved-source/STEP readback. C1 native/STEP readback is also in its [export report](../enclosure-c1/export-checks.json).
- [Screen-only project](quick-slicer-checks.json): one coupon, X1C/PLA/0.12 mm profile, source-mesh hash, saved layout and slice result.
- [Package/reopen checks](package-checks.json): all three projects loaded and re-sliced by Bambu Studio with empty warning strings, settings/count readback, local links and file identities.
- [Inventory preflight](inventory-preflight.json): existing record gaps remain separate from the current user PLA/M3 stock inputs; no stock was reserved or changed.

The [one-object L1 retest](../../../manufacturing/lcd-fit/README.md) reuses B2's
unchanged printed thumb screws. B2 and C1 also retain their own primary test
plates. The B2 retest establishes the shared LCD registration/viewing interface;
C1's M3/insert clamp fit remains a separate physical test using C1's own profile.

All current slice and native project-reopen warnings are empty. Actual layer
views were inspected for first skins, corrected supports/nubs, insert/thread
features and window edges. Digital geometry and successful slicing do not accept
the new coupon's physical fit. Record the next print result here before treating
L1 as an accepted interface.
