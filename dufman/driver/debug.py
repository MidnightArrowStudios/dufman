# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from io import TextIOWrapper
from sys import stdout

# dufman
from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverTarget


# FIXME: Refactor this so it doesn't rely on DriverPath, which was removed.

# ============================================================================ #
#                                                                              #
# ============================================================================ #

# def debug_driver_path(path:DriverPath, output:TextIOWrapper=stdout) -> None:

#     # Print boolean values as floats
#     raw_value:Any = path.get_equation_value()
#     if isinstance(raw_value, bool):
#         float_string:str = f"({ str(float(path.get_equation_value())) })"
#     else:
#         float_string:str = ""

#     # Variables
#     value:str = str(raw_value)
#     stage:str = str(path.get_equation_stage())
#     node:str = str(path.is_driven_by_node())

#     # Print to file
#     output.write(f"\tSTAGE          { stage }\n")
#     output.write(f"\tVALUE          { value } { float_string }\n")
#     output.write(f"\tNODE_DRIVEN    { node }\n")
#     output.write("\tPATHS:\n")

#     for target_url in path.get_target_urls():
#         output.write(f"\t\t{ target_url }\n")
#     output.write("\n")

#     return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def debug_driver_target(target:DriverTarget, output:TextIOWrapper=stdout) -> None:

    # indent:str = "*" * 80
    # output.write(f"{ indent }\n{ target.get_target_url() }\n\n")

    # paths:list[DriverPath] = []
    # _build_controller_path(paths, [], PathSegment(None, target))

    # for path in paths:
    #     debug_driver_path(path, output)

    return


# ---------------------------------------------------------------------------- #

def debug_driver_target_jcms(target:DriverTarget, output:TextIOWrapper=stdout) -> None:

    # indent:str = "*" * 80
    # output.write(f"{ indent }\n{ target.get_target_url() }\n\n")

    # for path in get_jcm_paths_for_target(target):
    #     debug_driver_path(path, output)

    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def debug_driver_map_jcms(driver_map:DriverMap, output_raw:TextIOWrapper, output_filtered:TextIOWrapper) -> None:

    for driver_target in driver_map:
        if driver_target.has_morph():
            debug_driver_target(driver_target, output_raw)

    for driver_target in driver_map:
        if driver_target.has_morph():
            debug_driver_target_jcms(driver_target, output_filtered)

    return
