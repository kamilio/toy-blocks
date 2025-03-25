from machine import Pin
import machine
from logger import Logger

class BoardConfig:
    def __init__(self, detected_board="ESP32"):
        self.logger = Logger("BoardConfig", debug=True)
        self.logger.info("Initializing board configuration...")
        self._detected_board = detected_board
        self._configure_pins()

    @property
    def detected_board(self):
        return self._detected_board

    def _configure_pins(self):
        self.logger.info(f"Configuring pins for {self._detected_board}")
        
        # Set default pin configuration (ESP32)
        # Core pins
        self.BOOT_BUTTON = 0
        self.BUILTIN_LED = 2
        self.LED_PIN = self.BUILTIN_LED
        
        # Communication pins
        self.I2C_SCL = 22
        self.I2C_SDA = 21
        self.SPI_MOSI = 23
        self.SPI_MISO = 19
        self.SPI_CLK = 18
        self.SPI_CS = 5
        
        # Button Controller specific
        self.BUTTON_LED = 8
        
        # Override for ESP32-C3
        if self._detected_board == "ESP32-C3":
            self.BOOT_BUTTON = 9
            self.BUILTIN_LED = 8
            self.LED_PIN = self.BUILTIN_LED
            self.I2C_SCL = 4
            self.I2C_SDA = 5
            self.BUTTON_LED = 2

    def get_pin(self, pin_number, mode=Pin.IN, pull=None):
        return Pin(pin_number, mode, pull)

    def is_builtin_led_active_low(self):
        self.logger.info(f"Checking LED active low state for {self._detected_board}")
        return self._detected_board == "ESP32-C3"
            
    @property
    def board_name(self):
        self.logger.info(f"Board name requested: {self._detected_board}")
        return self._detected_board
    
    @property
    def sound_pin(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("Sound pin not available on ESP32-C3")
        
        return 4
    
    @property
    def led_1_pin(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("LED 1 pin not available on ESP32-C3")
        
        return 5

    @property
    def shift_register_pins(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("Shift register not available on ESP32-C3")
        
        return {
            'ser': 32,   # Serial data
            'rclk': 33,  # Register clock
            'srclk': 26  # Shift register clock
        }
    
    @property
    def led_matrix_pins(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("LED matrix not available on ESP32-C3")
        
        return [
            [32, 33, 26, 27, 25]
        ]

    @property
    def dice_pins(self):
        if self._detected_board == "ESP32-C3":
            return [5, 4, 1, 6, 3, 7, 2]
        
        # Return 7 pins for the dice display 
        # Using available GPIO pins that don't conflict with other functionalities
        return [12, 13, 14, 15, 16, 17, 18]
    
    @property
    def custom_button_pin(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("Custom button pin not available on ESP32-C3")
        
        return 5