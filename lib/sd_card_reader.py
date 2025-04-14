import machine
import uasyncio as asyncio
from machine import SPI, Pin


class SDCardReader:
    def __init__(self, sck_pin, mosi_pin, miso_pin, cs_pin):
        """Initialize SD card reader with SPI interface

        Args:
            sck_pin: Clock pin number
            mosi_pin: Master Out Slave In pin number
            miso_pin: Master In Slave Out pin number
            cs_pin: Chip Select pin number
        """
        # Configure SPI pins
        self.spi = SPI(
            1,
            baudrate=1000000,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=machine.SPI.MSB,
            sck=Pin(sck_pin),
            mosi=Pin(mosi_pin),
            miso=Pin(miso_pin),
        )

        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)  # Deselect SD card

        self._running = False
        self._callbacks = {'status_change': None}

    def on_status_change(self, callback):
        """Register callback for SD card status changes

        Args:
            callback: Async function to call with status updates
        """
        self._callbacks['status_change'] = callback

    async def initialize(self):
        """Initialize the SD card"""
        self.cs.value(0)  # Select SD card
        # Send reset command
        self.spi.write(b'\x40\x00\x00\x00\x00\x95')
        # Wait for SD card to initialize
        await asyncio.sleep(0.1)  # 100ms
        self.cs.value(1)
        return True

    async def read_file(self, filename):
        """Read file from SD card asynchronously

        Args:
            filename: Name of file to read

        Returns:
            bytes: File contents

        Raises:
            ValueError: If file cannot be found or read
        """
        self.cs.value(0)
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            self.cs.value(1)
            return data
        except FileNotFoundError:
            self.cs.value(1)
            raise ValueError(f'File not found: {filename}') from None
        except Exception as e:
            self.cs.value(1)
            raise ValueError(f'Error reading file {filename}: {e!s}') from e

    async def read_wav(self, filename):
        """Read WAV file from SD card

        Args:
            filename: Name of WAV file

        Returns:
            tuple: (sample_rate, audio_data)
        """
        data = await self.read_file(filename)
        if not data:
            return None

        # Parse WAV header
        if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
            error_msg = f'Invalid WAV file format: {filename}'
            print(error_msg)
            raise ValueError(error_msg)

        # Extract sample rate from header
        sample_rate = int.from_bytes(data[24:28], 'little')
        # Skip header (44 bytes) to get audio data
        audio_data = data[44:]

        return (sample_rate, audio_data)

    async def monitor(self):
        """Monitor SD card status

        This method runs indefinitely until stop() is called.
        It's designed to be used with asyncio.gather().
        """
        self._running = True
        while self._running:
            try:
                # Check SD card status
                self.cs.value(0)
                # Send status command
                self.spi.write(b'\x4d\x00\x00\x00\x00\x01')
                status = self.spi.read(1)[0]
                self.cs.value(1)

                # Call status_change callback with status
                await self._run_callback('status_change', status)

            except Exception as e:
                print(f'Monitor error: {e}')
                # Just log the error in monitor, don't use callbacks for errors

            # Sleep a short time before checking again
            await asyncio.sleep(0.1)  # 100ms

    def stop(self):
        """Stop monitoring SD card status"""
        self._running = False

    async def _run_callback(self, callback_type, data=None):
        """Run a registered callback

        Args:
            callback_type: Type of callback to run ('status_change')
            data: Data to pass to the callback
        """
        callback = self._callbacks.get(callback_type)
        if callback:
            await asyncio.create_task(callback(data))
