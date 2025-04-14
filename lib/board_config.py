from machine import Pin


class BoardConfig:
    def __init__(self, detected_board='ESP32'):
        self._detected_board = detected_board

        if self._detected_board not in ['ESP32', 'ESP32-C3']:
            raise ValueError(f'Unsupported board type: {self._detected_board}')

        self._configure_pins()

    @property
    def detected_board(self):
        return self._detected_board

    def _configure_pins(self):
        # Set default pin configuration (ESP32)
        # Core pins
        self.BOOT_BUTTON = 0
        self.BUILTIN_LED = 2
        self.LED_PIN = self.BUILTIN_LED
        self.TTP223_BUTTON = 27  # Default TTP223 touch sensor pin for ESP32

        # Communication pins
        self.I2C_SCL = 22
        self.I2C_SDA = 21
        self.SPI_MOSI = 23
        self.SPI_MISO = 19
        self.SPI_CLK = 18
        self.SPI_CS = 5

        # Button Controller specific
        self.BUTTON_LED = 8

        # SPI pins for ESP32-C3
        self.ESP32_C3_SPI_MOSI = 6
        self.ESP32_C3_SPI_MISO = 7
        self.ESP32_C3_SPI_CLK = 10
        self.ESP32_C3_SPI_CS = 20

        # Override for ESP32-C3
        if self._detected_board == 'ESP32-C3':
            self.BOOT_BUTTON = 9
            self.TTP223_BUTTON = 20
            self.BUILTIN_LED = 8
            self.LED_PIN = self.BUILTIN_LED
            self.I2C_SCL = 4
            self.I2C_SDA = 5
            self.BUTTON_LED = 2
            self.SPI_MOSI = self.ESP32_C3_SPI_MOSI
            self.SPI_MISO = self.ESP32_C3_SPI_MISO
            self.SPI_CLK = self.ESP32_C3_SPI_CLK
            self.SPI_CS = self.ESP32_C3_SPI_CS

    def get_pin(self, pin_number, mode=Pin.IN, pull=None):
        return Pin(pin_number, mode, pull)

    def is_builtin_led_active_low(self):
        return self._detected_board == 'ESP32-C3'

    @property
    def board_name(self):
        return self._detected_board

    @property
    def sound_pin(self):
        if self._detected_board == 'ESP32-C3':
            raise NotImplementedError('Sound pin not available on ESP32-C3')

        return 4

    @property
    def led_1_pin(self):
        if self._detected_board == 'ESP32-C3':
            return 21  # Using available GPIO21

        return 5

    @property
    def shift_register_pins(self):
        if self._detected_board == 'ESP32-C3':
            return {
                'ser': 0,  # Serial data
                'rclk': 1,  # Register clock
                'srclk': 2,  # Shift register clock
            }

        return {
            'ser': 32,  # Serial data
            'rclk': 33,  # Register clock
            'srclk': 26,  # Shift register clock
        }

    @property
    def led_matrix_pins(self):
        if self._detected_board == 'ESP32-C3':
            return [
                [0, 1, 2, 3, 4]  # Using same configuration through shift register
            ]

        return [[32, 33, 26, 27, 25]]

    @property
    def dice_pins(self):
        if self._detected_board == 'ESP32-C3':
            return [5, 4, 1, 6, 3, 7, 2]

        # Return 7 pins for the dice display
        # Using available GPIO pins that don't conflict with other functionalities
        return [12, 13, 14, 15, 16, 17, 18]

    @property
    def custom_button_pin(self):
        if self._detected_board == 'ESP32-C3':
            return 3

        return 5
