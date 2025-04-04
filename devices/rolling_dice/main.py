import uasyncio
from auto_shutdown import AutoShutdown
from board_button import BoardButton
from board_config import BoardConfig
from rolling_dice import RollingDice

async def main():
    try:
        board_config = BoardConfig(detected_board="ESP32-C3")
        auto_shutdown = AutoShutdown(timeout=600)  # 600 seconds = 10 minutes
        rolling_dice = RollingDice(board_config.dice_pins)

        async def handle_cycle():
            rolling_dice.cycle_number()

        async def handle_roll():
            rolling_dice.roll()

        board_button = BoardButton(board_config)
        board_button.on_press(handle_roll)
        board_button.on_double_press(handle_cycle)
        
        rolling_dice.roll()  # Initial roll on startup

        await uasyncio.gather(
            board_button.monitor(),
            auto_shutdown.monitor(),
        )
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
        try:
            board_button.stop()
            auto_shutdown.stop()
            rolling_dice.clear()
        except Exception as e:
            print("Error during cleanup:", str(e))
    except Exception as e:
        print("Error in main:", str(e))
        raise

if __name__ == "__main__":
    print("Initializing dice system...")
    uasyncio.run(main())