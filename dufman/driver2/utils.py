# stdlib
from typing import Any

# dufman
from dufman.structs.channel import DsonChannel
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode
from dufman.url import AssetAddress


def get_channel_object(asset:Any, property_url:str) -> DsonChannel:
    """Return the DsonChannel object from an asset struct."""

    # Validate URL
    address:AssetAddress = AssetAddress.from_url(property_url)
    if not address.property_path:
        raise ValueError("URL does not contain enough info to locate channel.")

    # DsonModifier
    if isinstance(asset, DsonModifier):
        if address.property_path == asset.channel.channel_id:
            return asset.channel
        raise NotImplementedError(address.property_path)

    # DsonNode
    elif isinstance(asset, DsonNode):
        match address.property_path:

            # Center point
            case "center_point/x":
                return asset.center_point.x
            case "center_point/y":
                return asset.center_point.y
            case "center_point/z":
                return asset.center_point.z

            # End point
            case "end_point/x":
                return asset.end_point.x
            case "end_point/y":
                return asset.end_point.y
            case "end_point/z":
                return asset.end_point.z

            # Translation
            case "translation/x":
                return asset.translation.x
            case "translation/y":
                return asset.translation.y
            case "translation/z":
                return asset.translation.z

            # Orientation
            case "orientation/x":
                return asset.orientation.x
            case "orientation/y":
                return asset.orientation.y
            case "orientation/z":
                return asset.orientation.z

            # Rotation
            case "rotation/x":
                return asset.rotation.x
            case "rotation/y":
                return asset.rotation.y
            case "rotation/z":
                return asset.rotation.z

            # Scale
            case "scale/general":
                return asset.general_scale
            case "scale/x":
                return asset.scale.x
            case "scale/y":
                return asset.scale.y
            case "scale/z":
                return asset.scale.z

            # Unknown
            case _:
                raise NotImplementedError(address.property_path)

    return None