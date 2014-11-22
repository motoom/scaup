#! /usr/bin/env python

import sys
import soundcloud # Get it with: pip install soundcloud   Source: https://github.com/soundcloud/soundcloud-python, docs at https://developers.soundcloud.com/docs/api/reference

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

tracks_in_playlists = set()

playlists = client.get("/playlists", user_id=me.id)
for playlist in playlists:
    print "Playlist '%s' (#%s)" % (playlist.title, playlist.id)
    for track in playlist.tracks:
        print "    %s (#%s) %d" % (track["title"], track["id"], track["duration"])
        tracks_in_playlists.add(track["id"])
    print

print "Tracks which are not in any of your playlists:\n"
tracks = client.get("/tracks", user_id=me.id)
for track in tracks:
    if track.id in tracks_in_playlists:
        continue
    print "    '%s' (#%s)" % (track.title, track.id)
