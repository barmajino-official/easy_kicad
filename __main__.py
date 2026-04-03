# Global imports
import sys
import os
import argparse
import logging
import re
from textwrap import dedent
from typing import List
from enum import Enum

# 🛡️ Dynamic Path Injection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from helpers import __version__
except ImportError:
    from __init__ import __version__

from database.db_manager import DBManager
from easyeda.easyeda_api import EasyedaApi
from easyeda.easyeda_importer import (
    Easyeda3dModelImporter,
    EasyedaFootprintImporter,
    EasyedaSymbolImporter,
)
from easyeda.parameters_easyeda import EeSymbol
from helpers import (
    add_component_in_symbol_lib_file,
    get_local_config,
    id_already_in_symbol_lib,
    set_logger,
    update_component_in_symbol_lib_file,
    update_kicad_lib_tables,
)
from kicad.export_kicad_3d_model import Exporter3dModelKicad
from kicad.export_kicad_footprint import ExporterFootprintKicad
from kicad.export_kicad_symbol import ExporterSymbolKicad
from kicad.parameters_kicad_symbol import KicadVersion


def get_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "A Python script that convert any electronic components from LCSC or"
            " EasyEDA to a Easy-KiCad library"
        )
    )

    parser.add_argument("--lcsc_id", help="Specific LCSC id", required=False, type=str)
    parser.add_argument("--match", help="Fuzzy search for components in the DB (e.g., 'esp32')", required=False, type=str)

    parser.add_argument(
        "--symbol", help="Get symbol of this id", required=False, action="store_true"
    )

    parser.add_argument(
        "--footprint",
        help="Get footprint of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--3d",
        help="Get the 3d model of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--full",
        help="Get the symbol, footprint and 3d model of this id",
        required=False,
        action="store_true",
    )

    parser.add_argument(
        "--output",
        required=False,
        metavar="file.kicad_sym",
        help="Output file",
        type=str,
    )

    parser.add_argument(
        "--overwrite",
        required=False,
        help=(
            "overwrite symbol and footprint lib if there is already a component with"
            " this lcsc_id"
        ),
        action="store_true",
    )

    parser.add_argument(
        "--v5",
        required=False,
        help="Convert library in legacy format for KiCad 5.x",
        action="store_true",
    )

    parser.add_argument(
        "--project-relative",
        required=False,
        help="Sets the 3D file path stored relative to the project",
        action="store_true",
    )

    parser.add_argument(
        "--db",
        required=False,
        help="Path to the SQLite database",
        default="database/easy_kicad_catalog.db",
        type=str,
    )

    parser.add_argument(
        "--debug",
        help="set the logging level to debug",
        required=False,
        default=False,
        action="store_true",
    )

    return parser


