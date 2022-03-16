"""Module for managing the database"""

from threading import Lock

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

from model import Base, McServer, Player
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

    def clear_mcservers(self):
        """Deletes all McServer entries in the database"""

        with self.lock:
            self.session.query(McServer).delete()
            self.session.query(Player).delete()
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def add_mcserver_nocommit(self, mcserver_obj):
        """Add a McServer object to the database"""

        with self.lock:
            players = []
            for playername in mcserver_obj.players:
                temp_player = Player(name=playername)
                self.session.add(temp_player)
                players.append(temp_player)

            new_mcserver = McServer(address=mcserver_obj.address[0], ping=mcserver_obj.ping,
                                    version=mcserver_obj.version,
                                    online_players=mcserver_obj.online_players,
                                    players=players)
            self.session.add(new_mcserver)

    def commit(self):
        """Commits changes to database"""

        with self.lock:
            try:
                self.session.commit()
            except sqlalchemy.exc.IntegrityError:
                self.session.rollback()

    def get_mcservers(self):
        """Returns all McServer objects in the database"""

        with self.lock:
            ret_list = [McServerObj((item.address, "25565"), item.ping, item.version,
                                    item.online_players, [player.name for player in item.players])
                        for item in self.session.query(McServer).all()]
        return ret_list

    def get_number_of_mcservers(self):
        """Returns the number of McServer objects in the database"""

        return self.session.query(McServer).count()
