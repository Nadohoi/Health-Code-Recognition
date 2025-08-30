## Overview

This repository contains a computer-vision program that detects the color of "health codes" (historically used in China, including Hong Kong and Macao) from a camera feed or image and classifies them by color (e.g., green/yellow/red). While health codes have since been discontinued as COVID is no longer an A‑Class infectious disease, this codebase remains a useful reference for:

- Color-based detection and classification
- Camera capture and debugging utilities
- Raspberry Pi camera/thermometer integration examples

## Features

- Camera-based color detection pipeline
- Live webcam testing utility: `utility/camera_test.py`
- Color calibration utility: `utility/color_selection.py`
- Raspberry Pi thermometer testing utility: `utility/thermo_test.py`
- Multiple algorithm iterations: `ver.1/`, `ver.2/`, `ver.3/`, `ver.4/`
- Raspberry Pi tailored script: `Raspberry_Pi_Edition/recognition_pi.py`

## Repository Structure

- `ver.1/recognition_v1.py` — First working version, simplest pipeline.
- `ver.2/recognition_v2.py` — Improved robustness and parameters.
- `ver.3/recognition_v3.py` — Latest desktop iteration with better heuristics.
- `ver.4/recognition_v4.py` — Simplified classification using pixel counts across color masks.
- `Raspberry_Pi_Edition/recognition_pi.py` — Pi-specific integration.
- `utility/camera_test.py` — Check camera index, resolution, FPS.
- `utility/color_selection.py` — Interactive color range calibration.
- `utility/thermo_test.py` — Thermometer reading test for Pi setups.
- `requirements.txt` — Python dependencies.

## Requirements

- Python 3.8+ recommended
- A working webcam (for desktop) or Pi Camera (for Raspberry Pi)

Install dependencies:

```bash
pip install -r requirements.txt
```

Note: On Raspberry Pi, you may need additional system packages for camera and I2C sensors depending on your setup.

## Quick Start (Desktop)

1. Calibrate color thresholds (optional but recommended):
   ```bash
   python utility/color_selection.py
   ```
   Save the ranges/values you find useful.

2. Test your camera:
   ```bash
   python utility/camera_test.py
   ```

3. Run a recognition version (pick one):
   ```bash
   python ver.1/recognition_v1.py
   python ver.2/recognition_v2.py
   python ver.3/recognition_v3.py
   python ver.4/recognition_v4.py
   ```

## Quick Start (Raspberry Pi)

1. Ensure camera and (optionally) thermometer are enabled and accessible.
2. Test thermometer (if used):
   ```bash
   python utility/thermo_test.py
   ```
3. Run Pi recognition:
   ```bash
   python Raspberry_Pi_Edition/recognition_pi.py
   ```

## Utilities

- `camera_test.py` helps identify camera indices, test frame acquisition, and basic performance.
- `color_selection.py` opens an interactive window with trackbars to tune HSV (or BGR) thresholds for reliable color detection under your lighting.
- `thermo_test.py` validates your thermometer wiring and readout on Pi.

## Calibration Tips

- Perform calibration in the same lighting conditions as deployment.
- Prefer HSV thresholding for color robustness across brightness changes.
- Avoid over-narrow thresholds to reduce false negatives; test with multiple samples.

## Notes and Disclaimer

- This repository is kept for educational and historical purposes and should not be used for any health, medical, or access-control decisions.
- Be mindful of local laws and privacy when using cameras or capturing images.

## License

See `LICENSE` for details.