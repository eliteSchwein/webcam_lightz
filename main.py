from gpiozero import PWMLED, Button
from time import sleep

ledpin = 18
buttonpin = 21

ledValue = 0.0
buttonPressed = False

button = Button(buttonpin)
led = PWMLED(ledpin)

if __name__ == '__main__':
    while True:
        led.value = ledValue

        if(button.is_held):
            print('Held!')