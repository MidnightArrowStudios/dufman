# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from collections import OrderedDict
from pathlib import Path

from ..create.geometry import create_geometry_struct
from ..create.modifier import create_modifier_struct
from ..create.node import create_node_struct
from ..create.uv_set import create_uv_set_struct
from ..exceptions import SceneMissing
from ..file import open_dson_file
from ..structs.geometry import DsonGeometry
from ..structs.modifier import DsonModifier
from ..structs.node import DsonNode
from ..structs.uv_set import DsonUVSet
from ..utilities import check_path


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class DsonScene:

    def __init__(self:DsonScene, duf_filepath:Path) -> None:

        # Ensure type safety
        duf_filepath = check_path(duf_filepath)

        # Load DUF file from disk
        opened_file:dict = open_dson_file(duf_filepath)

        if not "scene" in opened_file:
            raise SceneMissing

        self.duf_file:dict = opened_file

        return

    # ======================================================================== #

    def get_node_instance_ids(self:DsonScene) -> list[str]:
        if "nodes" in self.duf_file["scene"]:
            return [ node["id"] for node in self.duf_file["scene"]["nodes"] ]
        else:
            return []

    def get_uv_set_instance_ids(self:DsonScene) -> list[str]:
        if "uvs" in self.duf_file["scene"]:
            return [ uv_set["id"] for uv_set in self.duf_file["scene"]["uvs"] ]
        else:
            return []

    def get_modifier_instance_ids(self:DsonScene) -> list[str]:
        if "modifiers" in self.duf_file["scene"]:
            return [ modifier["id"] for modifier in self.duf_file["scene"]["modifiers"] ]
        else:
            return []
