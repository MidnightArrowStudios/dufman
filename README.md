# What is DUFMan?
DUFMan (short for **D**SON **U**ser **F**ile **Man**ager) is a Python library for loading Daz Studio's DSF and DUF files in third-party applications. It parses the DSON file format, which is a flavor of JSON, validates the data contained inside it, and stores that data in struct-like dataclasses which can be passed around an importer as an opaque pointer.

It is written to be application-agnostic, but it is mainly targeted at Blender and follows Blender conventions.

The library is currently in an _extremely_ early state. It is neither feature-complete nor fit for production.

# How does it work?
The DSON format stores DSF files inside a content directory with a "/data/" folder as its root. Assets refer to other assets using URLs relative to the root. To simplify the parsing process, DUFMan is designed to emulate this. To access data, the user supplies a URL and an asset ID joined with the pound sign (#). This is identical to the way a DSON file stores references to other assets, allowing the same functionality to be shared between users and the automated parser.

The DSON format defines six types of assets: geometry, images, materials, modifiers, nodes, and UV sets. Currently, DUFMan can load (with varying degrees of completeness) geometry, modifiers, nodes, and UV sets. It also has the ability to encapsulate a scene and query it for information, although this is currently very limited.

More functionality will be added as development continues.

# How do I use it in Blender?
Sample script files for Blender's Python API are available at https://github.com/MidnightArrowStudios/duf-brewery. They are kept separate in order to comply with the terms of Blender's GPL license.

# Is "DUFMan" named after what I think it's named after?
[Oh, yeah!](https://simpsonswiki.com/wiki/Duffman)
