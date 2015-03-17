#! /usr/bin/env python

import sys
import soundcloud # Get it with: pip install soundcloud   Source: https://github.com/soundcloud/soundcloud-python, docs at https://developers.soundcloud.com/docs/api/reference
import time
import glob
import os
import itertools

try:
    import credentials
except ImportError:
    print """You haven't supplied your SoundCloud credentials yet. The program 'scaup.py' needs these.
If you haven't done so, first visit http://soundcloud.com/you/apps/ and register a new application.
Then, create a file 'credentials.py' (in the same directory as 'scaup.py') with the following lines,
filling in the information SoundCloud gave you, and also your SoundCloud username and password:

client_id = "287878237"
client_secret = "82378233"
username = "joe@example.com"
password = "secret"

...and rerun your program."""
    sys.exit()


def seconds2hmmss(x):
    "Convert a number of seconds (as a float) to a string like '1:23:58'."
    left = float(x)
    h = int(left / 3600.0)
    left -= 3600.0 * h
    m = int(left / 60.0)
    left -= 60.0 * m
    s = int(left)
    left -= s
    return "%d:%02d:%02d" % (h, m, s)

def audiofiles(dir):
    """Return a list of all audiofiles in the specified directory."""
    supported_audio = (".aiff", ".wav", ".flac", ".alac", ".ogg", ".mp2", ".mp3", ".aac", ".amr", ".wma")
    filenames = []
    for fullfn in glob.glob(os.path.join(dir, "*")):
        path, fn = os.path.split(fullfn)
        base, extension = os.path.splitext(fn)
        if extension.lower() in supported_audio:
            filenames.append(fn)
    return filenames


def trackart(dir, fn):
    """Given a directory and a filename of an audio file, return the correponding track art filename,
    i.e. a file with the same base, but with a graphics extension."""
    supported_graphic = (".jpg", ".png")
    base, _ = os.path.splitext(fn)
    for fullfn in glob.glob(os.path.join(dir, base + "*")):
        path, fn = os.path.split(fullfn)
        base, extension = os.path.splitext(fn)
        if extension.lower() in supported_graphic:
            return fn


def albumart(dir, audiofiles, artfiles):
    """Given a directory and lists of audio- and artfiles, return a graphics file that is in the directory,
    but not belonging to any audio file."""
    supported_graphic = (".jpg", ".png")
    filenames = set()
    for fullfn in glob.glob(os.path.join(dir, "*")):
        path, fn = os.path.split(fullfn)
        base, extension = os.path.splitext(fn)
        if extension.lower() in supported_graphic:
            filenames.add(fn)
    for fn in itertools.chain(audiofiles, artfiles):
        filenames.discard(fn)
    if len(filenames) == 1:
        return filenames.pop()
    else:
        return None


def login():    
    client = soundcloud.Client(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        username=credentials.username,
        password=credentials.password
        )
    me = client.get('/me')
    return client, me
    

def dumpfields(x):
    fields = x.fields()
    for k in sorted(fields):
        print k, fields[k]
    print
    
    
def dumptracks(client):
    tracks_in_playlists = set()

    playlists = client.get("/playlists", user_id=me.id)
    for playlist in playlists:
        print "Playlist '%s' (#%s)" % (playlist.title, playlist.id)
        for track in playlist.tracks:
            print "    %s (#%s) %s" % (track["title"], track["id"], seconds2hmmss(track["duration"]/1000.0))
            tracks_in_playlists.add(track["id"])
        print

    tracks = client.get("/tracks", user_id=me.id)  
    headerprinted = False
    for track in tracks:
        if track.id in tracks_in_playlists:
            continue
        if not headerprinted:
            headerprinted = True
            print "Tracks which are not in any of your playlists:\n"
        print "    %s (#%s) %s" % (track.title, track.id, seconds2hmmss(track.duration/1000.0))
    

def upload(client, dir, title=None, verbose=False):
    if dir.endswith("/"):
        dir = dir[:-1]
    if verbose:
        print "Processing directory '%s'" % dir
    audiofns = audiofiles(dir)
    artfns = []
    audioartfns = []
    for audiofn in audiofns:
        artfn = trackart(dir, audiofn)
        if artfn:
            artfns.append(artfn)
            audioartfns.append((audiofn, artfn))
            if verbose:
                print "Audio '%s' with art '%s'" % (audiofn, artfn)
        else:
            audioartfns.append((audiofn, None))
            if verbose:
                print "Audio '%s' without art" % audiofn

    albumfn = albumart(dir, audiofns, artfns)
    if verbose:
        if albumfn:
            print "Album art: %s" % albumfn
        else:
            print "No album art."
    
    # Upload tracks
    uploaded_trackids = []
    for audiofn, artfn in audioartfns:
        if not artfn and albumfn:
            artfn = albumfn
        if verbose:
            if artfn:
                print "Uploading '%s' with art '%s'" % (audiofn, artfn)
            else:
                print "Uploading '%s' without art" % audiofn
        basename, _ = os.path.splitext(audiofn)
        trackinfo = {
            "title": title or basename,
            "sharing": "public",
            #"license": "cc-by-sa",
            #"label_name": "Motoom Records",
            #"tag_list": "\"musique concrete\"",
            #"genre": "Musique concrete",
            "asset_data": open(os.path.join(dir, audiofn), "rb"),
            }
        if artfn:
            trackinfo["artwork_data"] = open(os.path.join(dir, artfn), "rb")            
        track = client.post("/tracks", track=trackinfo)    
        uploaded_trackids.append(track.id)
    trackids = map(lambda id: dict(id=id), uploaded_trackids)

    # Create the playlist
    _, base = os.path.split(dir)
    if not base:
        base = dir
    title = base
    playinfo = {
        "title": title,
        "sharing": "public",
        #"label_name": "Motoom Records",
        "playlist_type": "album",
        "tracks": trackids,
        }
    if albumfn:
        playinfo["artwork_data"] = open(os.path.join(dir, albumfn), "rb")
    client.post("/playlists", playlist=playinfo)
    if verbose:
        if albumfn:
            print "Playlist '%s' with art '%s' created." % (title, albumfn)
        else:
            print "Playlist '%s' (without art) created." % (title)


if __name__ == "__main__":
    client, me = login()        
    print "Logged in as %s (#%s)\n" % (me.full_name, me.id)

    if len(sys.argv) < 2:
        dumptracks(client)
    else:
        dir = sys.argv[1]
        upload(client, dir, verbose=True)
