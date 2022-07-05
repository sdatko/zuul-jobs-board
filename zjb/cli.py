#!/usr/bin/env python3

from zjb import puller
from zjb import server


def main(argv=None) -> None:
    puller.main()
    server.main()
