from ivr.ivt.camera import Camera


class RTSPCamera(Camera):
    type = 'rtsp'

    def __init__(self, *args, **kwargs):
        super(RTSPCamera, self).__init__(*args, **kwargs)



