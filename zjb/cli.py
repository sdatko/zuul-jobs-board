#!/usr/bin/env python3

import argparse
import multiprocessing
import signal

from zjb import puller
from zjb import server


def handle_sigterm(*args):
    raise KeyboardInterrupt()


def main() -> None:
    parser = argparse.ArgumentParser(description='''
        Utility to run Zuul Jobs Board processes (puller, server or both).
    ''')
    parser.add_argument('-p', '--puller', dest='puller',
                        default=False, action='store_true',
                        help='run the puller process')
    parser.add_argument('-s', '--server', dest='server',
                        default=False, action='store_true',
                        help='run the server process')

    args = parser.parse_args()

    if not args.puller and not args.server:
        parser.print_help()

    puller_process = multiprocessing.Process(target=puller.main)
    server_process = multiprocessing.Process(target=server.main)

    if args.puller:
        puller_process.start()
    if args.server:
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
