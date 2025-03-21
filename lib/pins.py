# pins.py

# GPIO pins
GPIO0 = 0    # Commonly used for Boot/Program
GPIO1 = 1    # UART0 TX
GPIO2 = 2    # Commonly used for built-in LED
GPIO3 = 3    # UART0 RX
GPIO4 = 4
GPIO5 = 5
GPIO6 = 6    # Reserved for SPI flash
GPIO7 = 7    # Reserved for SPI flash
GPIO8 = 8    # Reserved for SPI flash
GPIO9 = 9    # Reserved for SPI flash
GPIO10 = 10  # Reserved for SPI flash
GPIO11 = 11  # Reserved for SPI flash
GPIO12 = 12
GPIO13 = 13
GPIO14 = 14
GPIO15 = 15
GPIO16 = 16
GPIO17 = 17
GPIO18 = 18
GPIO19 = 19
GPIO21 = 21
GPIO22 = 22
GPIO23 = 23
GPIO25 = 25
GPIO26 = 26
GPIO27 = 27
GPIO32 = 32
GPIO33 = 33
GPIO34 = 34  # Input only
GPIO35 = 35  # Input only
GPIO36 = 36  # Input only (SVP)
GPIO37 = 37  # Input only (SVP)
GPIO38 = 38  # Input only (SVP)
GPIO39 = 39  # Input only (SVN)

# Special pins
BUILTIN_LED = GPIO2
BOOT_BUTTON = GPIO0

# ADC pins
ADC1_0 = GPIO36
ADC1_1 = GPIO37
ADC1_2 = GPIO38
ADC1_3 = GPIO39
ADC1_4 = GPIO32
ADC1_5 = GPIO33
ADC1_6 = GPIO34
ADC1_7 = GPIO35

ADC2_0 = GPIO4
ADC2_1 = GPIO0
ADC2_2 = GPIO2
ADC2_3 = GPIO15
ADC2_4 = GPIO13
ADC2_5 = GPIO12
ADC2_6 = GPIO14
ADC2_7 = GPIO27
ADC2_8 = GPIO25
ADC2_9 = GPIO26

# Touch pins
TOUCH0 = GPIO4
TOUCH1 = GPIO0
TOUCH2 = GPIO2
TOUCH3 = GPIO15
TOUCH4 = GPIO13
TOUCH5 = GPIO12
TOUCH6 = GPIO14
TOUCH7 = GPIO27
TOUCH8 = GPIO33
TOUCH9 = GPIO32

# I2C recommended pins
I2C_SCL = GPIO22
I2C_SDA = GPIO21

# SPI recommended pins
SPI_MOSI = GPIO23
SPI_MISO = GPIO19
SPI_CLK = GPIO18
SPI_CS = GPIO5