# Packet Sniffer & Anomaly Detector

This project implements a raw packet sniffer in C++ that communicates with a Python-based AI anomaly detector using ZeroMQ.

## Architecture

1.  **The Hand (C++)**: Captures raw packets, extracts IP headers, and sends metadata (Source IP, Packet Size) to Python.
2.  **The Nerve (ZeroMQ)**: High-speed IPC bridge between C++ and Python.
3.  **The Brain (Python)**: Uses an Isolation Forest (Unsupervised Learning) to detect traffic anomalies.

## Prerequisites

### macOS
1.  **Install ZeroMQ and pkg-config**:
    ```bash
    brew install zeromq pkg-config
    ```
2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Linux (Ubuntu/Debian)
1.  **Install ZeroMQ**:
    ```bash
    sudo apt install libzmq3-dev pkg-config
    ```
2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```


## Quick Start (macOS/Linux)

Run the setup script to create a virtual environment, install dependencies, and compile the code:
```bash
./setup.sh
```

## Compilation

Compile the C++ sniffer:

```bash
# Using pkg-config (Recommended for macOS/Linux)
g++ sniffer.cpp -o sniffer $(pkg-config --cflags --libs libzmq)
```

## Running the Project

**Note**: The C++ sniffer requires `sudo` privileges to open a raw socket.

1.  **Start the Python Brain** (in one terminal):
    ```bash
    python3 brain.py
    ```

2.  **Start the C++ Sniffer** (in another terminal):
    ```bash
    sudo ./sniffer
    ```

## Troubleshooting

-   **Socket Error**: Ensure you are running `./sniffer` with `sudo`.
-   **ZeroMQ Error**: Ensure `libzmq` is installed and linked correctly.
-   **macOS Specifics**: Raw sockets on macOS have some restrictions. If you don't see packets, try generating traffic (e.g., `ping 8.8.8.8`).
