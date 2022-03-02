"""Module containing the InfoGetter class"""

from datetime import datetime
from threading import Thread
from time import sleep

from database import db_manager

from discordbot.info_getter_thread import InfoGetterThread
from discordbot.mcserver import McServer


class InfoGetter():
    """Class providing information getting methods"""

    def __init__(self) -> None:
        self._max_threads = 2000
        self._running_threads = 0
        self._online_servers = 0
        self._total_pinged = 0
        self._start_time = None

    def rebuild_list(self):
        """Pings all stored addresses and saves gained information"""
        self._online_servers = 0
        self._total_pinged = 0
        self._start_time = datetime.now()

        # db_manager.INSTANCE.clear_mcservers()

        for addresses in self._get_stored_addresses():
            while self._running_threads >= self._max_threads:
                sleep(1)
                db_manager.INSTANCE.commit()
                yield None

            info_getter_thread = InfoGetterThread(self)
            info_getter_thread.add_list(addresses)
            Thread(target=info_getter_thread.ping_all).start()
            self._running_threads += 1

        while self._running_threads > 0:
            sleep(1)
            db_manager.INSTANCE.commit()
            yield None

        db_manager.INSTANCE.commit()

    @staticmethod
    def _get_stored_addresses():
        addresses = []
        for address in db_manager.INSTANCE.get_addresses():
            addresses.append(address)
            if len(addresses) >= 10:
                yield addresses.copy()
                addresses.clear()

        yield addresses.copy()

    def add_server_stats(self, info_obj: McServer):
        """Adds given McServer object to the database"""
        self._online_servers += 1

        players = []
        for playername in info_obj.players:
            if len(playername.split(" ")) == 1 and len(playername.split("§")) == 1 and playername not in ["", " "]:
                players.append(playername.strip())
        info_obj.players = players

        db_manager.INSTANCE.add_mcserver_nocommit(info_obj)

    def get_status(self):
        """Returns the _total_pinged, _online_servers and _start_time properties"""
        return [self._online_servers, self._total_pinged, self._start_time]
