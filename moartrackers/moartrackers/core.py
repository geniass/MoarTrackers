#
# core.py
#
# Copyright (C) 2009 geniass <geniassmchlachla@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from HTMLParser import HTMLParser
import urllib2

DEFAULT_PREFS = {
    "test":"NiNiNi"
}

"""Parses torrentz.eu to find the announcelist"""
class TorrentzHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.announcelist_url = "http://torrentz.eu"

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for name, value in attrs:
                if name == 'href':
                    if 'announcelist' in value:
                        self.announcelist_url = self.announcelist_url + value
                        log.info("Found announcelist: %s" % self.announcelist_url)
    def get_announcelist_url(self):
        if self.announcelist_url == "http://torrentz.eu":
            log.info("No announcelist found")
            raise Exception("The torrent hash doesn't exist on torrentz.eu")
        else:
            return self.announcelist_url





class Core(CorePluginBase):
    def enable(self):
        #self.config = deluge.configmanager.ConfigManager("moartrackers.conf", DEFAULT_PREFS)
        event_manager = component.get("EventManager")
        event_manager.register_event_handler("TorrentAddedEvent", self.on_torrent_added_event)
        log.info("MoarTrackers started")


    def disable(self):
        log.info("Stopping MoarTrackers")
        event_manager = component.get("EventManager")
        event_manager.deregister_event_handler("TorrentAddedEvent", self.on_torrent_added_event)

    def update(self):
        pass


    def on_torrent_added_event(self,torrent_id, *arg):
        log.info("MoarTrackers: on_torrent_added_event (torrent_id=%s)" % torrent_id)
        try:
            #log.info("torrent_id: %d" % torrent_id)
            torrent = component.get("TorrentManager").torrents[torrent_id]
            data = torrent.get_status(["name","is_finished"])
            log.info(data)

            if not data["is_finished"]:
                response = urllib2.urlopen("http://torrentz.eu/%s" % torrent_id)
                htmlParser = TorrentzHTMLParser()
                htmlParser.feed(response.read())
                
                tracker_page = urllib2.urlopen(htmlParser.get_announcelist_url()).read()
                trackers = tracker_page.split()
                tracker_list = []
                for t in trackers:
                    tracker_dict = {"tier":0}
                    tracker_dict["url"] = t
                    tracker_list.append(tracker_dict)
                log.info(tracker_list)

                torrent.set_trackers(tracker_list)

        except Exception as e:
            log.info(e.strerror)


   
