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

## Usecases
### Babylon 5
Since Babylon 5 was mangled for the DVD release (double cropped), some optimizations where necessary for a better quality.
To do this I added the following options to `hb_options`:
```
"--hqdn3d=medium", "--comb-detect=permissive", "--comb-detect=permissive", "--deinterlace=bob", "--decomb=bob"
```

### Stargate SG-1
The DVD releases for this series are different for several seasons. In some seasons, there are titles multiple times listed. To counter the ripping of the same title multiple times, I added the following hack on line 65:
```
    # SG1 Hack (only first half of titles)
    import math
    hack_titles = sorted(titles.keys())
    # hack_middle_index = int(len(hack_titles)/2)
    hack_middle_index = math.floor(len(hack_titles)/2)
    hack_first_half = hack_titles[:hack_middle_index]
    hack_old_titles = titles
    titles = {}
    for title in hack_first_half:
      titles[title] = hack_old_titles[title]
    internal_total_duration = internal_total_duration/2
```
