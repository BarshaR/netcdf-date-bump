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
import sys
import getopt
import argparse
import logging
import yaml
import netCDF4

input_file = ''
output_file = ''
dry_run = False
time_step = ''
start_time = ''
log_level = logging.ERROR

parser = argparse.ArgumentParser()
# parser.add_argument("-v", "--verbose", help="increase output verbosity",
#                     action="store_true")
parser.add_argument(
    '-i', '--input-file', type=str, help='path to input file')
parser.add_argument(
    '-o', '--output-file', type=str, help='name of output file (overwrites input file if not specified)')
parser.add_argument(
    '-d', '--dry-run', help='print the output instead of modifying the file', action='store_true')
parser.add_argument('-t', '--time-step',
                    help='Amount of time between time slices in hours')
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
        logging.error('Time step must be an hour value > 0')
        sys.exit(2)
else:
    logging.info(
        'No timestep provided, it will be calculated automatically as the difference between existing values')
