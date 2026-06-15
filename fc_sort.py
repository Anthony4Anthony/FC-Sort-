"""
=============================
FC-Sort Benchmark Framework
=============================
Each algorithm runs in its TRUE standard form on all n elements.
FC-Sort determines unique keys' frequency count and expands the unique keys by their frequency counts. All competitors operate directly on n elements using their own native mechanisms.

TABLE A — MECHANICAL versions (no builtins, pure manual loops)
TABLE B — OPTIMIZED versions  (clean Python, builtins present)

Algorithms:
  FC-Sort       — freq count → sort d keys → explode fill        [Algorithm in the study]
  Counting Sort — range array → count → prefix sum → place       [standard version]
  Radix Sort    — LSD digit passes over all n elements           [standard version]
  3-way Quick   — Dijkstra partition on all n elements in-place  [standard version]
  Timsort       — run detection and merge on all n elements        [standard version]

Benchmark specifications:
  Configurations :
    (n= 100_000, d = 10),
    (n= 100_000, d = 15),
    (n= 100_000, d = 20),
    (n= 100_000, d = 40),
    (n= 100_000, d = 80),
    (n= 100_000, d = 160),
    (n= 500_000, d = 320),
                   NOTE: Anyone can adjust the configurations- add more 'n', alter the values as you desire

  No of Runs     : 10
  Mechanical     : skipped for n > 1,000,000 (too slow) Note: Anyone can alter this restriction

  Correctness    : verified vs sorted() before timing (@sorted is python inbuilt sort method. Its results is compared with
                results from ALL participating algorithms to establish correctness

=============================================================================
"""

import random
import time
import statistics
import platform
import sys
import os


# ==============================
#           Shared functions
# =================================

def _insertion_sort(data):
    """Standard insertion sort. Used by FC-Sort to sort d keys only."""
    i = 1
    while i < len(data):
        key_tmp = data[i]
        j = i - 1
        while j >= 0 and data[j] > key_tmp:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key_tmp
        i += 1
    return data


# =======================================================
# OPTIMIZED Algorithms — True Standard Forms of ALgorithms
# ========================================================

#1. FC-Sort (This is the new algorithm introduced)
def fc_sort_optimized(my_series):

    #Counting the frequencies of all n elements into a dict
    freq = {}
    for x in my_series:
        if x in freq:
            freq[x] += 1
        else:
            freq[x] = 1
    #Case for all identical keys
    if len(freq) == 1:
        return my_series  # No need to sort; all elements are the same
    #Sort the distinct/unique keys with Insertion Sort
    distinct_keys = list(freq.keys())
    _insertion_sort(distinct_keys)

    arr_out = [0] * len(my_series)
    pos = 0
    #Explode the unique keys by their respective frequency count
    for val in distinct_keys:
        count = freq[val]
        for _ in range(count):
            arr_out[pos] = val
            pos += 1
    return arr_out


#2. Counting Sort — standard form
def counting_sort_optimized(my_series):

    if not my_series:
        return []

    min_val = min(my_series)
    max_val = max(my_series)
    r = max_val - min_val + 1

    count = [0] * r
    for x in my_series:
        count[x - min_val] += 1

    arr_out = [0] * len(my_series)
    pos = 0
    for i in range(r):
        for _ in range(count[i]):
            arr_out[pos] = i + min_val
            pos += 1
    return arr_out


