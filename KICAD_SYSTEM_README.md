# KiCad Library Generation & Table Management

This document explains how the `easy_kicad` tools dynamically generate and maintain KiCad's library "tables" (internal symbol structures and footprint directories).

---

## 1. Symbol Library Engine (`.kicad_sym`)
For KiCad 6+, a symbol library is a single S-expression file that acts as a container "table" for all parts within that category.

### **A. Initialization of the Table**
When creating a library (e.g., `resistors.kicad_sym`), the tool initializes a valid KiCad header.
*   **File**: `__main__.py` (Lines 180-195)
*   **Logic**: If the file doesn't exist, it writes the `(kicad_symbol_lib)` root node with version `20211014`.

### **B. The "Injection" Strategy (V6+)**
Since S-expressions must be enclosed in parentheses, simple appending is not possible. The tool uses a specialized binary-level insertion method:
*   **Source**: `helpers.py` (Lines 101-105)
*   **Algorithm**:
    1.  Open the library file in binary `rb+` (Read/Write) mode.
    2.  `lib_file.seek(-2, 2)`: Jump to the final `\n)` sequence.
    3.  `lib_file.truncate()`: Erase the closing parenthesis.
    4.  `lib_file.write(symbol_content)`: Inject the new symbol data.
    5.  `lib_file.write("\n)")`: Re-seal the file.
*   **Benefit**: This is highly efficient and prevents the tool from having to load or re-parse millions of symbols just to add one more.

### **C. Component Conflict & Update**
If the part already exists (checked via `id_already_in_symbol_lib`), the tool switches from injection to a Regex-based replacement.
*   **Source**: `helpers.py` (Line 75)
*   **Pattern**: `(symbol "{component_name}".*?)`
*   **Process**: It reads the file, swaps the old symbol block for the new one using `re.sub`, and adds a custom generator tag for identification.

---

## 2. Footprint Library Strategy (`.pretty`)
Footprint libraries in KiCad are managed as **Plugin Directories**.

### **A. Directory Table Management**
Before any footprint is written, the tool ensures the structural "table" (the directory) is ready.
*   **Logic**: `__main__.py` (Line 170) checks for the existence of `{lib_name}.pretty`.
*   **Storage**: Each footprint is saved as an individual `{part_name}.kicad_mod` file within that folder. 

### **B. Path & ID Mapping**
The tool automatically handles the mapping of these footprints into the Symbol properties.
*   **Source**: `kicad/export_kicad_symbol.py`
*   **Reference**: It generates a hidden property with `id=2` (KiCad's default Footprint field) and points it to `{LibraryName}:{PartName}`.

---

## 3. Tool Reference Summary

| Operation | Logic Location | Implementation Detail |
| :--- | :--- | :--- |
| **Header Creation** | `__main__.py:180` | `(kicad_symbol_lib ...)` template |
| **Symbol Insertion**| `helpers.py:101` | Binary Byte-Seek & Truncate |
| **Symbol Update** | `helpers.py:75` | Python `re.sub` for component swap |
| **Footprint Sync** | `__main__.py:170` | `os.mkdir` for `.pretty` folder |
| **3D Asset Sync**  | `__main__.py:175` | `os.mkdir` for `.3dshapes` folder |

---

## 4. Key Takeaways for Maintenance
- **Do not manually edit the last line** of a library file while a download is running; the `truncate` method relies on the specific `\n)` termination.
- **Library Registration**: The files created here follow the standard KiCad library specifications, allowing them to be added to `sym-lib-table` or `fp-lib-table` using absolute or relative paths.
