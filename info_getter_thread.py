"""Module containing the InfoGetterThread class"""

from mcstatus import MinecraftServer

from discordbot.mcserver import McServer

class InfoGetterThread():
    """Class that pings every address provided"""

    def __init__(self, info_getter) -> None:
        self.info_getter = info_getter
        self.input_list = []

    def add_list(self, input_list):
        """Add a list containing all the addresses"""
        self.input_list = input_list

    def ping_all(self):
        """Pings all given addresses"""
        for item in self.input_list:
            self._ping_address_with_return(item)
            self.info_getter._total_pinged += 1

        self.info_getter._running_threads -= 1

    def _ping_address_with_return(self, address):
        try:
            server = MinecraftServer(address, 25565)
            status = server.status()
            if status.players.sample is not None:
                players = [item.name for item in status.players.sample]
                if status.players.online > 12:
                    c = 12
                    tries = 10
                    online = status.players.online
                    while c < online and tries > 0:
                        status = server.status()
                        tries -= 1
                        for item in status.players.sample:
                            if not item in players:
                                c += 1
                                players.append(item.name)
            else:
                players = []

            info_obj = McServer((address, 25565), status.latency, status.version.name,
                            status.players.online, players)

        except TimeoutError:
            return None
        except ConnectionAbortedError:
            return None
        except ConnectionResetError:
            return None
        except IOError:
            return None

        self.info_getter.add_server_stats(info_obj)
