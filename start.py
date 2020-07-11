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


def readSequenceFile(filepath):

    sequencefile = open(filepath, 'r')
    seq_lines = sequencefile.readlines()

    tempo = None
    interval = None
    start_offset = None

    sequenceData = []

    for idx, linedata in enumerate(seq_lines):

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

        # data line checking
        if len(splitLine) < 3 or len(splitLine) > 5:
            print('Sequence data file is corrupted: line %d with invalid length' % (idx + 1))
            exit()

        # color code validation
        if len(splitLine[2]) != 6:
            print('Sequence data file is corrupted: line %d has an invalid color code length (has to be three bytes)' % (idx + 1))
            exit()

        try:
            int(splitLine[2], 16)
        except:
            print('Sequence data file is corrupted: line %d has an invalid hex color code' % (idx + 1))
            exit()

        # effects
        effectType = None
        effectDuration = None

        if len(splitLine) > 3:

            if(splitLine[3] != 'I' and splitLine[3] != 'O'):
                print('Sequence data file is corrupted: line %d has an invalid effect identifier' % (idx + 1))
                exit()

            effectType = splitLine[3]
            effectDuration = splitLine[4]

        sequenceData.append([splitLine[0], splitLine[1], splitLine[2], effectType, effectDuration])

    return sequenceData, tempo, interval, start_offset


def encodeData(sequence_data):

    # set metadata
    tempo = int(sequence_data[1]) if sequence_data[1] is not None else 120
    interval = int(sequence_data[2]) if sequence_data[2] is not None else 4
    start_offset = float(sequence_data[3]) if sequence_data[3] is not None else 0

    # timing
    time_interval = (60 / tempo) / interval

    # set notes
    note_data = []

    for idx_instr, instruction in enumerate(sequence_data[0]):

        time_start = start_offset + float(instruction[0]) * time_interval
        time_end = time_start + float(instruction[1]) * time_interval

        note_data.append([time_start, time_end, instruction[2]])

        # effects integration
        if instruction[3] == 'O':

            gradient_steps = int( int(instruction[4]) / 5)

            current_intensity_red = instruction[2][0:2]
            current_intensity_green = instruction[2][2:4]
            current_intensity_blue = instruction[2][4:6]

            current_timestart_offset = 0

            for step_idx in range(gradient_steps):

                # check if the effect is between notes
                time_start_effect = time_end + ( current_timestart_offset / 1000 )
                time_end_effect =   time_end + ( (current_timestart_offset + gradient_steps ) / 1000 )

                next_time_start = 0

                if not len(sequence_data[0]) - 1 == idx_instr :

                    next_time_start = start_offset + float(sequence_data[0][idx_instr + 1][0]) * time_interval

                if time_start_effect < next_time_start or len(sequence_data[0]) - 1 == idx_instr :

                    current_intensity_red =   format( int( int(current_intensity_red, 16) * ( (gradient_steps - step_idx) / gradient_steps )), '02x')
                    current_intensity_green = format( int( int(current_intensity_green, 16) * ( (gradient_steps - step_idx) / gradient_steps )), '02x')
                    current_intensity_blue =  format( int( int(current_intensity_blue, 16) * ( (gradient_steps - step_idx) / gradient_steps )), '02x')

                    calculated_intensity = ( str(current_intensity_red) + str(current_intensity_green) + str(current_intensity_blue) ).upper()

                    note_data.append([time_start_effect, time_end_effect, calculated_intensity])
                    current_timestart_offset += gradient_steps


        #TODO: make elif for fade in effect

    
    for i in range(len(note_data)):

        scheduler.enter(note_data[i][0], 1, sendRGBTick, argument=(note_data[i][2],))

        if not len(note_data) - 1 == i :

            # fill out empty spaces
            if (note_data[i+1][0] - note_data[i][1]) >= (time_interval - 0.005) : # time interval minus constant makes room for precisionless dif.
                scheduler.enter(note_data[i][1] + 0.001, 1, sendRGBTick, argument=('000000',))

        else:
            scheduler.enter(note_data[i][1] + 0.001, 1, sendRGBTick, argument=('000000',))


def sendRGBTick(hexvalue):

    if verbose:
        print(hexvalue)

    redvalue = hexvalue[0:2]*4
    greenvalue = hexvalue[2:4]*4
    bluevalue = hexvalue[4:6]*4

    subprocess.call([binary] + [redvalue, greenvalue, bluevalue] + ['-d', '511'])


### program startup
###################

sequence_file = './sequence_sample.rgbseq'

# params
params = sys.argv

idx_play = params.index('--play') if '--play' in params else None

if params[idx_play + 1]:
    sequence_file = params[idx_play + 1]

verbose = True if '--verbose' in params else False


# init
sequence_data = readSequenceFile(sequence_file)
encodeData(sequence_data)
scheduler.run() # play sequence
