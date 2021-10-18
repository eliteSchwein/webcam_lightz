import json

from gpiozero import PWMLED, Button
from time import sleep
import tornado.ioloop
import tornado.web

ledpin = 18
buttonpin = 21

ledValue = 0.0
buttonPressed = False
fadeUp = False

button = Button(buttonpin, hold_time=0.25)
led = PWMLED(ledpin)


def toggleLed():
    global buttonPressed
    global ledValue

    if buttonPressed:
        buttonPressed = False
        led.value = 0.0
        print("disable LEDs")
        return
    else:
        buttonPressed = True
        if ledValue == 0.0:
            ledValue = 1.0
        print("enable LEDs with " + str(ledValue))
        return


def handleButtonHeld():
    global fadeUp
    global ledValue
    global buttonPressed
    global button

    buttonPressed = True

    while button.is_held:
        if fadeUp:
            if ledValue == 1.0:
                fadeUp = False
            else:
                ledValue = round(ledValue + 0.005, 3)
        else:
            if ledValue == 0.0:
                fadeUp = True
            else:
                ledValue = round(ledValue - 0.005, 3)
        print("enable LEDs with " + str(ledValue))
        sleep(0.025)
    return

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        global ledValue
        global buttonPressed
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            json_args = json.loads(self.request.body)
            if not json_args["brightness"]:
                self.send_error(401)
                return
            try:
                brightness = float(json_args["brightness"])
                if brightness > 1.0 or brightness < 0.0:
                    self.send_error(401)
                    return
                ledValue = brightness
                buttonPressed = True
                self.send_error(200)
            except ValueError:
                self.send_error(401)
                return
        else:
            self.send_error(401)

def start_web():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == '__main__':
    button.when_activated = toggleLed
    button.when_held = handleButtonHeld

    web = start_web()
    web.listen(8080)
    tornado.ioloop.IOLoop.current().start()

    while True:
        if buttonPressed:
            led.value = ledValue
        sleep(0.05)
