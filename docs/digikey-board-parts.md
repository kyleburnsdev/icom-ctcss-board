# DigiKey parts for one populated board

Upload [digikey-board-parts.csv](../manufacturing/pcb/digikey-board-parts.csv)
to DigiKey's **Upload a List / My Lists**. It has **17 purchase lines and 39
individual parts**, with exact quantities for one board and no spares.

If prompted to map columns, use:

| CSV column | DigiKey field |
| --- | --- |
| DigiKey Part Number | DigiKey Part Number / Part Number |
| Quantity | Quantity |
| Customer Reference | Customer Reference |
| Manufacturer Part Number | Manufacturer Part Number, if offered |
| Manufacturer | Manufacturer, if offered |
| Description | Description / Notes, or ignore |

The first row is a header; part data begins on row 2. Customer references
identify the placement locations. Inspect the matched part numbers and
quantities before transferring the list to a cart. The CSV has been read back
and reconciled locally; it has not been uploaded to DigiKey.

## Included and separately required

The upload covers all **37 DigiKey-sourced schematic components** plus two
**Wurth 61301211821** female strips for U1. Each strip has 12 contacts on
2.54 mm pitch, a 2.5 +/- 0.2 mm wide body, an 8.5 +/- 0.15 mm insulator
height and 3.1 +/- 0.3 mm solder posts. Its body fits the assembly note's
3 mm width allowance. The manufacturer recommends nominal 1.02 mm PCB holes;
the board uses 1.1 mm holes. Assemble the two rows 15.24 mm apart, following
the [assembly procedure](implementation/assembly-and-bring-up.md).
See the [manufacturer drawing](https://www.we-online.com/components/products/datasheet/61301211821.pdf).

**U1 itself is not in the DigiKey upload.** The design specifies one Teyleten
Robot USB-C Pro Micro, 5 V / 16 MHz, sourced separately as
[Amazon B0B6HYLC44](https://www.amazon.com/dp/B0B6HYLC44).
Use that module with its two 12-pin male headers fitted; if the supplied module
has loose headers, solder those to the module before final insertion.
No alternate module or voltage version has been substituted.

Off-board LCD, encoder, LEDs, bypass switch, cable mates/wiring, enclosure
hardware, PCB stock and soldering consumables are outside this board-population
upload. Those are covered by their project assembly/enclosure requirements.

## Supplier correction

The existing schematic and reference BOM associate J3 MPN **61300511121**
with supplier SKU **732-5319-ND**. DigiKey's product listing identifies this
five-pin header as **732-5318-ND**. The upload uses the corrected supplier SKU;
the MPN, quantity, pitch and footprint are unchanged. This purchasing file
does not change schematic metadata or the historical reference BOM.

## Availability and source checks

Checked **2026-11-01** against DigiKey US listings. Each listed item showed
stock sufficient for one board and a unit/cut-tape purchase option. Counts
below are the displayed web listing snapshot, not a reservation or a cart
quote; DigiKey recalculates stock and price on upload.

| References | MPN / DigiKey listing | Required | Displayed stock |
| --- | --- | ---: | ---: |
| C1, C2, C4, C5 | [K104K15X7RF5TL2](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/K104K15X7RF5TL2/286538) | 4 | 299,870 |
| C3 | [R82DC4100AA60J](https://www.digikey.com/en/products/detail/kemet/R82DC4100AA60J/2571295) | 1 | 41 |
| C6 | [B32522C0475J000](https://www.digikey.com/en/products/detail/tdk-electronics-inc/B32522C0475J000/592709) | 1 | 6,039 |
| J1, J2 | [61300811121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300811121/4846839) | 2 | 38,362 |
| J3 | [61300511121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300511121/4846831) | 1 | 45,752 |
| J4, J6 | [61300411121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300411121/4846827) | 2 | 124,829 |
| J5 | [61300211121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300211121/4846823) | 1 | 406,800 |
| Q1 | [2N3904TAR](https://www.digikey.com/en/products/detail/onsemi/2N3904TAR/975250) | 1 | 295 |
| R1, R2 | [MRS16000C3301FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C3301FCT00/7351364) | 2 | 4,246 |
| R3, R9, R12-R15 | [MRS16000C1002FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1002FCT00/5063734) | 6 | 3,892 |
| R4, R8 | [MRS16000C1001FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1001FCT00/5063732) | 2 | 12,363 |
| R5, R11 | [MRS16000C1003FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C1003FCT00/7351351) | 2 | 4,749 |
| R6, R7 | [MRS16000C3300FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C3300FCT00/7351363) | 2 | 3,861 |
| R10 | [MRS16000C4701FCT00](https://www.digikey.com/en/products/detail/vishay-beyschlag-draloric-bc-components/MRS16000C4701FCT00/5063896) | 1 | 5,024 |
| RV1 | [3296W-1-103LF](https://www.digikey.com/en/products/detail/bourns-inc/3296W-1-103LF/1088045) | 1 | 30,067 |
| TP1-TP8 | [61300111121](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300111121/4846821) | 8 | 75,889 |
| U1 socket strips | [61301211821](https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61301211821/16608531) | 2 | 6,879 |

The current saved schematic was queried and its BOM exported through Konnect.
All 38 references, values, footprints, MPNs and supplier SKUs matched the
[reference BOM](reference/bom.csv) before the documented J3 purchasing
correction. Every DigiKey reference is covered exactly once in the grouped
upload. Sources were unchanged during generation:

- Schematic SHA256: `2b4d0f6b251cbe1a2bee54bc0166810619f8169cb23300a76d3e1122eb8bed77`.
- Reference BOM SHA256: `483ea872b81afee9f2dd951e9d5884d01e1a458523da26302d26f9f1a46ffa7d`.

[DigiKey's My Lists guidance](https://www.digikey.com/en/help-support/place-an-order/build-a-bom)
describes its BOM/list workflow.
