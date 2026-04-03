# Global imports
import json
import logging
import math
import os
import re
from datetime import datetime
from glob import escape

from barmajinokad import __version__
from barmajinokad.kicad.parameters_kicad_symbol import KicadVersion, sanitize_fields

sym_lib_regex_pattern = {
    "v5": r"(#\n# {component_name}\n#\n.*?ENDDEF\n)",
    "v6": r'\n  \(symbol "{component_name}".*?\n  \)',
    "v6_99": r"",
}


def set_logger(log_file: str, log_level: int) -> None:

    root_log = logging.getLogger()
    root_log.setLevel(log_level)

    if log_file:
        file_handler = logging.FileHandler(
            filename=log_file, mode="w", encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter(
                fmt="[{asctime}][{levelname}][{funcName}] {message}", style="{"
            )
        )
        root_log.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(
        logging.Formatter(fmt="[{levelname}] {message}", style="{")
    )
    root_log.addHandler(stream_handler)


def sanitize_for_regex(field: str):
    return re.escape(field)


def id_already_in_symbol_lib(
    lib_path: str, component_name: str, kicad_version: KicadVersion
) -> bool:
    with open(lib_path, encoding="utf-8") as lib_file:
        current_lib = lib_file.read()
        component = re.findall(
            sym_lib_regex_pattern[kicad_version.name].format(
                component_name=sanitize_for_regex(component_name)
            ),
            current_lib,
            flags=re.DOTALL,
        )
        if component != []:
            logging.warning(f"This id is already in {lib_path}")
            return True
    return False


def update_component_in_symbol_lib_file(
    lib_path: str,
    component_name: str,
    component_content: str,
    kicad_version: KicadVersion,
) -> None:
    with open(file=lib_path, encoding="utf-8") as lib_file:
        current_lib = lib_file.read()
        new_lib = re.sub(
            sym_lib_regex_pattern[kicad_version.name].format(
                component_name=sanitize_for_regex(component_name)
            ),
            component_content,
            current_lib,
            flags=re.DOTALL,
        )

        new_lib = new_lib.replace(
            "(generator kicad_symbol_editor)",
            "(generator https://github.com/uPesy/barmajinokad.py)",
        )

    with open(file=lib_path, mode="w", encoding="utf-8") as lib_file:
        lib_file.write(new_lib)


def add_component_in_symbol_lib_file(
    lib_path: str, component_content: str, kicad_version: KicadVersion
) -> None:

    if kicad_version == KicadVersion.v5:
        with open(file=lib_path, mode="a+", encoding="utf-8") as lib_file:
            lib_file.write(component_content)
    elif kicad_version == KicadVersion.v6:
        with open(file=lib_path, mode="rb+") as lib_file:
            lib_file.seek(-2, 2)
            lib_file.truncate()
            lib_file.write(component_content.encode(encoding="utf-8"))
            lib_file.write("\n)".encode(encoding="utf-8"))

        with open(file=lib_path, encoding="utf-8") as lib_file:
            new_lib_data = lib_file.read()

        with open(file=lib_path, mode="w", encoding="utf-8") as lib_file:
            lib_file.write(
                new_lib_data.replace(
                    "(generator kicad_symbol_editor)",
                    "(generator https://github.com/uPesy/barmajinokad.py)",
                )
            )


def get_local_config() -> dict:
    if not os.path.isfile("barmajinokad_config.json"):
        with open(file="barmajinokad_config.json", mode="w", encoding="utf-8") as conf:
            json.dump(
                {"updated_at": datetime.utcnow().timestamp(), "version": __version__},
                conf,
                indent=4,
                ensure_ascii=False,
            )
        logging.info("Create barmajinokad_config.json config file")

    with open(file="barmajinokad_config.json", encoding="utf-8") as conf:
        local_conf: dict = json.load(conf)

    return local_conf


def get_arc_center(start_x, start_y, end_x, end_y, rotation_direction, radius):
    arc_distance = math.sqrt(
        (end_x - start_x) * (end_x - start_x) + (end_y - start_y) * (end_y - start_y)
    )

    m_x = (start_x + end_x) / 2
    m_y = (start_y + end_y) / 2
    u = (end_x - start_x) / arc_distance
    v = (end_y - start_y) / arc_distance
    h = math.sqrt(radius * radius - (arc_distance * arc_distance) / 4)

    center_x = m_x - rotation_direction * h * v
    center_y = m_y + rotation_direction * h * u

    return center_x, center_y


def get_arc_angle_end(
    center_x: float, end_x: float, radius: float, flag_large_arc: bool
):
    theta = math.acos((end_x - center_x) / radius) * 180 / math.pi
    return 180 + theta if flag_large_arc else 180 + theta


def get_middle_arc_pos(
    center_x: float,
    center_y: float,
    radius: float,
    angle_start: float,
    angle_end: float,
):
    middle_x = center_x + radius * math.cos((angle_start + angle_end) / 2)
    middle_y = center_y + radius * math.sin((angle_start + angle_end) / 2)
    return middle_x, middle_y


def update_kicad_lib_tables(output_dir: str):
    """
    Scans output_dir for .kicad_sym files and .pretty folders
    and generates sym-lib-table and fp-lib-table in the same directory.
    """
    output_dir = os.path.abspath(output_dir)
    sym_table_path = os.path.join(output_dir, "sym-lib-table")
    fp_table_path = os.path.join(output_dir, "fp-lib-table")

    # 1. Update Symbol Table
    sym_libs = sorted([f for f in os.listdir(output_dir) if f.endswith(".kicad_sym")])
    sym_table_content = ["(sym_lib_table"]
    for lib in sym_libs:
        nickname = lib.replace(".kicad_sym", "")
        # Using absolute paths ensures KiCad always finds the files
        uri = os.path.join(output_dir, lib)
        sym_table_content.append(
            f'  (lib (name "{nickname}")(type "KiCad")(uri "{uri}")(options "")(descr ""))'
        )
    sym_table_content.append(")")

    with open(sym_table_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sym_table_content))
    
    # Touch the file to signal KiCad's watcher
    try:
        os.utime(sym_table_path, None)
    except Exception:
        pass

    # 2. Update Footprint Table
    fp_libs = sorted(
        [
            f
            for f in os.listdir(output_dir)
            if f.endswith(".pretty") and os.path.isdir(os.path.join(output_dir, f))
        ]
    )
    fp_table_content = ["(fp_lib_table"]
    for lib in fp_libs:
        nickname = lib.replace(".pretty", "")
        uri = os.path.join(output_dir, lib)
        fp_table_content.append(
            f'  (lib (name "{nickname}")(type "KiCad")(uri "{uri}")(options "")(descr ""))'
        )
    fp_table_content.append(")")

    with open(fp_table_path, "w", encoding="utf-8") as f:
        f.write("\n".join(fp_table_content))

    # Touch the file to signal KiCad's watcher
    try:
        os.utime(fp_table_path, None)
    except Exception:
        pass

    logging.info(f"Updated KiCad master library tables in {output_dir}")


def update_readme(output_dir: str, lcsc_id: str, component_name: str, description: str):
    """
    Updates a README.md file in the output directory with the new component.
    """
    readme_path = os.path.join(output_dir, "README.md")
    
    if not os.path.isfile(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Mirrored KiCad Components\n\n")
            f.write("| LCSC ID | Name | Description | Date |\n")
            f.write("| --- | --- | --- | --- |\n")

    date_str = datetime.now().strftime("%Y-%m-%d %a")
    line = f"| {lcsc_id} | {component_name} | {description} | {date_str} |\n"
    
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write(line)
