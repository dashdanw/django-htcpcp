"""Signals sent by HTCPCPMiddleware, for wiring up real (or imaginary) hardware.

Every signal is sent with ``request``, ``pot`` and ``variety`` keyword arguments.
"""

from django.dispatch import Signal

#: A pot started brewing. Also sent with ``additions``.
brew_started = Signal()
#: A client sent "stop". Also sent with ``elapsed`` and ``strength`` (None for coffee).
brew_stopped = Signal()
#: A client said WHEN.
when_said = Signal()
