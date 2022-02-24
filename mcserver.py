"""Module containing the McServer data object"""

from typing import List, Tuple

import discord

class McServer():
    """McServer data object, containing address, ping, version and players"""

    def __init__(self, address: Tuple[str, int], ping: float, version: str, online_players: int, players: List[str]) -> None:
        self.address = address
        self.ping = f"{ping:0.2f}"
        self.version = version
        self.online_players = online_players
        self.players = players

    def embed(self, title: str) -> discord.Embed:
        """Return the data object as an discord embed"""
        embed_var = discord.Embed(title=title, color=0x00ff00)
        embed_var.add_field(name="Address", value=f"{self.address[0]}:{self.address[1]}",
                           inline=False)
        embed_var.add_field(name="Ping", value=f"{self.ping} ms", inline=False)
        embed_var.add_field(name="Version", value=f"{self.version}", inline=False)
        embed_var.add_field(name="Online players", value=f"{self.online_players}", inline=False)
        embed_var.add_field(name="Players", value=f"{str(self.players)}", inline=False)
        return embed_var

    def __str__(self) -> str:
        return f"Address: {self.address}, Ping: {self.ping}, Version: {self.version},\
                 Online players: {self.online_players}, Players: {str(self.players)}"
