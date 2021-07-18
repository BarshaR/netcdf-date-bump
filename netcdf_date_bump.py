''' NetCDF date bump 

This tool updates the timestamps in a netcdf file based on the arguments passed in.

'''
from datetime import datetime, timedelta, timezone
from cftime import date2num, num2pydate
import netcdfdatebump.netcdf_utils as netcdf_utils
import netcdfdatebump.datetime_utils as datetime_utils
import sys
import argparse
import logging
from pprint import pprint

input_file = ''
output_file = ''
dry_run = False
time_step = None
start_time = ''

log_level = logging.ERROR

parser = argparse.ArgumentParser()

parser.add_argument(
    '-i', '--input-file', type=str, help='path to input file.')
parser.add_argument(
    '-o', '--output-file', type=str, help='name of output file (overwrites input file if not specified).')
parser.add_argument(
    '-d', '--dry-run', help='print the output instead of modifying the file.', action='store_true')
parser.add_argument('-t', '--time-step', type=int,
                    help='Amount of time between time slices in seconds.')
parser.add_argument('-s', '--start-time', type=str,
                    help='ISO formatted time which the new times will begin from.')
parser.add_argument('-l', '--log-level', choices=['debug', 'info', 'error'],
                    help='define log level. options: debug, info, error.')

args = parser.parse_args()

# Process arguments
if args.log_level:
    if args.log_level == 'debug':
        log_level = logging.DEBUG
    elif args.log_level == 'error':
        log_level = logging.ERROR
    elif args.log_level == 'info':
        log_level = logging.INFO
    logging.basicConfig(level=log_level)
print(f'log_level={logging.getLevelName(log_level)}')

if args.input_file:
    input_file = args.input_file
    logging.info(f'input-file={input_file}')
else:
    logging.error('Input file missing')
    sys.exit(2)

if args.output_file:
    output_file = args.output_file
    logging.info(f'output-file={output_file}')
else:
    logging.info(f'No output file provided, input file used.')
    output_file = input_file

if args.dry_run:
    dry_run = args.dry_run
    logging.info('dry-run=true')

if args.time_step:
    time_step = args.time_step
    logging.info(f'time-step={time_step}')
    if time_step < 0:
        logging.error('Time step must be seconds value > 0')
        sys.exit(2)
else:
    logging.info(
        'No timestep provided, it will be calculated automatically as the difference between existing values')


def main():
    update_nc_dates()


def update_nc_dates():
    nc_dataset = netcdf_utils.open_nc_file(input_file)

    nc_time = nc_dataset.variables['time']
    # Convert array of timestamps to python datetime objects
    curr_times_pydate = num2pydate(
        nc_time[:], units=nc_time.units, calendar='gregorian')

    time_step_delta = datetime_utils.generate_timedelta(
        curr_times_pydate, time_step)

    # TODO: Check if start datetime was supplied - this this as the starting time if provided.
    new_times = datetime_utils.generate_new_time_list(
        curr_times_pydate, time_step_delta)

    # Convert list of datetime objects to timestamps
    new_timestamps = date2num(
        new_times[:], units=nc_time.units, calendar='gregorian')

    # Only print new times if dry-run or debug is enabled
    if dry_run:
        datetime_utils.print_time_diff(curr_times_pydate, new_times)
    else:
        if log_level == logging.DEBUG:
            datetime_utils.print_time_diff(curr_times_pydate, new_times)
        netcdf_utils.replace_nc_times(new_timestamps, nc_dataset)
    # Close file
    netcdf_utils.close_nc_file(nc_dataset)
    logging.info("Success")


if __name__ == '__main__':
    main()
