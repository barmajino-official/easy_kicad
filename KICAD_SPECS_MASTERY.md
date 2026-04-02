# KiCad Specifications & Grammar Mastery

This document is a technical synthesis of the official KiCad documentation found in the `refers/` directory. It explains the "Blueprints" that the `barmajinokad` tool must follow to ensure 100% compatibility with KiCad 6.0 and 7.0.

---

## 1. The "Source of Truth" Directory (`refers/`)

The `refers/` folder contains seven core technical documents which act as the absolute grammar for all KiCad files.

| File | Specs Category | Implementation in `barmajinokad` |
| :--- | :--- | :--- |
| **`1.txt`** | **Master S-Expression Grammar** | Defines `at`, `pts`, `stroke`, and `effects` templates. |
| **`2.txt`** | **Footprint Library Spec** | Logic for `.kicad_mod` files and `.pretty` folder creation. |
| **`3.txt`** | **Board File (v6+) Spec** | Reference for stackup, tracks, vias, and net definitions. |
| **`4.txt`** | **Symbol Library Spec** | Dictates the `(kicad_symbol_lib)` header and property ordinals. |
| **`5.txt`** | **Schematic Spec** | Reference for `.kicad_sch`, labels, and hierarchical pins. |
| **`6.txt`** | **Worksheet Spec** | Specs for `.kicad_wks` custom title blocks and borders. |
| **`7.txt`** | **Legacy Engine (Pre-4.0)** | **Critical for `v5` export**: Handles 1/10000th-inch coordinate conversion. |

---

## 2. Core Grammar Rules (Derived from `1.txt`)

Every conversion performed by this tool adheres to these fundamental S-expression rules:

*   **Case Sensitivity**: All keywords (tokens) must be **lowercase**.
*   **S-Expression Balance**: All opening `(` must have a closing `)`. 
    *   *Note*: The tool uses a binary "poke" method (`seek(-2, 2)`) to inject symbols into these balanced structures.
*   **Coordinate Units**: KiCad 6+ uses **Millimeters (mm)** with a 6-decimal precision (nanometers). 
    *   *Warning*: Never output `mils` or `inches` without explicit conversion.
*   **Canonical Layering**: Layers like `1` must be named `F.Cu` (Front Copper) and `15` as `B.Cu` (Back Copper) to be recognized globally.

---

## 3. The "Why" and "How" of Component Properties

Based on `4.txt`, the tool enforces a strict property hierarchy (ID mapping) for every symbol:

| ID Ordinal | Mandatory Key | Typical Value |
| :--- | :--- | :--- |
| **0** | **Reference** | `U1`, `R?`, `J?` |
| **1** | **Value** | `NE555`, `10k`, `0.1uF` |
| **2** | **Footprint** | `LibraryName:FootprintName` |
| **3** | **Datasheet** | URL to PDF or LCSC detail page |
| **4+** | **Custom** | `LCSC Part #`, `Manufacturer`, `Price` |

---

## 4. Legacy Support Engine (`7.txt` Strategy)

The `v5` export mode is powered by the logic in `7.txt`. It enables support for older versions of KiCad and other software by switching from S-expressions to an ASCII-based "Block" format.

*   **Coordinate Scale**: 1 internal unit = 0.0001 inch.
*   **Header Syntax**: Starts with `EESchema-LIBRARY Version 2.4`.
*   **Block Markers**: Uses `$MODULE` and `$PAD` instead of `(footprint)` and `(pad)`.

---

## 5. Usage for Developers

When modifying the exporters (`kicad/export_*.py`), use this directory to:
1.  **Check Token Order**: Does `hide` go before or after `at`? (Check `1.txt`)
2.  **Verify New Features**: If adding a custom property (like `3D Rotation`), check the correct axis order `(rotate (xyz X Y Z))` in `3.txt`.
3.  **Validate Coordinate Math**: Ensure all center-to-edge calculations match the "center-point + radius" logic in the specs.

---

*This guide ensures that the 1.1 million parts mirrored by this tool are "factory-perfect" for KiCad.*
