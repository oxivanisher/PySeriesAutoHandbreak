# PySeriesAutoHandbrake

Python script for Linux (and possibly macOS) to simplify and automate the usage of HandBrakeCLI to rip DVD series to files.

## Motivation
I personally own a rather large collection of series on DVD discs. Since the modern
world no longer uses optical drives, I use this script to copy them for my own usage.
Please be aware, that depending on your location, this is a illegal task!

## Requirements
* python3
* pip3

## Preparation
Those commands have to be run in the root of the project directory.
1) Ensure virtualenv is installed with: `python3 -m pip install --user virtualenv`
2) Create virtual environment: `python3 -m venv venv`
3) Activate the virtual environment: `source venv/bin/activate`
3) Install the required libraries: `pip install -r requirements.txt`

## Run
Those commands have to be run in the root of the project directory.
1) Activate the virtual environment if not already active: `source venv/bin/activate`
2) Run the script: `./series_ah.py --help`
