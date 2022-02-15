from threading import Thread
from time import sleep
from datetime import datetime
from discordbot.info_getter_thread import InfoGetterThread
from database import db_manager
from discordbot.mcserver import McServer

class InfoGetter():
    def __init__(self) -> None:
        self._max_threads = 2000
        self._running_threads = 0
        self._online_servers = 0
        self._total_pinged = 0
        self._start_time = None

    def rebuild_list(self):
        self._online_servers = 0
        self._total_pinged = 0
        self._start_time = datetime.now()

        db_manager.instance.clear_mcservers()

        for addresses in self._get_stored_addresses():
            while self._running_threads >= self._max_threads:
                sleep(1)
                yield None

            info_getter_thread = InfoGetterThread(self, addresses)
            Thread(target=info_getter_thread.ping_all).start()
            self._running_threads += 1

        while self._running_threads > 0:
            sleep(1)
            yield None

    def _get_stored_addresses(self):
        addresses = []
        for address in db_manager.instance.get_addresses():
            addresses.append(address)
            if len(addresses) >= 10:
                yield addresses.copy()
                addresses.clear()

        yield addresses.copy()

    def _add_server_stats(self, info_obj: McServer):
        self._online_servers += 1
        db_manager.instance.add_mcserver(info_obj)
