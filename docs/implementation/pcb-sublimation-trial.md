# Sublimation branch contract and process evidence

Prepared 2026-11-12. Operator entry point:
[fabrication guide](../pcb-fabrication-guide.md).

| ID | Requirement / acceptance |
| --- | --- |
| SUB-01 | Isolate experiment on `feature/sublimation-silkscreen`; integrate only after physical results |
| SUB-02 | Mechanic white UV solder-mask foundation |
| SUB-03 | Converted Epson E-15000 with Cosmos Ink sublimation ink, as supplied by user |
| SUB-04 | Positive, finished-face-readable artwork; no transfer reflection; printer automatically mirrors |
| SUB-05 | Preserve current circuit, hole geometry, jig XY and Y-parallel flip |
| SUB-06 | Top-only color artwork with pin labels/test-point guide; bottom remains unprinted; no invented electrical/tolerance claims |
| SUB-07 | Small independent coupon first: six colors, white knockout, fine lines, orientation, adhesion and heat-cycle acceptance |
| SUB-08 | Preserve copper zero/map through pad clearing; floor-referenced drilling before first flip; top coating/transfer; conditional hole cleanup |
| SUB-09 | Inspect printed top and unprinted bottom after one transfer cycle; verify registration and solderability before assembly |

## Equipment and inventory

Printer/ink and mask brand above are established user inputs. The exact Mechanic
mask product code, Cosmos ink version, paper and driver/color profile are not
yet recorded. The selected experimental recipe is below; actual press results
remain unrecorded. Do not infer UVH900 or a different Epson model
from a search result. The user instructs us to assume a **generic 12 × 12-inch
clamshell T-shirt heat press**, with no make/model specifics. Use this assumption
for the trial without requiring model identification. Its nominal 304.8 × 304.8 mm
platen accommodates the 150 × 100 mm board in either artwork orientation; this
dimensional comparison does not establish pressure uniformity or a heat recipe.

The authoritative store resolved to
`C:/src/personal-repos/toolpath-studio-inventory` using machine harness settings;
`AGENT_INVENTORY_ROOT` was unset. Root/category manifests were read and searched
for heat press, sublimation, HTVRONT, EasyPress and likely model terms. No heat
press entry was found in the indexed records or a follow-up content search.
This is a missing record, not a claim the user lacks the press. The user-directed
generic press assumption resolves the trial's equipment format; an exact model
is not a prerequisite to coupon testing. No replacement inventory, inferred model
record or stock decrement was created.

The [read-only preflight](../verification/sublimation-inventory-preflight.json),
using [inherited milling inputs](../verification/sublimation-inventory-input.json),
does not pass: previous blank/tool/consumable IDs are absent, and the CNC record
does not provide the operational process/material/envelope fields required by
the helper. It is not a sublimation capability pass. No new material dimension,
tool, machine or physical recipe has been selected on the basis of this result.
Artwork generation is independent of those missing stock/heat-process records.

## Starting recipe and source basis

The operator should have an actionable first experiment rather than a list of
unselected parameters. For this board use **185 °C / 365 °F, 60 seconds, light
pressure, warm paper removal around 40–50 °C**. This is an agent-selected coupon
starting point for cured Mechanic white mask on 1.5 mm single-sided FR4, with the
top transfer facing the heated platen and a firm silicone lower support pad.
It is not a manufacturer qualification of this mask, and no exact Mechanic
variant is assumed from its brand name.

The initial comparison ladder changes temperature to **195 °C / 383 °F for 60 s**,
then dwell to **90 s**, with an optional final **200 °C / 392 °F for 90 s** only
while coatings remain sound. Start with a separate heat-only 185 °C / 60 s witness
to expose coating sticking/softening before a printed trial. A lower 175–180 °C
witness is a comparison if that fails, not proof of sufficient dye activation.
Use fresh coupons, not accumulated passes. Stop after acceptance; uniform faint
printing, poor local contact and coating damage call for different responses.

Source basis, checked 2026-11-12:

