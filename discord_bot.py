from datetime import datetime
from random import Random
from time import sleep

import discord
from mcstatus import MinecraftServer

from database import db_manager
from discordbot.info_getter import InfoGetter
from discordbot.mcserver import McServer

class DiscordBot(discord.Client):
    def __init__(self, info_getter: InfoGetter, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        self._info_getter = InfoGetter()

    def Start(self):
        token = open("discordbot/dc_token.txt").readline()
        self.run(token)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        # we do not want the bot to reply to itself
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
                embedVar = discord.Embed(title="Title", description="Desc", color=0x00ff00)
                embedVar.add_field(name="Field1", value="hi", inline=False)
                embedVar.add_field(name="Field2", value="hi2", inline=False)
                await message.channel.send(embed=embedVar)

    async def _rebuild_command(self, message):
        msg = [message]
        total_elements = db_manager.instance.get_number_of_addresses()
        embedVar = discord.Embed(title="Rebuilding list...", color=0x00ff00)
        wait_msg = await message.reply(embed=embedVar)

        for item in self._info_getter.rebuild_list():
            embedVar = discord.Embed(title="Rebuilding list...", color=0x00ff00)
            embedVar.add_field(name="Total", value=f"{self._info_getter._total_pinged}/{total_elements}", inline=False)
            embedVar.add_field(name="Responded", value=f"{self._info_getter._online_servers}", inline=False)
            embedVar.add_field(name="No response", value=f"{self._info_getter._total_pinged - self._info_getter._online_servers}", inline=False)
            embedVar.add_field(name="Elapsed", value=f"{datetime.now() - self._info_getter._start_time}", inline=False)
            await wait_msg.edit(embed=embedVar)

        await wait_msg.delete()
        embedVar = discord.Embed(title="Rebuild completed!", color=0x00ff00)
        embedVar.add_field(name="Total", value=f"{total_elements}", inline=False)
        embedVar.add_field(name="Online", value=f"{self._info_getter._online_servers}", inline=False)
        msg.append(await message.reply(embed=embedVar))
        sleep(10)

        for item in msg:
            await item.delete()

    async def _top_command(self, message):
        msg = [message]
        if len(message.content.split(" ")) == 1:
            count = 5
        else:
            count = int(message.content.split(" ")[1])

        mcservers_list = db_manager.instance.get_mcservers()
        mcservers_list.sort(key=lambda x:x.players, reverse=True)

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

        sleep(10)

        for item in msg:
            await item.delete()

    def _get_random_address(self):
        rnd = Random()
        info_obj = None
        c = 0

        while info_obj == None or info_obj.players == 0:
            length = db_manager.instance.get_number_of_addresses()
            rnd_number = rnd.randint(1, length)
            address = db_manager.instance.get_address(rnd_number)
            info_obj = self._ping_address_with_return(address)
            c += 1
            print(f"Tried {c} addresses...", end="\r")

        print(f"Tried {c} addresses...")
        return info_obj

    def _ping_address_with_return(self, address):
        try:
            status = MinecraftServer(address, 25565).status()
            return McServer((address, 25565), status.latency, status.version.name, status.players.online)
        except:
            return None
