# -*- coding: utf-8 -*-
"""
ivr.ivc.daos.models
~~~~~~~~~~~~~~~~~~~~~~~

This module implements the domain models for the IVC WSGI application,
based on the SQLAlchemy's ORM

:copyright: (c) 2015 by OpenSight (www.opensight.cn).

"""
from __future__ import unicode_literals, division
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Float, Text, \
    BigInteger, CHAR, Boolean
from sqlalchemy.ext.declarative import declarative_base
from ...common.utils import STRING, encode_json
import json



Base = declarative_base()

class SACamera(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'camera'

    _id = Column('id', BigInteger, nullable=False, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(length=36, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    device_uuid = Column(CHAR(length=36, convert_unicode=True),
                         nullable=False, server_default="", ForeignKey('device.uuid'))
    channel_index = Column(Integer, nullable=False, server_default="0")
    name = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(Text(convert_unicode=True), nullable=False, server_default="")
    longitude = Column(Float, server_default="0.0", nullable=False)
    latitude = Column(Float, server_default="0.0", nullable=False)
    altitude = Column(Float, server_default="0.0", nullable=False)
    project_name = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")
    flags = Column(Integer, nullable=False, server_default="0")
    is_online = Column(Boolean, nullable=False, server_default="0")

    device = relationship("SADevice", back_populates="cameras")

    def __repr__(self):
        return "SA Camera Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )



class SADevice(Base):
    """ The SQLAlchemy declarative model class for a camera object. """
    __tablename__ = 'device'

    _id = Column('id', BigInteger, nullable=False, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(length=36, convert_unicode=True),
                  nullable=False, index=True, unique=True)
    name = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    type = Column(String(length=32, convert_unicode=True), nullable=False, server_default="IVT")
    firmware_model = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    hardware_model = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    media_channel_num = Column(Integer, nullable=False, server_default="0")
    desc = Column(String(length=255, convert_unicode=True), nullable=False, server_default="")
    long_desc = Column(Text(convert_unicode=True), nullable=False, server_default="")
    longitude = Column(Float, server_default="0.0", nullable=False)
    latitude = Column(Float, server_default="0.0", nullable=False)
    altitude = Column(Float, server_default="0.0", nullable=False)
    project_name = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")
    flags = Column(Integer, nullable=False, server_default="0")
    is_online = Column(Boolean, nullable=False, server_default="0")
    login_code = Column(String(length=64, convert_unicode=True),
                      nullable=False, index=True, unique=True)
    login_passwd = Column(String(length=64, convert_unicode=True), nullable=False, server_default="")

    cameras = relationship("SACamera", order_by=SACamera._id, back_populates="device")

    def __repr__(self):
        return "SA Device Object(uuid:%s, name:%s)" % (
            self.uuid, self.name
        )

