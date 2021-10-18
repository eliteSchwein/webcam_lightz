from gpiozero import PWMLED, Button
from time import sleep

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
        ledValue = 0.0
        print("disable LEDs")
        return
    else:
        buttonPressed = True
        if (ledValue == 0.0):
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
                print("Reached Upper Limit!")
                return
            ledValue = round(ledValue + 0.1, 1)
        else:
            if ledValue == 0.0:
                print("Reached Down Limit!")
                fadeUp = True
                return
            ledValue = round(ledValue - 0.1, 1)
        print("enable LEDs with " + str(ledValue))
        sleep(0.2)
    return


if __name__ == '__main__':
    button.when_activated = toggleLed
    button.when_held = handleButtonHeld
    while True:
        led.value = ledValue
