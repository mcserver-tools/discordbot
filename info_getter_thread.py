"""Module containing the InfoGetterThread class"""

from mcstatus import MinecraftServer

from mcserver import McServer

class InfoGetterThread():
    """Class that pings every address provided"""

    def __init__(self, info_getter, function_after_success) -> None:
        self.info_getter = info_getter
        self._function_after_success = function_after_success
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
            players = self._get_playernames(server, status)

            info_obj = McServer((address, 25565), status.latency, status.version.name,
                            status.players.online, players)
            self.info_getter._online_servers += 1
            self._function_after_success(info_obj)
        except TimeoutError:
            return
        except ConnectionAbortedError:
            return
        except ConnectionResetError:
            return
        except IOError:
            return
        except KeyError as keyerr:
            if "text" in keyerr.args or "#" in keyerr.args:
                print("Retrying...")
                return self._ping_address_with_return(address)
        except IndexError as indexerr:
            if "bytearray" in indexerr.args:
                print("Retrying...")
                return self._ping_address_with_return(address)

    @staticmethod
    def _get_playernames(server: MinecraftServer, old_status):
        if old_status.players.sample is None:
            return []
        players = [(item.name, item.id) for item in old_status.players.sample]
        if old_status.players.online > 12:
            found_players = 12
            tries = 10
            online_players = old_status.players.online
            while found_players < online_players and tries > 0:
                status = server.status()
                tries -= 1
                if status.players.sample is not None:
                    for item in status.players.sample:
                        if not item in players:
                            found_players += 1
                            players.append((item.name, item.id))
        return players