def valid_arguments(arguments: dict) -> bool:
    if not arguments["lcsc_id"] and not arguments["match"]:
        logging.error("Either --lcsc_id or --match must be provided.")
        return False

    if arguments["lcsc_id"] and not arguments["lcsc_id"].startswith("C"):
        logging.error("lcsc_id should start by C....")
        return False

    if arguments["full"]:
        arguments["symbol"], arguments["footprint"], arguments["3d"] = True, True, True

    if not any([arguments["symbol"], arguments["footprint"], arguments["3d"]]):
        logging.error(
            "Missing action arguments\n"
            "  easy_kicad --lcsc_id=C2040 --footprint\n"
            "  easy_kicad --lcsc_id=C2040 --symbol"
        )
        return False

    kicad_version = KicadVersion.v5 if arguments.get("v5") else KicadVersion.v6
    arguments["kicad_version"] = kicad_version

    if arguments["project_relative"] and not arguments["output"]:
        logging.error(
            "A project specific library path should be given with --output option when"
            " using --project-relative option\nFor example: easy_kicad"
            " --lcsc_id=C2040 --full"
            " --output=C:/Users/your_username/Documents/Kicad/6.0/projects/my_project"
            " --project-relative"
        )
        return False

    if arguments["output"]:
        # Standardize path
        clean_output = arguments["output"].replace("\\", "/")
        
        if clean_output.endswith("/") or os.path.isdir(clean_output):
            # It's a directory!
            base_folder = clean_output.rstrip("/")
            lib_name = "easy_kicad"
        else:
            # It's a file prefix path (e.g. /app/outputFile/my_lib)
            parts = clean_output.split("/")
            base_folder = "/".join(parts[:-1])
            lib_name = parts[-1]

        if not os.path.isdir(base_folder):
            try:
                os.makedirs(base_folder, exist_ok=True)
            except Exception:
                logging.error(f"Can't create or find folder: {base_folder}")
                return False
    else:
        # Use a consistent absolute path for the default folder
        default_folder = os.path.abspath("outputFile")
        if not os.path.isdir(default_folder):
            os.makedirs(default_folder, exist_ok=True)

        base_folder = default_folder
        lib_name = "easy_kicad"
        arguments["use_default_folder"] = True

    arguments["output"] = os.path.join(base_folder, lib_name)

    # Create new footprint folder if it does not exist
    if not os.path.isdir(f"{arguments['output']}.pretty"):
        os.mkdir(f"{arguments['output']}.pretty")
        logging.info(f"Create {lib_name}.pretty footprint folder in {base_folder}")

    # Create new 3d model folder if don't exist
    if not os.path.isdir(f"{arguments['output']}.3dshapes"):
        os.mkdir(f"{arguments['output']}.3dshapes")
        logging.info(f"Create {lib_name}.3dshapes 3D model folder in {base_folder}")

    lib_extension = "kicad_sym" if kicad_version == KicadVersion.v6 else "lib"
    if not os.path.isfile(f"{arguments['output']}.{lib_extension}"):
        with open(
            file=f"{arguments['output']}.{lib_extension}", mode="w+", encoding="utf-8"
        ) as my_lib:
            my_lib.write(
                dedent(
                    """\
                (kicad_symbol_lib
                  (version 20211014)
                  (generator https://github.com/uPesy/easy_kicad.py)
                )"""
                )
                if kicad_version == KicadVersion.v6
                else "EESchema-LIBRARY Version 2.4\n#encoding utf-8\n"
            )
        logging.info(f"Create {lib_name}.{lib_extension} symbol lib in {base_folder}")

    return True


def delete_component_in_symbol_lib(
    lib_path: str, component_id: str, component_name: str
) -> None:
    with open(file=lib_path, encoding="utf-8") as f:
        current_lib = f.read()
        new_data = re.sub(
            rf'(#\n# {component_name}\n#\n.*?F6 "{component_id}".*?ENDDEF\n)',
            "",
            current_lib,
            flags=re.DOTALL,
        )

    with open(file=lib_path, mode="w", encoding="utf-8") as my_lib:
        my_lib.write(new_data)


def fp_already_in_footprint_lib(lib_path: str, package_name: str) -> bool:
    if os.path.isfile(f"{lib_path}/{package_name}.kicad_mod"):
        logging.warning(f"The footprint for this id is already in {lib_path}")
        return True
    return False


