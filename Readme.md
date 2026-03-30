# Modulation Classifier EE1003-2026

This project provides a suite of tools for modulating and demodulating text messages using Software Defined Radio (SDR). It is designed specifically for use with the **ADALM-PLUTO (PlutoSDR)**.

## Supported Modulation Schemes

### 1. BPSK (Binary Phase Shift Keying)
- **Sender**: `BPSK_sender.py` converts text to bits, adds a preamble and length header, and modulates the phase of the carrier. It includes repetition encoding for error robustness.
- **Receiver**: `BPSK_receiver.py` captures the signal, performs synchronization using the preamble, and decodes the message.

### 2. FSK (Frequency Shift Keying)
- **Sender**: `FSK_sender.py` uses frequency deviation (default ±60kHz) to represent bits.
- **Receiver**: `FSK_receiver.py` utilizes Fast Fourier Transform (FFT) to detect peak frequencies and reconstruct the bitstream.

### 3. QAM (Quadrature Amplitude Modulation)
- **Implementation**: `QAM.py` demonstrates 4-QAM (QPSK) transmission and reception. It maps bit pairs to complex I/Q points and handles phase rotation during recovery.

## Hardware Requirements
- Analog Devices ADALM-PLUTO SDR.
- Antennas suitable for the 915 MHz or 2.4 GHz bands (depending on script settings).

## Software Setup
- General python libraries like numpy, matplotlib, time are use.
- Apart from the above libraries the pyadi-iio is also required which can be installed by using `pip install pyadi-iio`

## Configuration
Most scripts are configured with the following default parameters:
- **Sample Rate**: 1 MSPS
- **Center Frequency**: 915 MHz (BPSK/FSK) or 2.4 GHz (QAM)
- **SDR URI**: Defaulted to `ip:192.168.2.1` or `usb:x.x.x`. Update the `PLUTO_RX_URI` or `PLUTO_TX_URI` in the scripts to match your device's address.

## Usage
1. **Connect your PlutoSDR** via USB or Network.
2. **Start the Transmitter**: Run the sender script for your desired modulation (e.g., `python FSK_sender.py`).
3. **Start the Receiver**: Run the corresponding receiver script (e.g., `python FSK_receiver.py`) to see the decoded output.