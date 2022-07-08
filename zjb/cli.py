#!/usr/bin/env python3

import multiprocessing

from zjb import puller
from zjb import server


def main() -> None:
    puller_process = multiprocessing.Process(target=puller.main)
    server_process = multiprocessing.Process(target=server.main)

    puller_process.start()
    server_process.start()

    puller_process.join()
    server_process.join()
