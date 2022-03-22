"""Module for managing the database"""

from threading import Lock

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from model import Base, McServer, Player, Status, StatusPlayer
from mcserver import McServer as McServerObj

# pylint: disable=R0801

class DBManager():
    """Class that manages the database"""

    def __init__(self):
        if DBManager.INSTANCE is None:
            db_connection = sqlalchemy.create_engine("sqlite:///discordbot/mcservers.db",
                                                     connect_args={'check_same_thread': False})
            Base.metadata.create_all(db_connection)

            session_factory = sessionmaker(db_connection, autoflush=False)
            _session = scoped_session(session_factory)
            self.session = _session()

            self.lock = Lock()

            DBManager.INSTANCE = self

    INSTANCE = None

    def add_mcserver_nocommit(self, mcserver_obj: McServerObj):
        """Add a McServer object to the database"""

        with self.lock:
            new_mcserver = McServer(address=mcserver_obj.address[0], version=mcserver_obj.version,
                                    statuses=[])
            self.session.add(new_mcserver)
            return new_mcserver

    def add_status_nocommit(self, mcserver_obj: McServerObj):
        """Add a McServer object as a Status object"""

        self.lock.acquire()
        
        mcserver_db = self.session.query(McServer).filter(McServer.address==mcserver_obj.address[0]).first()
        if mcserver_db == None:
            # print("Address couldn't be found in the database: " + mcserver_obj.address[0])
            self.lock.release()
            mcserver_db = self.add_mcserver_nocommit(mcserver_obj)
            self.lock.acquire()

        statusplayers = []
        for playername in mcserver_obj.players:
            temp_player = self.session.query(Player).filter(Player.uuid==playername[1]).first()
            if temp_player is None:
                temp_player = Player(name=playername[0], uuid=playername[1])
                self.session.add(temp_player)
            temp_statusplayer = StatusPlayer()
            temp_player.statusplayers.append(temp_statusplayer)
            self.session.add(temp_statusplayer)
            statusplayers.append(temp_statusplayer)

        new_status = Status(ping=mcserver_obj.ping, online_players=mcserver_obj.online_players)
        for item in statusplayers:
            new_status.statusplayers.append(item)
        self.session.add(new_status)
        mcserver_db.statuses.append(new_status)

        self.lock.release()

    def commit(self):
        """Commits changes to database"""

        with self.lock:
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def get_mcserver(self, address):
        """Return the McServer with the given address"""

        with self.lock:
            mcserver_db = self.session.query(McServer).filter(McServer.address==address).first()
            if mcserver_db is None:
                return None
            status = mcserver_db.statuses[-1]
            players = []
            for statusplayer in status.statusplayers:
                player = self.session.query(Player).get(statusplayer.player_id)
                players.append((player.name, player.uuid))
            return McServerObj((address, 25565), status.ping, mcserver_db.version, status.online_players, players)

    def get_mcservers(self):
        """Returns all McServer objects in the database"""

        with self.lock:
            ret_list = [McServerObj((item.address, "25565"), item.ping, item.version,
                                    item.online_players, [(player.name, player.uuid) for player in item.players])
                        for item in self.session.query(McServer).all()]
        return ret_list

    def get_number_of_mcservers(self):
        """Returns the number of McServer objects in the database"""

        return self.session.query(McServer).count()
