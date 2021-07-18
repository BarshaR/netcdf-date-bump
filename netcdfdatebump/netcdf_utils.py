''' NetCDF file utilities

This module abstracts the Unidata NetCDF4 python library
'''
import os
from pathlib import Path
import logging
import sys
from netCDF4 import Dataset

logger = logging.getLogger(__name__)


def open_nc_file(path):
    filename, file_extension = os.path.splitext(path)
    # Ensure file has .nc extension
    if file_extension != '.nc':
        logger.error('Invalid input file - .nc file extension missing')
        sys.exit(2)
    # Check if file exists before attempting to open
    file = Path(path)
    if file.is_file():
        logger.info('Input file is valid, attempting to open')
    else:
        logger.error('Invalid input file')
        sys.exit(2)
        # Open file in append mode
    return Dataset(path, 'a')

# Replace the time variable in a nc dataset with the supplied array


def replace_nc_times(times, dataset):
    dataset.variables['time'][:] = times


def close_nc_file(dataset):
    try:
        dataset.close()
    except Exception as e:
        logger.error(f'Error closing nc dataset: {e.__class__} occured')
        sys.exit(2)
