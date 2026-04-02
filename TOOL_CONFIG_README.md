# barmajinokad: Tool Settings & Configuration Reference

This document centralizes the static configurations, API constants, and design parameters used by the `barmajinokad` / `easyeda2kicad` conversion engine.

---

## 1. API & Network Constants
These endpoints are used to retrieve the raw component data from EasyEDA servers.

| Constant | Value / Template | Reference |
| :--- | :--- | :--- |
| `API_ENDPOINT` | `https://easyeda.com/api/products/{lcsc_id}/components?version=6.4.19.5` | [easyeda_api.py:8](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/easyeda/easyeda_api.py#L8) |
| `ENDPOINT_3D_MODEL` | `https://modules.easyeda.com/3dmodel/{uuid}` | [easyeda_api.py:9](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/easyeda/easyeda_api.py#L9) |
| `ENDPOINT_3D_MODEL_STEP` | `https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{uuid}` | [easyeda_api.py:10](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/easyeda/easyeda_api.py#L10) |
| `User-Agent` | `easyeda2kicad v{version}` | [easyeda_api.py:22](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/easyeda/easyeda_api.py#L22) |

---

## 2. KiCad Symbol Export Parameters (Static)

### KiCad V5 (Legacy) - Dimensions in **mil**
| Parameter | Value | Reference |
| :--- | :--- | :--- |
| `PIN_LENGTH` | 100 | [parameters_kicad_symbol.py:52](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L52) |
| `PIN_NUM_SIZE` | 50 | [parameters_kicad_symbol.py:54](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L54) |
| `PIN_NAME_SIZE` | 50 | [parameters_kicad_symbol.py:55](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L55) |
| `FIELD_FONT_SIZE` | 60 | [parameters_kicad_symbol.py:58](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L58) |
| `FIELD_OFFSET_START` | 200 | [parameters_kicad_symbol.py:59](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L59) |

### KiCad V6+ (Modern) - Dimensions in **mm**
| Parameter | Value | Reference |
| :--- | :--- | :--- |
| `PIN_LENGTH` | 2.54 | [parameters_kicad_symbol.py:123](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L123) |
| `PIN_NUM_SIZE` | 1.27 | [parameters_kicad_symbol.py:125](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L125) |
| `PIN_NAME_SIZE` | 1.27 | [parameters_kicad_symbol.py:126](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L126) |
| `PROPERTY_FONT_SIZE`| 1.27 | [parameters_kicad_symbol.py:128](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L128) |
| `FIELD_OFFSET_START`| 5.08 | [parameters_kicad_symbol.py:129](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_symbol.py#L129) |

---

## 3. KiCad Footprint Export Parameters

### Default Text Styles
| Context | Layer | Font Size | Thickness | Reference |
| :--- | :--- | :--- | :--- | :--- |
| `Reference` | `F.SilkS` | 1x1 mm | 0.15 mm | [parameters_kicad_footprint.py:19](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_footprint.py#L19) |
| `Value (Package)` | `F.Fab` | 1x1 mm | 0.15 mm | [parameters_kicad_footprint.py:23](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_footprint.py#L23) |
| `User Ref (%R)` | `F.Fab` | 1x1 mm | 0.15 mm | [parameters_kicad_footprint.py:26](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_footprint.py#L26) |

### Layer Mapping Table (EasyEDA ID -> KiCad Name)
| EasyEDA ID | KiCad Layer |
| :--- | :--- |
| 1 | `F.Cu` (Front Copper) |
| 2 | `B.Cu` (Bottom Copper) |
| 3 | `F.SilkS` (Front Silkscreen) |
| 10 | `Edge.Cuts` (Board Boundary) |
| 13 | `F.Fab` (Fabrication Layer) |
| 101 | `F.Fab` |

*Reference: [parameters_kicad_footprint.py:93-109](file:///home/barmajino/.platformio/penv/lib/python3.12/site-packages/barmajinokad/kicad/parameters_kicad_footprint.py#L93)*

---

## 4. Default File System Paths
If not specified via `--output` flag, the tools use the following defaults:

- **Root Library Folder**: `~/Documents/Kicad/easyeda2kicad/`
- **Footprint Library**: `easyeda2kicad.pretty`
- **3D Shapes Folder**: `easyeda2kicad.3dshapes`
- **Symbol Library**: `easyeda2kicad.kicad_sym` (V6) or `easyeda2kicad.lib` (V5)

---

## 5. Metadata Mapping
| KiCad Field | Data Source |
| :--- | :--- |
| `Manufacturer` | `BOM_Manufacturer` |
| `LCSC Part` | `lcsc.number` |
| `JLC Part` | `BOM_JLCPCB Part Class` |
| `Datasheet` | `lcsc.url` |
