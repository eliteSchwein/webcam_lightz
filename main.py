from gpiozero import PWMLED, Button
from time import sleep

ledpin = 18
buttonpin = 21

button = Button(buttonpin)
led = PWMLED(ledpin)

if __name__ == '__main__':
    while True:
        print('test')
