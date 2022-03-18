import importlib.util
import discord
from datetime import datetime
from time import sleep

from info_getter import InfoGetter
from db_manager import DBManager

spec = importlib.util.spec_from_file_location("db_manager",
                                                __file__.rsplit("\\", maxsplit=2)[0]
                                                + "\\pingserver\\db_manager.py")
db_manager_server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_manager_server_module)
db_manager_server = db_manager_server_module.DBManager()

async def status_command(message):
    msg = [message]
    total_elements = db_manager_server.get_number_of_addresses()
    embed_var = discord.Embed(title="Adding status...", color=0x00ff00)
    wait_msg = await message.reply(embed=embed_var)

    info_getter = InfoGetter()

    for item in info_getter.ping_addresses(_rebuild_iterator, _add_status):
        status = info_getter.get_status()
        embed_var = discord.Embed(title="Adding status...", color=0x00ff00)
        embed_var.add_field(name="Total", value=f"{status[1]}/{total_elements}", inline=False)
        embed_var.add_field(name="Responded", value=f"{status[0]}", inline=False)
        embed_var.add_field(name="No response", value=f"{status[1] - status[0]}", inline=False)
        embed_var.add_field(name="Elapsed",
                            value=f"{str(datetime.now()-status[2]).split('.', maxsplit=1)[0]}",
                            inline=False)
        await wait_msg.edit(embed=embed_var)

        DBManager.INSTANCE.commit()

    await wait_msg.delete()
    status = info_getter.get_status()
    embed_var = discord.Embed(title="Status adding completed!", color=0x00ff00)
    embed_var.add_field(name="Total", value=f"{total_elements}", inline=False)
    embed_var.add_field(name="Online", value=f"{status[0]}", inline=False)
    msg.append(await message.reply(embed=embed_var))

    DBManager.INSTANCE.commit()
    print(DBManager.INSTANCE.not_found)
    sleep(10)

    for item in msg:
        await item.delete()

async def rebuild_command(message):
    msg = [message]
    total_elements = db_manager_server.get_number_of_addresses()
    embed_var = discord.Embed(title="Rebuilding list...", color=0x00ff00)
    wait_msg = await message.reply(embed=embed_var)

    info_getter = InfoGetter(1000)

    for item in info_getter.ping_addresses(_rebuild_iterator, _add_mcserver):
        status = info_getter.get_status()
        embed_var = discord.Embed(title="Rebuilding list...", color=0x00ff00)
        embed_var.add_field(name="Total", value=f"{status[1]}/{total_elements}", inline=False)
        embed_var.add_field(name="Responded", value=f"{status[0]}", inline=False)
        embed_var.add_field(name="No response", value=f"{status[1] - status[0]}", inline=False)
        embed_var.add_field(name="Elapsed",
                            value=f"{str(datetime.now()-status[2]).split('.', maxsplit=1)[0]}",
                            inline=False)
        await wait_msg.edit(embed=embed_var)

        DBManager.INSTANCE.commit()

    await wait_msg.delete()
    status = info_getter.get_status()
    embed_var = discord.Embed(title="Rebuild completed!", color=0x00ff00)
    embed_var.add_field(name="Total", value=f"{total_elements}", inline=False)
    embed_var.add_field(name="Online", value=f"{status[0]}", inline=False)
    msg.append(await message.reply(embed=embed_var))

    DBManager.INSTANCE.commit()
    sleep(10)

    for item in msg:
        await item.delete()

def _rebuild_iterator():
    addresses = []
    for address in db_manager_server.get_addresses():
        addresses.append(address)
        if len(addresses) >= 10:
            yield addresses.copy()
            addresses.clear()
    yield addresses.copy()

def _add_mcserver(info_obj):
    """Adds given McServer object to the database"""

    players = []
    for playername in info_obj.players:
        if len(playername[0].split(" ")) == 1 and len(playername[0].split("§")) == 1 and \
            playername[0] not in ["", " "]:
            players.append((playername[0].strip(), playername[1]))
    info_obj.players = players

    DBManager.INSTANCE.add_mcserver_nocommit(info_obj)

def _add_status(info_obj):
    """Adds given McServer object as a status to the database"""

    players = []
    for playername in info_obj.players:
        if len(playername[0].split(" ")) == 1 and len(playername[0].split("§")) == 1 and \
            playername[0] not in ["", " "]:
            players.append((playername[0].strip(), playername[1]))
    info_obj.players = players

    DBManager.INSTANCE.add_status_nocommit(info_obj)
