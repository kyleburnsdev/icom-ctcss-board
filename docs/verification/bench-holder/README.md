# B1 bench-holder verification

Current checks refer to the source and manufacturing hashes in
[geometry.json](geometry.json), [slicer.json](slicer.json) and
[layer-checks.json](layer-checks.json). Sources include the current uncommitted
work; no physical print, insert installation, board mounting or electrical test
is claimed.

- FreeCAD 1.1.1 recompute, valid single-solid bodies, native save/reopen and
  closed print meshes. PCB mounting pattern is unchanged. The board sits at
  Z15 above floor Z3: 12 mm nominal underside room / 10 mm with the existing
  2 mm lead-tail allowance. PCB screw paths have 6 mm of modeled M3 thread at
  Z9–15 and open 3.4 mm clearance bores below; no blind floor is introduced.
  Native SubtractiveHelix features retain the helical subtraction through recompute. Additional
  volume checks confirm unobstructed lower bores/through cores and actual thread
  material in the upper posts; the mount coupon is also checked after reopening.
- The control panel is 30° above horizontal and has eight 0.6 mm raised legends.
  Native assembly and printed layer paths are inspected for labels, hardware
  openings, thread/post continuity and clearances. The keeper pin/socket overlap
  is intentional 0.1 mm diametral interference; its approximately 1.84 mm³
  intersection is an intentional press fit awaiting coupon acceptance, not an unintended collision.
- The source assembly has zero base/panel and base/PCB reference intersection.
  Reference display and connector blocks are simplified envelopes, not an exact
  populated-board or plug model. Final fit acceptance is the installed check.
- Three plates / ten objects use one PLA slot. Native slicer readback verifies
  transforms, bed seating, 5 mm brim margins, X1C exclusions, saved process values,
  plate names, expected quantities, embedded G-code and the two intended
  Z8.8–15.2 height-range overrides. Default layers are 0.20 mm; only these
  thread bands use 0.12 mm. Three coarse / five fine skin layers preserve 0.6 mm.
  Each native slice has an empty warning string. Layer sheets are
  [fit tests](slice-1.png), [base](slice-2.png) and [controls](slice-3.png).

The first flat candidate exposed an existing Bambu preset-name problem: values
embedded under the standard preset name were replaced by standard values on GUI
open. The current package uses a unique process **name** as well as its ID.
Opening the resulting project in Bambu Studio is a separate acceptance check;
ZIP contents alone do not establish the GUI adopted its settings.
The optimized project was reopened in Bambu Studio with the three named plates,
Generic PLA, unique 0.20 mm process, 4 walls, 3 coarse skin layers and height ranges
on the base and mount coupon. Actual per-object outer-wall Z steps independently
verify 0.12 mm inside their thread bands and 0.20 mm elsewhere, including the
other coupons on the same plate. See [slicer evidence](slicer.json) and
[package identity](package.json).

During the thread-length optimization, a new bore-volume check caught a defect
in the previous generated feature: recompute restored the pre-cut shape, filling
the upper screw path despite a valid solid. That package is superseded. The
current native SubtractiveHelix features and explicit bore checks replace the earlier
validity-only evidence. No earlier physical thread acceptance was claimed.

## Inventory findings and disposition

The read-only [preflight](inventory-preflight.json) uses this
[input](inventory-input.json) and the shared workshop store. It is **not a passed
stock/capability preflight**: imported filament/button/machine records have null
quantities, the machine lacks process/material/usable-envelope metadata, and the
new insert count is unknown. The helper also emits `unavailable` when a quantity
is null, even for records explicitly marked `in_stock`; those findings are not
evidence that the owned item is absent.

The user supplied the governing current facts: PLA is available; use the owned
16 mm momentary switch, owned nylon screws from the Nucleo project and M3 × D5 ×
L4 inserts. The Nucleo project identifies the nylon thread as M3 × 0.5, with
unrecorded screw lengths. The nominal 256³ printer volume is an established
input; actual prepared plate/brim/exclusion bounds are checked independently.
Generic PLA is the selected slicer profile; the user did not specify PLA Matte
or a filament brand. The preflight's legacy PLA Matte record is a catalog
candidate, not a claim that this is the user's actual spool. No inventory
quantity is inferred, reserved or decremented.

M3 insert dimensions and practical notes were added to
`stock/m3-d5-l4-heat-set-inserts` in the shared store and read back with the
inventory helper. Brand, knurl profile, alloy and count remain unspecified.
Pilot diameter and heat installation are resolved by the printed 4.4/4.6/4.8 mm
coupon; the production default is 4.6 mm. Use the guide's stop/accept transitions.

## Physical record

| Check | Result |
| --- | --- |
| PLA / printer / selected process used | Not run |
| Nylon thread fit and actual screw length | Not run |
| Selected insert pilot / tip temperature / dwell / retention | Not run |
| Panel hardware bores, labels and display retention | Not run |
| PCB seats on four posts; no lead or screw bottoming | Not run |
| Rails, knobs and panel remain stable during operation | Not run |
| First-power rails, current, temperature and PTT tests | Not run |

Record results here after performing the
[fabrication and bench procedure](../../bench-holder-guide.md). Superseded flat
candidate evidence is not current-revision validation.
