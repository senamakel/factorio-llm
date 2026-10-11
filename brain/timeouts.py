"""Operation deadlines and measured progress guards for the local brain controller."""
from contextlib import contextmanager
import json
import signal
import threading
import time


@contextmanager
def deadline(seconds, operation):
    """Interrupt blocking main-thread work after seconds; preserve nested timers.

    The local controller runs on macOS/Linux's main thread. Background-thread
    callers must use a worker process rather than silently losing this deadline.
    Network sockets also retain their own timeout. No asynchronous game command
    can be undone by this timer; the runner sends a bounded native stop on exit.
    """
    if seconds<=0:raise ValueError('deadline must be positive')
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError('brain operation deadlines require the main thread')
    previous_handler=signal.getsignal(signal.SIGALRM)
    previous_timer=signal.getitimer(signal.ITIMER_REAL)
    started=time.monotonic()
    effective=min(seconds,previous_timer[0]) if previous_timer[0]>0 else seconds
    def expired(signum, frame):
        raise TimeoutError(f'{operation} exceeded {effective:.2f}s')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,effective)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous_handler)
        if previous_timer[0]>0:
            remaining=max(.0001,previous_timer[0]-(time.monotonic()-started))
            signal.setitimer(signal.ITIMER_REAL,remaining,previous_timer[1])


class ProgressWatchdog:
    """Stop repeated failures or a stalled material/movement/research state."""
    def __init__(self, stall_seconds=120, max_failures=3, clock=time.monotonic):
        if stall_seconds<=0 or max_failures<=0:raise ValueError('watchdog limits must be positive')
        self.stall_seconds=stall_seconds;self.max_failures=max_failures;self.clock=clock
        self.last_progress=clock();self.signature=None;self.failures=0

    def check(self, state, result):
        """Raise TimeoutError on lack of meaningful progress or consecutive action failures."""
        player=(state.get('players') or [{}])[0]
        pos=player.get('position',{'x':0,'y':0})
        signature=json.dumps({'position':{k:round(v,1) for k,v in pos.items()},
                              'inventory':player.get('inventory'),
                              'entities':state.get('entities'),
                              'research':state.get('research_progress'),
                              'technologies':state.get('technologies'),
                              'red_produced':state.get('red_produced')},sort_keys=True)
        # Entity energy/status may fluctuate while nothing useful happens. Exclude
        # them from the signature; keep actual inventory, structure and fluid changes.
        payload=json.loads(signature)
        for entity in payload.get('entities') or []:
            for key in ('energy','status','remaining_burning_fuel'):entity.pop(key,None)
        signature=json.dumps(payload,sort_keys=True)
        if signature!=self.signature:self.signature=signature;self.last_progress=self.clock()
        self.failures=0 if result.get('ok') else self.failures+1
        if self.failures>=self.max_failures:raise TimeoutError(f'stopped after {self.failures} consecutive action failures')
        if self.clock()-self.last_progress>=self.stall_seconds:raise TimeoutError('no measured progress within stall timeout')
