# Commit changes

- Review all current changes using `git diff | cat` and ensure they are for micropython and esp32
- Run `make format` potentially `make format-unsafe` if needed to fix changes and you are confident they are safe
- Run `make test` and make sure all tests are passing
- Commit changes with simple description