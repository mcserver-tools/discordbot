"""Declaring data models"""

import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship

Base = sqlalchemy.ext.declarative.declarative_base()

# pylint: disable=R0903

class McServer(Base):
    """McServer representation."""

    __tablename__ = "mcserver"
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    address = sqlalchemy.Column(sqlalchemy.String, unique=True)
    ping = sqlalchemy.Column(sqlalchemy.Float)
    version = sqlalchemy.Column(sqlalchemy.String)
    online_players = sqlalchemy.Column(sqlalchemy.Integer)
    players = relationship("Player")

class Player(Base):
    """Player representation."""

    __tablename__ = "player"
    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("mcserver.mcserver_id"))
    name = sqlalchemy.Column(sqlalchemy.String)
