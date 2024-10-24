# What is DUFMan?
DUFMan (short for **D**SON **U**ser **F**ile **Man**ager) is a Python library designed to act as a base for bridges between Daz Studio and third-party applications. It parses data from Daz's DSON format, which is really a subset of JSON, and stores it as an intermediate representation consisting of struct-like dataclasses for easy access.

Although written to be application-agnostic, it is mainly targeted at Blender and follows Blender's standards.

It is currently in an _extremely_ early state and is not at all fit for production.

# How do I use it?
Like the DSON format itself, DUFMan operates on URLs relative to Daz Studio's "/data/" directory. This simplifies the file-parsing process, since the way the user accesses data is the same as the way a DSON file itself accesses data. Daz Studio assets come in six types: geometry, images, materials, modifiers, nodes, and UV sets. Currently, DUFMan can (barring bugs and errors) load geometry, modifiers, nodes, and UV sets. The general process for all six library data types is the same.

First, add a content directory.

```
from dufman.file import add_content_directory
add_content_directory("C:/My/Content/Directory/Daz 3D")
```

Then use a relative URL to create a struct-like wrapper object around the DSON data.

```
from dufman.create.geometry import create_geometry_struct
asset_url:str = "/data/DAZ 3D/Genesis 8/Male/Genesis8Male.dsf#geometry"
struct:DsonGeometry = create_geometry_struct(asset_url)
```

The DsonGeometry struct can then be passed to your application-specific code to create a mesh object.

More advanced functionality, like parsing DSON scenes and encapsulating them into objects, will follow as development continues.

# Is "DUFMan" named after what I think it's named after?
[Oh, yeah!](https://simpsonswiki.com/wiki/Duffman)
