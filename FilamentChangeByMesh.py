# Copyright (c) 2021 Ultimaker B.V.
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.

# Modification 06.09.2020
# add checkbox, now you can choose and use configuration from the firmware itself.

# Modification 30.01.2023
# script modified to support filament change based on mesh-color settings

from typing import List
from ..Script import Script

from UM.Logger import Logger
from UM.Application import Application #To get the current printer's settings.


class FilamentChangeByMesh(Script):

    _layer_keyword = ";LAYER:"

    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Filament Change By Mesh",
            "key": "FilamentChangeByMesh",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "plugin_enabled":
                {
                    "label": "Plugin enabled",
                    "description": "Use the plugin to postprocess generated G-code by adding filament change G-code when specified mesh is being printed.",
                    "type": "bool",
                    "default_value": false
                },
                "color1_meshes":
                {
                    "label": "Color 1 Meshes",
                    "description": "At what mesh should color change occur. This will be before each color change occurs. Specify multiple meshes of this color with a comma. Enter only file name without extension.",
                    "unit": "",
                    "type": "str",
                    "default_value": ""
                },
                "color2_meshes":
                {
                    "label": "Color 2 Meshes",
                    "description": "At what mesh should color change occur. This will be before each color change occurs. Specify multiple meshes of this color with a comma. Enter only file name without extension.",
                    "unit": "",
                    "type": "str",
                    "default_value": ""
                },
                "color3_meshes":
                {
                    "label": "Color 3 Meshes",
                    "description": "At what mesh should color change occur. This will be before each color change occurs. Specify multiple meshes of this color with a comma. Enter only file name without extension.",
                    "unit": "",
                    "type": "str",
                    "default_value": ""
                },
                "color4_meshes":
                {
                    "label": "Color 4 Meshes",
                    "description": "At what mesh should color change occur. This will be before each color change occurs. Specify multiple meshes of this color with a comma. Enter only file name without extension.",
                    "unit": "",
                    "type": "str",
                    "default_value": ""
                },
                "firmware_config":
                {
                    "label": "Use Firmware Configuration",
                    "description": "Use the settings in your firmware, or customise the parameters of the filament change here.",
                    "type": "bool",
                    "default_value": false
                },
                "initial_retract":
                {
                    "label": "Initial Retraction",
                    "description": "Initial filament retraction distance. The filament will be retracted with this amount before moving the nozzle away from the ongoing print.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 30.0,
                    "enabled": "not firmware_config"
                },
                "later_retract":
                {
                    "label": "Later Retraction Distance",
                    "description": "Later filament retraction distance for removal. The filament will be retracted all the way out of the printer so that you can change the filament.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 300.0,
                    "enabled": "not firmware_config"
                },
                "x_position":
                {
                    "label": "X Position",
                    "description": "Extruder X position. The print head will move here for filament change.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "enabled": "not firmware_config"
                },
                "y_position":
                {
                    "label": "Y Position",
                    "description": "Extruder Y position. The print head will move here for filament change.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "enabled": "not firmware_config"
                },
                "z_position":
                {
                    "label": "Z Position (relative)",
                    "description": "Extruder relative Z position. Move the print head up for filament change.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": 0
                },
                "retract_method":
                {
                    "label": "Retract method",
                    "description": "The gcode variant to use for retract.",
                    "type": "enum",
                    "options": {"U": "Marlin (M600 U)", "L": "Reprap (M600 L)"},
                    "default_value": "U",
                    "value": "\\\"L\\\" if machine_gcode_flavor==\\\"RepRap (RepRap)\\\" else \\\"U\\\"",
                    "enabled": "not firmware_config"
                },                    
                "machine_gcode_flavor":
                {
                    "label": "G-code flavor",
                    "description": "The type of g-code to be generated. This setting is controlled by the script and will not be visible.",
                    "type": "enum",
                    "options":
                    {
                        "RepRap (Marlin/Sprinter)": "Marlin",
                        "RepRap (Volumetric)": "Marlin (Volumetric)",
                        "RepRap (RepRap)": "RepRap",
                        "UltiGCode": "Ultimaker 2",
                        "Griffin": "Griffin",
                        "Makerbot": "Makerbot",
                        "BFB": "Bits from Bytes",
                        "MACH3": "Mach3",
                        "Repetier": "Repetier"
                    },
                    "default_value": "RepRap (Marlin/Sprinter)",
                    "enabled": "false"
                }
            }
        }"""

    ##  Copy machine name and gcode flavor from global stack so we can use their value in the script stack
    def initialize(self) -> None:
        super().initialize()

        global_container_stack = Application.getInstance().getGlobalContainerStack()
		
        if global_container_stack is None or self._instance is None:
            return

        for key in ["machine_gcode_flavor"]:
            self._instance.setProperty(key, "value", global_container_stack.getProperty(key, "value"))

    def execute(self, data: List[str]):
        """Inserts the filament change g-code at specific starting locations of specified meshes and their color index if its needed.

        :param data: A list of layers of g-code.
        :return: A similar list, with filament change commands inserted.
        """
        initial_retract = self.getSettingValueByKey("initial_retract")
        later_retract = self.getSettingValueByKey("later_retract")
        x_pos = self.getSettingValueByKey("x_position")
        y_pos = self.getSettingValueByKey("y_position")
        z_pos = self.getSettingValueByKey("z_position")
        firmware_config = self.getSettingValueByKey("firmware_config")

        all_meshes = []

        color1_meshes_str = self.getSettingValueByKey("color1_meshes")
        color1_meshes = color1_meshes_str.split(",")
        all_meshes.append(color1_meshes)

        color2_meshes_str = self.getSettingValueByKey("color2_meshes")
        color2_meshes = color2_meshes_str.split(",")
        all_meshes.append(color2_meshes)

        color3_meshes_str = self.getSettingValueByKey("color3_meshes")
        color3_meshes = color3_meshes_str.split(",")
        all_meshes.append(color3_meshes)

        color4_meshes_str = self.getSettingValueByKey("color4_meshes")
        color4_meshes = color4_meshes_str.split(",")
        all_meshes.append(color4_meshes)

        actual_color = 0.

        color_change = "\nM600"

        if not firmware_config:
            if initial_retract is not None and initial_retract > 0.:
                color_change = color_change + (" E%.2f" % initial_retract)

            if later_retract is not None and later_retract > 0.:
                # Reprap uses 'L': https://reprap.org/wiki/G-code#M600:_Filament_change_pause
                # Marlin uses 'U' https://marlinfw.org/docs/gcode/M600.html
                retract_method = self.getSettingValueByKey("retract_method")
                color_change = color_change + (" %s%.2f" % (retract_method, later_retract))

            if x_pos is not None:
                color_change = color_change + (" X%.2f" % x_pos)
                
            if y_pos is not None:
                color_change = color_change + (" Y%.2f" % y_pos)
                
            if z_pos is not None and z_pos > 0.:
                color_change = color_change + (" Z%.2f" % z_pos)

        color_change = color_change + " ; Generated by FilamentChangeByMesh plugin - "

        if self.getSettingValueByKey("plugin_enabled"):
            for layer in data:
                layer_index = data.index(layer)
                lines = layer.split("\n")
                for line in lines:
                    if line.startswith(";MESH:") and not line.startswith(";MESH:NONMESH"):
                        file_name = line[6:]
                        file_name_parts = file_name.rsplit(".",1)
                        mesh_to_find = file_name_parts[0]
                        mesh_color_found = 0.
                        for color_meshes in all_meshes:
                            if mesh_to_find in color_meshes:
                                mesh_color_found = all_meshes.index(color_meshes) + 1
                        if mesh_color_found > 0. and not actual_color == mesh_color_found:
                            if actual_color > 0.:
                                line_index = lines.index(line)
                                lines[line_index] = lines[line_index] + color_change + "actual color = " + str(actual_color) + "; color to load = " + str(mesh_color_found)
                            actual_color = mesh_color_found
                data[layer_index] = "\n".join(lines)
        return data
