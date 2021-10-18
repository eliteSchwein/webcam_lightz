from gpiozero import PWMLED, Button
from time import sleep

ledpin = 18
buttonpin = 21

ledValue = 0.0
buttonPressed = False

button = Button(buttonpin, hold_time=0.25)
led = PWMLED(ledpin)

if __name__ == '__main__':
    while True:
        led.value = ledValue

        if button.is_active:
            if buttonPressed:
                buttonPressed = False
                led.value = 0.0
            else:
                buttonPressed = True
                if(ledValue == 0.0):
                    ledValue = 1.0
                led.value = ledValue
        if button.is_held:
            print('Held!')