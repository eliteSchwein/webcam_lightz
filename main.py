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
        print("enable LEDs with " + str(ledValue))
        return


def handleButtonHeld():
    print('Held!')
    return


if __name__ == '__main__':
    button.when_activated = toggleLed
    button.when_held = handleButtonHeld
    while True:
        led.value = ledValue
