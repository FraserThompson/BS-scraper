BS-scraper
=====================
```
usage: scraper.py [-h] [-noimg] [-m]

BS-scraper, a modified version of ES-scraper for BeagleSNES

optional arguments:
  -h, --help  show this help message and exit
  -noimg      disables boxart downloading
  -m          manual mode (choose from multiple results)
```

This is an adaptation of elpendors ES-Scraper designed for use with BeagleSNES (http://beaglesnes.sourceforge.net) which runs on the BeagleBoard-xm or BeagleBone. It scans your rom folder and generates a complete games.cfg accordingly by scraping game information from http://thegamesdb.net. It also downloads, converts, and resizes boxart for your boxes folder.


For image resizing to work, you need to install PIL:
```
sudo apt-get install python-imaging
```

Capabilities
====================
It will attempt to find the title of each .smc file in thegamesdb.net. Once it has guessed this it will then gather the following:

* Boxart, which it will download to the ./boxes folder, also converting to .png and resizing to 200 pixels wide. If a file already exists with the same filename as the smc it will skip this step.
* Description, which it will split over four lines.
* Number of players, which it will put on the fifth line reserved for the description.
* Release date.
* Genres, which it will seperate by a slash if it finds multiples.

Each of these has a default so if it can't find information in the database it won't break your config. It then writes the blank file at the end which is required by Beaglesnes, and reports which game(s) it couldn't find online.

Usage
=====================
* Ensure that all your roms are labelled correctly. It works best if your filenames are fairly similar to the actual title of the game. 
* Run the script with python ./scraper.py in terminal. I would reccomend not running it on your microSD card. Run it on your ROM library locally then copy everything (boxes folder, rom folder, games.cfg) across manually. 
* That's it!

Limitations
====================

* It's not 100% accurate but it does a pretty good job. It was tested on a fairly complete library of 700 ROMs and after much squashing of bugs it seems to have identified all of them correctly. Some particular games will confuse http://thegamesdb.net if they're not labelled correctly eg. NHL '98 will be misidentified unless the file is labelled NHL 98, Prince of Persia 2 will be misidentified if it has roman numeral II, Breath Of Fire II will be misidentified if it has the number 2...

* For simplicity many of the original functions of ES-scraper were removed such as CRC checking and partial downloading. Because of this you cannot tell it to only add new games to the cfg. Each time it's run it will generate a whole new one.

* It's not hugely efficient.. I wrote it for accuracy over speed. Even so it processed and downloaded boxart for my entire library of 700 in about half an hour. The slowest part is downloading the boxart since many of the copies are fairly high res.

* If it badly screws up on a game it will probably break the cfg, but I've tested it extensively and it shouldn't do this. It should inform you in the unlikely event that this does happen.

* I have only tested it on Linux so I can't say whether it will work on other platforms. My lazy path stuff might cause problems.
