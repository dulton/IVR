# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.common.schema import Schema, EnumVal


class VideoQuality(object):
    HD = 'hd'
    SD = 'sd'
    LD = 'ld'
    _values = (HD, SD, LD)
    schema = EnumVal(_values)

