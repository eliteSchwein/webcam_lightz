import json

from gpiozero import PWMLED, Button
from time import sleep
import tornado.ioloop
import tornado.web
import tornado.websocket
from threading import Thread

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
        led.value = ledValue
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
        led.value = ledValue
        print("enable LEDs with " + str(ledValue))
        sleep(0.025)
    return


class GetHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.set_header("Content-Type", 'application/json')

    def get(self):
        self.write(json.dumps({"brightness": ledValue, "disabled": buttonPressed}))


class SetHandler(tornado.web.RequestHandler):
    def post(self):
        global ledValue
        global buttonPressed
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            json_args = json.loads(self.request.body)
            if json_args["off"]:
                buttonPressed = False
                led.value = 0.0
                return
            if json_args["on"]:
                buttonPressed = True
                led.value = ledValue
                return
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
                led.value = ledValue
                self.send_error(200)
            except ValueError:
                self.send_error(401)
                return
        else:
            self.send_error(401)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        return


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    __is_open = False
    __currentLedVal = ledValue
    __currentButtonPressed = buttonPressed

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print(message)
        self.write_message(u"You said: " + message)

    def on_close(self):
        self.__is_open = False
        print("WebSocket closed")


def start_web():
    print("Start API")
    web = handle_web()
    web.listen(8080)
    tornado.ioloop.IOLoop.current().start()


def handle_web():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/get", GetHandler),
        (r"/set", SetHandler),
        (r"/socket", EchoWebSocket),
    ])

if __name__ == '__main__':
    button.when_activated = toggleLed
    button.when_held = handleButtonHeld

    start_web()
