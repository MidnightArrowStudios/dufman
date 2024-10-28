# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from collections import OrderedDict
from pathlib import Path

from ..create.node import create_node_struct
from ..create.geometry import create_geometry_struct
from ..exceptions import SceneMissing
from ..file import open_dson_file
from ..structs.geometry import DsonGeometry
from ..structs.node import DsonNode
from ..utilities import check_path

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

        for node_instance_data in opened_file["scene"]["nodes"]:

            # TODO: Property validation/error handling

            node_instance_id:str = node_instance_data["id"]
            node_library_url:Path = Path(node_instance_data["url"])

            node_struct:DsonNode = create_node_struct(node_library_url, node_instance_data)
            self.node_instances[node_instance_id] = node_struct

        return


    def get_node_instance_ids(self:DsonScene) -> list[str]:
        return list(self.node_instances.keys())
