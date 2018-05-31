import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    def __init__():
        camera = picamera.PiCamera()
        camera.led = False
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    @staticmethod
    def start_record():
        camera.led = True
        pass

    @staticmethod
    def end_record():
        camera.led = False
        pass
