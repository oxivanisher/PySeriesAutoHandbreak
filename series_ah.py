#!/usr/bin/env python3

import click
import logging
import os
import subprocess
import time

logging.basicConfig(
    # filename=logPath,
    format="%(asctime)s %(levelname)-7s %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
    level=logging.INFO,
)


def human_readable_duration(timestamp):
    hours = timestamp // 3600
    timestamp = timestamp - (hours * 3600)
    minutes = timestamp // 60
    seconds = timestamp - (minutes * 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def run_handbrake(options):
    logging.debug("calling HandBrakeCLI with: %s" % " ".join(str(x) for x in options))
    result = subprocess.run([str(x) for x in ["HandBrakeCLI"] + options], capture_output=True)
    return result.stderr.decode().split('\n')


def analyze_scan(output, maxduration):
    titles = {}
    title_found = False

    index = 0
    duration = 0
    internal_total_duration = 0
    for line in output:
        if line.startswith("+ title"):
            logging.debug("found title marker")
            title_found = True
        if title_found:
            if line.startswith("  + index"):
                index = int(line.split()[-1])
                logging.debug("found title index: %s" % index)

            if line.startswith("  + duration:"):
                durations = line.split()[-1].split(":")
                duration = int(durations[0]) * 3600 + int(durations[1]) * 60 + int(durations[2])
                logging.debug("found duration in seconds: %s" % duration)

        if index and duration:
            if duration <= maxduration:
                titles[index] = duration
                internal_total_duration += duration
            title_found = False
            index = 0
            duration = 0

    logging.info("found %s titles with a total duration of %s" % (len(titles.keys()),
                                                                  human_readable_duration(internal_total_duration)))
    return titles


@click.command()
@click.option('--series', required=True, prompt='Series name', help='The series name')
@click.option('--season', required=True, prompt='Season number', help='Season the disc belongs to.')
@click.option('--extension', default="mkv", show_default=True,
              help='The extension used for created files. Should be according to the --preset option.')
@click.option('--nativelang', default="eng", show_default=True,
              help='The native language chosen for audio and subtitles.')
@click.option('--device', default="/dev/dvd", show_default=True, help='The optical drive to be used.')
@click.option('--destpath', default="%s/Videos" % os.path.expanduser("~"), show_default=True,
              help='The location where the video files are stored.')
@click.option('--preset', default="Matroska/H.264 MKV 576p25", show_default=True,
              help='The HandBrakeCLI used to encode files. See available options with: HandBrakeCLI -z')
@click.option('--minduration', default=600, show_default=True, help='Minimal number of seconds for episode detection.')
@click.option('--maxduration', default=6600, show_default=True, help='Maximal number of seconds for episode detection.')
@click.option('--debug', is_flag=True, default=False, show_default=True, help="Show also debug output")
def run(series, season, extension, nativelang, device, destpath, preset, minduration, maxduration, debug):
    """Simple script to control HandBrakeCLI for ripping series. Please be aware, that you have to"""
    """run this script on the disks in the correct order or the episodes will be wrongly numbered!"""
    script_start_time = time.time()

    # enable debug output if required
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # set some variables
    internal_destpath = os.path.join(destpath, series)
    season_string = "{:02d}".format(int(season))
    episode_string = "00"

    # ensure the target directory exists
    if not os.path.exists(internal_destpath):
        logging.info("creating path %s" % internal_destpath)
        os.mkdir(internal_destpath)

    # scan the disc for titles we are interested in
    logging.info("scanning for titles...")
    result = run_handbrake(["--min-duration", minduration, "--title", "0", "--input", device])
    titles = analyze_scan(result, maxduration)

    # find last episode file
    last_file = None
    for file in sorted(os.listdir(internal_destpath)):
        if file.endswith(extension):
            if season_string in file:
                last_file = file

    # calculate next episode
    if last_file:
        last_episode_str = last_file[len(series) + 5:-4]
        logging.debug("found last episode: %s" % last_episode_str)
        episode_string = "{:02d}".format(int(last_episode_str) + 1)

    for title in sorted(titles.keys()):
        # set default options
        hb_options = ["--all-audio", "--all-subtitles", "--subtitle-burned=none"]

        # set device
        hb_options.extend(["--input", device])

        # set output filename
        episode_string = "{:02d}".format(int(episode_string) + 1)
        output_filename = "%s S%sE%s.%s" % (series, season_string, episode_string, extension)
        hb_options.extend(["--output", os.path.join(internal_destpath, output_filename)])

        # set handbreak preset
        hb_options.extend(["--preset", preset])

        # set title to rip
        hb_options.extend(["--title", title])

        # set native language
        hb_options.extend(["--native-language", nativelang])

        # run the rip
        logging.info("ripping title %s with duration %s to file %s..." % (title, human_readable_duration(titles[title]),
                                                                          output_filename))
        rip_start = time.time()
        run_handbrake(hb_options)
        logging.info("  ripping took %s" % human_readable_duration(time.time() - rip_start))

        logging.info("script finished after %s" % human_readable_duration(time.time() - script_start_time))

if __name__ == '__main__':
    run()
