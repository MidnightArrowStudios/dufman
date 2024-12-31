# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Any, Iterator, Self

from dufman.enums import ChannelType


# ============================================================================ #
#                                                                              #
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


    @staticmethod
    def _create_basic(struct:Self, channel_json:dict) -> None:

        # -------------------------------------------------------------------- #
        
        # Verify channel's type is valid
        if not "type" in channel_json:
            raise ValueError("Missing required property \"type\"")

        chstr:str = channel_json["type"]
        try:
            struct.channel_type = ChannelType(chstr)
        except ValueError as ve:
            raise ValueError(f"Channel type \"{chstr}\" is not valid") from ve

        # -------------------------------------------------------------------- #

        # ID
        if "id" in channel_json:
            struct.channel_id = channel_json["id"]
        else:
            raise ValueError("Missing required property \"id\"")

        # Name
        if "name" in channel_json:
            struct.name = channel_json["name"]
        else:
            raise ValueError("Missing required property \"name\"")

        # Label
        if "label" in channel_json:
            struct.label = channel_json["label"]

        # Visible
        if "visible" in channel_json:
            struct.visible = channel_json["visible"]

        # Locked
        if "locked" in channel_json:
            struct.locked = channel_json["locked"]

        # Auto follow
        if "auto_follow" in channel_json:
            struct.auto_follow = channel_json["auto_follow"]

        return


    # ======================================================================== #

    @staticmethod
    def load(channel_json:dict, **kwargs) -> Self:
        channel_type:ChannelType = ChannelType(channel_json["type"])
        match channel_type:
            case ChannelType.BOOL:
                return DsonChannelBool.load(channel_json, **kwargs)
            case ChannelType.FLOAT:
                return DsonChannelFloat.load(channel_json, **kwargs)
            case _:
                raise NotImplementedError(channel_type)


    # ======================================================================== #

    def get_value(self:Self) -> Any:
        raise NotImplementedError


# ============================================================================ #
#                                                                              #
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


    @staticmethod
    def load(channel_json:dict, default_value:bool=False) -> Self:

        struct:Self = DsonChannelBool()
        DsonChannel._create_basic(struct, channel_json)

        # Default value
        if "value" in channel_json:
            struct.default_value = channel_json["value"]
        else:
            struct.default_value = default_value

        # Current value
        if "current_value" in channel_json:
            struct.current_value = channel_json["current_value"]
        else:
            struct.current_value = struct.default_value

        # Minimum value
        if "min" in channel_json:
            struct.minimum_value = channel_json["min"]

        # Maximum value
        if "max" in channel_json:
            struct.maximum_value = channel_json["max"]

        # Clamp values
        if "clamped" in channel_json:
            struct.clamp_values = channel_json["clamped"]

        # Value increment
        if "step_size" in channel_json:
            struct.value_increment = channel_json["step_size"]

        # Can use image map
        if "mappable" in channel_json:
            struct.can_use_image_map = channel_json["mappable"]

        return struct


    def __bool__(self:Self) -> bool:
        return bool(self.current_value)


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


    @staticmethod
    def load(channel_json:dict, default_value:float=0.0) -> Self:

        struct:Self = DsonChannelFloat()
        DsonChannel._create_basic(struct, channel_json)

        # Default value
        if "value" in channel_json:
            struct.default_value = channel_json["value"]
        else:
            struct.default_value = default_value

        # Current value
        if "current_value" in channel_json:
            struct.current_value = channel_json["current_value"]
        else:
            struct.current_value = struct.default_value

        # Minimum value
        if "min" in channel_json:
            struct.minimum_value = channel_json["min"]

        # Maximum value
        if "max" in channel_json:
            struct.maximum_value = channel_json["max"]

        # Clamp values
        if "clamped" in channel_json:
            struct.clamp_values = channel_json["clamped"]

        # Display as percent
        if "display_as_percent" in channel_json:
            struct.display_as_percent = channel_json["display_as_percent"]

        # Value increment
        if "step_size" in channel_json:
            struct.value_increment = channel_json["step_size"]

        # Can use image map
        if "mappable" in channel_json:
            struct.can_use_image_map = channel_json["mappable"]

        return struct


    def __float__(self:Self) -> float:
        return float(self.current_value)


    def get_value(self:Self) -> float:
        return float(self)



# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonChannelVector:

    x:DsonChannelFloat = None
    y:DsonChannelFloat = None
    z:DsonChannelFloat = None


    @staticmethod
    def load(json_array:list[dict], default_x:float=0.0, default_y:float=0.0, default_z:float=0.0) -> Self:

        x_dict:dict = None
        y_dict:dict = None
        z_dict:dict = None

        if json_array:
            for item in json_array:
                channel_id:str = item["id"].upper()
                if channel_id == 'X':
                    x_dict = item
                if channel_id == 'Y':
                    y_dict = item
                if channel_id == 'Z':
                    z_dict = item

        vector:Self = DsonChannelVector()
        vector.x = DsonChannelFloat.load(x_dict, default_value=default_x)
        vector.y = DsonChannelFloat.load(y_dict, default_value=default_y)
        vector.z = DsonChannelFloat.load(z_dict, default_value=default_z)

        return vector


    def __iter__(self:Self) -> Iterator:
        return iter([ float(self.x), float(self.y), float(self.z) ])
