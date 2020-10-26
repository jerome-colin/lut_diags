"""
Collection of LUT objects definitions
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.1.0"

import os, sys
import numpy as np
import Luts.Lut as lut
import Luts.utilities as utl
from xml.dom import minidom


class Collection:
    """
    Superclass for TxtCollection (from SOS wrapper) and HdrCollection (CS format). A Collection is primarily a dictionary of LUT objects referenced by their wavelength, with additional meta-data.
    The creation of the Collection is agnostic to the actual content of 'path', and gathers meta-data and binary
    values automatically.

    Public methods:
        load: create a collection of LUT objects as dict in self.luts

    Attributes:
        sensor (str): name of sensor found from filename
        aerosol (str): name of aerosol type from filename
        bands (numpy.array): vector of wavelengths from filename
        prop (str): prop from filename
        luts (dict): dictionary of Lut objects referenced by their wavelength

    Usage example:
        venus_refl = Collection("tests/VENUS_zerodeuxSansAbsorption", var='refl')
    """

    def __init__(self, path, var, log=None, verbose=True):
        """

        :param path: mandatory path to LUT directory
        :param var: name of variable, eg. 'albedo'
        :param log: if None then default logfile name, else not yet implemented
        :param verbose: defaults to True to print to sdt_out
        """
        self.path = path
        self.var = var
        self.verbose = verbose

        # Init a logger
        if log is None:
            self.logger = utl.get_logger("Luts")

        # Load attributes as str, int and dict of Lut
        self.sensor, self.aerosol, self.prop, self.luts = self._load(var)

    def _load(self, var):
        # Overridden by child classes
        pass

    @staticmethod
    def _get_dir_content(path):
        """
        Return a list of elements in a given path
        :return: a list
        """
        try:
            items = os.listdir(path)
            if len(items) == 0:
                print("ERROR: not file found in %s" % path)
                sys.exit(1)
            else:
                return items
        except FileNotFoundError as e:
            print("ERROR: %s" % e)
            sys.exit(1)

    @staticmethod
    def _get_dir_path(path):
        """
        Add a trailing '/' and check if str is actually a directory
        :param path: a string
        :return: a string
        """
        path.strip()
        if path[-1] != '/':
            path += '/'

        if os.path.isdir(path):
            return path
        else:
            print("ERROR: %s is not a directory to Txt collection of LUTs" % path)
            sys.exit(1)


class TxtCollection(Collection):
    def __init__(self, path, var, log=None, verbose=True):
        super().__init__(path, var, log=None, verbose=True)

    def _load(self, var):
        # clean-up path and check if it's actually a directory
        path = self._get_dir_path(self.path)

        # get directory content
        items = self._get_dir_content(path)

        # get a list of bands by wavelengths (nm)
        bands = self._get_bands(path, items)

        # assumption on the types of LUTs to expect in this collection
        lut_types = ['albedo', 'lut_inv_CS', 'lut_inv', 'refl', 'Tdif', 'Tdir']

        # get basic information
        sensor, aerosol, prop = self._get_infos(path, items, lut_types)

        # log
        self.logger.info("This collection if for %s with aerosol type %s with prop set to %3.2f" % (
            sensor, aerosol, float(prop)))
        self.logger.info("Found %i bands for wavelengths %s" % (len(bands), str(bands)))

        # verbosity
        if self.verbose:
            print("This collection if for %s with aerosol type %s with prop set to %3.2f" % (
                sensor, aerosol, float(prop)))
            print("Found %i bands for wavelengths %s" % (len(bands), str(bands)))

        # load var if defined
        return sensor, aerosol, prop, self._get_luts(var, path, items, bands)

    def _get_bands(self, path, items):
        """
        Return an array of band wavelengths in LUT collection
        :param items: list of files from _discover
        :return: a numpy array
        """
        band_list = []
        for item in items:
            if os.path.isfile(path + item) and (item[-3:] == "txt" or item[-3:] == "TXT"):
                band_list.append(item.split('_')[-1].split('.')[0])

            if os.path.isfile(path + item) and item[-3:] == "HDR":
                fhdr_meta = minidom.parse(path + item)

        band_arr = np.array(band_list)
        return np.unique(band_arr)

    def _get_infos(self, path, items, lut_types):
        """
        Return the name of the sensor from the filename
        :return: a string of sensor, aerosol, proportion
        """
        for item in items:
            if os.path.isfile(path + item) and item.split('_')[0] == lut_types[0]:
                return item.split('_')[2], item.split('_')[3], item.split('_')[5]
                break

            if os.path.isfile(self.path + item) and item[-3:] == "HDR":
                fhdr_meta = minidom.parse(path + item)
                return fhdr_meta.getElementsByTagName("Mission")[0].firstChild.nodeValue, "Unknown", 0
                break

    def _get_luts(self, var, path, items, bands):
        """
        Load LUT files in LUT object collection
        :return: an array of LUT objects
        """
        luts = dict()

        for item in items:
            if os.path.isfile(path + item) and (item[-3:] == "txt" or item[-3:] == "TXT"):
                for band in bands:
                    if item.split('_')[0] == var and item.split('_')[-1].split('.')[0] == band:
                        self.logger.info("Found LUT %s for band %s" % (var, band))
                        l = lut.Lut(path + item, self.logger, name=var)
                        luts.update({band: l})

        if not bool(luts):
            # dict is empty
            print("ERROR: couldn't find any LUT for %s, check your syntax" % var)
            sys.exit(2)
        else:
            return luts


class HdrCollection(Collection):
    def __init__(self, path, var, log=None, verbose=True):
        super().__init__(path, var, log=None, verbose=True)
