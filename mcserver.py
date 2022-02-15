from typing import Tuple

import discord

class McServer():
    def __init__(self, address: Tuple[str, int], ping: float, version: str, players: int) -> None:
        self.address = address
        self.ping = "{:0.2f}".format(ping)
        self.version = version
        self.players = players

    def embed(self, title: str) -> discord.Embed:
        embedVar = discord.Embed(title=title, color=0x00ff00)
        embedVar.add_field(name="Address", value=f"{self.address[0]}:{self.address[1]}", inline=False)
        embedVar.add_field(name="Ping", value=f"{self.ping} ms", inline=False)
        embedVar.add_field(name="Version", value=f"{self.version}", inline=False)
        embedVar.add_field(name="Players", value=f"{self.players}", inline=False)
        return embedVar

    def __str__(self) -> str:
        return f"Address: {self.address}, Ping: {self.ping}, Version: {self.version}, Players: {self.players}"
