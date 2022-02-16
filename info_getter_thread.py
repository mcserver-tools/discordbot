from mcstatus import MinecraftServer

from discordbot.mcserver import McServer

class InfoGetterThread():
    def __init__(self, info_getter, input_list) -> None:
        self.info_getter = info_getter
        self.input_list = input_list
        self.update_players = False
        if type(input_list[0]) == McServer:
            self.update_players = True

    def ping_all(self):
        for item in self.input_list:
            if not self.update_players:
                self._ping_address_with_return(item)
            else:
                self._ping_address_with_return(item.address[0])
            self.info_getter._total_pinged += 1

        self.info_getter._running_threads -= 1

    def _ping_address_with_return(self, address):
        try:
            status = MinecraftServer(address, 25565).status()
            info_obj = McServer((address, 25565), status.latency, status.version.name, status.players.online)
        except:
            return

        if not self.update_players:
            self.info_getter._add_server_stats(info_obj)
        else:
            self.info_getter._update_players(info_obj)
