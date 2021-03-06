import time
import picamera


# Approx 1.5m per image - 10GB per hour when taking 2 photos every second.
IMAGES_PER_SECOND = 0.1
RESOLUTION = (1920, 1080)
FRAME_RATE = 16

def start_capture():
    with picamera.PiCamera() as camera:
        camera.resolution = RESOLUTION
        camera.framerate = FRAME_RATE

        # Wait for the automatic gain control to settle
        time.sleep(2)

        # Now fix the values
        camera.shutter_speed = camera.exposure_speed
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g

        for filename in camera.capture_continuous('images/img{timestamp}.jpg'):
            print('Captured %s' % filename)
            time.sleep(1 / IMAGES_PER_SECOND)

if __name__ == '__main__':
    start_capture()