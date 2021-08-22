'''
Datetime utility class
'''
import logging
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pprint import pformat

logger = logging.getLogger(__name__)
TIME_STEPS_MIN = 2


def generate_timedelta(times_pydate: List[datetime], time_step: Optional[int]):
    # Ensure time array meets minimum timestep values for the delta calculation
    if time_step is not None:
        # Set the delta to the user specified duration
        logger.info('User provided time step delta used')
        return timedelta(seconds=time_step)
    else:
        # Set timestep delta to diff between first two times in array
        logger.info(
            'time step delta not provided, generating delta from time diff')
        try:
            delta = times_pydate[1] - times_pydate[0]
            return delta
        except (IndexError, ValueError, TypeError) as err:
            logger.error('Error calculating delta from date list: %s', err)
            raise GenerateTimeDeltaException from err


def generate_new_time_list(times_pydate: List[datetime],
                           time_step_delta: timedelta):
    logger.info('Generating new times based on datetime.now in UTC')
    # Set the starting date in the sequence to begin at todays date - leaving
    # the time portion unchanged.

    try:
        start_datetime = times_pydate[0]
    except (IndexError, TypeError, ValueError) as err:
        logger.error('Invalid date list provided: %s', err)
        raise InvalidDateListException() from err

        # Extract the time part of the starting date
    start_time = start_datetime.time()
    # Extract the date part of now() - where now is in UTC
    # This tries to mitigate issues where the local system time is not UTC.
    start_date = datetime.now(timezone.utc).date()
    logger.debug('current UTC date - %s', start_date)
    # Combine the two together - the rest of the times will be
    # bumped from this datetime
    # Note, this new_start_datetime is not timezone aware.
    # However, this is fine as its releative to the UTC date above.
    new_start_datetime = datetime.combine(date=start_date, time=start_time)
    # Replace each existing time with the new_start_datetime
    new_times = [new_start_datetime for time in times_pydate]
    # Modify each datetime and by adding time_step_delta * index
    new_times = [(new_times[i] + (i * time_step_delta))
                 for i in range(len(new_times))]
    logger.debug('New times array generated:')
    logger.debug(pformat(new_times))
    return new_times


def print_time_diff(old_times: List[datetime], new_times: List[datetime]):
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


def parse_start_datetime(date_str: str) -> datetime:
    try:
        logger.debug('Parsing start-time')
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as err:
        logger.debug(err)
        logger.error(
            'Failed to parse date: %s. Required format: \
                YYYY-MM-DDTHH:MM:SSZ', date_str)
        raise


class InvalidDateListException(Exception):
    pass


class GenerateTimeDeltaException(Exception):
    pass
