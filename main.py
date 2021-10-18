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

clients = []

button = Button(buttonpin, hold_time=0.25)
led = PWMLED(ledpin)

def updateValues(val, pressed):
    global buttonPressed
    global ledValue

    buttonPressed = pressed
    ledValue = val

    if not pressed:
        led.value = 0.0
    else:
        led.value = ledValue

    for client in clients:
        if not client.ws_connection.stream.socket:
            clients.remove(client)
        else:
            client.send_message(json.dumps({"brightness": ledValue, "disabled": buttonPressed}))


def toggleLed():
    global buttonPressed
    global ledValue

    if buttonPressed:
        updateValues(0.0, False)
        print("disable LEDs")
        return
    else:
        buttonPressed = True
        if ledValue == 0.0:
            ledValue = 1.0
        updateValues(ledValue, True)
        print("enable LEDs with " + str(ledValue))
        return


def handleButtonHeld():
    global fadeUp
    global ledValue
    global buttonPressed
    global button

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

        updateValues(ledValue, True)
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
                updateValues(0.0, False)
                return
            if json_args["on"]:
                updateValues(ledValue, True)
                return
            if not json_args["brightness"]:
                self.send_error(401)
                return
            try:
                brightness = float(json_args["brightness"])
                if brightness > 1.0 or brightness < 0.0:
                    self.send_error(401)
                    return
                updateValues(brightness, True)
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

    def open(self):
        print("WebSocket opened")
        self.write_message(json.dumps({"brightness": ledValue, "disabled": buttonPressed}))
        clients.append(self)

    def on_message(self, message):
        print(message)
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")
        clients.remove(self)

    @classmethod
    def send_message(self, message):
        self.write_message(message)
        return True


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
