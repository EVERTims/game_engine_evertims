# Blender (BGE) module of the EVERTims project

Holds the files related to EVERTims Blender module: a pyton module used in the Blender Game Engine (BGE) to communicate with the EVERTims client (main program that handles room acoustics simulation). While the virtual room is rendered in the BGE, the python module communicates the room geometry and materials to the EVERTims client along with Sources and Listeners current position/orientation. An additional debug option allows to see raytracing results as rays drawn in the BGE scene. See the [EVERTims website] for more details.

## How to use

After launching the EVERTims client (main program that handles room acoustics simulation), open the evertMain.blend and run the BGE. Make sure that the network parameters defined in the ./scripts/run-evertims.py script match the ones defined in the EVERTims client.

## How to re-use

Copy the ./scripts/evertims/ python module in your new Blender project folder, use it as shown in ./scripts/run-evertims.py. See the [EVERTims website] for a detailed tutorial.

[EVERTims website]: (https://evertims.github.io/website)
