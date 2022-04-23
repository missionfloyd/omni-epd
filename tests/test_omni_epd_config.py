import unittest
import os
import time
import json
import glob
import pytest
from shutil import copyfile
from omni_epd import EPDNotFoundError, EPDConfigurationError
from omni_epd import displayfactory
from omni_epd.virtualepd import VirtualEPD
from omni_epd.conf import IMAGE_DISPLAY, CONFIG_FILE

TEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))


class TestomniEpd(unittest.TestCase):
    goodEpd = "omni_epd.mock"  # this should always be a valid EPD
    badEpd = "omni_epd.bad"  # this is not a valid EPD
    badConfig = 'bad_conf.ini'  # name of invalid configuration file

    def _delete_ini(self):
        fileList = glob.glob(os.path.join(os.getcwd(), "*.ini"))

        for f in fileList:
            # don't bother catching errors - just let it fail out
            os.remove(f)

    @pytest.fixture(autouse=True)
    def run_before_and_after_tests(self):
        # clean up any files left over from previous tests
        self._delete_ini()

        yield

        # clean up any files made during this test
        self._delete_ini()

    def setup_config(self, source_config_file_name, target_config_file_name):
        copyfile(os.path.join(TEST_PATH, 'ini', source_config_file_name), os.path.join(os.getcwd(), target_config_file_name))
        time.sleep(1)

    def test_supported_diplays(self):
        """
        Test that displays can be loaded
        """
        drivers = displayfactory.list_supported_displays()

        assert len(drivers) > 0

    def test_loading_error(self):
        """
        Confirm error thrown if an invalid name passed to load function
        """
        self.assertRaises(EPDNotFoundError, displayfactory.load_display_driver, self.badEpd)

    def test_loading_success(self):
        """
        Confirm a good display can be loaded and extends VirtualEPD
        """
        epd = displayfactory.load_display_driver(self.goodEpd)

        assert isinstance(epd, VirtualEPD)

    def test_global_conf(self):
        """
        Test loading of omni-epd.ini config file
        Once loaded confirm options from file exist within display class config
        Also confirm values not in the config file aren't changed from defaults
        """
        # set up a global config file
        self.setup_config(CONFIG_FILE, CONFIG_FILE)

        epd = displayfactory.load_display_driver(self.goodEpd)

        assert epd._config.has_option(IMAGE_DISPLAY, 'rotate')
        assert epd._config.getfloat(IMAGE_DISPLAY, 'rotate') == 90

        # test that mode is default
        assert epd.mode == 'bw'

    def test_device_config(self):
        """
        Test that when both omni-epd.ini file is present and device specific INI present
        that the device specific config overrides options in global config
        """
        deviceConfig = self.goodEpd + ".ini"

        # set up a global config file and device config
        self.setup_config(CONFIG_FILE, CONFIG_FILE)
        self.setup_config(deviceConfig, deviceConfig)

        epd = displayfactory.load_display_driver(self.goodEpd)

        # device should override global
        assert epd._config.has_option(IMAGE_DISPLAY, 'flip_horizontal')
        self.assertFalse(epd._config.getboolean(IMAGE_DISPLAY, 'flip_horizontal'))

        # test mode and palette configurations
        assert epd.mode == 'palette'
        assert len(json.loads(epd._get_device_option('palette_filter', "[]"))) == 5  # confirms custom palette will be loaded

    def test_load_device_from_conf(self):
        """
        Test that a device will load when given the type= option in the omni-epd.ini file
        and no args to load_display_driver()
        """
        deviceConfig = self.goodEpd + ".ini"

        # set up a global config file
        self.setup_config(CONFIG_FILE, CONFIG_FILE)
        self.setup_config(deviceConfig, deviceConfig)

        # should load driver from ini file without error
        epd = displayfactory.load_display_driver()

        # test that driver specific file also loaded
        assert epd._config.has_option(IMAGE_DISPLAY, 'flip_horizontal')
        self.assertFalse(epd._config.getboolean(IMAGE_DISPLAY, 'flip_horizontal'))

        # should attempt to load passed in driver, and fail, instead of one in conf file
        self.assertRaises(EPDNotFoundError, displayfactory.load_display_driver, self.badEpd)

    def test_configuration_error(self):
        """
        Confirm that an EPDConfigurationError is thrown by passing a bad mode value
        to a display
        """
        deviceConfig = self.goodEpd + ".ini"

        # copy bad config file to be loaded
        self.setup_config(self.badConfig, deviceConfig)

        # load the display driver, shoudl throw EPDConfigurationError
        self.assertRaises(EPDConfigurationError, displayfactory.load_display_driver, self.goodEpd)
