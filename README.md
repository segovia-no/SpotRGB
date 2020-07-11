# SpotRGB

SpotRGB is a RGB software that plays sequence files at the rhythm of Spotify. This app is WIP.

### Features

 - For now, the program only has the ability to play sequences from a file

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

### Todos

 - Spotify playback synchronization

### License
MIT

**Free Software, Hell Yeah!**