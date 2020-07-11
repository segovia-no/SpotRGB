# SpotRGB

SpotRGB is a RGB software that plays sequence files at the rhythm of Spotify. This app is WIP.


### Features

 - Play sequences from a file
 - Fade in / Fade out effects
 - WIP: Sync playback with spotify


### Compatibility

- MSI motherboards. To see if your specific motherboard is compatible refer to the [msi-rgb](https://github.com/nagisa/msi-rgb) repo to see if your motherboard is compatible.

- Only Linux compatible for the moment.


### Installation / Dev Environment

SpotRGB requires Python 3 to run properly

First, you should get the code and compile the msi-rgb binary from [nagisa/msi-rgb repo](https://github.com/nagisa/msi-rgb)

After that, clone this repo using these commands on any folder

```
$ git clone https://github.com/segovia-no/SpotRGB
$ cd SpotRGB
```

Then copy your msi-rgb binary to the cloned repo with the name "msi-rgb"

```
$ cp /PATH/TO/MSIBINARY/msi-rgb ./msi-rgb
```

Lastly execute the start.py file with sudo permissions (because the msi-rgb binary requires low level access to send data to the rgb chip)

```
$ sudo python3 ./start.py
```

### Playing an RGB sequence

Use the "--play" flag to play a .rgbseq file. Example;

```
$ sudo python3 ./start.py --play ./sequence_sample.rgbseq
```

If you want to see the hex codes sent in real time you can use the "--verbose" flag


### Sequence file format

Each .seqrgb file has metadata at the top of the file like this

```
TEMPO       104  # in beats per minute
INTERVAL    4    # divides each beat in "x" intervals
OFFSET      0    # start time delay after invoking the script (in ms)
```

The interval gives you an easier control over the timing between notes as it tries to reproduce the behavior of musical theory in a simplified way.

Next, the "note" data is storaged in this format;

```
# <startbeat> | <duration (# intervals)> | <colorcode> | <effect [o = fade out] (optional) > | <effect duration in ms. (optional)>

```
For example, the following line will start at the 0 beat, lasts 2 intervals, it displays the white color, has a fadeout effect and the effect lasts 50ms

```
0	2	FFFFFF  O   50
```

You can also omit the effects by just not writing the last 2 arguments;

```
0	2	FFFFFF
```

### Current issues
 - The amount of fade out steps for a give note can be taxing on the "send rgb tick" function, a low level access through interface with the rust app can mitigate this issue.


### Todos

 - Spotify playback synchronization
 - Low level access to the RGB system


### License
MIT

**Free Software, Hell Yeah!**