# MicroPython Unsupported Modules

## Unsupported Modules & Workarounds

* **contextlib**
  * Error: `ImportError: no module named 'contextlib'`
  * Fix: Replace `with contextlib.suppress()` with simple try-except blocks

* **typing**
  * Error: `ImportError: no module named 'typing'`
  * Fix: Remove type annotations (not used at runtime)

* **enum**
  * Error: `ImportError: no module named 'enum'`
  * Fix: Use regular classes with class variables instead