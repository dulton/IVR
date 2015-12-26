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

    def from_camera(self, camera):
        self.uuid = camera.uuid
        self.device_uuid = camera.device_uuid
        self.channel_index = camera.channel_index
        self.name = camera.name
        self.flags = camera.flags
        self.is_online = camera.is_online
        self.desc = camera.desc
        self.long_desc = camera.long_desc
        self.longitude = camera.longitude
        self.latitude = camera.latitude
        self.altitude = camera.altitude
        self.project_name = camera.project_name
        self.ctime = camera.ctime
        self.utime = camera.utime

    def to_camera(self, camera_cls):
        camera = camera_cls(project_name=self.project_name,
                            uuid=self.uuid,
                            device_uuid=self.device_uuid,
                            channel_index=self.channel_index,
                            name=self.name,
                            flags=self.flags,
                            is_online=self.is_online,
                            desc=self.desc,
                            long_desc=self.long_desc,
                            longitude=self.longitude,
                            latitude=self.latitude,
                            altitude=self.altitude,
                            ctime=self.ctime,
                            utime=self.utime)
        return camera

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

    cameras = relationship("SACamera", order_by=SACamera.id, back_populates="device")
    project = relationship("SAProject", back_populates="devices")


    def __repr__(self):
        return "SA Device Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )

    def from_device(self, device):
        self.uuid = device.uuid
        self.name = device.name
        self.flags = device.flags
        self.type = device.type
        self.firmware_model = device.firmware_model
        self.hardware_model = device.hardware_model
        self.media_channel_num = device.media_channel_num
        self.is_online = device.is_online
        self.desc = device.desc
        self.long_desc = device.long_desc
        self.longitude = device.longitude
        self.latitude = device.latitude
        self.altitude = device.altitude
        self.project_name = device.project_name
        self.ctime = device.ctime
        self.utime = device.utime
        self.ltime = device.ltime
        self.login_code = device.login_code
        self.login_passwd = device.login_passwd

    def to_device(self, device_cls):
        device = device_cls(project_name=self.project_name,
                            uuid=self.uuid, name=self.name,
                            type=self.type,
                            firmware_model=self.firmware_model,
                            hardware_model=self.hardware_model,
                            flags=self.flags,
                            is_online=self.is_online,
                            desc=self.desc, long_desc=self.long_desc,
                            media_channel_num=self.media_channel_num,
                            login_code=self.login_code,
                            login_passwd=self.login_passwd,
                            longitude=self.longitude,
                            latitude=self.latitude,
                            altitude=self.altitude,
                            ctime=self.ctime, utime=self.utime,
                            ltime=self.ltime)
        return device

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

    cameras = relationship("SACamera", order_by=SACamera.id, back_populates="project")
    devices = relationship("SADevice", order_by=SADevice.id, back_populates="project")
    users = relationship('SAUser', secondary=project_user_relation,
                         back_populates="projects")

    def __repr__(self):
        return "SA Project Object(name:%s)" % (
            self.name
        )

    def from_project(self, project):
        self.name = project.name
        self.title = project.title
        self.desc = project.desc
        self.long_desc = project.long_desc
        self.ctime = project.ctime
        self.utime = project.utime
        self.max_media_sessions = project.max_media_sessions

    def to_project(self, project_cls):
        return project_cls(name=self.name, title=self.title,
                           desc=self.desc, long_desc=self.long_desc,
                           max_media_sessions=self.max_media_sessions,
                           ctime=self.ctime, utime=self.utime)

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


