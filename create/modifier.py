# ============================================================================ #
"""Functions to instantiate a DsonModifier object."""

from pathlib import Path

# pylint: disable=E0402
from ..datatypes import DsonMorph, DsonSkinBinding, DsonVector
from ..library import get_asset_data_from_library
from ..observers import _modifier_struct_created
from ..structs.modifier import DsonModifier
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_modifier_struct(dsf_filepath:Path, instance_data:dict=None) -> DsonModifier:
    """Parses a DSON modifier dictionary into a DsonModifier wrapper struct."""

    dsf_filepath = check_path(dsf_filepath)

    library_data:dict = get_asset_data_from_library(dsf_filepath, "modifier_library")

    struct:DsonModifier = DsonModifier()

    asset_url:AssetURL = parse_url_string(str(dsf_filepath))
    struct.dsf_file = asset_url.file_path
    struct.library_id = library_data["id"]
    struct.instance_data = instance_data["id"] if instance_data else None

    # ======================================================================== #

    # Content type
    # TODO: Default value?
    if "presentation" in library_data:
        struct.content_type = library_data["presentation"]["type"]

    # Parenting
    if "parent" in library_data:
        struct.library_parent = library_data["parent"]
    if instance_data and "parent" in instance_data:
        struct.instance_parent = instance_data["parent"]

    # Skin binding
    skin_dictionary:dict = None
    if "skin" in library_data:
        skin_dictionary = library_data["skin"]
    if instance_data and "skin" in instance_data:
        skin_dictionary = instance_data["skin"]

    if skin_dictionary:
        struct.skin_binding = DsonSkinBinding()
        struct.skin_binding.target_node = skin_dictionary["node"]
        struct.skin_binding.target_geometry = skin_dictionary["geometry"]
        struct.skin_binding.expected_vertices = skin_dictionary["vertex_count"]
        struct.skin_binding.bone_weights = {}

        for joint in skin_dictionary.get("joints", []):
            bone_url:str = joint["node"]
            bone_weights:list = []

            if "node_weights" in joint:
                bone_weights = [ (weight[0], weight[1]) for weight in joint["node_weights"] ]

            struct.skin_binding.bone_weights[bone_url] = bone_weights

    # Morph data
    morph_dictionary:dict = None
    if "morph" in library_data:
        morph_dictionary = library_data["morph"]
    if instance_data and "morph" in instance_data:
        morph_dictionary = instance_data["morph"]

    if morph_dictionary:
        struct.morph = DsonMorph()
        struct.morph.expected_vertices = morph_dictionary["vertex_count"]
        struct.morph.deltas = {}

        # Instead of "float3_indexed_array", store the data inside a dictionary
        #   using the vertex index as the key for easy lookup.
        for delta in morph_dictionary["deltas"]:
            index:int = delta[0]
            offset:DsonVector = DsonVector.create(delta[1:])
            struct.morphs.deltas[index] = offset

    # ======================================================================== #

    _modifier_struct_created(struct, library_data, instance_data)

    return struct
