import sys

try:
    import credentials
except ImportError:
    print """You haven't supplied your credentials yet.
If you haven't done so, first visit http://soundcloud.com/you/apps/ and register a new application.
Then, create a file 'credentials.py' with the following lines, filling in the information SoundCloud gave you:

client_id = "287878237"
client_secret = "82378233"
username = "joe@example.com"
password = "secret"

...and rerun scaup."""
    sys.exit()
    