# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module which provides a way to inspect data during loading.

Struct callbacks take the 'Any' type because attempts to load the actual
struct dataclasses lead to circular import errors.
"""

from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple


# ============================================================================ #

class _Callback(NamedTuple):
    """Struct-like object for storing an observer's properties."""
    function:Callable
    userdata:dict


# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_dson_file_opened:list[_Callback] = []

def register_on_dson_file_opened(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a DSON file is opened as a plaintext document."""
    _on_dson_file_opened.append(_Callback(callback, userdata))
    return

def _dson_file_opened(absolute_filepath:Path, dson_file:str) -> None:
    for callback in _on_dson_file_opened:
        callback.function(callback.userdata, absolute_filepath, dson_file)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_dson_file_loaded:list[_Callback] = []

def register_on_dson_file_loaded(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a DSON file is instantiated as a DSON dictionary."""
    _on_dson_file_loaded.append(_Callback(callback, userdata))
    return

def _dson_file_loaded(absolute_filepath:Path, dson_file:dict) -> None:
    for callback in _on_dson_file_loaded:
        callback.function(callback.userdata, absolute_filepath, dson_file)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_geometry_struct_created:list[_Callback] = []

def register_on_geometry_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a geometry asset is instantiated from a DSON library."""
    _on_geometry_struct_created.append(_Callback(callback, userdata))
    return

def _geometry_struct_created(struct:"DsonGeometry", geometry_json:dict) -> None:
    for callback in _on_geometry_struct_created:
        callback.function(callback.userdata, struct, geometry_json)
    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_modifier_struct_created:list[_Callback] = []

def register_on_modifier_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a modifier asset is instantiated from a DSON library."""
    _on_modifier_struct_created.append(_Callback(callback, userdata))
    return

def _modifier_struct_created(struct:"DsonModifier", modifier_json:dict) -> None:
    for callback in _on_modifier_struct_created:
        callback.function(callback.userdata, struct, modifier_json)
    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_node_struct_created:list[_Callback] = []

def register_on_node_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a node asset is instantiated from a DSON library."""
    _on_node_struct_created.append(_Callback(callback, userdata))
    return

def _node_struct_created(struct:"DsonNode", node_json:dict) -> None:
    for callback in _on_node_struct_created:
        callback.function(callback.userdata, struct, node_json)
    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_uv_set_struct_created:list[_Callback] = []

def register_on_uv_set_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a UV Set asset is instantiated from a DSON library."""
    _on_uv_set_struct_created.append(_Callback(callback, userdata))
    return

def _uv_set_struct_created(struct:"DsonUVSet", uv_set_json:dict) -> None:
    for callback in _on_uv_set_struct_created:
        callback.function(callback.userdata, struct, uv_set_json)
    return
