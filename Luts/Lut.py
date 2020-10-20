"""
LUT object definitions
"""

__author__ = "jerome.colin'at'cesbio.cnes.fr"
__license__ = "MIT"
__version__ = "0.1.0"

import numpy as np
import xarray as xr


class Lut():
    """
    A LUT object contains primarily the lut values in self.data (xarray), and additional meta-data

    Public methods : none, all private

    Attributes:
        data (xarray): contains the lut values from binary file
        dims (str): label of lut dimension
        dims_len (list): size of dimensions
        coords (dict): xarray coordinates
        fmeta (str): name of meta-data file
        name (str): label name of the variable from lut
    """
    def __init__(self, meta_file, logger, name='x', verbose=True):
        """

        :param meta_file: (str) filename
        :param logger: (logger)
        :param name: (str, optional) name of the variable in the lut
        :param verbose: (bool) print to std_out if True
        """
        self.fmeta = meta_file
        self.name = name

        # Get dimension names, lengths and ranges from meta file
        self.dims, self.dims_len, self.coords = self._get_meta()

        self.data = self._load_binary()
        logger.info("Loaded binary to xarray of shape %s" % str(self.data.shape))

        # log
        logger.info(self.data.coords)

        # verbosity
        if verbose:
            print(self.fmeta[:-4])
            print(self.data.coords)

    def _get_meta(self):
        """
        Get dimension names, lengths and ranges from meta file
        :return: list of dimensions, list of ndarray of steps, array of len of dims
        """
        f_meta = open(self.fmeta, 'r')
        l = f_meta.readlines()
        f_meta.close()

        dims = []
        dims_len = []
        steps = []
        coords = dict()

        for i in range(len(l)):
            dims.append(l[i].split(' ')[0])
            steps.append(np.array(l[i].split(' ')[1:-1]))
            dims_len.append(len(steps[i]))
            coords.update({l[i].split(' ')[0]: np.array(l[i].split(' ')[1:-1]).astype(float)})

        return dims, dims_len, coords

    def _load_binary(self):
        """
        Load data from binary LUT
        :return: an xarray
        """
        data = np.fromfile(self.fmeta[:-4], dtype=np.float32)
        return xr.DataArray(data.reshape(self.dims_len), dims=self.dims, coords=self.coords, name=self.name)
