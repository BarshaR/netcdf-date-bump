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
from datetime import datetime, timedelta
from cftime import num2date, date2num, num2pydate
import netcdfdatebump.netcdf_utils as netcdf_utils
import sys
import argparse
import logging

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
    ''' TODO: 
        - read time variable as array
        - if timestep is set - create time delta variable with the specified value
            - else calculate the time step by the delta of times[1] and times[0]
        - Create a new array with updated times
            - take the first time in the array, update the year and date portion - leaving the time in tact
            - Starting at times[1], set each time to times[0] + (delta * index)
            - this should give you a sequence which starts from the current date and increments based on the timestep value


    '''
    curr_times = nc_dataset.variables['time']
    # Convert array of timestamps to python datetime objects
    times_as_pydate = num2pydate(
        curr_times[:], units=curr_times.units, calendar='gregorian')
    print(times_as_pydate)
    # Ensure time array meets minimum timestep values for the delta calculation
    if time_step is not None:
        # Set the delta to the user specified duration
        time_step_delta = timedelta(seconds=time_step)
    elif time_step is None and len(times_as_pydate) >= TIME_STEPS_MIN:
        # Should check existance before directly accessing indexes
        # Set timestep delta to diff between first two times in array
        time_step_delta = times_as_pydate[1] - times_as_pydate[0]
    else:
        logging.error(
            'No timestep provided and times array length is too small to derive it')
        sys.exit(2)

    # Set the starting date in the sequence to begin at todays date - leaving the time portion unchanged.
    start_datetime = times_as_pydate[0]
    # Extract the time part of the starting date
    start_time = start_datetime.time()
    # Extract the date part of now()
    start_date = datetime.now().date()
    # Combine the two together - the rest of the times will be bumped from this datetime
    new_start_datetime = datetime.combine(date=start_date, time=start_time)
    print(f'New start datetime= {new_start_datetime}')
    print(f'timestep delta = {time_step_delta}')

    # print(curr_times)
    # times_as_date = num2date(
    #     curr_times[:], units=curr_times.units, calendar='gregorian')
    # times_as_pydate = num2pydate(
    #     curr_times[:], units=curr_times.units, calendar='gregorian')
    # print(times_as_date)
    # print(times_as_pydate)

    # date1 = times_as_pydate[0]
    # date2 = times_as_pydate[1]
    # date_delta = date2 - date1
    # Close file
    netcdf_utils.close_nc_file(nc_dataset)


if __name__ == '__main__':
    main()
