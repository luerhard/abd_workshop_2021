from multiprocessing import JoinableQueue, Queue, Process
import os
import signal
import time

import setproctitle


class QueuedMultiProcessor:
    STOP_SIGNAL = "STOP"
    QUEUE_SIZE = 1500
    SLEEP_IF_FULL = 0.01

    def __init__(
        self,
        stream,
        worker,
        writer,
        worker_setup=None,
        writer_setup=None,
        writer_teardown=None,
        logger=None,
        chunksize=1,
    ):

        self.worker = worker
        self.worker_initializer = worker_setup

        self.writer = writer
        self.writer_initializer = writer_setup
        self.writer_teardown = writer_teardown

        self.chunksize = chunksize

        self.stream = stream
        self.logger = logger

        self.processes = []
        self.name = "Main Process"

    def writer_wrapper(self):
        self.name = "py_WRITER"
        setproctitle.setproctitle(self.name)
        if self.writer_initializer:
            self.writer_initializer()

        while True:
            chunk = self.out_queue.get()
            if chunk == self.STOP_SIGNAL:
                break
            for item in chunk:
                self.writer(item)

        if self.writer_teardown:
            if self.logger:
                self.logger.info("Tearing down Writer")
            self.writer_teardown()

    def worker_wrapper(self, i):
        self.name = f"py_WORKER_{i}"
        setproctitle.setproctitle(self.name)
        if self.worker_initializer:
            self.worker_initializer()

        while True:
            cache = []
            chunk = self.in_queue.get()
            if chunk == self.STOP_SIGNAL:
                self.in_queue.task_done()
                break
            for item in chunk:
                result = self.worker(item)
                cache.append(result)
            self.out_queue.put(cache)
            self.in_queue.task_done()

    def kill_all_workers(self, *args):
        if self.logger:
            self.logger.critical("KILLING %s", self.name)
        os.kill(os.getpid(), signal.SIGKILL)

    def _run(self, n_workers):

        self.in_queue = JoinableQueue(maxsize=self.QUEUE_SIZE)
        self.out_queue = Queue(maxsize=self.QUEUE_SIZE)

        signal.signal(signal.SIGINT, self.kill_all_workers)
        self.write_process = Process(target=self.writer_wrapper)
        self.write_process.start()

        for i, _ in enumerate(range(n_workers), 1):
            proc = Process(target=self.worker_wrapper, args=(i,))
            proc.start()
            self.processes.append(proc)

        cache = []
        for item in self.stream:
            cache.append(item)
            while self.in_queue.full():
                time.sleep(self.SLEEP_IF_FULL)
            if len(cache) > self.chunksize:
                self.in_queue.put(cache)
                cache = []
        self.in_queue.put(cache)
        for _ in self.processes:
            self.in_queue.put(self.STOP_SIGNAL)

        if self.logger:
            self.logger.info("joining in_queue")
        self.in_queue.join()

        for worker in self.processes:
            worker.join()

        if self.logger:
            self.logger.info("killing processes")

        self.out_queue.put(self.STOP_SIGNAL)
        self.write_process.join()

    def run(self, n_workers=2):
        setproctitle.setproctitle("py_MAIN")
        self._run(n_workers)
