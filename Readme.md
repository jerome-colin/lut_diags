# Luts package

Beta for testing

## Luts.Collection

A Collection is primarily a dictionary of LUT objects referenced by their wavelength, with additional meta-data. The creation of the Collection is
agnostic to the actual content of 'path', and gathers meta-data and binary values automatically.

### Public methods:
- load: create a collection of LUT objects as dict in self.luts. This method can be called on creation of the Collection by passing 'var=x' where 'x' could be eg. 'refl' or 'albedo', etc...

### Attributes:
- sensor (str): name of sensor found from filename
- aerosol (str): name of aerosol type from filename
- bands (numpy.array): vector of wavelengths from filename
- prop (str): prop from filename
- luts (dict): dictionary of Lut objects referenced by their wavelength  

### Usage example:

`import Luts.Collection as lt`

Create a collection of Luts for 'refl':

`venus_refl = lt.Collection("tests/VENUS_zerodeuxSansAbsorption", var='refl')`

Show available bands :

`print(venus_refl.bands)`

Slice the lut for 492nm along tau, alt, d_phi, th_v, th_s and plot the resulting r_toa = f(r_surf):

`venus_refl.luts['492'].data.sel(tau='0.125', alt='0', d_phi='0.0', th_v='7.0', th_s='15.0').plot()
`

## Luts.Lut

A LUT object contains primarily the lut values in self.data (xarray), and additional meta-data

### Public methods : 
none, all private

### Attributes:
- data (xarray): contains the lut values from binary file
- dims (str): label of lut dimension
- dims_len (list): size of dimensions
- coords (dict): xarray coordinates
- fmeta (str): name of meta-data file
- name (str): label name of the variable from lut

### Usage: 
only through a Collection (recommended)