"""Main module of the discordbot"""

from db_manager import DBManager
from discord_bot import DiscordBot

if __name__ == "__main__":
    DBManager()
    DiscordBot().start_bot()
