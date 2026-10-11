"""Exclusive per-actor controller ownership and safe local process inspection."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess

DATA=Path(__file__).resolve().parents[1]/'server/data'


@contextmanager
def ownership(actor_id, objective):
    """Hold a private nonblocking lock so two agents cannot control the same actor."""
    DATA.mkdir(parents=True,exist_ok=True)
    path=DATA/f'brain-{actor_id}.lock'
    with path.open('a+') as lock:
        path.chmod(0o600)
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise RuntimeError('another controller owns this actor') from exc
        lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
        (DATA/'brain.pid').write_text(str(os.getpid()))
        (DATA/'controller.json').write_text(json.dumps({'actor':actor_id,'pid':os.getpid(),'objective':objective}))
        try:yield
        finally:fcntl.flock(lock,fcntl.LOCK_UN)


def status():
    """Read the private controller reference and verify the PID still runs this brain."""
    path=DATA/'controller.json'
    if not path.exists():return {'running':False}
    info=json.loads(path.read_text())
    result=subprocess.run(['ps','-p',str(info['pid']),'-o','command='],capture_output=True,text=True,timeout=2)
    info['running']=result.returncode==0 and '-m brain' in result.stdout
    return info


def stop():
    """Send SIGTERM only to a verified local brain controller; its halt handler stops inputs."""
    info=status()
    if info['running']:os.kill(info['pid'],signal.SIGTERM)
    return {**info,'stop_requested':info['running']}
