import attr

from rpi_ws281x import PixelStrip, Color

from pi_dawn import graphics

LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 30   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


@attr.s(init=False)
class LedScreen:
    width = attr.ib(type=int)
    height = attr.ib(type=int)

    def __init__(self, width, height, gamma_r=2, gamma_g=2, gamma_b=2):
        self.width = width
        self.height = height
        self.lut_r = self.build_gamma_lut(gamma_r)
        self.lut_g = self.build_gamma_lut(gamma_g)
        self.lut_b = self.build_gamma_lut(gamma_b)
        self.bayer_map = self.build_bayer_map()
        self.pixels = PixelStrip(width*height, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.pixels.begin()

        
        
    def make_surface(self):
        return graphics.Surface(self)

    def draw_surface(self, surface):
        for x in range(self.width):
            for y in range(self.height):
                r, g, b = surface.get_pixel(x, y)
                r, g, b = self.lut_r[r], self.lut_g[g], self.lut_b[b]
                t = self.bayer_map[y % 2][x % 2]
                r = max(0, min(255, round(r + t)))
                g = max(0, min(255, round(g + t)))
                b = max(0, min(255, round(b + t)))
                if x % 2 == 0:
                    offset = self.height - y - 1 + x * self.height
                else:
                    offset = y + x * self.height
                self.pixels.setPixelColor(offset, Color(r, b, g))
        self.pixels.show()

    @staticmethod
    def build_gamma_lut(g):
        inverse_g = 1 / g
        return [255 * ((i / 255) ** inverse_g) for i in range(256)]

    @staticmethod
    def build_bayer_map():
        map = [
            [0.0, 2.0],
            [3.0, 1.0],
        ]
        for x in range(2):
            for y in range(2):
                map[y][x] = 0.5 * map[y][x] - 1.0
        return map
