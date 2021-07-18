from datetime import datetime, timedelta, timezone
from pprint import pprint, pformat
from cftime import date2num, num2pydate
import netcdfdatebump.netcdf_utils as netcdf_utils
import logging
import sys

logger = logging.getLogger(__name__)
TIME_STEPS_MIN = 2


def generate_timedelta(times_pydate, time_step):
    # Ensure time array meets minimum timestep values for the delta calculation
    if time_step is not None:
        # Set the delta to the user specified duration
        logger.info('User provided time step delta used')
        return timedelta(seconds=time_step)
    elif time_step is None and len(times_pydate) >= TIME_STEPS_MIN:
        # TODO: Should check existance before directly accessing indexes
        # Set timestep delta to diff between first two times in array
        logger.info(
            'time step delta not provided, generating delta from time diff')
        return times_pydate[1] - times_pydate[0]
    else:
        logging.error(
            'No timestep delta provided and times array length is too small to derive it')
        sys.exit(2)


def generate_new_time_list(times_pydate, time_step_delta):
    logger.info('Generating new times based on datetime.now in UTC')
    # Set the starting date in the sequence to begin at todays date - leaving the time portion unchanged.
    start_datetime = times_pydate[0]
    # Extract the time part of the starting date
    start_time = start_datetime.time()
    # Extract the date part of now() - where now is in UTC
    # This tries to mitigate issues where the local system time is not UTC. When the date is returned, it can result in inconsistencies based on the timezone offset.
    start_date = datetime.now(timezone.utc).date()
    logger.debug(f'current UTC date - {start_date}')
    # Combine the two together - the rest of the times will be bumped from this datetime
    # Note, this new_start_datetime is not timezone aware. However, this is fine as its releative to the UTC date above.
    new_start_datetime = datetime.combine(date=start_date, time=start_time)
    # Replace each existing time with the new_start_datetime
    new_times = [new_start_datetime for time in times_pydate]
    # Modify each datetime and by adding time_step_delta * index
    new_times = [(new_times[i] + (i * time_step_delta))
                 for i in range(len(new_times))]
    logger.debug('New times array generated:')
    logger.debug(pformat(new_times))
    return new_times


def print_time_diff(old_times, new_times):
    # Ensure time arrays are the same length
    # TODO: cleanup to properly support logging framework
    if len(old_times) == len(new_times):
        print('===========================================')
        print('    OLD TIME        -->   NEW TIME         ')
        print('===========================================')
        for i in range(len(old_times)):
            print(f'{old_times[i].isoformat()} --> {new_times[i].isoformat()}')
        print('===========================================')
    else:
        logging.error(
            "Unable to print time diff - time arrays are of different length")
