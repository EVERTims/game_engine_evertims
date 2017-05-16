# Blender addon of the EVERTims project

Add the EVERTims GUI panel to Blender tool bar, used to setup EVERTims scenes for real-time auralization during both room design (in edit mode) and exploration (using the blender game engine). See the [EVERTims website](https://evertims.github.io) for further insight on the framework.


## Install

See the Installation section of the website.


## Architecture

The addon is a wrapper around the ```evertims``` python module. The module holds classes to communicate room, listener(s) and source(s) properties (geometry, materials, position, etc.) to the EVERTims ray-tracing client (main program running image sources simulation, see website). The addon allows to use the module for real-time auralization of a Blender scene during its design (edit mode) and exploration (BGE). 

addon wrapper files:
```
├── __init__.py
├── operators.py
└── ui.py
```

```evertims``` module files:
```
├── assets
│   ├── evertims-assets.blend (example how to use scene + ready to import assets)
│   ├── scripts
│   │   ├── evertims
│   │   │   ├── __init__.py
│   │   │   └── evertClass.py
│   │   └── run-evertims.py (example how to use bge script)
```

## How to use: Standalone python module

The addon/wrapper can be discarded for BGE only auralization. Copy/paste both ``assets/evertims-standalone.blend`` file and ``assets/scripts`` folder in a new project folder. Launch the EVERTims client (main program that handles room acoustics simulation), open the ``evertims-standalone.blend``, and run the BGE. Make sure that the network parameters defined in the ``scripts/run-evertims.py`` script match the ones defined in the EVERTims client.
