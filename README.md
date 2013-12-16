BS-scraper
=====================
```
usage: scraper.py [-h] [-noimg] [-offline] [-m]

BS-scraper, a modified version of ES-scraper for BeagleSNES

optional arguments:
  -h, --help  show this help message and exit
  -noimg      disables boxart downloading
  -offline    disables internet searching, just generates a cfg
  -m          manual mode (choose from multiple results)
```

This is an adaptation of elpendors ES-Scraper designed for use with BeagleSNES (http://beaglesnes.sourceforge.net) which runs on the BeagleBoard-xm or BeagleBone. It scans your rom folder and generates a complete games.cfg accordingly by scraping game information from http://thegamesdb.net. It also downloads, converts, and resizes boxart for your boxes folder.


For image resizing to work, you need to install PIL:
```
sudo apt-get install python-imaging
```

Capabilities
====================
By default it will attempt to find the title of each .smc file in thegamesdb.net. Once it has guessed this it will then gather the following:

* Boxart, which it will download to the ./boxes folder, also converting to .png and resizing to 200 pixels wide. If a file already exists with the same filename as the smc it will skip this step and use blank_box.png intead.
* Title, it picks this up from the filename but it's somewhat more robust now so they don't have to be identical.
* Description, which it will split over four lines.
* Number of players, which it will put on the fifth line reserved for the description.
* Release date.
* Genres, which it will seperate by a slash if it finds multiples.

It then writes the blank line at the end which is required by Beaglesnes, and reports which game(s) it couldn't find online. If you just want a quick config from your rom folder without all the extra info or boxart you can use the -offline option and if you just don't want boxart to be downloaded you can use -noimg.

Usage
=====================
* Ensure that all your roms are labelled correctly. It works best if your filenames are fairly similar to the actual title of the game.
* Run the script with python ./scraper.py in terminal. I would reccomend not running it on your microSD card. Run it on your ROM library locally then copy everything (boxes folder, rom folder, games.cfg) across manually. 
* That's it!

Limitations
====================

* For simplicity many of the original functions of ES-scraper were removed such as CRC checking and partial downloading. Because of this you cannot tell it to only add new games to the cfg. Each time it's run it will generate a whole new one. You can tell it to skip images though, and it will automatically skip images if they're already there.

* It's not hugely efficient... I wrote it for accuracy over speed. Even so it processed and downloaded boxart for my entire library of 700 in about half an hour. The slowest part is downloading the boxart since many of the copies are fairly high res. If you just want a config you can use the -offline option and it will be much faster.

* If it badly screws up on a game it will probably break the cfg, but I've tested it extensively and it shouldn't do this. It should inform you in the unlikely event that this does happen.

* I have only tested it on Linux so I can't say whether it will work on other platforms. My lazy path stuff might cause problems.
