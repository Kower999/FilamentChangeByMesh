# FilamentChangeByMesh
Post-process script to add g-code for filament change based on mesh-color setting instead of layer based approach.

INSTALATION

1. To install this script just copy file `FilamentChangeByMesh.py` into corresponding folder of cura.

It should be something like this:

`C:\Users\(yourusername)\AppData\Roaming\cura\(version)\scripts\`

After you copied the script don't forget to restart Cura.

2. To activate script add it through Extensions\Post Processing\Modify G-Code menu.

3. Add script by button and find it by name "Filament Change By Mesh".

4. Enable plugin and set your color->mesh pairs corresponding to your needs. You can set more than one mesh to same color. Just separate mesh names(stl file names) by comma ","

5. Enjoy multicolored prints with single extruder printers ;)

Notes:
- by mesh i mean separate stl files (objets/models)

