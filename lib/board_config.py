from machine import Pin
import machine
from logger import Logger

class BoardConfig:
    def __init__(self):
        self.logger = Logger("BoardConfig", debug=True)
        self.logger.info("Initializing board configuration...")
        self._detected_board = self._detect_board()
        self._configure_pins()

    @property
    def detected_board(self):
        return self._detected_board

    def _detect_board(self):
        try:
            chip_id = machine.unique_id()
            freq = machine.freq()
            
            # Handle both real and mock scenarios safely
            chip_id_str = ""
            try:
                chip_id_str = ':'.join('%02x' % b for b in chip_id)
            except:
                chip_id_str = str(chip_id)
                
            self.logger.info(f"Detecting board - Chip ID: {chip_id_str}, Frequency: {freq}Hz")
            
            # Force ESP32 detection since we know it's an ESP32
            self.logger.info("Detected ESP32 board")
            return "ESP32"
        except Exception as e:
            self.logger.info(f"Detection failed: {str(e)}, defaulting to ESP32 board")
            return "ESP32"

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
    def led_matrix_pins(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("LED matrix not available on ESP32-C3")
        
        return [
            [32, 33, 26, 27, 25]
        ]
    
    @property
    def custom_button_pin(self):
        if self._detected_board == "ESP32-C3":
            raise NotImplementedError("Custom button pin not available on ESP32-C3")
        
        return 34