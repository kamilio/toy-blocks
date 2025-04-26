# Coding Python
## General
- Do not write many comments, only rarely comment on unusual stuff
- Do not catch exception, especially if we are not attempting to recover

## Components
- Each component e.g. button is a class
- Class has constructor to define the configuration e.g. pins
    - The constructor shouldn't execute anything that might slow down the startup
    - Use `.initialize` method if you need to do anything async
- Instance has two kind of public methods
    - listeners - on_{event} to define callbacks
        - do not use on_error 
    - actions - do_something - actions e.g. blink() - this could be async if needed
        - typically actions should throw errors
- It should have `async monitor()` method that is going to be used in asyncio.gather together with other components

```
async def monitor(self):
    self._running = True
    while self._running:
        # do things
        await uasyncio.sleep(sensible_time)
```

- It should have stop method

```
def stop(self):
    self._running = False
```                

- Callbacks are async, but micropython implements async methods as generators so execute them accordingly
    -  Use `await uasyncio.create_task(callback())`


# Structure main.py

- initialize components
- define callbacks (listeners) that execute actions
- asyncio.gather() to monitor all components

# Pin config
- Define a new subclass of lib/pin_config.py
- Subclass lives in `main.py`


# Testing
Make sure to add tests
Mocking
- Use existing mocks in conftest
- Always await coroutines in tests. You define callbacks, so make sure to await them.
- Must ask me when adding new mocks
    - When approved -a dd new mocks into the mock files or conftest

# Verify files
- Create only when specifically requested
- It should have a single method `async verify_{something}(pin_config):`
- Simplest possible way to test the component, whether the wiring is correct e.g. beeper should beep and we are done
- I will include this file in my project for debuggin when needed, do not call anywhere
- Never add this `if __name__ == "__main__": main()`


# Other files when writing python code
- No markdown files
- No example files