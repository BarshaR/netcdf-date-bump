''' NetCDF file utilities

This module abstracts the Unidata NetCDF4 python library
'''
import logging
from typing import List, Optional
# pylint: disable=no-name-in-module
from netCDF4 import Dataset
from utils import datetime_utils


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


def get_nc_create_time(dataset: Dataset) -> Optional[str]:
    try:
        return dataset.createTime
    except AttributeError as err:
        logger.error('createTime does not exist: %s', err)
        return None


def set_nc_create_time(timestamp: int, dataset: Dataset):
    try:
        dataset.createTime = timestamp
    except AttributeError as err:
        logger.error('Cound not set createTime, it does not exist: %s', err)


def get_nc_create_time_string(dataset: Dataset) -> Optional[str]:
    try:
        return dataset.creationTimeString
    except AttributeError as err:
        logger.error('creationTimeString does not exist: %s', err)
        return None


def set_nc_createTimeString(time_str, dataset: Dataset):
    try:
        dataset.creationTimeString = time_str
    except AttributeError as err:
        logger.error('Cound not set createTime, it does not exist: %s', err)


def replace_nc_create_time(create_time_timestamp: int, dataset: Dataset):
    set_nc_create_time(
        create_time_timestamp,
        dataset)
    set_nc_createTimeString(
        datetime_utils.datetime_to_create_time_string(create_time_timestamp),
        dataset)


class NetcdfFileIOException(OSError):
    pass
