from streamswitch.stream_mngr import create_stream
from streamswitch.sources.rtsp_source import RTSP_SOURCE_TYPE_NAME
from streamswitch.port_mngr import SubProcessPort
from streamswitch.ports.rtsp_port import RTSP_PORT_PROGRAM_NAME
from streamswitch.sender_mngr import create_sender
from streamswitch.senders.native_ffmpeg_sender import NATIVE_FFMPEG_SENDER_TYPE_NAME


src = create_stream(RTSP_SOURCE_TYPE_NAME,
                    'rs1',
                    'rtsp://192.168.2.100:554/user=admin&password=123456&id=1&type=1',
                    log_file='src.log')
port = SubProcessPort(port_name='tp', port_type=RTSP_PORT_PROGRAM_NAME)
port.start()
sender = sender = create_sender(NATIVE_FFMPEG_SENDER_TYPE_NAME,
                                'ts1',
                                'rtmp://121.41.72.231:11935/live/t1',
                                log_file='sender.log',
                                dest_format='flv',
                                stream_name='rs1',
                                extra_options={'vcodec': 'copy'})