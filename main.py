from gpiozero import PWMLED, Button
from time import sleep

ledpin = 18
buttonpin = 21

ledValue = 0.0
buttonPressed = False

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
        if (ledValue == 0.0):
            ledValue = 1.0
        led.value = ledValue
        print("enable LEDs with " + ledValue)
        return


def handleButton():
    if button.is_held:
        print('Held!')
        return
    if button.is_active:
        toggleLed()


if __name__ == '__main__':
    while True:
        led.value = ledValue
        handleButton()
        sleep(1)
