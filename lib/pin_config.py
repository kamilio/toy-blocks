class PinConfigEsp32:
    """ESP32 pin configuration"""
    BOOT_BUTTON = 0
    LED_PIN = 2
    
    def is_builtin_led_active_low(self):
        return False


class PinConfigEsp32C3:
    """ESP32-C3 pin configuration"""
    BOOT_BUTTON = 9
    LED_PIN = 2
    
    def is_builtin_led_active_low(self):
        return False