#3. Radix Sort — standard LSD form
def radix_sort_optimized(my_series):

    if not my_series:
        return []

    n = len(my_series)
    min_val = min(my_series)
    offset  = -min_val if min_val < 0 else 0

    arr = [x + offset for x in my_series]   # shift to non-negative
    max_val = max(arr)

    exp = 1
    while max_val // exp > 0:
        output     = [0] * n
        count_buf  = [0] * 10

        for x in arr:
            count_buf[(x // exp) % 10] += 1

        for i in range(1, 10):
            count_buf[i] += count_buf[i - 1]

        for i in range(n - 1, -1, -1):
            digit = (arr[i] // exp) % 10
            count_buf[digit] -= 1
            output[count_buf[digit]] = arr[i]
            i -= 1

        arr = output
        exp *= 10

    return [x - offset for x in arr]


#4. 3-way Quicksort — standard Dijkstra form
def quicksort_3way_optimized(my_series):

    arr = list(my_series)

    def _qs3(arr, lo, hi):
        if hi <= lo:
            return
        # Median-of-three pivot for stability
        mid = (lo + hi) // 2
        if arr[lo] > arr[mid]:
            arr[lo], arr[mid] = arr[mid], arr[lo]
        if arr[lo] > arr[hi]:
            arr[lo], arr[hi] = arr[hi], arr[lo]
        if arr[mid] > arr[hi]:
            arr[mid], arr[hi] = arr[hi], arr[mid]

        pivot = arr[mid]
        arr[mid], arr[lo] = arr[lo], arr[mid]

        lt, gt, ii = lo, hi, lo + 1
        while ii <= gt:
            if arr[ii] < pivot:
                arr[lt], arr[ii] = arr[ii], arr[lt]
                lt += 1; ii += 1
            elif arr[ii] > pivot:
                arr[ii], arr[gt] = arr[gt], arr[ii]
                gt -= 1
            else:
                ii += 1
        _qs3(arr, lo, lt - 1)
        _qs3(arr, gt + 1, hi)

    _qs3(arr, 0, len(arr) - 1)
    return arr


# 5. Timsort — standard pure-Python form
MIN_RUN = 32

def timsort_optimized(my_series):

    arr = list(my_series)
    n   = len(arr)
    if n < 2:
        return arr

    def _ins_range(arr, lo, hi):
        i = lo + 1
        while i <= hi:
            key_tmp = arr[i]
            j = i - 1
            while j >= lo and arr[j] > key_tmp:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key_tmp
            i += 1

    def _merge(arr, lo, mid, hi):
        left     = arr[lo:mid + 1]
        left_len = len(left)
        i, j, pos = 0, mid + 1, lo
        while i < left_len and j <= hi:
            if left[i] <= arr[j]:
                arr[pos] = left[i]; i += 1
            else:
                arr[pos] = arr[j];  j += 1
            pos += 1
        while i < left_len:
            arr[pos] = left[i]; i += 1; pos += 1

    lo = 0
    while lo < n:
        _ins_range(arr, lo, min(lo + MIN_RUN - 1, n - 1))
        lo += MIN_RUN

    size = MIN_RUN
    while size < n:
        lo = 0
        while lo < n:
            mid = min(lo + size - 1, n - 1)
            hi  = min(lo + 2 * size - 1, n - 1)
            if mid < hi:
                _merge(arr, lo, mid, hi)
            lo += 2 * size
        size *= 2

    return arr

#------------------------------------------------------------------------------

# ================================================
#  MECHANICAL ALGORITHMS — True Standard forms S
# ================================================

# 1. FC-Sort mechanical
def fc_sort_mechanical(my_series):

    n = 0
    while True:
        try:
            _ = my_series[n]; n += 1
        except IndexError:
            break

    freq_keys = [None] * n
    freq_vals = [0]    * n
    freq_size = 0

    i = 0
    while i < n:
        x = my_series[i]
        found = 0; j = 0
        while j < freq_size:
            if freq_keys[j] == x:
                freq_vals[j] += 1; found = 1; break
            j += 1
        if found == 0:
            freq_keys[freq_size] = x
            freq_vals[freq_size] = 1
            freq_size += 1
        i += 1
    #Case for all Identical Keys
    if freq_size == 1:
        return list(my_series)
 
    s = 1
    while s < freq_size:
        key_tmp = freq_keys[s]; val_tmp = freq_vals[s]; j = s - 1
        while j >= 0 and freq_keys[j] > key_tmp:
            freq_keys[j + 1] = freq_keys[j]
            freq_vals[j + 1] = freq_vals[j]
            j -= 1
        freq_keys[j + 1] = key_tmp
        freq_vals[j + 1] = val_tmp
        s += 1

    arr_out = [0] * n; pos = 0; i = 0
    while i < freq_size:
        val = freq_keys[i]; count = freq_vals[i]; c = 0
        while c < count:
            arr_out[pos] = val; pos += 1; c += 1
        i += 1
    return arr_out


#2. Counting Sort mechanical
def counting_sort_mechanical(my_series):

    n = 0
    while True:
        try:
            _ = my_series[n]; n += 1
        except IndexError:
            break

    # Manual min and max
    min_val = my_series[0]
    max_val = my_series[0]
    i = 1
    while i < n:
        if my_series[i] < min_val:
            min_val = my_series[i]
        if my_series[i] > max_val:
            max_val = my_series[i]
        i += 1

    r = max_val - min_val + 1
    count = [0] * r

    # Count occurrences
    i = 0
    while i < n:
        count[my_series[i] - min_val] += 1
        i += 1

    # Reconstruct output
    arr_out = [0] * n
    pos = 0
    i = 0
    while i < r:
        c = 0
        while c < count[i]:
            arr_out[pos] = i + min_val
            pos += 1
            c += 1
        i += 1
    return arr_out


#3. Radix Sort mechanical
def radix_sort_mechanical(my_series):

    n = 0
    while True:
        try:
            _ = my_series[n]; n += 1
        except IndexError:
            break

    # Manual min for offset
    min_val = my_series[0]
    i = 1
    while i < n:
        if my_series[i] < min_val:
            min_val = my_series[i]
        i += 1
    offset = -min_val if min_val < 0 else 0

    # Build shifted working array
    arr = [0] * n
    i = 0
    while i < n:
        arr[i] = my_series[i] + offset
        i += 1

    # Manual max of shifted array
    max_val = arr[0]
    i = 1
    while i < n:
        if arr[i] > max_val:
            max_val = arr[i]
        i += 1


    exp = 1
    while max_val // exp > 0:
        count_buf = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        output    = [0] * n

        i = 0
        while i < n:
            count_buf[(arr[i] // exp) % 10] += 1
            i += 1

        i = 1
        while i < 10:
            count_buf[i] += count_buf[i - 1]
            i += 1

        i = n - 1
        while i >= 0:
            digit = (arr[i] // exp) % 10
            count_buf[digit] -= 1
            output[count_buf[digit]] = arr[i]
            i -= 1

        i = 0
        while i < n:
            arr[i] = output[i]
            i += 1

        exp *= 10


    arr_out = [0] * n
    i = 0
    while i < n:
        arr_out[i] = arr[i] - offset
        i += 1
    return arr_out


#4. 3-way Quicksort mechanical
def quicksort_3way_mechanical(my_series):

    n = 0
    while True:
        try:
            _ = my_series[n]; n += 1
        except IndexError:
            break

    arr = [0] * n
    i = 0
    while i < n:
        arr[i] = my_series[i]
        i += 1


    stack     = [0] * (n * 2 + 8)
    stack_top = 0
    stack[0]  = 0
    stack[1]  = n - 1
    stack_top = 2

    while stack_top > 0:
        stack_top -= 2
        lo = stack[stack_top]
        hi = stack[stack_top + 1]

        if hi <= lo:
            continue

        # Small partition: insertion sort
        if hi - lo < 16:
            s = lo + 1
            while s <= hi:
                key_tmp = arr[s]; j = s - 1
                while j >= lo and arr[j] > key_tmp:
                    arr[j + 1] = arr[j]; j -= 1
                arr[j + 1] = key_tmp
                s += 1
            continue

        # Median-of-three pivot
        mid = (lo + hi) // 2
        if arr[lo] > arr[mid]:
            arr[lo], arr[mid] = arr[mid], arr[lo]
        if arr[lo] > arr[hi]:
            arr[lo], arr[hi]  = arr[hi],  arr[lo]
        if arr[mid] > arr[hi]:
            arr[mid], arr[hi] = arr[hi],  arr[mid]

        pivot = arr[mid]
        arr[mid], arr[lo] = arr[lo], arr[mid]

        lt = lo; gt = hi; ii = lo + 1
        while ii <= gt:
            if arr[ii] < pivot:
                arr[lt], arr[ii] = arr[ii], arr[lt]
                lt += 1; ii += 1
            elif arr[ii] > pivot:
                arr[ii], arr[gt] = arr[gt], arr[ii]
                gt -= 1
            else:
                ii += 1

        if stack_top + 4 < len(stack):
            stack[stack_top]     = lo
            stack[stack_top + 1] = lt - 1
            stack_top += 2
            stack[stack_top]     = gt + 1
            stack[stack_top + 1] = hi
            stack_top += 2

    return arr


#5. Timsort mechanical
def timsort_mechanical(my_series):
    """
    Standard Timsort — mechanical. No builtins, no slicing. Operates on all n elements.
    Has Manual run detection and merge with Manual temp buffer for merge. No frequency-count dict.
    """
    MIN_RUN_M = 32

    n = 0
    while True:
        try:
            _ = my_series[n]; n += 1
        except IndexError:
            break

    arr = [0] * n
    i = 0
    while i < n:
        arr[i] = my_series[i]
        i += 1

    # Phase 1: insertion sort runs of size MIN_RUN_M
    lo = 0
    while lo < n:
        hi = lo + MIN_RUN_M - 1
        if hi >= n:
            hi = n - 1
        s = lo + 1
        while s <= hi:
            key_tmp = arr[s]; j = s - 1
            while j >= lo and arr[j] > key_tmp:
                arr[j + 1] = arr[j]; j -= 1
            arr[j + 1] = key_tmp
            s += 1
        lo += MIN_RUN_M

    # Phase 2: bottom-up merge
    size = MIN_RUN_M
    while size < n:
        lo = 0
        while lo < n:
            mid = lo + size - 1
            if mid >= n:
                mid = n - 1
            hi = lo + 2 * size - 1
            if hi >= n:
                hi = n - 1

            if mid < hi:
                left_len = mid - lo + 1
                tmp = [0] * left_len
                t = 0
                while t < left_len:
                    tmp[t] = arr[lo + t]
                    t += 1

                ii = 0; jj = mid + 1; pos = lo
                while ii < left_len and jj <= hi:
                    if tmp[ii] <= arr[jj]:
                        arr[pos] = tmp[ii]; ii += 1
                    else:
                        arr[pos] = arr[jj]; jj += 1
                    pos += 1
                while ii < left_len:
                    arr[pos] = tmp[ii]; ii += 1; pos += 1

            lo += 2 * size
        size *= 2

    return arr


# ===========================
# Benchmanrk Code (Frameword)
# ===========================

RUNS = 10

OPTIMIZED_ALGORITHMS = [
    ("FC-Sort",       fc_sort_optimized),
    ("Counting Sort", counting_sort_optimized),
    ("Radix Sort",    radix_sort_optimized),
    ("3-way Quick",   quicksort_3way_optimized),
    ("Timsort",       timsort_optimized),

]

MECHANICAL_ALGORITHMS = [
    ("FC-Sort",       fc_sort_mechanical),
    ("Counting Sort", counting_sort_mechanical),
    ("Radix Sort",    radix_sort_mechanical),
    ("3-way Quick",   quicksort_3way_mechanical),
    ("Timsort",       timsort_mechanical),
]

# Configs: (n, d)
STRESS_CONFIGS = [

    (100_000, 5),
    (100_000, 10),
    (100_000, 15),
    (100_000, 20),
    (100_000, 40),
    (100_000, 80),
    (100_000, 160),
    (500_000, 320),

]

# Mechanical skipped for n above this (too slow)
MECH_THRESHOLD = 1_000_000 #Note-You can alter this limitation to observe specific testing objectives


def generate_dataset(n, d, seed=42):
    """Reproducible low-entropy dataset: n elements, d distinct integer keys."""
    random.seed(seed)
    keys = list(range(1, d + 1))
    return [random.choice(keys) for _ in range(n)]


def verify_correctness(algorithms, data):
    """Verify all algorithms match sorted() on a small sample."""
    sample    = data[:5000]
    reference = sorted(sample)
    failures  = []
    for name, func in algorithms:
        result = func(sample[:])
        if result != reference:
            failures.append(name)
    return failures


def time_function(func, data, runs):
    """Time func(data) over 'runs' independent runs, fresh copy each time."""
    times = []
    for _ in range(runs):
        data_copy = data[:]
        t_start   = time.perf_counter()
        func(data_copy)
        t_end     = time.perf_counter()
        times.append(t_end - t_start)
    return times


def run_benchmark(algorithms, n, d):
    """Run all algorithms on one (n, d) configuration."""
    data     = generate_dataset(n, d)
    failures = verify_correctness(algorithms, data)
    if failures:
        print(f"\n  !! CORRECTNESS FAILURE: {failures}")

    results = []
    for name, func in algorithms:
        times    = time_function(func, data, RUNS)
        mean_ms  = statistics.mean(times)   * 1000
        stdev_ms = statistics.stdev(times)  * 1000
        med_ms   = statistics.median(times) * 1000
        min_ms   = min(times)               * 1000
        results.append({
            "name":     name,
            "mean_ms":  mean_ms,
            "stdev_ms": stdev_ms,
            "min_ms":   min_ms,
        })

    results.sort(key=lambda r: r["mean_ms"])
    for rank, r in enumerate(results, 1):
        r["rank"] = rank
    return results


def format_table(title, all_results, configs):
    """Format a results table — one block per (n, d) configuration."""
    lines = []
    lines.append("")
    lines.append("=" * 92)
    lines.append(f"  {title}")
    lines.append(f"  Runs per config: {RUNS}   |   Times in milliseconds (ms)")
    lines.append("=" * 92)

    for (n, d) in configs:
        lines.append("")
        lines.append(f"  n = {n:>12,}   |   unique/distinct keys d = {d}")
        lines.append("-" * 92)
        lines.append(f"  {'Algorithm':<18}  {'Mean':>10}  {'±StDev':>9}  "
                     f"{'Rank':>5}")
        lines.append("  " + "-" * 68)
        for r in all_results[(n, d)]:
            lines.append(
                f"  {r['name']:<18}  "
                f"{r['mean_ms']:>8.2f}ms  "
                f"{r['stdev_ms']:>7.2f}ms  "
                #f"{r['min_ms']:>8.2f}ms  "
                f"  #{r['rank']}"
            )

    lines.append("")
    lines.append("=" * 92)
    return "\n".join(lines)


def print_machine_info():
    lines = []
    lines.append("")
    lines.append("=" * 92)
    lines.append("  FC-SORT STRESS BENCHMARK — MACHINE INFORMATION")
    lines.append("=" * 92)
    lines.append(f"  OS           : {platform.system()} {platform.release()}")
    lines.append(f"  Machine      : {platform.machine()}")
    lines.append(f"  Processor    : {platform.processor()}")
    lines.append(f"  Python       : {sys.version.split()[0]}")
    lines.append(f"  Runs/config  : {RUNS}")
    lines.append(f"  Mech limit   : mechanical skipped for n > {MECH_THRESHOLD:,}")
    lines.append("  NOTE         : All competitors run in TRUE standard form.")
    lines.append("                 No frequency-count wrapper applied to competitors.")
    lines.append("=" * 92)
    block = "\n".join(lines)
    print(block)
    return block


# =============================================================================
# ── MAIN ──────────────────────────────────────────────────────────────────────
# =============================================================================

if __name__ == "__main__":

    header_block = print_machine_info()

    mech_configs = [(n, d) for (n, d) in STRESS_CONFIGS if n <= MECH_THRESHOLD]
    skip_mech    = [(n, d) for (n, d) in STRESS_CONFIGS if n >  MECH_THRESHOLD]

    opt_results  = {}
    mech_results = {}

    total = len(STRESS_CONFIGS)
    done  = 0

    print("\n  Running benchmarks...\n")
    if skip_mech:
        print(f"  Mechanical skipped for: {skip_mech}\n")

    for (n, d) in STRESS_CONFIGS:
        done += 1
        pct   = int(100 * done / total)

        print(f"  [{pct:3d}%]  n={n:>12,}  d={d:>3}  optimized  ...",
              end="", flush=True)
        opt_results[(n, d)] = run_benchmark(OPTIMIZED_ALGORITHMS, n, d)
        print("  done")

        if n <= MECH_THRESHOLD:
            print(f"         n={n:>12,}  d={d:>3}  mechanical ...",
                  end="", flush=True)
            mech_results[(n, d)] = run_benchmark(MECHANICAL_ALGORITHMS, n, d)
            print("  done")
        else:
            print(f"         n={n:>12,}  d={d:>3}  mechanical   SKIPPED")

    # This section contain the TaBLES --------------------------
    table_b = format_table(
        "TABLE B — OPTIMIZED VERSIONS  (all n, standard algorithm forms)",
        opt_results, STRESS_CONFIGS
    )

    if mech_configs:
        table_a = format_table(
            f"TABLE A — MECHANICAL VERSIONS  (n <= {MECH_THRESHOLD:,} only,"
            f" standard algorithm forms)",
            mech_results, mech_configs
        )
    else:
        table_a = "  TABLE A: all configs exceeded MECH_THRESHOLD — not run."

    print(table_b)
    print(table_a)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "fc_sort_stress_results.txt")
    with open(out_path, "w") as f:
        f.write(header_block + "\n")
        f.write(table_b    + "\n")
        f.write(table_a    + "\n")

    print(f"\n  Results saved to: {out_path}\n")

