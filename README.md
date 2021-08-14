# netcdf-date-bump

`netcdf-date-bump` is a CLI that lets you easily bump the dates within a netcdf data file. 

Contents
========

 * [Why?](#why)
 * [Setup](#setup)
 * [Usage](#usage)

### Why?
---
I wanted a CLI tool that allows you to:

+ Update all the timestamps in a NetCDF file to begin at the current date whilst retaining the existing time step intervals (e.g 1 hour, 3 hour or daily time intervals between timestamps).
+ Update the timestamps to a user defined date and/or user defined time step interval.
+ Run in a non-destructive dry mode where it will only print the proposed changes - allowing the user to validate before modifying the NetCDF file.

### Setup
---

#### Requirements

+ Python 3.8+
+ Pip3
+ venv

#### Local development

1. Download the repository
    + `gh repo clone BarshaR/netcdf-date-bump`
2. Navigate to the project
    + `cd netcdf-date-bump`
3. Initialise a new Python virtual enviornment
    + `python -m venv .venv`
4. Activate the venv
    + `source .venv/bin/activate`
5. Install pip dependencies
    + `pip install -r requirements.txt`

Note, depending on your environment you may need to reference pip as `python -m pip` instead of just `pip`.

#### Create a standalone executable

PyInstaller can be used to generate a standalone executable version of this CLI tool. 
This is the simplest way to use the tool as you don't even need to have python installed.

##### Using PyInstaller

PyInstaller bundles a Python application into a single executable package with all its dependencies. This allows us to run the CLI on any machine from a single file.

1. Grab PyInstaller from pip - 
    + `pip install pyinstaller`
2. Generate the executable
    + `pyinstaller --onefile netcdf_date_bump.py`

###### Ubuntu
If you are using Ubuntu, the `binutils` package is required for PyInstaller.

``` shell
sudo apt-get install binutils
```

**Note -** 
> The output of PyInstaller is specific to the active operating system and the active version of Python.

For more information, read the [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/index.html) docs.


### Usage
---

To use the CLI, simply run `$ netcdf_date_bump`.

```shell
Usage: netcdf_date_bump [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [-d] [-t TIME_STEP] [-s START_TIME] [-l {debug,info,error}]

  Written by Richard Barsha (@BarshR).

Options:
    -h, --help                                show this help message and exit.
    -v, --version                             show version info.
    -i INPUT_FILE, --input-file INPUT_FILE    path to input file.
    -o OUTPUT_FILE, --output-file OUTPUT_FILE name of output file (overwrites input file if not specified).
    -d, --dry-run                             print the output instead of modifying the file.
    -t TIME_STEP, --time-step TIME_STEP       Amount of time between time slices in seconds.
    -s START_TIME, --start-time START_TIME    ISO formatted time which the new times will begin from.
    -l {debug,info,error}, --log-level {debug,info,error} define log level.
```
