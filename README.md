# Blender 2.93.1. Add-on File Conversion Helper (obj to fbx)
Blender 2.93.1. Add-on that can help you convert multiple objs to a single fbx with multiple sub-components. I modified the batch wavefront import [add-on 'p2or' wrote](https://blenderartists.org/t/how-to-import-multiple-objects-at-one-time/558614/7) so that it removes the default cube, camera and light and sets the model at the world origin ready to be exported as fbx. Surprisingly, Blender does not natively support multiple obj import so I had to build on the existing add-on. (Even if you select multiple files and click the import button, only one file will be imported.) The models I had to work with came with an offset, and it was not located at (0,0,0) although it was not located at the center, so what set_origin function fixes that. 

You need to do step 1 to 4 only once to automate the process. 
1. Install Blender 2.93.1 and open the software
2. Download the 'FileConversionHelper.py' file
3. Open Blender
4. Inside Blender, go to Edit → Preferences → Add-ons →  Install  → Click 'FileConversionHelper.py' from the file browser pop-up → Enable the addon by clicking the check mark square in front of the name Import-Export:FileConversionHelper
5. Go to File → Import → Multiple OBJs → Shift+click multiple obj files you want to import from the file browser pop-up. Wait until you see it at the origin (0,0,0) of the scene 
6. Go to File →  Export  → FBX (.fbx). Choose the location and name of the fbx file. 
