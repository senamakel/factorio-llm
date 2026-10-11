"""Timeouts must terminate blocking operations and detect genuine lack of progress."""
import signal
import time
import unittest
from brain.timeouts import deadline,ProgressWatchdog


class TimeoutTest(unittest.TestCase):
    def test_blocked_operation_times_out_and_restores_signal_handler(self):
        before=signal.getsignal(signal.SIGALRM)
        with self.assertRaises(TimeoutError):
            with deadline(.03,'blocked operation'):time.sleep(.2)
        self.assertEqual(signal.getsignal(signal.SIGALRM),before)
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0],0)

    def test_clock_ticking_without_inventory_or_movement_is_not_progress(self):
        now=[0];watchdog=ProgressWatchdog(10,clock=lambda:now[0])
        state={'tick':1,'players':[{'position':{'x':0,'y':0},'inventory':{}}]}
        watchdog.check(state,{'ok':True})
        now[0]=11;state['tick']=600
        with self.assertRaises(TimeoutError):watchdog.check(state,{'ok':True})

    def test_three_failed_actions_stop_even_if_some_state_changes(self):
        watchdog=ProgressWatchdog()
        watchdog.check({}, {'ok':False});watchdog.check({}, {'ok':False})
        with self.assertRaisesRegex(TimeoutError,'consecutive'):watchdog.check({}, {'ok':False})
