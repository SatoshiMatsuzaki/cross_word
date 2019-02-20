#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import os
import logging

from crossword import CrossWord

# setting logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# TODO: default values will be read from setting file.


@click.command(context_settings={"ignore_unknown_options": True})
@click.option('-s', '--size', default=4, type=int, help="cross word size")
@click.option('-b', '--blocks', default=[], type=str,
              help="number(0<x<size-2) or positions of blocks. Setting as positions, input following 1:2,2:4,4:1")
@click.option('-d', '--dict', default=None, type=str, help="dictionary path")
def cli(size, blocks, dict):
    """

    :param size:
    :param blocks:
    :param dict:
    :return:
    """

    cw = CrossWord(5, [(2, 2), (2, 5), (4, 2), (5, 4)])

    cw.show()

    cw.create()

    cw.show()


if __name__ == '__main__':
    cli()
