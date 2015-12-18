from ivr.ivt.stream import Stream

from streamswitch.sources.rtsp_source import RTSP_SOURCE_TYPE_NAME


class RTSPStream(Stream):
    type = 'rtsp'
    stsw_source_type = RTSP_SOURCE_TYPE_NAME