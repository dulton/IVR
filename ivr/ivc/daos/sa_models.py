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
    is_online = Column(SmallInteger, nullable=False, server_default=text("0"))     # 0: offline  1: online   2: broadcast
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
    is_public = Column(Boolean(), nullable=False, server_default=text("0"))
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
        self.is_public = project.is_public

    def to_project(self, project_cls):
        return project_cls(name=self.name, title=self.title,
                           desc=self.desc, long_desc=self.long_desc,
                           max_media_sessions=self.max_media_sessions,
                           is_public=self.is_public,
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
    flags = Column(Integer, nullable=False, server_default=text("0"))
    cellphone = Column(String(length=32, convert_unicode=True), nullable=False, server_default="")
    email = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")

    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    utime = Column(TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ltime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))

    projects = relationship('SAProject', secondary=project_user_relation,
                            back_populates="users")
    access_keys = relationship("SAAccessKey", order_by=SAAccessKey.id, back_populates="user")

    def __repr__(self):
        return "SA User Object(name:%s)" % (
            self.username
        )

    def from_user(self, user):
        self.username = user.username
        self.password = user.password
        self.title = user.title
        self.desc = user.desc
        self.long_desc = user.long_desc
        self.flags = user.flags
        self.cellphone = user.cellphone
        self.email = user.email
        self.ctime = user.ctime
        self.utime = user.utime
        self.ltime = user.ltime

    def to_user(self, user_cls):
        return user_cls(username=self.username, password=self.password,
                        title=self.title,
                        desc=self.desc, long_desc=self.long_desc,
                        flags=self.flags, cellphone=self.cellphone,
                        email=self.email, ctime=self.ctime, utime=self.utime,
                        ltime=self.ltime)


class SASessionLog(Base):
    """ The SQLAlchemy declarative model class for a session log object. """
    __tablename__ = 'sessionlog'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(length=36, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    project_name = Column(String(length=64, convert_unicode=True),
                          ForeignKey('project.name', onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False, server_default="")
    camera_uuid = Column(CHAR(length=36, convert_unicode=True),
                         ForeignKey('camera.uuid', onupdate="CASCADE"),  # should not be deleted when camera is deleted
                         nullable=False, server_default="")
    stream_format = Column(CHAR(length=16, convert_unicode=True),
                           nullable=False, server_default="")
    stream_quality = Column(CHAR(length=8, convert_unicode=True),
                            nullable=False, server_default="")
    ip = Column(BigInteger, nullable=False, server_default=text("0")) # only ipv4 supported
    user_agent = Column(String(length=255, convert_unicode=True), nullable=False, server_default="") # overflow be careful
    user = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")
    secret_id = Column(String(lenth=64, convert_unicode=True), nullable=True)
    start = Column(TIMESTAMP(), nullable=False, server_default=text("0"))
    end = Column(TIMESTAMP(), nullable=False, server_default=text("0"))

    def __repr__(self):
        return "SA Camera Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )

    def from_session_log(self, session_log):
        self.uuid = session_log.uuid
        self.project_name = session_log.project_name
        self.camera_uuid = session_log.camera_uuid
        self.stream_format = session_log.stream_format
        self.stream_quality = session_log.stream_quality
        self.ip = session_log.ip
        self.user_agent = session_log.user_agent
        self.user = session_log.user
        self.secret_id = session_log.secret_id
        self.start = session_log.start
        self.end = session_log.end

    def to_session_log(self, session_log_cls):
        session_log = session_log_cls(project_name=self.project_name,
                                      camera_uuid = self.camera_uuid,
                                      stream_format = self.stream_format,
                                      stream_quality = self.stream_quality,
                                      ip = self.ip,
                                      user_agent = self.user_agent,
                                      user = self.user,
                                      secret_id = self.secret_id,
                                      start = self.start,
                                      end = self.end)
        return session_log

class SAAccessKey(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'access_key'

    id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=True)
    key_id = Column(String(length=32, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    secret = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")

    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")

    username = Column(String(length=64, convert_unicode=True),
                          ForeignKey('user.username', onupdate="CASCADE", ondelete="CASCADE"),
                          nullable=False, server_default="")
    enabled = Column(Boolean(), nullable=False, server_default=text("0"))
    key_type = Column(SmallInteger, nullable=False, server_default=text("0"))
    ctime = Column(TIMESTAMP(), nullable=False, server_default=text("0"))

    user = relationship("SAUser", back_populates="access_keys")


    def __repr__(self):
        return "SA AccessKey Object(key_id:%s)" % (
            self.key_id
        )

    def from_access_key(self, access_key):
        self.key_id = access_key.key_id
        self.secret = access_key.secret
        self.key_type = access_key.key_type
        self.username = access_key.username
        self.desc = access_key.desc
        self.enabled = access_key.enabled
        self.ctime = access_key.ctime

    def to_access_key(self, access_key_cls):
        return access_key_cls(key_id=self.key_id, secret=self.secret,
                              username=self.username, key_type=self.key_type,
                              enabled=self.enabled, desc=self.desc,
                              ctime=self.ctime)