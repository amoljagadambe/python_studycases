import concurrent.futures
import time


def do_one_task(seconds):
    print(f'Sleeping {seconds} second(s)...')
    time.sleep(seconds)
    return True


def do_second_task(seconds):
    print(f'Sleeping {seconds} second(s)...')
    # time.sleep(seconds)
    return [1.23, 2]


if __name__ == "__main__":
    t1 = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_obj_one_task = executor.submit(do_one_task, 2)
        future_obj_second_task = executor.submit(do_second_task, 3)

    data_out = future_obj_one_task.result()
    data_out_list = future_obj_second_task.result()

    t2 = time.perf_counter()

    print(f'Finished in {t2 - t1} seconds')
