# training_utils.py

import sys
import os
# Get the current directory and parent directory for importing modules
# This is done to allow importing modules from the parent directory
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

import queue
import multiprocessing

class DataLoaderWithTimeout:
    def __init__(self, dataloader):
        self.dataloader = dataloader
        self.data_queue = multiprocessing.Manager().Queue()
        self.pool = multiprocessing.Pool(processes=1)
        self.should_stop = multiprocessing.Value('b', False)

    def __len__(self):
        return len(self.dataloader)

    def load_data(self):
        try:
            for item in self.dataloader:
                if self.should_stop.value:
                    break
                self.data_queue.put(item)
        except Exception as e:
            self.data_queue.put(e)

    def __iter__(self):
        self.pool.apply_async(self.load_data)

        while True:
            try:
                item = self.data_queue.get(timeout=1)
                if isinstance(item, Exception):
                    raise item
                yield item
            except queue.Empty:
                if not any(process.is_alive() for process in self.pool._pool):
                    break
            finally:
                if self.should_stop.value:
                    break

    def stop(self):
        self.should_stop.value = True
        self.pool.terminate()
        self.pool.join()

    def add_worker_process(self, process):
        pass