# easy_kicad Analysis Report

## Overview

This report documents an analysis of the easy_kicad tool, focusing on font size control, component organization, and metadata support in KiCad libraries.

## Questions and Findings

### 1. Font Size Control

**Question**: Can we control font size and pin font size in the tool?

**Answer**: Currently NO - font sizes are hardcoded in the configuration.

**Code References**:

- **File**: `kicad/parameters_kicad_symbol.py`
- **Lines**: 51-62 (KiExportConfigV5 class)
  ```python
  PIN_NUM_SIZE = 50
  PIN_NAME_SIZE = 50
  FIELD_FONT_SIZE = 60
  ```
- **Lines**: 122-133 (KiExportConfigV6 class)
  ```python
  PIN_NUM_SIZE = 1.27
  PIN_NAME_SIZE = 1.27
  PROPERTY_FONT_SIZE = 1.27
  ```

**Functions**: Font sizes are used in `KiSymbolInfo.export_v5()` and `export_v6()` methods.

### 2. Component Organization/Categorization

**Question**: Why aren't components organized by category (MOSFET, transistor NPN/PNP, connector green, etc.)?

**Answer**: The tool doesn't implement categorization logic - components are appended sequentially to library files.

**Code References**:

- **File**: `helpers.py`
- **Function**: `add_component_in_symbol_lib_file()` (lines 95-118)

  ```python
  # For v5: just appends to the end
  with open(file=lib_path, mode="a+", encoding="utf-8") as lib_file:
      lib_file.write(component_content)

  # For v6: inserts before closing )
  with open(file=lib_path, mode="rb+") as lib_file:
      lib_file.seek(-2, 2)
      lib_file.truncate()
      lib_file.write(component_content.encode(encoding="utf-8"))
      lib_file.write("\n)".encode(encoding="utf-8"))
  ```

**Issue**: No sorting or categorization logic implemented.

### 3. Metadata Support (Keywords, Description, Category)

**Question**: Does KiCad support keywords, description, category for search matching?

**Answer**: YES, KiCad supports these features, but easy_kicad doesn't extract them from the API.

**API Data Available** (from testing):

```json
{
  "description": "Component description",
  "tags": ["keyword1", "keyword2"],
  "dataStr": {
    "head": {
      "c_para": {
        "JLCPCB Part Class": "MOSFET"
      }
    }
  }
}
```

**Current Extraction** (`easyeda/easyeda_importer.py`, lines 115-128):

```python
info=EeSymbolInfo(
    name=ee_data_info["name"],
    prefix=ee_data_info["pre"],
    package=ee_data_info.get("package", None),
    manufacturer=ee_data_info.get("BOM_Manufacturer", None),
    datasheet=ee_data["lcsc"].get("url", None),
    lcsc_id=ee_data["lcsc"].get("number", None),
    jlc_id=ee_data_info.get("BOM_JLCPCB Part Class", None),
)
```

**Missing Fields**: `description`, `tags` are not extracted.

**KiCad Symbol Export** (`kicad/parameters_kicad_symbol.py`):

- **V5**: Uses F0-F7 fields (lines 145-210)
- **V6**: Uses properties with IDs 0-6 (lines 214-320)
- **Limitation**: No keywords, description, or category properties added

## Testing Command Executed

**Command**:

```bash
cd . && python -c "
import json
from easy_kicad.easyeda.easyeda_api import EasyedaApi

api = EasyedaApi()
try:
    result = api.get_cad_data_of_component('C123456')
    if result:
        print('API Response keys:', list(result.keys()))
        if 'dataStr' in result and 'head' in result['dataStr'] and 'c_para' in result['dataStr']['head']:
            print('c_para keys:', list(result['dataStr']['head']['c_para'].keys()))
        if 'lcsc' in result:
            print('lcsc keys:', list(result['lcsc'].keys()))
    else:
        print('No data returned')
except Exception as e:
    print('Error:', e)
"
```

**Output**:

```
API Response keys: ['uuid', 'title', 'description', 'docType', 'type', 'thumb', 'lcsc', 'szlcsc', 'owner', 'tags', 'updateTime', 'updated_at', 'dataStr', 'verify', 'SMT', 'datastrid', 'jlcOnSale', 'writable', 'isFavorite', 'packageDetail']
c_para keys: ['pre', 'name', 'package', 'nameAlias', 'Contributor', 'Supplier', 'Supplier Part', 'Manufacturer', 'Manufacturer Part', 'Value', 'JLCPCB Part Class']
lcsc keys: ['id', 'number', 'step', 'min', 'price', 'stock', 'url']
```

## Key Issues Identified

1. **Font sizes are hardcoded** - no customization options
2. **No component categorization** - sequential addition only
3. **Missing metadata extraction** - keywords, description, category not utilized
4. **Limited KiCad integration** - not taking advantage of KiCad's search/filtering capabilities

## Recommendations

1. **Add font size command-line options** (`--pin-font-size`, `--field-font-size`)
2. **Implement categorization logic** with `--category` option
3. **Extract and export metadata fields**:
   - Description → KiCad "Description" property
   - Tags → KiCad "Keywords" property
   - JLCPCB Part Class → KiCad "Category" property
4. **Add search optimization** for better component discovery

## Files Analyzed

- `__main__.py` - Main entry point and CLI
- `easyeda/easyeda_api.py` - API communication
- `easyeda/easyeda_importer.py` - Data extraction logic
- `easyeda/parameters_easyeda.py` - Data structures
- `kicad/parameters_kicad_symbol.py` - KiCad symbol export
- `kicad/parameters_kicad_footprint.py` - KiCad footprint export
- `helpers.py` - Library file management

## Conclusion

The easy_kicad tool provides basic conversion functionality but misses opportunities for better KiCad integration through metadata support and organization features. The underlying KiCad format supports rich metadata, but the tool doesn't leverage it.
