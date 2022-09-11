"""
Copyright 2021 Rob Weber

This file is part of omni-epd

omni-epd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import importlib.util
import sys

# config file name
CONFIG_FILE = "omni-epd.ini"

# config option sections
EPD_CONFIG = "EPD"
IMAGE_DISPLAY = "Display"
IMAGE_ENHANCEMENTS = "Image Enhancements"


# helper method to check if a module is (or can be) installed
def check_module_installed(moduleName):
    result = False

    # check if the module is already loaded, or can be loaded
    if (moduleName in sys.modules or (importlib.util.find_spec(moduleName)) is not None):
        result = True

    return result