| Source | Supported process information | Application to this trial |
| --- | --- | --- |
| [Unisub message-board instructions](https://www.unisub.com/knowledge-hub/step-by-step-instructions/how-to-sublimate-message-boards/) | Approximately 195 °C hard-substrate processing; secure transfer with heat tape; protective paper | Reference for rigid-substrate handling; not a PCB-mask temperature rating |
| [JPPlus process settings](https://ast.jpplus.com/support/solutions/articles/65000165510-sublimation-settings-time-temperature-pressure) | Coated metals and FR plastics commonly use roughly 190–205 °C and about 60–75 s, with pressure depending on coating | Supports a bounded thermal test range; FR plastic sublimation blanks are not automatically equivalent to this FR4/mask stack |
| [Sawgrass quick-reference settings](https://www.sawgrassink.com/wp-content/uploads/2023/07/Sublimation-HeatPress-Settings.pdf) | Examples around 204 °C / 60 s / medium pressure with blowout paper; settings are starting points | The board starts below those examples and at lighter pressure to examine mask behavior |
| [Transfer Press operating guidance](https://www.thetransferpress.co.uk/PBCPPlayer.asp?ID=2374266) | Paper/substrate moisture can produce defects; absorbent protective paper helps where PTFE does not absorb moisture | Fresh unwaxed blowout paper is the disposable barrier; a thin PTFE cover is optional outside it |

The chosen light pressure, warm peel and lower initial temperature are engineering
trial choices. The mechanism to watch is a coating that accepts heat transiently
but softens or takes a paper/tape imprint under sustained clamping. Tolerance of
a short soldering event would not establish this longer press-cycle behavior.
Warm peel is the first compromise between prolonged paper contact and handling
hot/possibly softened mask; fresh-coupon cold/hot comparisons are provided in the
guide. No nominal psi is assigned to an uncalibrated clamshell knob.

Use the existing smooth firm silicone lower pad if suitable. A separate 2–3 mm
heat-press silicone sheet rated at least 210 °C is a selected accessory candidate
only if needed; tape, PTFE cover and blowout-paper stock are not recorded in the
inventory. The preparation checklist does not reserve stock, authorize a purchase
or claim inventory preflight success. Do not substitute an unknown foam, textile
pillow or general-purpose rubber for a temperature-rated support.

The [press-stack drawing](../images/pcb-sublimation-press-stack.svg) is schematic;
its plan uses the current 100 × 150 mm top outline and four jig-hole centers.
Neither a silicone support nor a PTFE cover is inserted between ink and mask.
Edge tape prevents movement/lift; a continuous airtight wrap is not required.
The guide and log carry these proposed settings separately from observed results.

## Digital checks versus physical acceptance

The artwork generator verifies the current PCB/project/library hashes against
the existing native export manifest, checks native export hashes, and checks
the read-only native text/pad metadata's PCB hash. The saved PCB is unchanged.
Konnect has no board-text bounding-box reader; KiCad's native read-only API
supplies that metadata. No source save, text patch or live-state substitution.

For the sublimation top derivative, native KiCad plotting changes the subtitle
in memory to **SELECTABLE CTCSS | 5V PRO MICRO**, omitting the manufacturing note
from the finished-board artwork. The original monochrome board/CAM remains
unchanged. The derivative Gerber and its text metadata are exported together and
hash-bound; no hand-cropped glyphs or substituted font. Regeneration preserves
this intentional artwork override.

Color is applied to native Gerber geometry inside native text bounds. Neutral
outlines remain. A boxed eight-row test-point guide replaces the decorative
waveform above U1. Native text is 0.8 mm high on a 1.45 mm row pitch. Its point/net
assignments are checked against the saved PCB during native export. The frame
is checked against existing legend strokes, registration exclusions, pads and
selected component-body envelopes; those envelopes' hash and minimum clearance
are included in the artwork evidence. TP1 is probe return, TP2 RAW input, TP3
regulated +5 V, TP4 raw PWM, TP5 filtered tone, TP6 microphone/tone mix, TP7
active-low PTT sense and TP8 radio keying output. No measured voltage or tone
amplitude is implied. Physical readability remains part of coupon acceptance.
All SVG geometry is positive; PDF converts SVG Y-down to PDF Y-up solely for
page display. This is not a transfer mirror.

Top portrait coordinates are `(Kx−50, Ky−50)`. The printer performs the sole
transfer reflection. Top J1 pin 1 is (40,130) in the page field.
The four registration holes retain the established board geometry and clearance.

The transfer artwork is **top only**. The native export and generator produce
no bottom print or preview. KiCad remains authoritative for circuit geometry.
The bottom retains protective mask and exposed pads, with no second transfer.

[Hash evidence](../verification/pcb-sublimation.json) records clipped native
legend area. Named color groups are editable SVG assets,
and regeneration is driven by maintained scripts. Repeated generation verifies
source identity; it does not establish dye uptake, heat resistance or registration.

[Print QA](../verification/pcb-sublimation-print-qa.json) checks all four output
hashes, SVG dimensions, two single-page Letter PDFs with scaling disabled,
the top J1 coordinate, four registration holes and local documentation links.
The final PDF sheets, top preview and updated jig illustration were visually
inspected. These are digital checks only.

No sublimation press run has been reported. The separate laser transparency
[test](../pcb-attempt-log.md#laser-transparency-transfer-test) demonstrates viable
heat transfer; its settings do not qualify sublimation. Before accepting this
sibling method, complete the coupon/board log with actual settings, coating
adhesion, readability, pad solderability, hole inspection and electrical checks.
Follow the [fabrication guide](../pcb-fabrication-guide.md) for pre-flip drilling
and conditional cleanup. Digital checks do not establish physical acceptance.