def main(argv: List[str] = sys.argv[1:]) -> int:
    print(f"-- Easy-KiCad v{__version__} --")

    # cli interface
    parser = get_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as err:
        return err.code
    arguments = vars(args)

    if arguments["debug"]:
        set_logger(log_file=None, log_level=logging.DEBUG)
    else:
        set_logger(log_file=None, log_level=logging.INFO)

    if not valid_arguments(arguments=arguments):
        return 1

    # Base folder for all output (determined by valid_arguments)
    output_base_folder = os.path.dirname(arguments["output"])

    # Initialize DB manager
    db = DBManager(db_path=arguments.get("db"))
    
    # Determine the list of IDs to process
    if arguments.get("match"):
        lcsc_ids = db.search_components(arguments["match"])
        if not lcsc_ids:
            logging.error(f"No components found matching '{arguments['match']}'")
            return 1
        logging.info(f"Found {len(lcsc_ids)} components matching '{arguments['match']}'. Starting bulk download...")
    else:
        lcsc_ids = [arguments["lcsc_id"]]

    # --- PROCESS EACH COMPONENT ---
    total_parts = len(lcsc_ids)
    for index, component_id in enumerate(lcsc_ids, 1):
        # Get Metadata for categorization and skipping
        metadata = db.get_part_metadata(component_id)
        progress_str = f"[{index}/{total_parts}]"
        easyeda_symbol = None
        easyeda_footprint = None

        # Determine library file name and path for this part
        lib_name = "MISC - Others" # Default
        raw_cat = "Others"
        raw_sub = "Miscellaneous"

        if metadata:
            raw_cat = metadata['category_name']
            raw_sub = metadata['subcategory_name'] or "Others"
            prefix = metadata.get('shorthand') or raw_cat[:4].upper()
            mfr_part = metadata.get('mfr_part_no', '') or ""
            description = metadata.get('description', '') or ""
            
            # Smart Sort logic
            SMART_SORT_RULES = {
                "RESISTOR": ("RES", "Resistors"),
                "CAPACITOR": ("CAP", "Capacitors"),
                "DIODE": ("DIO", "Diodes"),
                "CRYSTAL": ("XTAL", "Crystals"),
                "RESONATOR": ("XTAL", "Resonators"),
                "ESP32": ("MCU", "ESP32_E"),
                "TRANSMITTER": ("RF", "Wireless"),
                "RECEIVER": ("RF", "Wireless"),
                "OPTOCOUPLER": ("OPT", "Optocouplers"),
                "TRANSISTOR": ("TRN", "Transistors"),
                "MOSFET": ("TRN", "Transistors"),
                "INDUCTOR": ("IND", "Inductors"),
                "TRANSFORMER": ("IND", "Transformers"),
                "CONNECTOR": ("CON", "Connectors"),
                "HEADER": ("CON", "Headers"),
                "RELAY": ("RLY", "Relays"),
                "FUSE": ("FUS", "Fuses"),
                "SWITCH": ("SWI", "Switches"),
                "REGULATOR": ("PWR", "Power_ICs"),
                "MPU": ("MCU", "Processors"),
                "MCU": ("MCU", "Microcontrollers"),
                "SENSOR": ("SEN", "Sensors"),
                "LED": ("OPTO", "LEDs"),
                "FLASH": ("MEM", "Memory"),
                "EEPROM": ("MEM", "Memory"),
            }
            for keyword, (sh, sub) in SMART_SORT_RULES.items():
                if keyword in description.upper() or keyword in mfr_part.upper():
                    prefix = sh
                    raw_sub = sub
                    break
            
            clean_sub = raw_sub.replace(" & ", "_and_").replace(" ", "_").replace("/", "_")
            lib_name = f"{prefix} - {clean_sub}"

        target_lib_path = os.path.join(output_base_folder, lib_name)
        kicad_version = arguments["kicad_version"]
        sym_lib_ext = "kicad_sym" if kicad_version == KicadVersion.v6 else "lib"
        full_lib_file = f"{target_lib_path}.{sym_lib_ext}"

        # Improved Skip Logic: Only skip if mirrored AND the file actually exists
        if metadata and metadata.get('is_mirrored') and not arguments["overwrite"]:
            if os.path.isfile(full_lib_file):
                logging.info(f"{progress_str} Skipping {component_id} (already mirrored and file exists).")
                continue
            else:
                logging.warning(f"{progress_str} {component_id} is marked as mirrored but library file is missing. Re-downloading...")

        logging.info(f"{progress_str} == Mirroring Part: {component_id} ==")
        
        # Get CAD data
        api = EasyedaApi()
        cad_data = api.get_cad_data_of_component(lcsc_id=component_id)

        if not cad_data:
            logging.error(f"Failed to fetch data for part {component_id}. Skipping...")
            continue
        
        arguments['output'] = target_lib_path
        
        # This re-initializes folders/headers if needed for the current part's library
        valid_arguments(arguments=arguments)
        
        kicad_version = arguments["kicad_version"]
        sym_lib_ext = "kicad_sym" if kicad_version == KicadVersion.v6 else "lib"

        # SYMBOL
        if arguments["symbol"]:
            logging.info(f"Generating Symbol for {component_id}...")
            importer = EasyedaSymbolImporter(easyeda_cp_cad_data=cad_data)
            easyeda_symbol = importer.get_symbol()
            if easyeda_symbol:
                if metadata:
                    easyeda_symbol.info.category = raw_cat
                    easyeda_symbol.info.subcategory = raw_sub
                    easyeda_symbol.info.description = metadata['description']
                
                # Additional check in the file itself (secondary safety)
                is_already_in_lib = id_already_in_symbol_lib(
                    lib_path=f"{arguments['output']}.{sym_lib_ext}",
                    component_name=easyeda_symbol.info.name,
                    kicad_version=kicad_version,
                )

                if is_already_in_lib and not arguments["overwrite"]:
                    pass # Already handled by is_mirrored DB check but good for safety
                else:
                    exporter = ExporterSymbolKicad(symbol=easyeda_symbol, kicad_version=kicad_version)
                    kicad_symbol_lib = exporter.export(
                        footprint_lib_name=arguments["output"].split("/")[-1].split(".")[0],
                    )
                    if is_already_in_lib:
                        update_component_in_symbol_lib_file(
                            lib_path=f"{arguments['output']}.{sym_lib_ext}",
                            component_name=easyeda_symbol.info.name,
                            component_content=kicad_symbol_lib,
                            kicad_version=kicad_version,
                        )
                    else:
                        add_component_in_symbol_lib_file(
                            lib_path=f"{arguments['output']}.{sym_lib_ext}",
                            component_content=kicad_symbol_lib,
                            kicad_version=kicad_version,
                        )
                    logging.info(f"Symbol {component_id} saved/updated.")
            else:
                logging.error(f"Could not extract symbol for {component_id}.")

        # FOOTPRINT
        if arguments["footprint"]:
            logging.info(f"Generating Footprint for {component_id}...")
            importer = EasyedaFootprintImporter(easyeda_cp_cad_data=cad_data)
            easyeda_footprint = importer.get_footprint()
            
            if easyeda_footprint:
                fp_path = f"{arguments['output']}.pretty"
                if os.path.isfile(f"{fp_path}/{easyeda_footprint.info.name}.kicad_mod") and not arguments["overwrite"]:
                    pass
                else:
                    ki_footprint = ExporterFootprintKicad(footprint=easyeda_footprint)
                    model_3d_path = f"{arguments['output']}.3dshapes"
                    ki_footprint.export(
                        footprint_full_path=f"{fp_path}/{easyeda_footprint.info.name}.kicad_mod",
                        model_3d_path=model_3d_path,
                    )
                    logging.info(f"Footprint {component_id} saved.")
            else:
                logging.error(f"Could not extract footprint for {component_id}.")

        # 3D MODEL
        if arguments["3d"]:
            logging.info(f"Downloading 3D Model for {component_id} (this can take time for large parts)...")
            importer_3d = Easyeda3dModelImporter(
                easyeda_cp_cad_data=cad_data, download_raw_3d_model=True
            )
            exporter_3d = Exporter3dModelKicad(model_3d=importer_3d.output)
            
            if exporter_3d.input:
                exporter_3d.export(lib_path=arguments["output"])
                logging.info(f"3D-Model {component_id} saved.")
            else:
                logging.error(f"Could not extract 3D model for {component_id}.")

        # FINAL STEP: MARK AS MIRRORED IN DB
        db.mark_mirrored(component_id)
        
        logging.info(f"== Finished Part {component_id}. Persistent state saved. ==")

    # REBUILD MASTER TABLES AT THE END
    update_kicad_lib_tables(output_base_folder)
    logging.info("Bulk Mirroring Complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
