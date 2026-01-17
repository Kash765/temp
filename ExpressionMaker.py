from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep

class ExpressionMaker:
    def __init__(self):
        self.serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(self.serial, rotate=0)

    def neutral(self):
        with canvas(self.device) as draw:
            draw.ellipse([(10, 10), (50, 50)], fill="white", outline="black", width=1)
            draw.ellipse([(78, 10), (118, 50)], fill="white", outline="black", width=1)
            draw.ellipse([(56, 62), (62, 66)], fill="white", outline="black", width=1)
            
        sleep(10)
        
    def sleepy(self):
        with canvas(self.device) as draw:
            # Sleepy eyes (half-closed arcs)
            draw.arc([(10, 20), (50, 45)], start=0, end=180, fill="white", width=2)
            draw.arc([(78, 20), (118, 45)], start=0, end=180, fill="white", width=2)

            # Small relaxed mouth
            draw.arc([(48, 62), (70, 72)], start=0, end=180, fill="white", width=2)

            # Tiny "zzz" dot for extra cuteness
            #draw.ellipse([(100, 0), (104, 4)], fill="white", outline="black")


    def happy(self):
        with canvas(self.device) as draw:
            # Happy eyes (smiling crescents)
            draw.arc([(10, 10), (50, 50)], start=200, end=340, fill="white", width=2)
            draw.arc([(78, 10), (118, 50)], start=200, end=340, fill="white", width=2)

            # Blush cheeks
            draw.ellipse([(6, 42), (18, 54)], fill="white", outline="black", width=1)
            draw.ellipse([(110, 42), (122, 54)], fill="white", outline="black", width=1)

            # Big smile
            draw.arc([(40, 58), (78, 90)], start=200, end=340, fill="black", width=2)

    def angry(self):
        with canvas(self.device) as draw:
            # Angry eyes (sharp, open)
            draw.ellipse([(10, 14), (50, 46)], fill="white", outline="black", width=2)
            draw.ellipse([(78, 14), (118, 46)], fill="white", outline="black", width=2)

            # Very angry eyebrows (steep inward slant, lowered)
            draw.line([(8, 18), (48, 10)], fill="black", width=4)     # Left eyebrow
            draw.line([(120, 18), (80, 10)], fill="black", width=4)  # Right eyebrow

            # Optional: eyebrow shadow to cover eyes more
            draw.line([(10, 20), (46, 14)], fill="black", width=3)
            draw.line([(118, 20), (82, 14)], fill="black", width=3)

            # Small pouty mouth
            draw.arc([(50, 58), (68, 68)], start=20, end=160, fill="white", width=2)


    def old_angry(self):
        with canvas(self.device) as draw:
            # Angry eyes (sharp, open)
            draw.ellipse([(10, 12), (50, 44)], fill="white", outline="black", width=2)
            draw.ellipse([(78, 12), (118, 44)], fill="white", outline="black", width=2)

            # Eyebrows (slanted inward)
            draw.line([(12, 8), (48, 18)], fill="black", width=2)
            draw.line([(118, 8), (82, 18)], fill="black", width=2)

            # Small pouty mouth
            draw.arc([(50, 58), (68, 68)], start=20, end=160, fill="white", width=2)


expression = ExpressionMaker()
'''expression.neutral()
sleep(5)
expression.sleepy()
sleep(5)
expression.happy()
sleep(5)'''
expression.angry()