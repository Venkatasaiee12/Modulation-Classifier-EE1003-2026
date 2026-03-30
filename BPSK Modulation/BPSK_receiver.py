import adi
import numpy as np


PLUTO_URI = "ip:192.168.2.1"
SAMPLE_RATE = 1_000_000
CENTER_FREQ = 915_000_000
SAMPLES_PER_SYMBOL = 100
PREAMBLE = "11100010110100101110001011010010"
REPETITION = 3
MAX_MESSAGE_CHARS = 300


def repeat_decode(bits: str, factor: int) -> str:
    usable = len(bits) - (len(bits) % factor)
    return "".join(
        "1" if bits[i:i + factor].count("1") > factor // 2 else "0"
        for i in range(0, usable, factor)
    )


def bits_to_text(bits: str) -> str:
    return "".join(chr(int(bits[i:i + 8], 2)) for i in range(0, len(bits), 8))


def decode_capture(rx: np.ndarray) -> str | None:
    best_text = None
    best_score = -1
    coded_length_size = 16 * REPETITION
    needed_symbols = len(PREAMBLE) + coded_length_size
    preamble_score_min = len(PREAMBLE) - 4

    for offset in range(SAMPLES_PER_SYMBOL):
        usable = (len(rx) - offset) // SAMPLES_PER_SYMBOL
        if usable < needed_symbols:
            continue

        symbol_stream = rx[offset:offset + usable * SAMPLES_PER_SYMBOL].reshape(-1, SAMPLES_PER_SYMBOL).mean(axis=1)
        diff = symbol_stream[1:] * np.conj(symbol_stream[:-1])
        bits = "".join("1" if sample.real < 0 else "0" for sample in diff)

        best_start = -1
        best_local = -1
        for i in range(len(bits) - len(PREAMBLE)):
            local = sum(bits[i + j] == PREAMBLE[j] for j in range(len(PREAMBLE)))
            if local > best_local:
                best_local = local
                best_start = i

        if best_local < preamble_score_min:
            continue

        frame_bits = bits[best_start:]
        coded_len_bits = frame_bits[len(PREAMBLE):len(PREAMBLE) + coded_length_size]
        if len(coded_len_bits) < coded_length_size:
            continue

        msg_len = int(repeat_decode(coded_len_bits, REPETITION), 2)
        if msg_len <= 0 or msg_len > MAX_MESSAGE_CHARS:
            continue

        data_start = len(PREAMBLE) + coded_length_size
        data_end = data_start + (msg_len * 8 * REPETITION)
        if len(frame_bits) < data_end:
            continue

        payload_bits = repeat_decode(frame_bits[data_start:data_end], REPETITION)
        try:
            text = bits_to_text(payload_bits)
        except ValueError:
            continue

        if text.isprintable() and best_local > best_score:
            best_text = text
            best_score = best_local

    return best_text


def main() -> None:
    sdr = adi.Pluto(PLUTO_URI)
    sdr.sample_rate = SAMPLE_RATE
    sdr.rx_lo = CENTER_FREQ
    sdr.rx_rf_bandwidth = SAMPLE_RATE
    sdr.gain_control_mode_chan0 = "manual"
    sdr.rx_hardwaregain_chan0 = 40
    sdr.rx_buffer_size = 300000

    print("Receiving...")

    for _ in range(5):
        sdr.rx()

    received = None
    for _ in range(8):
        rx = np.concatenate((np.asarray(sdr.rx()), np.asarray(sdr.rx())))
        received = decode_capture(rx)
        if received is not None:
            break

    if received is None:
        print("Sync not found")
    else:
        print("\nReceived Message:")
        print(received)


if __name__ == "__main__":
    main()
