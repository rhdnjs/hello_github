# coding=utf-8

#
# A Last.fm API interface.
# Copyright (C) 2013  Никола "hauzer" Вукосављевић
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from . import info

import  requests
import  json
import  sqlite3

import  hashlib
import  time
import  inspect


VERSION     = info.VERSION
USER_AGENT  = "{}/{}".format(info.NAME, VERSION)

API_ROOT                = "https://ws.audioscrobbler.com/2.0/"
REQUEST_RATE_PERIOD     = 300
REQUEST_RATE_INTERVAL   = 5
MAX_REQUESTS            = REQUEST_RATE_PERIOD / REQUEST_RATE_INTERVAL
MAX_USERNAME_LENGTH     = 15

KEY     = "312a23775128fd0f9a6d8d3e7a87a4b4"
SECRET  = "d03bece4e91f9a25b0b2b78c75c7c327"


#
# Errors as shown on Last.fm API pages.
#

class RequestError(Exception): pass
class InvalidServiceError(RequestError): pass
class InvalidMethodError(RequestError): pass
class AuthenticationFailedError(RequestError): pass
class InvalidFormatError(RequestError): pass
class InvalidParametersError(RequestError): pass
class InvalidResourceSpecifiedError(RequestError): pass
class OperationFailedError(RequestError): pass
class InvalidSessionKeyError(RequestError): pass
class InvalidApiKeyError(RequestError): pass
class ServiceOfflineError(RequestError): pass
class SubscribersOnlyError(RequestError): pass
class InvalidMethodSignatureError(RequestError): pass
class TokenNotAuthorizedError(RequestError): pass
class TokenExpiredError(RequestError): pass
class TemporaryErrorError(RequestError): pass
class TrialExpiredError(RequestError): pass
class NotEnoughContentError(RequestError): pass
class NotEnoughMembersError(RequestError): pass
class NotEnoughFansError(RequestError): pass
class NotEnoughNeighboursError(RequestError): pass
class SuspendedApiKeyError(RequestError): pass
class StationDeprecatedError(RequestError): pass
class GeoRestrictedError(RequestError): pass
class RateLimitExceededError(RequestError): pass

error_codes = {
    2: InvalidServiceError,              # 2 : Invalid service - This service does not exist
    3: InvalidMethodError,               # 3 : Invalid Method - No method with that name in this package
    4: AuthenticationFailedError,        # 4 : Authentication Failed - You do not have permissions to access the service
    5: InvalidFormatError,               # 5 : Invalid format - This service doesn't exist in that format
    6: InvalidParametersError,           # 6 : Invalid parameters - Your request is missing a required parameter
    7: InvalidResourceSpecifiedError,    # 7 : Invalid resource specified
    8: OperationFailedError,             # 8 : Operation failed - Something else went wrong
    9: InvalidSessionKeyError,           # 9 : Invalid session key - Please re-authenticate
    10: InvalidApiKeyError,              # 10 : Invalid API key - You must be granted a valid key by last.fm
    11: ServiceOfflineError,             # 11 : Service Offline - This service is temporarily offline. Try again later.
    12: SubscribersOnlyError,            # 12 : Subscribers Only - This station is only available to paid last.fm subscribers
    13: InvalidMethodSignatureError,     # 13 : Invalid method signature supplied
    14: TokenNotAuthorizedError,         # 14 : This token has not been authorized
    15: TokenExpiredError,               # 15 : This token has expired
    16: TemporaryErrorError,             # 16 : There was a temporary error processing your request. Please try again
    18: TrialExpiredError,               # 18 : Trial Expired - This user has no free radio plays left. Subscription required
    20: NotEnoughContentError,           # 20 : Not Enough Content - There is not enough content to play this station
    21: NotEnoughMembersError,           # 21 : Not Enough Members - This group does not have enough members for radio
    22: NotEnoughFansError,              # 22 : Not Enough Fans - This artist does not have enough fans for for radio
    23: NotEnoughNeighboursError,        # 23 : Not Enough Neighbours - There are not enough neighbours for radio
    26: SuspendedApiKeyError,            # 26 : Suspended API key - Access for your account has been suspended, please contact Last.fm
    27: StationDeprecatedError,          # 27 : Deprecated - This station is no longer available
    28: GeoRestrictedError,              # 28 : Geo Restricted - This station is not available with this client/country combination
    29: RateLimitExceededError,          # 29 : Rate limit exceeded - Your IP has made too many requests in a short period
    }


