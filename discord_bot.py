"""Module containing the DiscordBot class"""

from datetime import datetime
from random import Random
from time import sleep
import importlib.util

import discord
from mcstatus import MinecraftServer

from db_manager import DBManager
from info_getter import InfoGetter
from mcserver import McServer

class DiscordBot(discord.Client):
    """Class providing a discord bot"""

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self._info_getter = InfoGetter()

    def start_bot(self):
        """Start the discord bot"""
        with open("discordbot/dc_token.txt", "r", encoding="utf-8") as file:
            token = file.readline()
        self.run(token)

    async def on_ready(self):
        """Builtin for when the bot is ready to use"""
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        """Builtin for when a user sends a message"""
        if message.author.id == self.user.id:
            return

        if message.content[0] == "$":
            msg_text = message.content[1::]
            if msg_text.startswith("hello"):
                await self._hello_command(message)
            elif msg_text.startswith("rebuild"):
                await self._rebuild_command(message)
            elif msg_text.startswith("top"):
                await self._top_command(message)
            elif msg_text.startswith("embed"):
                embed_var = discord.Embed(title="Title", description="Desc", color=0x00ff00)
                embed_var.add_field(name="Field1", value="hi", inline=False)
                embed_var.add_field(name="Field2", value="hi2", inline=False)
                await message.channel.send(embed=embed_var)

    async def _rebuild_command(self, message):
        spec = importlib.util.spec_from_file_location("db_manager",
                                                      __file__.rsplit("\\", maxsplit=2)[0]
                                                      + "\\pingserver\\db_manager.py")
        db_manager_server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_manager_server_module)
        db_manager_server = db_manager_server_module.DBManager()

        DBManager.INSTANCE.clear_mcservers()

        msg = [message]
        total_elements = db_manager_server.get_number_of_addresses()
        embed_var = discord.Embed(title="Rebuilding list...", color=0x00ff00)
        wait_msg = await message.reply(embed=embed_var)

        for item in self._info_getter.rebuild_list(db_manager_server):
            status = self._info_getter.get_status()
            embed_var = discord.Embed(title="Rebuilding list...", color=0x00ff00)
            embed_var.add_field(name="Total", value=f"{status[1]}/{total_elements}", inline=False)
            embed_var.add_field(name="Responded", value=f"{status[0]}", inline=False)
            embed_var.add_field(name="No response", value=f"{status[1] - status[0]}", inline=False)
            embed_var.add_field(name="Elapsed",
                                value=f"{str(datetime.now()-status[2]).split('.', maxsplit=1)[0]}",
                                inline=False)
            await wait_msg.edit(embed=embed_var)

        await wait_msg.delete()
        status = self._info_getter.get_status()
        embed_var = discord.Embed(title="Rebuild completed!", color=0x00ff00)
        embed_var.add_field(name="Total", value=f"{total_elements}", inline=False)
        embed_var.add_field(name="Online", value=f"{status[0]}", inline=False)
        msg.append(await message.reply(embed=embed_var))
        sleep(10)

        for item in msg:
            await item.delete()

    @staticmethod
    async def _top_command(message):
        msg = [message]
        if len(message.content.split(" ")) == 1:
            count = 5
        else:
            count = int(message.content.split(" ")[1])

        mcservers_list = DBManager.INSTANCE.get_mcservers()
        mcservers_list.sort(key=lambda x:x.online_players, reverse=True)

        for item in mcservers_list[:count:]:
            msg.append(await message.reply(embed=item.embed("Top servers")))

        sleep(count * 5)

        for item in msg:
            await item.delete()

    async def _hello_command(self, message):
        msg = [message]

        msg.append(await message.reply('Hello!', mention_author=True))

        wait_msg = await message.reply("Getting random address...")
        info_obj = self._get_random_address()
        await wait_msg.delete()
        msg.append(await message.reply(embed=info_obj.embed("A randomly chosen mc server ip")))

        sleep(15)

        for item in msg:
            await item.delete()

    def _get_random_address(self):
        spec = importlib.util.spec_from_file_location("db_manager",
                                                      __file__.rsplit("\\", maxsplit=2)[0]
                                                      + "\\pingserver\\db_manager.py")
        db_manager_server_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_manager_server_module)
        db_manager_server = db_manager_server_module.DBManager()

        address_count = db_manager_server.get_number_of_addresses()
        rnd = Random()
        info_obj = None
        counter = 0

        while info_obj is None or len(info_obj.players) == 0:
            rnd_number = rnd.randint(1, address_count)
            address = db_manager_server.get_address(rnd_number)
            info_obj = self._ping_address_with_return(address)
            counter += 1
            print(f"Tried {counter} addresses...", end="\r")

        print(f"Tried {counter} addresses...")
        return info_obj

    def _ping_address_with_return(self, address):
        try:
            server = MinecraftServer(address, 25565)
            status = server.status()
            if status.players.sample is not None:
                players = self._get_playernames(server)
            else:
                players = []

            return McServer((address, 25565), status.latency, status.version.name,
                            status.players.online, players)
        except TimeoutError:
            return None
        except ConnectionAbortedError:
            return None
        except ConnectionResetError:
            return None
        except IOError:
            return None

    @staticmethod
    def _get_playernames(server: MinecraftServer):
        status = server.status()
        players = [item.name for item in status.players.sample]
        if status.players.online > 12:
            found_players = 12
            tries = 10
            online_players = status.players.online
            while found_players < online_players and tries > 0:
                status = server.status()
                tries -= 1
                for item in status.players.sample:
                    if not item in players:
                        found_players += 1
                        players.append(item.name)
        return players
