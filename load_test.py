#!/usr/bin/env python3
"""Benchmark reproducible for B+ insertion and temporal range searches."""

from datetime import datetime, timedelta, timezone
from time import perf_counter

from domain.api_log import ApiLog
from storage.bplus_tree import BPlusTree


SIZES = (1_000, 10_000, 50_000, 100_000)


def build_record(index):
    timestamp = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=index)
    timestamp_text = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ApiLog(
        timestamp=timestamp_text,
        service="load-test-service",
        method="GET",
        endpoint="/health",
        status_code=200 if index % 20 else 500,
        latency=10 + index % 100,
        trace_id=f"trace-{index}",
        message="Database connection timeout" if index % 20 == 0 else "OK",
    )


def benchmark(size):
    tree = BPlusTree(order=32)
    insertion_start = perf_counter()
    for index in range(size):
        record = build_record(index)
        tree.insert(record.timestamp, record)
    insertion_seconds = perf_counter() - insertion_start

    range_start = build_record(size // 2).timestamp
    range_end = build_record(min(size - 1, size // 2 + 999)).timestamp
    search_start = perf_counter()
    results = tree.range_search(range_start, range_end)
    search_seconds = perf_counter() - search_start

    return insertion_seconds, search_seconds, len(results), tree.count_records()


def main():
    print("Registros | Insercion (s) | Busqueda rango (s) | Resultados | Total")
    print("-" * 72)
    for size in SIZES:
        insertion, search, result_count, total = benchmark(size)
        print(
            f"{size:9d} | {insertion:14.4f} | {search:18.6f} | "
            f"{result_count:10d} | {total:5d}"
        )


if __name__ == "__main__":
    main()
