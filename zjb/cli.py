#!/usr/bin/env python3

import multiprocessing
import signal

from zjb import puller
from zjb import server


def handle_sigterm(*args):
    raise KeyboardInterrupt()


def main() -> None:
    puller_process = multiprocessing.Process(target=puller.main)
    server_process = multiprocessing.Process(target=server.main)

    puller_process.start()
    server_process.start()

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        if puller_process.is_alive():
            puller_process.join()
        if server_process.is_alive():
            server_process.join()
    except KeyboardInterrupt:
        if puller_process.is_alive():
            puller_process.terminate()
        if server_process.is_alive():
            server_process.terminate()
    else:
        puller_process.close()
        server_process.close()
