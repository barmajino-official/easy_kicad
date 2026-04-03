# Easy-KiCad - High-Performance KiCad Library Mirroring Tool

Easy-KiCad is a powerful tool designed to mirror electronic components from the LCSC/EasyEDA catalog directly into native KiCad 8.0+ libraries.

## 🚀 Quick Start

To mirror components based on a search term:

```bash
python3 -m easy-kicad --match="esp32" --full
```

### Command Flags

- `--match="TERM"`: Fuzzy search for components in the database (e.g., "transistor", "capacitor").
- `--lcsc_id="CXXXX"`: Mirror a specific LCSC part number.
- `--full`: Download the **Symbol**, **Footprint**, and **3D Model** (recommended).
- `--symbol`: Download only the symbol.
- `--footprint`: Download only the footprint.
- `--3d`: Download only the 3D model.
- `--overwrite`: Overwrite existing files even if they are already mirrored.
- `--debug`: Enable detailed logging for troubleshooting.

## 📂 Output Structure

All mirrored components are stored in the `outputFile/` directory, organized by category:

- `outputFile/RES - Resistors.kicad_sym`: Categorized symbol libraries.
- `outputFile/RES - Resistors.pretty/`: Categorized footprint folders.
- `outputFile/RES - Resistors.3dshapes/`: Categorized 3D models (WRL/STEP).
- `outputFile/sym-lib-table`: Master symbol library table for KiCad.
- `outputFile/fp-lib-table`: Master footprint library table for KiCad.

## ⚙️ Configuration & Database

The tool uses a local SQLite database (`database/easykicadprovition.db`) to track mirrored components and prevent redundant downloads.

### Smart Categorization
The tool automatically sorts components into logical libraries based on their metadata and description. For example, any component with "Resistor" in its description will be grouped into the `RES - Resistors` library.

## 🛠️ Stability Features

- **Crash Resistance**: The tool safely handles missing or incomplete CAD data from EasyEDA, skipping problematic parts instead of interrupting the bulk process.
- **Incremental Sync**: It tracks the `is_mirrored` state in the database but also verifies the physical file existence on disk before skipping any part.
- **Unified Output**: All components are grouped into a single, portable `outputFile` folder.

## 🔌 Integration with KiCad

To use the mirrored library in KiCad:
1. Open Easy-KiCad.
2. Go to **Preferences** -> **Manage Symbol Libraries**.
3. Add a new library using the `outputFile/sym-lib-table`.
4. Go to **Preferences** -> **Manage Footprint Libraries**.
5. Add a new library using the `outputFile/fp-lib-table`.

*Note: In KiCad, follow step 2-5 to register the libraries.*

*Note: This tool was previously known as barmajinokad.*
