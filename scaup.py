#! /usr/bin/env python

import sys
import soundcloud # Get it with: pip install soundcloud   Source: https://github.com/soundcloud/soundcloud-python, docs at https://developers.soundcloud.com/docs/api/reference
import time

try:
    import credentials
except ImportError:
    print """You haven't supplied your credentials yet.
If you haven't done so, first visit http://soundcloud.com/you/apps/ and register a new application.
Then, create a file 'credentials.py' with the following lines, filling in the information SoundCloud gave you,
and also your SoundCloud username and password:

client_id = "287878237"
client_secret = "82378233"
username = "joe@example.com"
password = "secret"

...and rerun scaup."""
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



client = soundcloud.Client(
    client_id=credentials.client_id,
    client_secret=credentials.client_secret,
    username=credentials.username,
    password=credentials.password
    )
me = client.get('/me')

def dumpfields(x):
    fields = x.fields()
    for k in sorted(fields):
        print k, fields[k]
    print
        
print "Logged in as %s (#%s)\n" % (me.full_name, me.id)


if len(sys.argv) < 2:
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
else:
    dir = sys.argv[1]
    print dir
    
    # Upload two tracks
    uploaded_trackids = []

    for basename in ("gus", "alligator"):
        print "Uploading %s..." % basename
        track = client.post("/tracks", track={
            "title": basename.capitalize(),
            "sharing": "public",
            "license": "cc-by-sa",
            "label_name": "Motoom Records",
            "tag_list": "\"musique concrete\"",
            "genre": "Musique concrete",
            "artwork_data": open("%s.jpg" % basename, "rb"),   
            "asset_data": open("%s.aiff" % basename, "rb"),
            })    
        uploaded_trackids.append(track.id)

    trackids = map(lambda id: dict(id=id), uploaded_trackids)

    # Create the playlist
    client.post("/playlists", playlist={
        "title": "Stamp %s" % time.time(),
        "sharing": "public",
        "label_name": "Motoom Records",
        "playlist_type": "album",
        "artwork_data": open("alligatorbus.jpg", "rb"),   
        "tracks": trackids,
        })

