# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Functions to instantiate a DsonNode object."""

from pathlib import Path

from ..datatypes import DsonChannelVector, DsonFormula, DsonOperation
from ..enums import FormulaStage, FormulaOperator, NodeType, RotationOrder
from ..exceptions import MissingRequiredProperty
from ..file import extract_single_property
from ..library import get_asset_data_from_library
from ..observers import _node_struct_created
from ..structs.node import DsonNode
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_node_struct(dsf_filepath:Path, instance_data:dict=None) -> DsonNode:
    """Parses a DSON node dictionary into a DsonNode wrapper struct."""

    # Ensure type safety
    dsf_filepath:Path = check_path(dsf_filepath)

    # Load the DSON dictionary from disk
    library_data:dict = get_asset_data_from_library(dsf_filepath, "node_library")

    _validate(dsf_filepath, library_data, instance_data)

    struct:DsonNode = DsonNode()

    # Header information
    asset_url:AssetURL = parse_url_string(str(dsf_filepath))
    struct.dsf_file = asset_url.file_path
    struct.library_id = library_data["id"]
    struct.instance_id = instance_data["id"] if instance_data else None

    # Extract properties
    _name(struct, library_data, instance_data)
    _label(struct, library_data, instance_data)
    _source(struct, library_data, instance_data)
    _node_type(struct, library_data, instance_data)
    _content_type(struct, library_data, instance_data)
    _parent(struct, library_data, instance_data)
    _inherits_scale(struct, library_data, instance_data)
    _rotation_order(struct, library_data, instance_data)
    _center_point(struct, library_data, instance_data)
    _end_point(struct, library_data, instance_data)
    _translation(struct, library_data, instance_data)
    _orientation(struct, library_data, instance_data)
    _rotation(struct, library_data, instance_data)
    _scale(struct, library_data, instance_data)
    _general_scale(struct, library_data, instance_data)
    _formulas(struct, library_data, instance_data)

    # Fire observers
    _node_struct_created(struct, library_data, instance_data)

    return struct


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _validate(dsf_filepath:str, library_data:dict, instance_data:dict) -> None:

    if library_data and not "id" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "id")

    if library_data and not "name" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "name")

    if library_data and not "label" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "label")

    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _center_point(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.center_point = DsonChannelVector.create_from_dson_data("center_point",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    return

# ============================================================================ #

def _content_type(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    # Per DSON specs, presentation cannot be overridden
    if library_data and "presentation" in library_data:
        struct.content_type = library_data["presentation"]["type"]
    else:
        struct.content_type = None

    return

# ============================================================================ #

def _end_point(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.end_point = DsonChannelVector.create_from_dson_data("end_point",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    return

# ============================================================================ #

def _formulas(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    formula_list:dict = None
    if library_data and "formulas" in library_data:
        formula_list = library_data["formulas"]
    if instance_data and "formulas" in instance_data:
        formula_list = instance_data["formulas"]

    if not formula_list:
        return

    struct.formulas = []

    for dictionary in formula_list:
        formula:DsonFormula = DsonFormula()
        struct.formulas.append(formula)

        formula.output = dictionary["output"]

        if "stage" in dictionary:
            formula.stage = FormulaStage(dictionary["stage"])

        formula.operations = []

        for op_dict in dictionary["operations"]:
            operation:DsonOperation = DsonOperation()
            formula.operations.append(operation)

            operation.operator = FormulaOperator(op_dict["op"])

            if "url" in op_dict:
                operation.url = op_dict["url"]

            if "val" in op_dict:
                operation.value = op_dict["val"]

    return

# ============================================================================ #

def _general_scale(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.general_scale = 1.0
    if library_data and "general_scale" in library_data:
        struct.general_scale = library_data["general_scale"]
    if instance_data and "general_scale" in instance_data:
        struct.general_scale = instance_data["general_scale"]

    return

# ============================================================================ #

def _inherits_scale(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    # TODO: Do we ever need to worry about instance parents here?

    # All nodes inherit scale by default, except bones with bone parents.
    default_inherits_scale:bool = True

    if struct.node_type == NodeType.BONE and struct.parent:
        parent_url:AssetURL = parse_url_string(struct.parent)
        prop_path:list[str] = [ "node_library", parent_url.asset_id, "type" ]

        parent_type:str = None

        if parent_url.file_path:
            parent_type = extract_single_property(parent_url.file_path, prop_path)
        else:
            parent_type = extract_single_property(str(struct.dsf_file), prop_path)

        if parent_type and parent_type == "bone":
            default_inherits_scale = False

    struct.inherits_scale = default_inherits_scale
    if library_data and "inherits_scale" in library_data:
        struct.inherits_scale = library_data["inherits_scale"]
    if instance_data and "inherits_scale" in instance_data:
        struct.inherits_scale = instance_data["inherits_scale"]

    return

# ============================================================================ #

def _label(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    if library_data and "label" in library_data:
        struct.label = library_data["label"]
    if instance_data and "label" in instance_data:
        struct.label = instance_data["label"]

    return

# ============================================================================ #

def _name(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    if library_data and "name" in library_data:
        struct.name = library_data["name"]
    if instance_data and "name" in instance_data:
        struct.name = instance_data["name"]

    return

# ============================================================================ #

def _node_type(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    # Per DSON specs, node type cannot be overridden
    if library_data and "type" in library_data:
        struct.node_type = NodeType(library_data["type"])
    else:
        struct.node_type = NodeType.NODE

    return

# ============================================================================ #

def _orientation(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.orientation = DsonChannelVector.create_from_dson_data("orientation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    return

# ============================================================================ #

def _parent(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    # TODO: Does instance parent overwrite library parent, or should that be
    #   kept sepatate?
    if library_data and "parent" in library_data:
        struct.parent = library_data["parent"]

    return

# ============================================================================ #

def _rotation(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.rotation = DsonChannelVector.create_from_dson_data("rotation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    return

# ============================================================================ #

def _rotation_order(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    if library_data and "rotation_order" in library_data:
        struct.rotation_order = RotationOrder(library_data["rotation_order"])
    if instance_data and "rotation_order" in instance_data:
        struct.rotation_order = RotationOrder(instance_data["rotation_order"])

    return

# ============================================================================ #

def _scale(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.scale = DsonChannelVector.create_from_dson_data("scale",
        library_data, instance_data, default=(1.0, 1.0, 1.0))

    return

# ============================================================================ #

def _source(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    if library_data and "source" in library_data:
        struct.source = library_data["source"]
    if instance_data and "source" in instance_data:
        struct.source = instance_data["source"]

    return

# ============================================================================ #

def _translation(struct:DsonNode, library_data:dict, instance_data:dict) -> None:

    struct.translation = DsonChannelVector.create_from_dson_data("translation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    return

# ============================================================================ #
