# -*- coding: utf-8 -*-
"""
ivr.ivc.daos.models
~~~~~~~~~~~~~~~~~~~~~~~

This module implements the domain models for the IVC WSGI application,
based on the SQLAlchemy's ORM

:copyright: (c) 2015 by OpenSight (www.opensight.cn).

"""
from __future__ import unicode_literals, division
from sqlalchemy import Column, ForeignKey, text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Float, Text, \
    BigInteger, CHAR, Boolean, TIMESTAMP, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from ...common.utils import STRING, encode_json
import json


Base = declarative_base()


class SACamera(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'camera'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(length=36, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    device_uuid = Column(CHAR(length=36, convert_unicode=True),
                         ForeignKey('device.uuid', onupdate="CASCADE", ondelete="CASCADE"),
                         nullable=False, server_default="")
    channel_index = Column(Integer, nullable=False, server_default=text("0"))
    name = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(String(length=1024, convert_unicode=True), nullable=False, server_default="")
    longitude = Column(Float, server_default="0.0", nullable=False)
    latitude = Column(Float, server_default="0.0", nullable=False)
    altitude = Column(Float, server_default="0.0", nullable=False)
    project_name = Column(String(length=64, convert_unicode=True),
                          ForeignKey('project.name', onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False, server_default="")
    flags = Column(Integer, nullable=False, server_default=text("0"))
    is_online = Column(SmallInteger, nullable=False, server_default=text("0"))
    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    utime = Column(TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    device = relationship("SADevice", back_populates="cameras")
    project = relationship("SAProject", back_populates="cameras")

    def __repr__(self):
        return "SA Camera Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )


class SADevice(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'device'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(length=36, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    name = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    type = Column(String(length=32, convert_unicode=True), nullable=False, server_default="IVT")
    firmware_model = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    hardware_model = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    media_channel_num = Column(Integer, nullable=False, server_default=text("0"))
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(String(length=1024, convert_unicode=True), nullable=False, server_default="")
    longitude = Column(Float, server_default="0.0", nullable=False)
    latitude = Column(Float, server_default="0.0", nullable=False)
    altitude = Column(Float, server_default="0.0", nullable=False)
    project_name = Column(String(length=64, convert_unicode=True),
                          ForeignKey('project.name', onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False, server_default="")
    flags = Column(Integer, nullable=False, server_default=text("0"))
    is_online = Column(SmallInteger, nullable=False, server_default=text("0"))
    login_code = Column(String(length=64, convert_unicode=True),
                        nullable=False, index=True, unique=True)
    login_passwd = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")
    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    utime = Column(TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ltime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))

    cameras = relationship("SACamera", order_by=SACamera._id, back_populates="device")
    project = relationship("SAProject", back_populates="devices")


    def __repr__(self):
        return "SA Device Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )

project_user_relation = Table('project_user_relation', Base.metadata,
                              Column('id', BigInteger, nullable=False, primary_key=True, autoincrement=True),
                              Column('user_username', String(length=64, convert_unicode=True),
                                      ForeignKey('user.username', onupdate="CASCADE", ondelete="CASCADE"),
                                     nullable=False),
                              Column('project_name', String(length=64, convert_unicode=True),
                                     ForeignKey('project.name', onupdate="CASCADE", ondelete="CASCADE"),
                                     nullable=False)
                              )


class SAProject(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'project'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String(length=64, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    title = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(String(length=1024, convert_unicode=True), nullable=False, server_default="")
    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    utime = Column(TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    max_media_sessions = Column(Integer, nullable=False, server_default=text("0"))

    cameras = relationship("SACamera", order_by=SACamera._id, back_populates="project")
    devices = relationship("SADevice", order_by=SADevice._id, back_populates="project")
    users = relationship('SAUser', secondary=project_user_relation,
                         back_populates="projects")

    def __repr__(self):
        return "SA Project Object(name:%s)" % (
            self.name
        )


class SAUser(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'user'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    username = Column(String(length=64, convert_unicode=True),
                      nullable=False, index=True, unique=True)
    password = Column(String(length=64, convert_unicode=True),
                      nullable=False, server_default="")
    title = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(String(length=1024, convert_unicode=True), nullable=False, server_default="")

    cellphone = Column(String(length=32, convert_unicode=True), nullable=False, server_default="")
    email = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")

    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    utime = Column(TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ltime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))

    projects = relationship('SAProject', secondary=project_user_relation,
                            back_populates="users")

    def __repr__(self):
        return "SA User Object(name:%s)" % (
            self.username
        )


