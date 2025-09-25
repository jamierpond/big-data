import os
from queue import Queue
import time
import threading

# this was faster than using a collections.deque, idk why
q = Queue(maxsize=100000)  # maxsize can be adjusted as needed

# config
BATCH_SIZE = 10000

# clear the log file at start
if os.path.exists("data.log"):
    os.remove("data.log")


def creates_lots_of_data_from_a_sensor():
    while True:
        t = time.time()
        q.put(f"data at {t}" + "x" * 1000)


def write_data_to_log():
    with open("data.log", "a") as f:
        while True:
            print(f"Queue size: {q.qsize()}")
            n = 0
            str_batch = ""
            while q:
                str_batch += q.get() + "\n"
                n += 1
                if n >= BATCH_SIZE:
                    f.write(str_batch)
                    f.flush()
                    n = 0
            else:
                print("No data to write, sleeping...")
                time.sleep(0.1)


def main():
    # to calculate write speed
    start_time = time.time()

    data_thread = threading.Thread(target=creates_lots_of_data_from_a_sensor)
    data_thread.daemon = True
    data_thread.start()

    log_thread = threading.Thread(target=write_data_to_log)
    log_thread.daemon = True
    log_thread.start()

    while True:
        try:
            with open("data.log", "r") as f:
                f.seek(0, 2)  # Move to end of file
                size = f.tell()
                size_mb = size / (1024 * 1024)
                size_gb = size / (1024 * 1024 * 1024)
                now = time.time()
                gb_ps = size_gb / (now - start_time)
                percent_deque_full = (q.qsize() / q.maxsize) * 100
                print(f"Log file size: {size_mb:.2f} MB ({size_gb:.2f} GB), Write speed: {gb_ps:.4f} GB/s, Queue usage: {percent_deque_full:.2f}%")
        except FileNotFoundError:
            print("Log file not found yet.")


if __name__ == "__main__":
    main()
