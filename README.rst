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
