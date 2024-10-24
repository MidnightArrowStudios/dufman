# ============================================================================ #
"""Defines custom data types which represent DSON dictionaries."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

# pylint: disable=C0301

# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonChannelFloat:
    """A user-facing float property."""

    default:float = 0.0
    current:float = 0.0
    #minimum:float = 0.0
    #maximum:float = 1.0
    #use_limits:bool = False


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonChannelVector:
    """A wrapper for three user-facing float properties representing a 3D coordinates."""

    x:DsonChannelFloat = None
    y:DsonChannelFloat = None
    z:DsonChannelFloat = None

    @classmethod
    def parse_channels(cls:type, dson_data:dict, vector_name:str, axis:str,
            property_name:str, default:float=0.0) -> float:
        """Parses a list of three DSON objects representing the X, Y, and Z axes."""
        if not dson_data or not vector_name in dson_data:
            return default
        for channel in dson_data[vector_name]:
            channel_id:str = channel["id"].upper()
            axis_name:str = axis.upper()
            if channel_id == axis_name and property_name in channel:
                return channel[property_name]
        return default


    @classmethod
    def create_from_dson_data(cls:type, vector_name:str, library_data:dict,
            instance_data:dict=None, default:tuple=(0.0, 0.0, 0.0)) -> DsonChannelVector:
        """Factory method to instantiate a DsonFloatVector from DSON dictionaries."""

        vector:DsonChannelVector = cls()
        vector.x = DsonChannelFloat()
        vector.y = DsonChannelFloat()
        vector.z = DsonChannelFloat()

        # Library default
        vector.x.default = cls.parse_channels(library_data, vector_name, 'X', "value", default[0])
        vector.y.default = cls.parse_channels(library_data, vector_name, 'Y', "value", default[1])
        vector.z.default = cls.parse_channels(library_data, vector_name, 'Z', "value", default[2])

        # Instance default
        vector.x.default = cls.parse_channels(instance_data, vector_name, 'X', "value", vector.x.default)
        vector.y.default = cls.parse_channels(instance_data, vector_name, 'Y', "value", vector.y.default)
        vector.z.default = cls.parse_channels(instance_data, vector_name, 'Z', "value", vector.z.default)

        # Library current
        vector.x.current = cls.parse_channels(library_data, vector_name, 'X', "current_value", vector.x.default)
        vector.y.current = cls.parse_channels(library_data, vector_name, 'Y', "current_value", vector.y.default)
        vector.z.current = cls.parse_channels(library_data, vector_name, 'Z', "current_value", vector.z.default)

        # Library default
        vector.x.current = cls.parse_channels(instance_data, vector_name, 'X', "current_value", vector.x.current)
        vector.y.current = cls.parse_channels(instance_data, vector_name, 'Y', "current_value", vector.y.current)
        vector.z.current = cls.parse_channels(instance_data, vector_name, 'Z', "current_value", vector.z.current)

        return vector

# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonMorph:
    """An intermediate representation of DSON morph data."""

    expected_vertices       : int       = 0
    deltas                  : dict      = None


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonPolygon:
    """A wrapper for the vertex indices which constitute a mesh's face."""

    vertex_1:int = None
    vertex_2:int = None
    vertex_3:int = None
    vertex_4:int = None

    @classmethod
    def create(cls:type, indices:list[int]) -> DsonPolygon:
        """Factory method to validate input data."""

        if not (len(indices) >= 3 and len(indices) <= 4):
            raise ValueError

        # FIXME: Implement error handling
        # converted_values:list[int] = []
        # for parameter in values:
        #     try:
        #         converted_values.append(int(parameter))
        #     except ValueError as e:
        #         raise e

        return cls(
            vertex_1=indices[0],
            vertex_2=indices[1],
            vertex_3=indices[2],
            vertex_4=indices[3] if len(indices) == 4 else None,
            )


    def get_vertex_indices(self:DsonPolygon) -> list[int]:
        """Convenience method to get vertex indices, or None if invalid."""
        properties:list[Any] = [
            self.vertex_1,
            self.vertex_2,
            self.vertex_3,
            self.vertex_4,
            ]

        values:list[int] = []

        # Cull duplicate vertices, which will cause an error in BMesh.
        for value in properties:
            if value not in values:
                values.append(value)

        # If culling results in two or less vertices, return None so BMesh
        # knows not to try and process it.
        if len(values) >= 3:                        # pylint: disable=R1705
            return values
        else:
            return None


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonSkinBinding:
    """An intermediate representation of DSON weightmapping data."""

    target_node                 : str       = None
    target_geometry             : str       = None
    expected_vertices           : int       = 0
    bone_weights                : dict      = None


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonVector:
    """A wrapper for the three floats which define a 3D coordinate."""

    x:float = 0.0
    y:float = 0.0
    z:float = 0.0

    @classmethod
    def create(cls:type, *arguments) -> DsonVector:
        """Factory method to validate input data."""

        message:str = "DsonVector only accepts three floats or a collection of three floats."

        # import pdb
        # breakpoint()

        values:list[float] = []
        if len(arguments) == 1 and isinstance(arguments[0], (list, tuple, set)):
            values.extend(arguments[0])
        elif len(arguments) == 3:
            values.extend(arguments)
        else:
            raise ValueError(message)

        if len(values) != 3:
            raise ValueError(message)

        for value in values:
            try:
                float(value)
            except ValueError as ve:
                raise ValueError(message) from ve

        return cls(x=values[0], y=values[1], z=values[2])
