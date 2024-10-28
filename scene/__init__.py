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
from ..enums import NodeType
from ..exceptions import SceneMissing
from ..file import open_dson_file
from ..structs.geometry import DsonGeometry
from ..structs.modifier import DsonModifier
from ..structs.node import DsonNode
from ..structs.uv_set import DsonUVSet
from ..url import AssetURL, parse_url_string
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
    #                                                                          #
    # ======================================================================== #

    def _get_node_by_id(self:DsonScene, node_instance_id:str) -> dict:

        if not "nodes" in self.duf_file["scene"]:
            return None

        node_data:dict = None

        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == node_instance_id:
                node_data = node
                break

        return node_data

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_geometry_instance_ids(self:DsonScene, node_instance_id:str) -> list[str]:

        if not "nodes" in self.duf_file["scene"]:
            return []

        node_data:dict = None

        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == node_instance_id:
                node_data = node
                break

        if not (node_data and "geometries" in node_data):
            return []

        geometry_ids:list[str] = []

        for geometry in node_data["geometries"]:
            geometry_ids.append(geometry["id"])

        return geometry_ids

    # ======================================================================== #

    def get_node_instance_ids(self:DsonScene) -> list[str]:
        if "nodes" in self.duf_file["scene"]:
            return [ node["id"] for node in self.duf_file["scene"]["nodes"] ]
        else:
            return []

    # ======================================================================== #

    def get_uv_set_instance_ids(self:DsonScene) -> list[str]:
        if "uvs" in self.duf_file["scene"]:
            return [ uv_set["id"] for uv_set in self.duf_file["scene"]["uvs"] ]
        else:
            return []

    # ======================================================================== #

    def get_modifier_instance_ids(self:DsonScene) -> list[str]:
        if "modifiers" in self.duf_file["scene"]:
            return [ modifier["id"] for modifier in self.duf_file["scene"]["modifiers"] ]
        else:
            return []

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_node_parent_id(self:DsonScene, child_id:str) -> str:

        if not "nodes" in self.duf_file["scene"]:
            return None

        child_data:dict = None

        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == child_id:
                child_data = node
                break

        if not (child_data and "parent" in child_data):
            return None

        parent_url:AssetURL = parse_url_string(child_data["parent"])

        return parent_url.asset_id

    # ======================================================================== #

    def get_node_parent_in_place_id(self:DsonScene, child_id:str) -> str:

        if not "nodes" in self.duf_file["scene"]:
            return None

        child_data:dict = None

        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == child_id:
                child_data = node
                break

        if not (child_data and "parent_in_place" in child_data):
            return None

        parent_url:AssetURL = parse_url_string(child_data["parent_in_place"])

        return parent_url.asset_id

    # ======================================================================== #

    def get_node_child_ids(self:DsonScene, parent_id:str) -> list[str]:

        if not "nodes" in self.duf_file["scene"]:
            return []

        child_ids:list[str] = []

        for node in self.duf_file["scene"]["nodes"]:
            if not node["parent"]:
                continue
            parent_url:AssetURL = parse_url_string(node["parent"])
            if parent_url.asset_id == parent_id:
                child_ids.append(node["id"])

        return child_ids

    # ======================================================================== #

    def get_node_hierarchy_root_id(self:DsonScene, bone_id:str) -> str:

        node_data:dict = self._get_node_by_id(bone_id)

        if not (node_data and NodeType(node_data["type"]) == NodeType.BONE):
            return None

        root_id:str = None
        pointer:dict = node_data

        while True:
            
            if not (pointer and "parent" in pointer):
                break

            parent_url:AssetURL = parse_url_string(pointer)

            match( NodeType(pointer["type"]) ):
                case NodeType.BONE:
                    pointer = self._get_node_by_id(parent_url.asset_id)
                    continue
                case NodeType.FIGURE:
                    root_id = pointer
                    break
                case _:
                    # TODO: Error handling?
                    break

        return root_id

    # ======================================================================== #

    def get_node_hierarchy_bone_ids(self:DsonScene, figure_id:str) -> list[str]:

        if not "nodes" in self.duf_file["scene"]:
            return []

        node_data:dict = None

        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == figure_id:
                node_data = node
                break

        if not node_data:
            return []

        node_type:NodeType = NodeType(node_data["type"])

        if node_type != NodeType.FIGURE:
            return []

        hierarchy_ids:list[str] = []

        node_children:list[dict] = []
        node_children.extend( self.get_node_child_ids(figure_id) )

        while node_children:
            child_data:dict = node_children.pop(0)

            child_id:str = child_data["id"]

            if NodeType(child_data["type"]) == NodeType.BONE:
                hierarchy_ids.append( child_id )
                node_children.extend( self.get_node_child_ids(child_id) )

        return hierarchy_ids

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def create_geometry_struct(self:DsonScene, node_id:str, geometry_id:str) -> DsonGeometry:

        if not "nodes" in self.duf_file["scene"]:
            return None

        node_instance_data:dict = None
        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == node_id:
                node_instance_data = node
                break

        if not (node_instance_data and "geometries" in node_instance_data):
            return None

        geometry_instance_data:dict = None

        for geometry in node_instance_data["geometries"]:
            if geometry["id"] == geometry_id:
                geometry_instance_data = geometry
                break

        library_url:Path = Path(geometry_instance_data["url"])

        return create_geometry_struct(library_url, geometry_instance_data)

    # ======================================================================== #

    def create_node_struct(self:DsonScene, node_id:str) -> DsonNode:

        if not "nodes" in self.duf_file["scene"]:
            return None

        node_instance_data:dict = None
        for node in self.duf_file["scene"]["nodes"]:
            if node["id"] == node_id:
                node_instance_data = node
                break

        library_url:Path = Path(node_instance_data["url"])

        return create_node_struct(library_url, node_instance_data)

    # ======================================================================== #

    def create_uv_set_struct(self:DsonScene, uv_set_id:str) -> DsonUVSet:

        if not "uvs" in self.duf_file["scene"]:
            return None

        uv_set_instance_data:dict = None
        for uv_set in self.duf_file["scene"]["uvs"]:
            if uv_set["id"] == uv_set_id:
                uv_set_instance_data = uv_set
                break

        library_url:Path = Path(uv_set_instance_data["url"])

        return create_uv_set_struct(library_url, uv_set_instance_data)

    # ======================================================================== #

    def create_modifier_struct(self:DsonScene, modifier_id:str) -> DsonModifier:

        if not "modifiers" in self.duf_file["scene"]:
            return None

        modifier_instance_data:dict = None
        for modifier in self.duf_file["scene"]["modifiers"]:
            if modifier["id"] == modifier_id:
                modifier_instance_data = modifier
                break

        library_url:Path = Path(modifier_instance_data["url"])

        return create_modifier_struct(library_url, modifier_instance_data)

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #
