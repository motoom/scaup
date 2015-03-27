#! /usr/bin/env python

import sys
import soundcloud # Get it with: pip install soundcloud   Source: https://github.com/soundcloud/soundcloud-python, docs at https://developers.soundcloud.com/docs/api/reference

try:
    import credentials
except ImportError:
    print """You haven't supplied your SoundCloud credentials yet. See the source of 'scaup.py' for details."""
    sys.exit()


def login():    
    client = soundcloud.Client(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        username=credentials.username,
        password=credentials.password
        )
    me = client.get('/me')
    return client, me


def wipe(client):
    playlists = client.get("/playlists", user_id=me.id)
    for playlist in playlists:
        print "Deleting playlist '%s' (#%s)" % (playlist.title, playlist.id)
        client.delete(playlist.uri)

    tracks = client.get("/tracks", user_id=me.id)  
    for track in tracks:
        print "Deleting track %s (#%s)" % (track.title, track.id)
        client.delete(track.uri)


if __name__ == "__main__":
    s = raw_input("Warning: This program deletes all your tracks and playlists from your SoundCloud. Type 'yes' if you really want this: ")
    if s != "yes":
        print "Cancelled."
        sys.exit()    
    client, me = login()        
    print "Logged in as %s (#%s)\n" % (me.full_name, me.id)
    wipe(client)
