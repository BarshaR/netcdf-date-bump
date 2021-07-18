''' NetCDF date bump 

This tool updates the timestamps in a netcdf file based on the arguments passed in.

It supports the following - 
- Automatic detection of timestamp resolution e.g 1 hourly, 3 hourly or daily
    - If a custom resolution is needed, it can be specified
- Updates will be made based on UTC time, if the script runs on a machine using a local timezone
it will be ignored. 
- Dry run mode will print the proposed time stamp changes instead of modifying the file.
- All paths should be passed in relative to the execution of the script, maybe this should be absolute

'''
from datetime import datetime, timedelta, timezone
from cftime import date2num, num2pydate
import netcdfdatebump.netcdf_utils as netcdf_utils
import sys
import argparse
import logging
from pprint import pprint

input_file = ''
output_file = ''
dry_run = False
time_step = None
start_time = ''
TIME_STEPS_MIN = 2
log_level = logging.ERROR

parser = argparse.ArgumentParser()

parser.add_argument(
    '-i', '--input-file', type=str, help='path to input file')
parser.add_argument(
    '-o', '--output-file', type=str, help='name of output file (overwrites input file if not specified)')
parser.add_argument(
    '-d', '--dry-run', help='print the output instead of modifying the file', action='store_true')
parser.add_argument('-t', '--time-step',
                    help='Amount of time between time slices in seconds')
parser.add_argument('-l', '--log-level', choices=['debug', 'info', 'error'],
                    help='define log level. options: debug, info, error')

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

    time_step_delta = generate_timedelta(curr_times_pydate)

    # TODO: Check if start datetime was supplied - this this as the starting time if provided.
    new_times = generate_new_time_list(curr_times_pydate, time_step_delta)

    # Convert list of datetime objects to timestamps
    new_timestamps = date2num(
        new_times[:], units=nc_time.units, calendar='gregorian')

    # Only print new times if dry-run or debug is enabled
    if dry_run:
        print_time_diff(curr_times_pydate, new_times)
    else:
        if log_level == logging.DEBUG:
            print_time_diff(curr_times_pydate, new_times)
        netcdf_utils.replace_nc_times(new_timestamps, nc_dataset)
    # Close file
    netcdf_utils.close_nc_file(nc_dataset)


def print_time_diff(old_times, new_times):
    # Ensure time arrays are the same length
    if len(old_times) == len(new_times):
        print('===================')
        for i in range(len(old_times)):
            print(f'{old_times[i].isoformat()} --> {new_times[i].isoformat()}')
        print('===================')
    else:
        logging.error(
            "Unable to print time diff - time arrays are of different length")


def generate_timedelta(times_pydate):
    # Ensure time array meets minimum timestep values for the delta calculation
    if time_step is not None:
        # Set the delta to the user specified duration
        return timedelta(seconds=time_step)
    elif time_step is None and len(times_pydate) >= TIME_STEPS_MIN:
        # TODO: Should check existance before directly accessing indexes
        # Set timestep delta to diff between first two times in array
        return times_pydate[1] - times_pydate[0]
    else:
        logging.error(
            'No timestep provided and times array length is too small to derive it')
        sys.exit(2)


def generate_new_time_list(times_pydate, time_step_delta):

    # Set the starting date in the sequence to begin at todays date - leaving the time portion unchanged.
    start_datetime = times_pydate[0]
    # Extract the time part of the starting date
    start_time = start_datetime.time()
    # Extract the date part of now() - where now is in UTC
    # This tries to mitigate issues where the local system time is not UTC. When the date is returned, it can result in inconsistencies based on the timezone offset.
    start_date = datetime.now(timezone.utc).date()
    # Combine the two together - the rest of the times will be bumped from this datetime
    # Note, this new_start_datetime is not timezone aware. However, this is fine as its releative to the UTC date above.
    new_start_datetime = datetime.combine(date=start_date, time=start_time)

    new_times = [new_start_datetime for time in times_pydate]
    # Iterate each datetime and add time_step_delta * index
    new_times = [(new_times[i] + (i * time_step_delta))
                 for i in range(len(new_times))]
    return new_times


if __name__ == '__main__':
    main()
