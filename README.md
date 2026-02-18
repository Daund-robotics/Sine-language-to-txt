# Sign Language to Text Conversion

This project converts hand gestures into text using Python and OpenCV. It is designed to run on a Raspberry Pi 4B.

## Installation on Raspberry Pi

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Daund-robotics/Sine-language-to-txt.git
    cd Sine-language-to-txt
    ```

2.  **Run the setup script:**
    This script installs all necessary system and Python dependencies.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

## Usage

1.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

2.  **Run the main program:**
    ```bash
    python3 main.py
    ```

## Configuration

-   **Calibration:** If the lighting conditions change, run `python3 data_creation.py` to recalibrate the HSV values for your environment.
-   **Add Gestures:** Use `data_creation.py` to record new gestures and label them.