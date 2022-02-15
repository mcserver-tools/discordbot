from mcstatus import MinecraftServer

from discordbot.mcserver import McServer

class InfoGetterThread():
    def __init__(self, info_getter, addresses) -> None:
        self.info_getter = info_getter
        self.addresses = addresses

    def ping_all(self):
        for address in self.addresses:
            self._ping_address_with_return(address)
            self.info_getter._total_pinged += 1

        self.info_getter._running_threads -= 1

    def _ping_address_with_return(self, address):
        try:
            status = MinecraftServer(address, 25565).status()
            info_obj = McServer((address, 25565), status.latency, status.version.name, status.players.online)
        except:
            return
        self.info_getter._add_server_stats(info_obj)
