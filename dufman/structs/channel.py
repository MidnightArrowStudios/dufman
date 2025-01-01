# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines structs which encapsulate DSON's "channel" datatypes.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/channel/start
"""

# stdlib
from dataclasses import dataclass
from typing import Any, Iterator, Self

# dufman
from dufman.enums import ChannelType


# ============================================================================ #
# DsonChannel struct                                                           #
# ============================================================================ #

@dataclass
class DsonChannel:

    channel_id              : str           = None
    channel_type            : ChannelType   = ChannelType.FLOAT

    name                    : str           = None
    label                   : str           = None

    visible                 : bool          = True
    locked                  : bool          = False
    auto_follow             : bool          = False


    # ======================================================================== #

    @staticmethod
    def _create_basic(struct:Self, channel_dson:dict) -> None:

        # Verify channel's type is valid
        if not "type" in channel_dson:
            raise ValueError("Missing required property \"type\"")

        chstr:str = channel_dson["type"]
        try:
            struct.channel_type = ChannelType(chstr)
        except ValueError as ve:
            raise ValueError(f"Channel type \"{chstr}\" is not valid") from ve

        # -------------------------------------------------------------------- #

        # ID
        if "id" in channel_dson:
            struct.channel_id = channel_dson["id"]
        else:
            raise ValueError("Missing required property \"id\"")

        # Name
        if "name" in channel_dson:
            struct.name = channel_dson["name"]
        else:
            raise ValueError("Missing required property \"name\"")

        # Label
        if "label" in channel_dson:
            struct.label = channel_dson["label"]

        # Visible
        if "visible" in channel_dson:
            struct.visible = channel_dson["visible"]

        # Locked
        if "locked" in channel_dson:
            struct.locked = channel_dson["locked"]

        # Auto follow
        if "auto_follow" in channel_dson:
            struct.auto_follow = channel_dson["auto_follow"]

        # -------------------------------------------------------------------- #

        return


    # ======================================================================== #

    @staticmethod
    def load_from_dson(channel_dson:dict, **kwargs) -> Self:

        if not channel_dson:
            return None

        if not isinstance(channel_dson, dict):
            raise TypeError

        channel_type:ChannelType = ChannelType(channel_dson["type"])

        # -------------------------------------------------------------------- #

        match channel_type:
            case ChannelType.BOOL:
                return DsonChannelBool.load_from_dson(channel_dson, **kwargs)
            case ChannelType.FLOAT:
                return DsonChannelFloat.load_from_dson(channel_dson, **kwargs)
            case _:
                raise NotImplementedError(channel_type)

        # -------------------------------------------------------------------- #

        return None


    # ======================================================================== #

    def get_value(self:Self) -> Any:
        raise NotImplementedError


# ============================================================================ #
# DsonChannelBool struct                                                     #
# ============================================================================ #

@dataclass
class DsonChannelBool(DsonChannel):

    default_value:bool = False
    current_value:bool = False
    minimum_value:int = 0
    maximum_value:int = 1

    clamp_values:bool = False
    value_increment:int = 1
    can_use_image_map:bool = False


    # ======================================================================== #

    @staticmethod
    def load_from_dson(channel_dson:dict, **kwargs) -> Self:

        if not channel_dson:
            return

        if not isinstance(channel_dson, dict):
            raise TypeError

        struct:Self = DsonChannelBool()

        # -------------------------------------------------------------------- #

        DsonChannel._create_basic(struct, channel_dson)

        # Default value
        if "value" in channel_dson:
            struct.default_value = channel_dson["value"]
        else:
            struct.default_value = kwargs.get("default_value", False)

        # Current value
        if "current_value" in channel_dson:
            struct.current_value = channel_dson["current_value"]
        else:
            struct.current_value = struct.default_value

        # Minimum value
        if "min" in channel_dson:
            struct.minimum_value = channel_dson["min"]

        # Maximum value
        if "max" in channel_dson:
            struct.maximum_value = channel_dson["max"]

        # Clamp values
        if "clamped" in channel_dson:
            struct.clamp_values = channel_dson["clamped"]

        # Value increment
        if "step_size" in channel_dson:
            struct.value_increment = channel_dson["step_size"]

        # Can use image map
        if "mappable" in channel_dson:
            struct.can_use_image_map = channel_dson["mappable"]

        return struct


    # ======================================================================== #

    def __bool__(self:Self) -> bool:
        return bool(self.current_value)


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> bool:
        return bool(self)


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonChannelFloat(DsonChannel):

    default_value:float = 0.0
    current_value:float = 0.0
    minimum_value:float = 0.0
    maximum_value:float = 1.0

    clamp_values:bool = False
    display_as_percent:bool = False
    value_increment:float = 1.0
    can_use_image_map:bool = False


    # ======================================================================== #

    @staticmethod
    def load_from_dson(channel_dson:dict, **kwargs) -> Self:

        if not channel_dson:
            return None

        if not isinstance(channel_dson, dict):
            raise TypeError

        struct:Self = DsonChannelFloat()

        # -------------------------------------------------------------------- #

        DsonChannel._create_basic(struct, channel_dson)

        # Default value
        if "value" in channel_dson:
            struct.default_value = channel_dson["value"]
        else:
            struct.default_value = kwargs.get("default_value", 0.0)

        # Current value
        if "current_value" in channel_dson:
            struct.current_value = channel_dson["current_value"]
        else:
            struct.current_value = struct.default_value

        # Minimum value
        if "min" in channel_dson:
            struct.minimum_value = channel_dson["min"]

        # Maximum value
        if "max" in channel_dson:
            struct.maximum_value = channel_dson["max"]

        # Clamp values
        if "clamped" in channel_dson:
            struct.clamp_values = channel_dson["clamped"]

        # Display as percent
        if "display_as_percent" in channel_dson:
            struct.display_as_percent = channel_dson["display_as_percent"]

        # Value increment
        if "step_size" in channel_dson:
            struct.value_increment = channel_dson["step_size"]

        # Can use image map
        if "mappable" in channel_dson:
            struct.can_use_image_map = channel_dson["mappable"]

        # -------------------------------------------------------------------- #

        return struct


    # ======================================================================== #

    def __float__(self:Self) -> float:
        return float(self.current_value)


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> float:
        return float(self)


# ============================================================================ #
# DsonChannelVector struct                                                     #
# ============================================================================ #

@dataclass
class DsonChannelVector:

    x:DsonChannelFloat = None
    y:DsonChannelFloat = None
    z:DsonChannelFloat = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(channel_vector:list[dict], **kwargs) -> Self:

        x_dict:dict = None
        y_dict:dict = None
        z_dict:dict = None

        if channel_vector:
            for item in channel_vector:
                channel_id:str = item["id"].upper()
                if channel_id == 'X':
                    x_dict = item
                if channel_id == 'Y':
                    y_dict = item
                if channel_id == 'Z':
                    z_dict = item

        # TODO: Document that function can take:
        #   default_value
        #   default_x
        #   default_y
        #   default_z

        default_value:float = kwargs.get("default_value", 0.0)
        default_x:float = kwargs.get("default_x", default_value)
        default_y:float = kwargs.get("default_y", default_value)
        default_z:float = kwargs.get("default_z", default_value)

        vector:Self = DsonChannelVector()
        vector.x = DsonChannelFloat.load_from_dson(x_dict, default_value=default_x)
        vector.y = DsonChannelFloat.load_from_dson(y_dict, default_value=default_y)
        vector.z = DsonChannelFloat.load_from_dson(z_dict, default_value=default_z)

        return vector


    # ======================================================================== #

    def __iter__(self:Self) -> Iterator:
        return iter([ float(self.x), float(self.y), float(self.z) ])
