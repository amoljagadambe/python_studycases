import concurrent.futures
import time


class SimpleObject(object):

    def __init__(self, name):
        self.name = name
        l = list(name)
        l.reverse()
        self.name_backwards = ''.join(l)

    def __repr__(self):
        return self.name_backwards


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
        future_obj_class_obj = executor.map(SimpleObject, ['pickle', 'cpickle', 'last'])
        future_obj_one_task = executor.submit(do_one_task, 2)
        future_obj_second_task = executor.submit(do_second_task, 3)

    data_out = future_obj_one_task.result()
    data_out_list = future_obj_second_task.result()
    print(list(future_obj_class_obj))
    t2 = time.perf_counter()

    print(f'Finished in {t2 - t1} seconds')
