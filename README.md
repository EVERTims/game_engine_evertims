# Blender (BGE) addon of the EVERTims project

Holds the files related to the Blender addon associated with the EVERTims framework. EVERTims is a real-time raytracing engine dedicated to architectural and VR auralization (simulates acoustic propagation in a given environment for life-like soundscapes). The addon provides a GUI pannel (in Blender) with tools to create an EVERTims scene.

Integrated to this addon is a pyton module, used in the Blender Game Engine (BGE) to communicate with the EVERTims client (main program that handles room acoustics simulation). While the virtual room is rendered in the BGE, the python module communicates the room geometry and materials to the EVERTims client along with Sources and Listeners current position/orientation. An additional debug option allows to see raytracing results as rays drawn in the BGE scene. See the [EVERTims website] for more details.

## How to use: Addon + underlying python module

Install the addon as you would any Blender addon. Once activated (look for EVERTims in the addon preferences), the GUI can be found in the 3D View > Toolbox under the flag ``EVERTims``. Creating a template scene is all that's required (making sure the EVERTims client is up and running) before running the BGE (check the ``Draw rays in BGE`` option for visual feedback on EVERTims raytracing). Detailed install / how-to-use instructions can be found on the [EVERTims website].

## How to use: Standalone python module

Assuming you want complete control over the module behavior (and you're willing to dig into python code), you may discard the whole content of this folder and simply copy/paste both ``assets/evertims-standalone.blend`` file and ``assets/scripts`` folder in your new project folder. Launch the EVERTims client (main program that handles room acoustics simulation), open the ``evertims-standalone.blend`` and run the BGE. Make sure that the network parameters defined in the ``scripts/run-evertims.py`` script match the ones defined in the EVERTims client. Once the whole thing runs, feel free to dig from the ``scripts/run-evertims.py`` script to the ``scripts/evertims`` module itself. See the [EVERTims website] for a detailed tutorial.

[EVERTims website]: (https://evertims.github.io/website)
