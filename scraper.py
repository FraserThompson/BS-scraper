#!/usr/bin/env python
import os, imghdr, urllib, urllib2, sys, PIL, argparse, zlib, unicodedata, re, Image
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement

parser = argparse.ArgumentParser(description='BS-scraper, a modified version of ES-scraper for BeagleSnes ')
parser.add_argument("-noimg", help="disables boxart downloading", action='store_true')
parser.add_argument("-m", help="manual mode (choose from multiple results)", action='store_true')
args = parser.parse_args()

def normalize(s):
   #return ''.join((c for c in unicodedata.normalize('NFKD', unicode(s)) if unicodedata.category(c) != 'Mn')).replace("\n", " ")
   return s.encode('ascii', 'ignore').replace("\n", " ")
def fixExtension(file):    
    newfile="%s.%s" % (os.path.splitext(file)[0],imghdr.what(file))
    os.rename(file, newfile)
    return newfile

def getFiles(base):
    dict=set([])
    for files in sorted(os.listdir(base)):
        if files.endswith(tuple(ES_systems[var][2].split(' '))):
            filepath=os.path.abspath(os.path.join(base, files))
            dict.add(filepath)
    return dict

def searchGame(data, title):
   results=data.findall('Game')
   if len(results) > 1:
      for i,v in enumerate(results):
         try:
            if getTitle(v).lower() == title.lower():
               return i
         except Exception as e:
            print "Exception! %s %s %s" % (e, getTitle(v), getGamePlatform(v))
   return 0

def getGamesListID(file):
    title=re.sub(r'\[.*?\]|\(.*?\)', '', os.path.splitext(os.path.basename(file))[0]).strip()
    URL = "http://thegamesdb.net/api/GetGamesList.php"
    platform = "Super Nintendo (SNES)"
    values={'name':title,'platform':platform}

    try:
        req = urllib2.Request(URL,urllib.urlencode(values), headers={'User-Agent' : "RetroPie Scraper Browser"})
        remotedata = urllib2.urlopen( req )
        data=ET.parse(remotedata).getroot()
    except ET.ParseError:
        print "Malformed XML found, skipping game.. (source: {%s})" % URL
        return None

    try:
       if data.find("Game") is not None:
          if title == getTitle(data.find("Game")):
             return getID(data.findall("Game")[chooseResult(data)] if args.m else data.find("Game"))
          else:
             return getID(data.findall("Game")[searchGame(data, title)])
             
       else:
          return None
    except Exception, err:
        print "Skipping game..(%s)" % str(err)
        return None

def getGameInfo(game_id):
    URL = "http://thegamesdb.net/api/GetGame.php"
    values={'id':game_id}

    try:
        req = urllib2.Request(URL,urllib.urlencode(values), headers={'User-Agent' : "RetroPie Scraper Browser"})
        remotedata = urllib2.urlopen( req )
        data=ET.parse(remotedata).getroot()
    except ET.ParseError:
        print "Malformed XML found, skipping game.. (source: {%s})" % URL
        return None

    try:
       if data.find("Game") is not None:
          return data.find("Game")
       else:
          return None
    except Exception, err:
        print "Skipping game..(%s)" % str(err)
        return None

def getText(node):
    return normalize(node.text) if node is not None else None

def getID(nodes):
   return getText(nodes.find("id"))

def getCoop(nodes):
   return getText(nodes.find("co-op"))

def getTitle(nodes):
   return getText(nodes.find("GameTitle"))

def getPlayers(nodes):
   return getText(nodes.find("Players"))

def getGamePlatform(nodes):
   return getText(nodes.find("Platform"))

def getDescription(nodes):
   return getText(nodes.find("Overview"))

def getImage(nodes):
   return getText(nodes.find("Images/boxart[@side='front']"))

def getTGDBImgBase(nodes):
    return nodes.find("baseImgUrl").text

def getRelDate(nodes):
   return getText(nodes.find("ReleaseDate"))

