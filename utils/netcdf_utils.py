''' NetCDF file utilities

This module abstracts the Unidata NetCDF4 python library
'''
import logging
from typing import List
# pylint: disable=no-name-in-module
from netCDF4 import Dataset


logger = logging.getLogger(__name__)


def open_nc_file(path: str) -> Dataset:
    try:
        dataset = Dataset(path, 'a')
    except OSError as err:
        logger.error('Failed to open Netcdf file: %s', err.strerror)
        raise NetcdfFileIOException(err.strerror) from err
    return dataset

# Replace the time variable in a nc dataset with the supplied array


def replace_nc_times(times: List[int], dataset: Dataset):
    dataset.variables['time'][:] = times


def close_nc_file(dataset: Dataset):
    try:
        dataset.close()
    except OSError as err:
        logger.error('Error closing nc dataset: %s', err)
        raise NetcdfFileIOException('Error closing Netcdf file') from err

# TODO: Add method to update the issue time, next issue time and creation time


class NetcdfFileIOException(OSError):
    pass
