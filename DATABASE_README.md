# easy_kicad Database Overview

## File Information
- **Location**: `/home/barmajino/.platformio/penv/lib/python3.12/site-packages/easy_kicad/database/easykicadprovition.db`
- **Size**: ~1.3 GB
- **Type**: SQLite 3

---

## Purpose
This database serves as the high-performance local mirror of the **LCSC Component Catalog** (approximately 1.1 million parts). It acts as both a metadata cache for component searching and a state tracker for the **"War-Engine"** mirroring process.

---

## Schema Architecture

### 1. `categories`
Top-level grouping of components.
- **Columns**: `id`, `name`
- **Example**: `1|Connectors`, `3|Transistors`

### 2. `subcategories`
Granular grouping linked to top-level categories.
- **Columns**: `id`, `name`, `category_id`, `expected_count`
- **Example**: `2|Wire To Board / Wire To Wire Connector|1|17570`

### 3. `components`
The primary data table containing part details and synchronization state.
- **Key Columns**:
    - `lcsc_id`: The LCSC Part Number (e.g., `C123456`).
    - `mfr_part_no`: Manufacturer's part number.
    - `manufacturer`, `package`, `description`.
    - `is_indexed`: Boolean flag indicating if basic metadata is processed.
    - `is_downloaded`: Boolean flag indicating if KiCad assets (sym/footprint) are local.
    - `raw_metadata`: JSON string containing the full response from the EasyEDA API.
    - `symbol_path`, `footprint_path`, `model_3d_path`: Local filesystem paths to generated KiCad assets.

---

## System Statistics
- **Total Components**: 1,143,366
- **Subcategories**: 491
- **Top-level Categories**: 38

---

## Tool Integration
The `easy_kicad` engine uses this database to:
1. **Accelerate Lookups**: Instead of hitting the EasyEDA API for every query, the tool first checks this local mirror.
2. **Track Mirroring Progress**: The `is_downloaded` and `error_log` fields are used by the "War-Engine" (async worker engine) to identify which parts need to be processed or re-certified.
3. **Query Interface**: Supports complex search across the 1.1M parts using the `description` and `manufacturer` indices.

---

## Usage Example (SQL)
To find the count of downloaded components in the "MOSFETs" subcategory:
```sql
SELECT count(*) 
FROM components 
WHERE subcategory_id IN (SELECT id FROM subcategories WHERE name LIKE '%MOSFET%') 
AND is_downloaded = 1;
```
