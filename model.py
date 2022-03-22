"""Declaring data models"""

import datetime
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
    version = sqlalchemy.Column(sqlalchemy.String)
    statuses = relationship("Status", lazy='noload')

class Status(Base):
    """Status representation."""

    __tablename__ = "status"
    status_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    mcserver_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("mcserver.mcserver_id"))
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    ping = sqlalchemy.Column(sqlalchemy.Float)
    online_players = sqlalchemy.Column(sqlalchemy.Integer)
    statusplayers = relationship("StatusPlayer")

class Player(Base):
    """Player representation."""

    __tablename__ = "player"
    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    uuid = sqlalchemy.Column(sqlalchemy.String, unique=True)
    statusplayers = relationship("StatusPlayer")

class StatusPlayer(Base):
    """Status and Player crosstable."""

    __tablename__ = "statusplayer"
    statusplayer_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    status_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("status.status_id"))
    player_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("player.player_id"))
