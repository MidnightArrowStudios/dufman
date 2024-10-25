# What is DUFMan?
DUFMan (short for **D**SON **U**ser **F**ile **Man**ager) is a Python library for loading Daz Studio's DSF and DUF files in third-party applications. It parses the DSON file format, which is a flavor of JSON, validates the data contained inside it, and stores that data in struct-like dataclasses which can be passed around an importer as an opaque pointer.

It is written to be application-agnostic, but it is mainly targeted at Blender and follows Blender conventions.

The library is currently in an _extremely_ early state. It is neither feature-complete nor fit for production.

# How do I use it?
The DSON format stores DSF files inside a content directory with a "/data/" folder as its root. Assets refer to other assets using URLs relative to the root. To simplify the parsing process, DUFMan is designed to emulate this. To access data, the user supplies a URL and an asset ID joined with the pound sign (#). This is identical to the way a DSON file stores references to other assets, allowing the same functionality to be shared between users and the automated parser.

To extract an asset, first add a content directory.

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

This struct can then be passed to your application-specific code to create a native representation of the asset.

The DSON format defines six types of assets: geometry, images, materials, modifiers, nodes, and UV sets. Currently, DUFMan can load (with varying degrees of completeness) geometry, modifiers, nodes, and UV sets. Advanced functionality, like the ability to encapsulate DSON scenes as an object and query them to construct a scene tree, will follow as development continues.

# Is "DUFMan" named after what I think it's named after?
[Oh, yeah!](https://simpsonswiki.com/wiki/Duffman)
