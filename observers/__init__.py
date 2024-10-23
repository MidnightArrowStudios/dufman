# ============================================================================ #
"""Module which provides a way to inspect data during loading."""

from collections.abc import Callable
from pathlib import Path

from ..structs.geometry import DsonGeometry
from ..structs.modifier import DsonModifier
from ..structs.node import DsonNode
from ..structs.uv_set import DsonUVSet

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_dson_file_opened:list[tuple[Callable, dict]] = []

def register_on_dson_file_opened(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a DSON file is opened as a plaintext document."""
    _on_dson_file_opened.append((callback, userdata))
    return

def _dson_file_opened(url_path:Path, dson_file:str) -> None:
    for entry in _on_dson_file_opened:
        entry[0](entry[1], url_path, dson_file)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_dson_file_loaded:list[tuple[Callable, dict]] = []

def register_on_dson_file_loaded(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a DSON file is instantiated as a DSON dictionary."""
    _on_dson_file_loaded.append((callback, userdata))
    return

def _dson_file_loaded(url_path:Path, dson_file:dict) -> None:
    for entry in _on_dson_file_loaded:
        entry[0](entry[1], url_path, dson_file)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_geometry_struct_created:list[tuple[Callable, dict]] = []

def register_on_geometry_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a geometry asset is instantiated from a DSON library."""
    _on_geometry_struct_created.append((callback, userdata))
    return

def _geometry_struct_created(struct:DsonGeometry, library:dict, instance:dict=None) -> None:
    for entry in _on_geometry_struct_created:
        entry[0](entry[1], struct, library, instance)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_modifier_struct_created:list[tuple[Callable, dict]] = []

def register_on_modifier_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a modifier asset is instantiated from a DSON library."""
    _on_modifier_struct_created.append((callback, userdata))
    return

def _modifier_struct_created(struct:DsonModifier, library:dict, instance:dict=None) -> None:
    for entry in _on_modifier_struct_created:
        entry[0](entry[1], struct, library, instance)
    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_node_struct_created:list[tuple[Callable, dict]] = []

def register_on_node_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a node asset is instantiated from a DSON library."""
    _on_node_struct_created.append((callback, userdata))
    return

def _node_struct_created(struct:DsonNode, library:dict, instance:dict=None) -> None:
    for entry in _on_node_struct_created:
        entry[0](entry[1], struct, library, instance)
    return

# ============================================================================ #
#                                                                              #
# ============================================================================ #

_on_uv_set_struct_created:list[tuple[Callable, dict]] = []

def register_on_uv_set_struct_created(callback:Callable, userdata:dict) -> None:
    """Registers a callback after a UV Set asset is instantiated from a DSON library."""
    _on_uv_set_struct_created.append((callback, userdata))
    return

def _uv_set_struct_created(struct:DsonUVSet, library:dict, instance:dict=None) -> None:
    for entry in _on_uv_set_struct_created:
        entry[0](entry[1], struct, library, instance)
    return
