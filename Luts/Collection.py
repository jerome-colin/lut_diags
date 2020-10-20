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


class Collection:
    """
    A Collection is primarily a dictionary of LUT objects referenced by their wavelength, with additional meta-data.
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

    def __init__(self, path, var=None, log=None, verbose=True):
        """

        :param path: mandatory path to LUT directory
        :param var: optional name of variable, eg. 'albedo'
        :param log: if None then default logfile name, else not yet implemented
        :param verbose: defaults to True to print to sdt_out
        """
        self.path = path.strip()
        if self.path[-1] != '/':
            self.path += '/'

        # init logger
        if log is None:
            self.logger = utl.get_logger("Luts")

        # get directory content
        try:
            self.items = os.listdir(self.path)
        except FileNotFoundError as e:
            print("ERROR: %s" % e)
            sys.exit(1)

        # get a list of bands by wavelengths (nm)
        self.bands = self._get_bands()

        # assumption on the types of LUTs to expect in this collection
        self.lut_types = ['albedo', 'lut_inv_CS', 'lut_inv', 'refl', 'Tdif', 'Tdir']

        # get basic information
        self.sensor, self.aerosol, self.prop = self._get_infos()

        # log
        self.logger.info("This collection if for %s with aerosol type %s with prop set to %3.2f" % (
            self.sensor, self.aerosol, float(self.prop)))
        self.logger.info("Found %i bands for wavelengths %s" % (len(self.bands), str(self.bands)))

        # verbosity
        if verbose:
            print("This collection if for %s with aerosol type %s with prop set to %3.2f" % (
                self.sensor, self.aerosol, float(self.prop)))
            print("Found %i bands for wavelengths %s" % (len(self.bands), str(self.bands)))

        # load var if defined
        if var is not None:
            self.var = var
            self.load(var)
        else:
            self.var = 'x'

    def _get_bands(self):
        """
        Return an array of band wavelengths in LUT collection
        :param items: list of files from _discover
        :return: a numpy array
        """
        band_list = []
        for item in self.items:
            if os.path.isfile(self.path + item) and (item[-3:] == "txt" or item[-3:] == "TXT"):
                band_list.append(item.split('_')[-1].split('.')[0])

        band_arr = np.array(band_list)
        return np.unique(band_arr)

    def _get_infos(self):
        """
        Return the name of the sensor from the filename
        :return: a string of sensor, aerosol, proportion
        """
        for item in self.items:
            if os.path.isfile(self.path + item) and item.split('_')[0] == self.lut_types[0]:
                return item.split('_')[2], item.split('_')[3], item.split('_')[5]
                break

    def load(self, lut_type):
        """
        Load LUT files in LUT object collection
        :return: an array of LUT objects
        """
        self.luts = dict()

        for item in self.items:
            if os.path.isfile(self.path + item) and (item[-3:] == "txt" or item[-3:] == "TXT"):
                for band in self.bands:
                    if item.split('_')[0] == lut_type and item.split('_')[-1].split('.')[0] == band:
                        self.logger.info("Found LUT %s for band %s" % (lut_type, band))
                        l = lut.Lut(self.path + item, self.logger, name=self.var)
                        self.luts.update({band: l})

        if not bool(self.luts):
            # dict is empty
            print("ERROR: couldn't find any LUT for %s, check your syntax" % lut_type)
            sys.exit(2)

    def get(self, band):
        pass
