"""Module containing the InfoGetter class"""

from datetime import datetime
from threading import Thread
from time import sleep

from db_manager import DBManager
from info_getter_thread import InfoGetterThread

class InfoGetter():
    """Class providing information getting methods"""

    def __init__(self, max_threads = 100) -> None:
        self._max_threads = max_threads
        self._running_threads = 0
        self._online_servers = 0
        self._total_pinged = 0
        self._start_time = None

    def ping_addresses(self, address_iterator, success_callback):
        self._start_time = datetime.now()

        for addresses in address_iterator():
            while self._running_threads >= self._max_threads:
                sleep(1)
                yield None

            info_getter_thread = InfoGetterThread(self, success_callback)
            info_getter_thread.add_list(addresses)
            Thread(target=info_getter_thread.ping_all).start()
            self._running_threads += 1

        while self._running_threads > 0:
            sleep(1)
            yield None

    def finished(self):
        return self._running_threads == 0 and self._total_pinged > 0

    def get_status(self):
        """Returns the _total_pinged, _online_servers and _start_time properties"""
        return [self._online_servers, self._total_pinged, self._start_time]