def getPublisher(nodes):
   return getText(nodes.find("Publisher"))

def getDeveloper(nodes):
   return getText(nodes.find("Developer"))

def getGenres(nodes):
    genres=[]
    if nodes.find("Genres") is not None:
       for item in nodes.find("Genres").iter("genre"):
          genres.append(item.text)
          
    return genres if len(genres)>0 else None

def resizeImage(img,output):
    ext = os.path.splitext(output)[1]
    maxWidth = 200

    if ext != ".png":
       ext = ".png"
       
    print "Resizing boxart.."
    height = int((float(img.size[1])*float(maxWidth/float(img.size[0]))))
    print "Saving boxart as " + os.path.splitext(output)[0] + ext
    img.resize((maxWidth,height), Image.ANTIALIAS).save(os.path.splitext(output)[0] + ext)
    
    return os.path.splitext(output)[0] + ext
        

def downloadBoxart(path,output):
   os.system("wget -q http://thegamesdb.net/banners/%s --output-document=\"%s\"" % (path,output))

def chooseResult(nodes):
    results=nodes.findall('Game')
    if len(results) > 1:
        for i,v in enumerate(results):
            try:
                print "[%s] %s | %s" % (i,getTitle(v), getGamePlatform(v))
            except Exception as e:
                print "Exception! %s %s %s" % (e, getTitle(v), getGamePlatform(v))

        return int(raw_input("Select a result (or press Enter to skip): "))
    else:
        return 0

