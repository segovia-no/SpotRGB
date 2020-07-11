import os, sys, subprocess
import requests, json
import sched, time

import mysticconfig as cfg

# binary definition
binary = './msi-rgb'

if not os.path.isfile(binary):
    print('msi-rgb binary is not present in this folder. Terminating')
    exit()


# spotify api connection
if not cfg.configfile["spotify_oauth"]:
    print('The spotify oauth token is empty. Terminating')
    exit()

playbackAPIURL = 'https://api.spotify.com/v1/me/player'
headers = { 'Authorization': ('Bearer ' + cfg.configfile["spotify_oauth"]) }

spotReq = requests.get(playbackAPIURL, headers = headers)
print(spotReq.text)


# scheduler init
scheduler = sched.scheduler(time.time, time.sleep)

def sendRGBTick(hexvalue):

    if not len(hexvalue) == 6:
        print('invalid hex value')
        return

    print(hexvalue)

    #TODO: check if every value is a valid hex value (0 -> F)

    redvalue = hexvalue[0:2]*4
    greenvalue = hexvalue[2:4]*4
    bluevalue = hexvalue[4:6]*4

    subprocess.call([binary] + [redvalue, greenvalue, bluevalue])


# sequence loading from file
def readSequenceFile(filepath):

    sequencefile = open(filepath, 'r')
    seq_lines = sequencefile.readlines()

    tempo = None
    interval = None
    start_offset = None

    sequenceData = []

    for linedata in seq_lines:

        splitLine = linedata.split()

        # metadata
        if splitLine[0] == 'TEMPO' and len(splitLine) == 2:
            tempo = splitLine[1]
            continue

        if splitLine[0] == 'INTERVAL' and len(splitLine) == 2:
            interval = splitLine[1]
            continue

        if splitLine[0] == 'OFFSET' and len(splitLine) == 2:
            start_offset = splitLine[1]
            continue

        # data parsing
        if not len(splitLine) == 3:
            print('Sequence data file is corrupted')
            exit()

        sequenceData.append([splitLine[0], splitLine[1], splitLine[2]])

    return sequenceData, tempo, interval, start_offset


def insertSequenceTiming(sequence_data):

    # set metadata
    tempo = int(sequence_data[1]) if sequence_data[1] is not None else 120
    interval = int(sequence_data[2]) if sequence_data[2] is not None else 4
    start_offset = float(sequence_data[3]) if sequence_data[3] is not None else 0

    # timing
    time_interval = (60 / tempo) / interval

    # set scheduled times
    note_data = []

    for instruction in sequence_data[0]:

        time_start = start_offset + float(instruction[0]) * time_interval
        time_end = time_start + float(instruction[1]) * time_interval

        note_data.append([time_start, time_end, instruction[2]])

    # fill out empty spaces
    for i in range(len(note_data)):

        scheduler.enter(note_data[i][0], 1, sendRGBTick, argument=(note_data[i][2],))

        if not len(note_data) - 1 == i:

            if (note_data[i+1][0] - note_data[i][1]) >= (time_interval - 0.005) : # time interval minus constant makes room for precisionless dif.
                scheduler.enter(note_data[i][1] + 0.001, 1, sendRGBTick, argument=('000000',))

        else:
            scheduler.enter(note_data[i][1] + 0.001, 1, sendRGBTick, argument=('000000',))


### program startup

sequence_file = './sequence_sample.rgbseq'

# params
params = sys.argv

if params[0] == '-play' and params[1]:
    sequence_file = params[1]


seq_data = readSequenceFile(sequence_file)
insertSequenceTiming(seq_data)
scheduler.run()
