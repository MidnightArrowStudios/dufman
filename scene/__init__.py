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
        self.node_instances:OrderedDict = OrderedDict()
        self.uv_set_instances:OrderedDict = OrderedDict()
        self.modifier_instances:OrderedDict = OrderedDict()

        scene:dict = opened_file["scene"]

        # TODO: Property validation/error handling

        # duf_file["scene"]["nodes"]
        for node_instance_data in scene.get("nodes", []):

            node_instance_id:str = node_instance_data["id"]
            node_library_url:Path = Path(node_instance_data["url"])

            node_struct:DsonNode = create_node_struct(node_library_url, node_instance_data)
            self.node_instances[node_instance_id] = node_struct

        # duf_file["scene"]["uvs"]
        for uv_set_instance_data in scene.get("uvs", []):

            uv_set_instance_id:str = uv_set_instance_data["id"]
            uv_set_library_url:Path = Path(uv_set_instance_data["url"])

            uv_set_struct:DsonUVSet = create_uv_set_struct(uv_set_library_url, uv_set_instance_data)
            self.uv_set_instances[uv_set_instance_id] = uv_set_struct

        # duf_file["scene"]["uvs"]
        for modifier_instance_data in scene.get("modifiers", []):

            modifier_instance_id:str = modifier_instance_data["id"]
            modifier_library_url:Path = Path(modifier_instance_data["url"])

            modifier_struct:DsonModifier = create_modifier_struct(modifier_library_url, modifier_instance_data)
            self.modifier_instances[modifier_instance_id] = modifier_struct

        return

    # ======================================================================== #

    def get_node_instance_ids(self:DsonScene) -> list[str]:
        return list(self.node_instances.keys())

    def get_uv_set_instance_ids(self:DsonScene) -> list[str]:
        return list(self.uv_set_instances.keys())

    def get_modifier_instance_ids(self:DsonScene) -> list[str]:
        return list(self.modifier_instances.keys())
