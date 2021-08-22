''' NetCDF date bump

This tool updates the timestamps in a netcdf file based on the arguments
passed in.

'''
import sys
import argparse
import logging
from cftime import date2num, num2pydate
from utils import netcdf_utils, datetime_utils

INPUT_FILE = ''
OUTPUT_FILE = ''
DRY_RUN = False
TIME_STEP = None
START_TIME = None

LOG_LEVEL = logging.ERROR

parser = argparse.ArgumentParser()

parser.add_argument(
    '-i', '--input-file', type=str, help='path to input file.')
parser.add_argument(
    '-o', '--output-file', type=str,
    help='name of output file (overwrites input file if not specified).')
parser.add_argument(
    '-d', '--dry-run', help='print the output instead of modifying the file.',
    action='store_true')
parser.add_argument('-t', '--time-step', type=str,
                    help='Amount of time between time slices in seconds.')
parser.add_argument('-s', '--start-time', type=str,
                    help='ISO formatted time which the new times will begin \
                        from.')
parser.add_argument('-l', '--log-level', choices=['debug', 'info', 'error'],
                    help='define log level. options: debug, info, error.')

args = parser.parse_args()


def exit_program(message: str = "Exiting program", exit_code: int = 2) -> None:
    logger.error(message)
    sys.exit(exit_code)


# Process arguments
if args.log_level:
    if args.log_level == 'debug':
        LOG_LEVEL = logging.DEBUG
    elif args.log_level == 'error':
        LOG_LEVEL = logging.ERROR
    elif args.log_level == 'info':
        LOG_LEVEL = logging.INFO
    logging.basicConfig(level=LOG_LEVEL)
print(f'log_level={logging.getLevelName(LOG_LEVEL)}')

logger = logging.getLogger(__name__)

if args.input_file:
    INPUT_FILE = args.input_file
    logger.info('input-file=%s', INPUT_FILE)
else:
    logger.error('Input file missing')
    exit()

if args.output_file:
    OUTPUT_FILE = args.output_file
    logger.info('output-file=%s', OUTPUT_FILE)
else:
    logger.info('No output file provided, input file used.')
    OUTPUT_FILE = INPUT_FILE

if args.dry_run:
    DRY_RUN = args.dry_run
    logger.info('dry-run=true')

if args.start_time:
    try:
        START_TIME = datetime_utils.parse_start_datetime(args.start_time)
    except ValueError:
        exit_program()
    else:
        if START_TIME:
            logger.info('start-time=%s', START_TIME)
        else:
            exit_program('start-time is invalid.')

if args.time_step:
    try:
        TIME_STEP = int(args.time_step)
    except ValueError as err:
        exit_program(f'Invalid time step provided: {err}')
    else:
        logger.info('time-step=%s', TIME_STEP)
        if TIME_STEP < 0:
            exit_program('Time step must be seconds value > 0')
else:
    logger.info(
        'No timestep provided, it will be calculated automatically as the \
            difference between existing values')


def main():
    """Main method"""
    update_nc_dates()


def update_nc_dates() -> None:
    """Update the dates in the given NetCDF file"""
    try:
        nc_dataset = netcdf_utils.open_nc_file(INPUT_FILE)
    except netcdf_utils.NetcdfFileIOException:
        exit_program()

    nc_time = nc_dataset.variables['time']
    # Convert array of timestamps to python datetime objects
    curr_times_pydate = num2pydate(
        nc_time[:], units=nc_time.units, calendar='gregorian')

    # TODO: Wrap this in an if statement to handle time delta response
    time_step_delta = datetime_utils.generate_timedelta(
        curr_times_pydate, TIME_STEP)

    # TODO: Check if start datetime was supplied - this this as the starting
    # time if provided.
    new_times = datetime_utils.generate_new_time_list(
        curr_times_pydate, time_step_delta)

    # Convert list of datetime objects to timestamps
    new_timestamps = date2num(
        new_times[:], units=nc_time.units, calendar='gregorian')

    # Only print new times if dry-run or debug is enabled
    if DRY_RUN:
        datetime_utils.print_time_diff(curr_times_pydate, new_times)
    else:
        if LOG_LEVEL == logging.DEBUG:
            datetime_utils.print_time_diff(curr_times_pydate, new_times)
        netcdf_utils.replace_nc_times(new_timestamps, nc_dataset)
    # Close file
    try:
        netcdf_utils.close_nc_file(nc_dataset)
    except netcdf_utils.NetcdfFileIOException:
        exit_program()
    logger.info("Success")


if __name__ == '__main__':
    main()
