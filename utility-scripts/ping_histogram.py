#!/usr/bin/env python3
"""
ping_histogram.py

Pings a website n times with a delay of k seconds between pings,
then plots a histogram of the measured latencies with logarithmically
spaced bins (equal width on log scale).

Usage:
    python ping_histogram.py <host> <n> <k> [output.png]

Arguments:
    host       – website or IP address to ping
    n          – number of pings (positive integer)
    k          – delay between pings in seconds (positive float)
    output.png – optional output filename (default: ping_latency.png)
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from ping3 import ping


def main():
    if len(sys.argv) < 4:
        print("Usage: python ping_histogram.py <host> <n> <k> [output.png]")
        sys.exit(1)

    host = sys.argv[1]
    try:
        n = int(sys.argv[2])
        if n <= 0:
            raise ValueError("n must be positive")
    except ValueError:
        print("Error: n must be a positive integer")
        sys.exit(1)

    try:
        k = float(sys.argv[3])
        if k <= 0:
            raise ValueError("k must be positive")
    except ValueError:
        print("Error: k must be a positive number")
        sys.exit(1)

    output_file = sys.argv[4] if len(sys.argv) > 4 else "ping_latency.png"

    print(f"Pinging {host} {n} times, waiting {k} seconds between pings...")

    latencies = []
    for i in range(n):
        latency_sec = ping(host, timeout=2)
        if latency_sec is not None:
            latency_ms = latency_sec * 1000.0
            latencies.append(latency_ms)
            print(f"Ping {i + 1}: {latency_ms:.2f} ms")
        else:
            print(f"Ping {i + 1}: failed")
        if i < n - 1:
            time.sleep(k)

    if not latencies:
        print("No successful pings, cannot create histogram.")
        sys.exit(1)

    print(f"\nSuccessful pings: {len(latencies)}/{n}")
    print(
        f"Min: {min(latencies):.2f} ms, Max: {max(latencies):.2f} ms, "
        f"Avg: {sum(latencies) / len(latencies):.2f} ms"
    )

    min_val = min(latencies)
    max_val = max(latencies)
    num_bins = 100

    if min_val <= 0:
        min_val = 1e-3

    bins = np.logspace(np.log10(min_val), np.log10(max_val), num_bins)

    plt.figure(figsize=(10, 6))
    plt.hist(latencies, bins=bins, edgecolor="black", alpha=0.7)
    plt.xscale("log")
    plt.title(f"Ping Latency Distribution for {host} (log-spaced bins)")
    plt.xlabel("Latency (ms) – log scale")
    plt.ylabel("Frequency")
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.axvline(np.mean(latencies), color="red", linewidth=1, label="Mean")  # type: ignore
    plt.axvline(
        np.median(latencies),
        color="blue",
        linestyle="dotted",
        linewidth=1,
        label="Median",
    )
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"Histogram saved to {output_file}")


if __name__ == "__main__":
    main()