def scanFiles():
    name="Super Nintendo (SNES)"
    folderRoms="/rom"
    extension=".smc"
    
    folderRoms=os.getcwd()+folderRoms

    global existinglist

    gamelist = Element('gameList')

    destinationFolder = os.getcwd();

    print "Scanning folder..(%s)" % folderRoms

    if os.path.exists("games.cfg"):
       print "games.cfg already exists: %s" % os.path.abspath("games.cfg")
       s = raw_input("Overwrite?! y/n ")
       if (s == "n"):
          print "Kay, quitting."
          exit()
    
    existinglist = open("games.cfg", "w+")
    count = len(os.listdir(folderRoms))
    failed_list=[] # List of games it couldn't find the DB
    badlyfailed_list=[] # List of games which didn't get added properly
    actual_count=0 # Counts up as it succesfully finds games in the DB
    print "There are", count, "games in the rom folder."
    existinglist.write(str(count) + "\n") # Start the file off with the ROM count

    for root, dirs, allfiles in os.walk(folderRoms, followlinks=True):
        allfiles.sort()
        for files in allfiles:
            if files.endswith(tuple(extension.split(' '))):
                try:
                    filepath=os.path.abspath(os.path.join(root, files))
                    filename = os.path.splitext(files)[0]
    
                    print "Trying to identify %s.." % files
                    
                    game_id=getGamesListID(filepath) # Uses the more accurate getGamesList API function to get the ID
                    data=getGameInfo(game_id) # Passes the ID to get the rest of the game info

                    # Defaults so it will still have something to add if it can't find the game
                    str_title=filename
                    str_des="No description available."
                    str_img="blank_box.png"
                    str_rd="199X"
                    str_pub=""
                    str_dev=""
                    str_players="?"
                    str_coop=""
                    lst_genres=["Unknown"]
     
                    if data is None:
                       print "%s not found in database. Adding it to cfg with generic data." % files
                       failed_list.append(files)
                    else:
                       result=data
                       str_title=getTitle(result)
                       str_des=getDescription(result)
                       str_img=getImage(result)
                       str_rd=getRelDate(result)
                       str_pub=getPublisher(result)
                       str_dev=getDeveloper(result)
                       str_players=getPlayers(result)
                       str_coop=getCoop(result)
                       lst_genres=getGenres(result)
                       print "Game Found: %s" % str_title
                       
                       imgpath = "./boxes/" + filename + ".png"
                       imgexists = os.path.exists(imgpath) # Check to see if the image is already there

                       if str_img is not None and args.noimg is False and imgexists != True:
                          print "Downloading boxart.."
                          downloadBoxart(str_img,imgpath)
                          imgpath=fixExtension(imgpath) # Make sure the extension is right for the file downloaded
                          try:
                             imgpath = resizeImage(Image.open(imgpath),imgpath)
                          except:
                             print "Image resize error"
                          str_img=os.path.basename(imgpath)
                       else:
                          print "Skipping image download for " + str_title
                          if imgexists == True:
                             str_img=filename + ".png"
                          
                       if str_des is None:
                          str_des = "No description available."
                             
                       if str_rd is None:
                          str_rd = "199X"
                       
                       if str_dev is None:
                          str_dev = ""

                       if str_players is None:
                          str_players = "?"

                       if str_coop is None:
                          str_coop = ""
    
                       if lst_genres is None:
                          lst_genres = ["Genre"]

                    existinglist.write(str_title + "\n") # Title
                    existinglist.write(files + "\n") # Filename
                    existinglist.write(str_img + "\n"); # Boxart 

                    # Split the description into lines and write it
                    str_des = normalize(str_des)
                    lst_des = str_des.split(" ")
                    des_line = ""
                    des_linecount = 0 # Keeps track of the number of lines
                    des_charcount = 0 # Keeps track of how many characters in the line
                    des_index = 0 # Keeps track of the index in the list of words
                    des_numwords = len(lst_des)
                    while des_linecount < 4 and des_index != des_numwords:
                       des_line += lst_des[des_index] + " " # Add each word and a space to the line
                       des_charcount += len(lst_des[des_index]) # Add the length of each word to the character count
                       
                       if des_charcount + len(lst_des[des_index]) > 35 or des_index == des_numwords-1:
                          if des_linecount != 3:
                             existinglist.write(des_line + "\n")
                          else: # If it's the last line then replace last word with ...
                             existinglist.write(des_line.rsplit(" " or "," or "!" or "?", 2)[0] + "...\n")
                          des_line = "" # Start the line over again
                          des_charcount = 0
                          des_linecount += 1
                       
                       des_index += 1
                       
                    # Add blank lines if description doesn't take up the full space
                    if (des_linecount < 4):
                        while (des_linecount < 4):
                           existinglist.write("\n")
                           des_linecount += 1

                    existinglist.write("Players: " + str_players) # Number of players
                    if str_coop=="Yes":
                       existinglist.write(", Co-op\n")
                    else:
                       existinglist.write("\n")
                    existinglist.write(str_rd + "\n") # Release date
                    
                    # Add all genres found, seperated by a slash
                    genre=""
                    for thing in lst_genres:
                       genre += thing + "/"
                    existinglist.write(genre[:-1] + "\n")

                    actual_count += 1

                except KeyboardInterrupt:
                   print "Ctrl+C detected. Closing work now..."
                except Exception, d:
                   e = sys.exc_info()[0]
                   print "Exception caught! %s" % e
                   print d
                   badlyfailed_list.append(files)
                   
    # Write the blank line at the end
    existinglist.write("\n")
    
    # Remove all the jpeg files. This probably isn't the best way of doing it. 
    print "Performing cleanup...\n"
    filelist = [f for f in os.listdir("./boxes") if f.endswith(".jpeg") ]
    for f in filelist:
       os.remove("./boxes/"+ f)
    
    if count == 0:
        print "No games found."
    else:
        print actual_count, "out of ", count, "games were added to games.cfg succesfully."
        if len(failed_list) > 0:
           print "The following games couldn't be found in the database and generic data was added: "
           for game in failed_list:
              print game + ", " 
        if len(badlyfailed_list) > 0:
           print "The following games screwed up for whatever reason and probably broke games.cfg:"
           for game in badlyfailed_list:
              print game + ", "

print parser.description

if args.noimg:
    print "Boxart downloading disabled."
else:
   scanFiles()
