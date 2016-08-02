# -*- coding: utf-8 -*-
"""

This is a wrapper executing a command and sending its stdout/stderr to the
Sentry server.

Useful to work with cron jobs. Unless misconfigured, the wrapper itself is
quiet. It launches the program, captures its output, and if the program has
been ended with non-zero exit code, builds a message and puts it to the remote
server.

.. warning:: Don't try to launch scripts producing a lot of data to
             stdout / stderr with this wrapper, as it stores everything in
             memory and thus can easily make your system swap.

Example of cron task::

    SENTRY_DSN='http://...../'
    */30 * * * *  raven-sh -- bash -c 'echo hello world; exit 1'

"""
from __future__ import absolute_import
from __future__ import print_function

import warnings

import os
import sys
import optparse
import logging
import raven
from raven.utils.json import json
from pprint import pprint
import subprocess as subp


def store_json(option, opt_str, value, parser):
    try:
        value = json.loads(value)
    except ValueError:
        print("Invalid JSON was used for option %s.  Received: %s" % (opt_str, value))
        sys.exit(1)
    setattr(parser.values, option.dest, value)


class Runner(object):

    def __init__(self):
        parser = self.get_parser()
        self.opts, self.args = parser.parse_args()
        self.raven = self.get_raven()
        if not self.args:
            raise SystemExit('Command to execute is not defined. Exit')
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(format='%(message)s')

    def get_parser(self):
        parser = optparse.OptionParser(usage=__doc__)
        parser.add_option('--dsn', dest='dsn',
                          help='Sentry DSN. Alternatively setup SENTRY_DSN '
                               'environment variable')

        parser.add_option("--extra", action="callback", callback=store_json,
                          type="string", nargs=1, dest="extra",
                          help='extra data to save (as json string)')

        parser.add_option("--tags", action="callback", callback=store_json,
                          type="string", nargs=1, dest="tags",
                          help='tags to save with message (as json string)')

        parser.add_option('--debug', action='store_true',
                          help='Don\'t send anything to remote server. '
                               'Just print stdout and stderr')

        parser.add_option('--message', help='Message string to send to sentry '
                                            '(optional)')
        return parser

    def run(self):
        pipe = subp.Popen(self.args, stdout=subp.PIPE, stderr=subp.PIPE)
        out, err = pipe.communicate()
        self.log(out, err, pipe.returncode)

    def log(self, out, err, returncode):
        if returncode == 0:
            return

        tags = self.opts.tags or {}
        tags.update({
            'returncode': returncode,
            'callable': self.args[0]
        })
        extra = self.opts.extra or {}
        extra.update({
            'returncode': returncode,
            'command': self.get_command(),
        })
        extra.update(string_to_chunks('stdout', out.rstrip()))
        extra.update(string_to_chunks('stderr', err.rstrip()))

        capture_message_kwargs = dict(
            message=self.get_raven_message(returncode),
            level=logging.ERROR,
            tags=tags,
            extra=extra,
        )

        if self.opts.debug:
            pprint(capture_message_kwargs)
        else:
            self.raven.captureMessage(**capture_message_kwargs)

    def get_raven_message(self, returncode):
        if self.opts.message:
            return self.opts.message
        return '"%s" failed with code %d' % (self.get_command(), returncode)

    def get_command(self):
        return ' '.join(self.args)

    def get_raven(self):
        dsn = self.opts.dsn or os.getenv('SENTRY_DSN')
        error_msg = 'Neither --dsn option or SENTRY_DSN env variable defined'

        if not dsn and self.opts.debug:
            warnings.warn(error_msg)
            dsn = 'https://x:x@localhost/1'

        if not dsn:
            raise SystemExit(error_msg)

        return raven.Client(dsn=dsn)


def string_to_chunks(name, string, max_chars=400):
    """
    Sentry has message size limits: no more than 400 chars in a string, and no more than 50 elements in a list.

    Since stdout and stderr is the only important piece of data we have, we do our best to collect as much as possible
    """
    chunks = []
    chunk_items = []
    chunk_chars = 0

    for line in (string or '').splitlines():

        if chunk_chars + len(line) + 1 <= max_chars:  # +1 is "\n" to join
            # keep adding values to current chunk
            chunk_items.append(line)
            chunk_chars += len(line) + 1
        else:
            # close current chunk and create a new one
            if chunk_items:
                chunks.append('\n'.join(chunk_items))
            chunk_items = [line]
            chunk_chars = len(line) + 1

    # final action: close current chunk
    if chunk_items:
        chunks.append('\n'.join(map(str, chunk_items)))

    # format output
    if not chunks:
        return {}

    if len(chunks) == 1:
        return {name: chunks[0]}

    ret = {}
    positions = len(str(len(chunks)))  # e.g. returns 3 for 111 chunks
    template = '%s%%0%dd' % (name, positions)  # something like 'stdout%03d'
    for i, chunk in enumerate(chunks):
        ret[template % i] = chunk
    return ret


def main():
    runner = Runner()
    runner.run()

if __name__ == '__main__':
    main()
