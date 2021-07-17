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


def close_nc_file(dataset):
    dataset.close()