class Package:
    def __init__(self, app):
        self.app = app
        

class AlbumPackage(Package):
    def add_tags(self, artist, album, tags):
        self.app.request_auto()
    
    def get_buy_links(self, country, artist = None, album = None, mbid = None, autocorrect = None):
        data = self.app.request_auto()
        return data["affiliations"]
    
    def get_info(self, artist = None, album = None, username = None, autocorrect = None, lang = None, mbid = None):
        data = self.app.request_auto()
        return data["album"]
    
    def get_shouts(self, artist = None, album = None, page = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    def get_tags(self, artist = None, album = None, user = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["tags"]
    
    def get_top_tags(self, artist = None, album = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    def remove_tag(self, tag, artist, album):
        self.app.request_auto()
    
    def search(self, album, page = None, limit = None):
        data = self.app.request_auto()
        return data["results"]
        
        
class ArtistPackage(Package):
    def add_tags(self, artist, tags):
        self.app.request_auto()
    
    def get_corrections(self, artist):
        data = self.app.request_auto()
        return data["corrections"]
    
    def get_events(self, artist = None, page = None, limit = None, autocorrect = None, festivalsonly = None, mbid = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_info(self, artist = None, username = None, autocorrect = None, lang = None, mbid = None):
        data = self.app.request_auto()
        return data["artist"]
    
    def get_past_events(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_podcast(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["rss"]
    
    def get_shouts(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    def get_similar(self, artist = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["similarartists"]
    
    def get_tags(self, artist = None, user = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["tags"]
    
    def get_top_albums(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    def get_top_fans(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["topfans"]
    
    def get_top_tags(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    def get_top_tracks(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def remove_tag(self, artist, tag):
        self.app.request_auto()
    
    def search(self, artist, page, limit):
        data = self.app.request_auto()
        return data["results"]
    
    def share(self, artist, recipient, message = None, public = None):
        self.app.request_auto()
    
    def shout(self, artist, message):
        self.app.request_auto()
        
        
class AuthPackage(Package):
    def get_mobile_session(self, username, password):
        data = self.app.request_auto()
        return data["session"]
    
    def get_token(self):
        data = self.app.request_auto()
        token = Token(self.app, data["token"])
        
        return token
    
    def get_session(self, token):
        data = self.app.request_auto()
        return data["session"]
    
    def get_url(self, callback):
        return "http://www.last.fm/api/auth/?api_key={}&cb={}".format(self.app.key, callback)
    
    
class ChartPackage(Package):
    def get_hyped_artists(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["artists"]

    def get_hyped_tracks(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["tracks"]

    def get_loved_tracks(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["tracks"]

    def get_top_artists(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["artists"]

    def get_top_tags(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["tags"]

    def get_top_tracks(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["tracks"]
    
        
class EventPackage(Package):
    def attend(self, event, status):
        self.app.request_auto()
    
    def get_attendees(self, event, page = None, limit = None):
        data = self.app.request_auto()
        return data["attendees"]
    
    def get_info(self, event):
        data = self.app.request_auto()
        return data["event"]
    
    def get_shouts(self, event, page = None, limit = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    def share(self, event, recipient, message = None, public = None):
        self.app.request_auto()
    
    def shout(self, event, message):
        self.app.request_auto()
        
        
class GeoPackage(Package):
    def get_events(self, tag = None, page = None, limit = None, long = None,
                   lat = None, location = None, distance = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_metro_artist_chart(self, metro, country, page = None, limit = None,
                               start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_metro_hype_artist_chart(self, metro, country, page = None, limit = None,
                                    start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_metro_hype_track_chart(self, metro, country, page = None, limit = None,
                                   start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def get_metro_track_chart(self, metro, country, page = None, limit = None,
                              start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def get_metro_unique_artist_chart(self, metro, country, page = None, limit = None,
                                      start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_metro_unique_track_chart(self, metro, country, page = None, limit = None,
                                     start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def get_metro_weekly_chart_list(self, metro):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    def get_metros(self, country = None):
        data = self.app.request_auto()
        return data["metros"]
    
    def get_top_artists(self, country, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_top_tracks(self, country, page = None, limit = None, location = None):
        data = self.app.request_auto()
        return data["toptracks"]
        
        
class GroupPackage(Package):
    def get_hype(self, group):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    def get_members(self, group, page = None, limit = None):
        data = self.app.request_auto()
        return data["members"]
    
    def get_weekly_album_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyalbumchart"]
    
    def get_weekly_artist_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    def get_weekly_chart_list(self, group):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    def get_weekly_track_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklytrackchart"]
        
        
class LibraryPackage(Package):
    def add_album(self, albums):
        params = to_arrays(albums, ["artist", "album"])
        albums = None
    
        data = self.app.request_auto(params)
        return data["albums"]
    
    def add_artist(self, artists):
        params = to_array(artists, "artist")
        artists = None
    
        data = self.app.request_auto(params)
        return data["artists"]
    
    def add_track(self, artist, track):
        self.app.request_auto()
    
    def get_albums(self, user, artist, limit = None, page = None):
        data = self.app.request_auto()
        return data["albums"]
    
    def get_artists(self, user, limit = None, page = None):
        data = self.app.request_auto()
        return data["artists"]
    
    def get_tracks(self, user, artist, album, limit = None, page = None):
        data = self.app.request_auto()
        return data["tracks"]
    
    def remove_album(self, artist, album):
        self.app.request_auto()
    
    def remove_artist(self, artist):
        self.app.request_auto()
    
    def remove_scrobble(self, artist, track, timestamp):
        self.app.request_auto()
    
    def remove_track(self, artist, track):
        self.app.request_auto()
        
        
class PlaylistPackage(Package):
    def add_track(self, playlistid, artist, track):
        self.app.request_auto()
    
    def create(self, title = None, description = None):
        self.app.request_auto()
        
        
class RadioPackage(Package):
    def get_playlist(self, bitrate = None, rtp = None, discovery = None, speed_multiplier = None, buylinks = None):
        data = self.app.request_auto()
        return data["playlist"]
    
    def search(self, name):
        data = self.app.request_auto()
        return data["stations"]
    
    def tune(self, station, lang = None):
        data = self.app.request_auto()
        return data["station"]
        
        
class TagPackage(Package):
    def get_info(self, tag = None, lang = None):
        data = self.app.request_auto()
        return data["tag"]
    
    def get_similar(self, tag):
        data = self.app.request_auto()
        return data["similartags"]
    
    def get_top_albums(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    def get_top_artists(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_top_tags(self, ):
        data = self.app.request_auto()
        return data["toptags"]
    
    def get_top_tracks(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def get_weekly_artist_chart(self, tag, limit = None, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    def get_weekly_chart_list(self, tag):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    def get_search(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["results"]
        
        
class TasteometerPackage(Package):
    def compare(self, type1, value1, type2, value2, limit = None):
        data = self.app.request_auto()
        return data["comparison"]
        
        
class TrackPackage(Package):
    def add_tags(self, artist, track, tags):
        self.app.request_auto()
    
    def ban(self, artist, track):
        self.app.request_auto()
    
    def get_buy_links(self, country, artist = None, track = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["affiliations"]
    
    def get_corrections(self, artist, track):
        data = self.app.request_auto()
        return data["corrections"]
    
    def get_fingerprint_metadata(self, fingerprintid):
        data = self.app.request_auto()
        return data["tracks"]
    
    def get_info(self, artist = None, track = None, username = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["track"]
    
    def get_shouts(self, artist = None, track = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    def get_similar(self, artist = None, track = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["similartracks"]
    
    def get_tags(self, artist = None, track = None, user = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["tags"]
    
    def get_top_fans(self, artist = None, track = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["topfans"]
    
    def get_top_tags(self, artist = None, track = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    def love(self, artist, track):
        self.app.request_auto()
    
    def remove_tag(self, artist, track, tag):
        self.app.request_auto()
    
    def scrobble(self, scrobbles):
        params = classes_to_arrays(scrobbles)
        scrobbles = None
    
        data = self.app.request_auto(params)
    
        return data["scrobbles"]
    
    def search(self, track, artist = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["results"]
    
    def share(self, artist, track, recipient, message = None, public = None):
        self.app.request_auto()
    
    def unban(self, artist, track):
        self.app.request_auto()
    
    def unlove(self, artist, track):
        self.app.request_auto()
    
    def update_now_playing(self, artist, track, album = None, duration = None, \
                           mbid = None, tracknumber = None, albumartist = None, \
                           context = None):
        data = self.app.request_auto()
        return data["nowplaying"]
        
        
class UserPackage(Package):
    def get_artist_tracks(self, user, artist, page = None, starttimestamp = None, endtimestamp = None):
        data = self.app.request_auto()
        return data["artisttracks"]
    
    def get_banned_tracks(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["bannedtracks"]
    
    def get_events(self, user, page = None, limit = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_friends(self, user, page = None, limit = None, recenttracks = None):
        data = self.app.request_auto()
        return data["friends"]
    
    def get_info(self, user = None):
        data = self.app.request_auto()
        return data["user"]
    
    def get_loved_tracks(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["lovedtracks"]
    
    def get_neighbours(self, user, limit = None):
        data = self.app.request_auto()
        return data["neighbours"]
    
    def get_new_releases(self, user, userecs = None):
        data = self.app.request_auto()
        return data["albums"]
    
    def get_past_events(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_personal_tags(self, user, tag, taggingtype, page = None, limit = None):
        data = self.app.request_auto()
        return data["taggings"]
    
    def get_playlists(self, user):
        data = self.app.request_auto()
        return data["playlists"]
    
    def get_recent_stations(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["recentstations"]
    
    def get_recent_tracks(self, user, extended = None, page = None, limit = None, from_ = None, to = None):
        data = self.app.request_auto()
        return data["recenttracks"]
    
    def get_recommended_artists(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["recommendations"]
    
    def get_recommended_events(self, page = None, limit = None, latitude = None, longitude = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_shouts(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    def get_top_albums(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    def get_top_artists(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    def get_top_tags(self, user, limit = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    def get_top_tracks(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    def get_weekly_album_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyalbumchart"]
    
    def get_weekly_artist_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    def get_weekly_chart_list(self, user):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    def get_weekly_track_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklytrackchart"]
    
    def shout(self, user, message):
        self.app.request_auto()
        
        
class VenuePackage(Package):
    def get_events(self, venue, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    def get_past_events(self, venue, page = None, limit = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    def search(self, venue, page = None, limit = None, country = None):
        data = self.app.request_auto()
        return data["results"]


class Token:
    """
    The authentication token returned by some :py:class:`~lastfm.lfm.Auth` methods.
    
    """

    
    def __str__(self):
        return self.str
    
    def __init__(self, app, token):
        self.str = token
        self.url = "http://www.last.fm/api/auth/?api_key=" + app.key + "&token=" + token


class Scrobble:
    def __init__(self, artist, track, timestamp, album = None, duration = None, mbid = None, \
                 tracknumber = None, albumartist = None, streamid = None, chosenbyuser = None, \
                 context = None):
        self.artist         = artist
        self.track          = track
        self.timestamp      = timestamp
        self.album          = album
        self.duration       = duration
        self.mbid           = mbid
        self.tracknumber    = tracknumber
        self.albumartist    = albumartist
        self.streamid       = streamid
        self.chosenbyuser   = chosenbyuser
        
from .user import User

class App:
    def __init__(self, api_key):
        self.api_key = api_key
        self.user = User(self)
    """
    Represents a single Last.fm application.
    
    A Last.fm application is associated with an `API account <http://www.last.fm/api/account/create>`_.
    
    :param key:
        The key of an API account.
        
    :type key:
        string
    
    :param secret:
        The secret of an API account.
    
    :type secret:
        string
    
    :param db:
        The name of the file which will hold a :mod:`sqlite3 <python:sqlite3>` database
        tied to this application. The purpose of the database is to keep track of the
        number of requests made, so the application can comply to the
        point 4.4 of  `Last.fm's API Terms of Service <http://www.last.fm/api/tos>`_.
        If the parameter is *None*, the library will not limit the number of requests
        in any way, but the Last.fm servers probably will.
        
    :type db:
        string
    
    """


    def __init__(self, key = KEY, secret = SECRET, db_file = None, info = None):
        self.album       = AlbumPackage(self)
        self.artist      = ArtistPackage(self)
        self.auth        = AuthPackage(self)
        self.chart       = ChartPackage(self)
        self.event       = EventPackage(self)
        self.geo         = GeoPackage(self)
        self.group       = GroupPackage(self)
        self.library     = LibraryPackage(self)
        self.playlist    = PlaylistPackage(self)
        self.radio       = RadioPackage(self)
        self.tag         = TagPackage(self)
        self.tasteometer = TasteometerPackage(self)
        self.track       = TrackPackage(self)
        self.user        = UserPackage(self)
        self.venue       = VenuePackage(self)
        
        self.key            = key
        self.secret         = secret
        self.session_key    = None
        self.info           = info
        
        if db_file is not None:
            self.db = sqlite3.connect(db_file)
            self.dbc = self.db.cursor()
            
            if not self.db_table_exists_timestamps():
                self.db_create_table_timestamps()
        else:
            self.db = None

            
    def request(self, pkg, method, params):
        """
        Makes an API request.
        
        :param pkg:
            The name of the package in which the method resides.
            
        :type pkg:
            string
            
        :param method:
            The name of the method.
            
        :type method:
            string
            
        :param params:
            Parameters to be sent.
            
        :type params:
            dict
            
        :returns:
            The response.
            
        :rtype:
            :mod:`json object <python:json>`
        
        """
        
        
        if not self.can_request():
            raise RateLimitExceededError("Exceeded the limit of one request per five seconds over five minutes.")
    
    
        params.update({"api_key": self.key,
                       "method": pkg + "." + method,
                       "sk": self.session_key,
                       "format": "json"})
    
        # Remove keys with a value of None.
        params = dict((key, params[key]) for key in params if params[key] is not None)
        
        # Convert all objects to strings, as expected by the API
        for key in params.copy():
            if isinstance(params[key], bool):
                if params[key]:
                    params[key] = "1"
                else:
                    params[key] = "0"
    
            elif not isinstance(params[key], str):
                try:
                    params[key] = ",".join(params[key])
    
                except TypeError:
                    params[key] = str(params[key])
        
        params["api_sig"] = self.sign_request(params)
        
        
        resp = requests.post(API_ROOT, params, headers = self.get_headers(self.info))
        self.log_request()
        data = json.loads(resp.text)
        
        try:
            raise error_codes[data["error"]](data["message"])
        except KeyError:
            pass
        
        return data


    def request_auto(self, special_params = None, pkg = None, method = None):
        """
        An automated version of :py:func:`request`, designed to reduce repetitive code.
        
        It will generate the package, method and request parameters from its
        calling function's signature. If the caller is in a class, *self* is ignored.
        If the caller is in a class whose parent or ancestor is :py:class:`Package.Package`, then the
        class' name is used as the name of the package. The caller's name, stripped of underscores,
        is used as the name of the method. Argument names are used as parameter keys, and argument
        values as parameter values. Argument names are stripped of trailing underscores,
        to permit use of keywords as parameter keys.
        
        :param special_params:
            Additional parameters merged with automatically generated ones.
            
        :type special_params:
            :class:`dict <python:dict>`
            
        :param pkg:
            The name of the package in which the method resides.
            
        :type pkg:
            :mod:`string <python:string>`
            
        :param method:
            The name of the method.
            
        :type method:
            :mod:`string <python:string>`
            
        :returns:
            The response.
            
        :rtype: :mod:`json object <python:json>`
        
        """
        
        
        frame_record = inspect.stack()[1]
    
        if(method is None):
            method = frame_record[3].replace("_", "").lower()
            
        args, _, _, locals_ = inspect.getargvalues(frame_record[0])
        params = dict((arg, locals_[arg]) for arg in args)
        
        for key, value in params.items():
            if key == "self":
                params[key] = None
                
                if isinstance(value, Package):
                    pkg = value.__class__.__name__.lower()
    
        if(special_params is not None):
            params.update(special_params)
    
        params = dict((key.rstrip('_'), params[key]) for key in params)
    
        return self.request(pkg, method, params)
    

    def sign_request(self, params):
        """
        Generates an API signature, which is needed for authorized API requests.
        
        :param params:
            All parameters intended to be sent with the request.
            
        :type params:
            dict
            
        :returns:
            The signature.
            
        :rtype:
            :mod:`string <python:string>`
        
        """
    
    
        # Parameters are alphabetically sorted by their key, and then concatenated
        # in a keyvalue manner. The application's secret is appended afterwards,
        # the whole thing is UTF-8 encoded, and then md5() hashed, hex digest of it
        # being the signature. Some parameters mustn't be included in the calculation.
    
        # Keys excluded from the calculation
        forbid_keys = ["format"]
    
        concat_params = ""
        for key in sorted(list(params)):
            if key not in forbid_keys:
                concat_params += key + params[key]
    
        concat_params += self.secret
    
        sig = hashlib.md5(concat_params.encode("utf-8")).hexdigest()
        
        return sig


    def can_request(self):
        if self.requests_logged() >= MAX_REQUESTS:
            return False
        else:
            return True
    
    
    def log_request(self):
        if self.db is None:
            return
        
        self.dbc.execute("insert into timestamps (timestamps) values (?)", (int(time.time()),))
        self.db.commit()
    
    
    def requests_logged(self):
        if self.db is None:
            return 0
        
        self.dbc.execute("delete from timestamps where timestamps < ?", (int(time.time()) - REQUEST_RATE_PERIOD,))
        self.dbc.execute("select count(timestamps) from timestamps")
        requests = self.dbc.fetchone()[0]
        self.db.commit()
        
        return requests
    
    
    def get_headers(self, info):
        if info is None:
            info = ("unknown", "unknown")
        
        user_agent = "{}/{} {}".format(info[0], info[1], USER_AGENT)
        return {"User-Agent": user_agent}
    
    
    def db_table_exists_timestamps(self):
        self.dbc.execute("select exists(select * from sqlite_master " \
                         "where type = \"table\" and name = \"timestamps\")")
        return self.dbc.fetchone()[0]
    
    
    def db_create_table_timestamps(self):
        self.dbc.execute("create table timestamps (timestamps integer)")
        self.db.commit()


#
# Utility functions
#

def to_array(xs, key):
    array = {}

    for i, x in enumerate(xs):
        array[key + "[" + str(i) + "]"] = x

    return array


def to_arrays(xs, keys):
    arrays = {}

    for x, key in zip(list(zip(*xs)), keys):
        arrays.update(to_array(x, key))

    return arrays


def class_attrs(cls):
    attrs = dict((key, value) for key, value in inspect.getmembers(cls)
                    if not callable(value) and not(key.startswith("__") and key.endswith("__")))
    
    return attrs


def class_to_arrays(cls, i = 0):
    attrs = class_attrs(cls)
    
    arrays = {}
    for key, value in attrs.items():
        arrays[key + "[" + str(i) + "]"] = value

    return arrays

def classes_to_arrays(classes):
    arrays = {}
    for i, cls in enumerate(classes):
        arrays.update(class_to_arrays(cls, i))

    return arrays

