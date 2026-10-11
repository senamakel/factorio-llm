"""Durable SQLite history for recursive-factorio; journal offsets commit with events."""
from contextlib import AbstractContextManager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import zlib

DEFAULT_DB = Path(__file__).resolve().parents[1]/'server/data/brain.sqlite3'


def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',', ':'),ensure_ascii=False,allow_nan=False)


class EventStore(AbstractContextManager):
    """Store observations, decisions, outcomes and learned scores in a WAL database."""
    def __init__(self, path=DEFAULT_DB, secrets=()):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(self.path,os.O_CREAT|os.O_RDWR,0o600); os.close(fd)
        self.path.chmod(0o600)
        self.secrets=tuple(s for s in secrets if s)
        self.conn=sqlite3.connect(self.path,timeout=15)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY, recorded_at REAL NOT NULL, game_tick INTEGER,
                kind TEXT NOT NULL, source TEXT NOT NULL, payload_json TEXT NOT NULL,
                source_key TEXT UNIQUE);
            CREATE INDEX IF NOT EXISTS events_tick ON events(game_tick);
            CREATE INDEX IF NOT EXISTS events_kind ON events(kind);
            CREATE TABLE IF NOT EXISTS cursors(
                path TEXT PRIMARY KEY, identity TEXT NOT NULL, generation INTEGER NOT NULL,
                offset INTEGER NOT NULL, prefix BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS snapshots(
                id INTEGER PRIMARY KEY, recorded_at REAL NOT NULL, game_tick INTEGER,
                state_hash TEXT NOT NULL, state_zlib BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS decisions(
                id INTEGER PRIMARY KEY, snapshot_id INTEGER REFERENCES snapshots(id),
                recorded_at REAL NOT NULL, phase TEXT NOT NULL, decision_json TEXT NOT NULL,
                applied INTEGER NOT NULL DEFAULT 0, outcome_json TEXT);
            CREATE TABLE IF NOT EXISTS learning(
                action_key TEXT PRIMARY KEY, attempts INTEGER NOT NULL, failures INTEGER NOT NULL,
                total_reward REAL NOT NULL, updated_at REAL NOT NULL);
        ''')

    def close(self):
        self.conn.close()

    def __exit__(self,*args):
        self.close()

    def redact(self,value):
        if isinstance(value,dict):
            return {k:('[redacted]' if any(t in k.lower() for t in ('password','api_key','token','secret'))
                       else self.redact(v)) for k,v in value.items()}
        if isinstance(value,list):
            return [self.redact(v) for v in value]
        if isinstance(value,str):
            for secret in self.secrets:
                value=value.replace(secret,'[redacted]')
        return value

    def log(self,kind,payload,tick=None,source='brain',source_key=None):
        with self.conn:
            self.conn.execute('INSERT OR IGNORE INTO events VALUES(NULL,?,?,?,?,?,?)',
                (time.time(),tick,kind,source,encode(self.redact(payload)),source_key))

    def ingest(self,path,limit=10000):
        """Import complete JSONL records exactly once; leave a partial final line for next time."""
        path=Path(path).resolve()
        if not path.exists():
            return 0
        stat=path.stat(); identity=f'{stat.st_dev}:{stat.st_ino}'
        row=self.conn.execute('SELECT identity,generation,offset,prefix FROM cursors WHERE path=?',(str(path),)).fetchone()
        generation,offset,prefix=(0,0,b'') if row is None else (row[1],row[2],row[3])
        with path.open('rb') as stream:
            current_prefix=stream.read(64)
            if row and (row[0]!=identity or stat.st_size<offset or current_prefix[:len(prefix)]!=prefix):
                generation+=1; offset=0
            stream.seek(offset)
            count=0
            with self.conn:
                for _ in range(limit):
                    position=stream.tell(); line=stream.readline()
                    if not line or not line.endswith(b'\n'):
                        break
                    try:
                        event=json.loads(line)
                        tick=event.get('tick'); kind=event.get('kind','unknown')
                    except (ValueError,AttributeError):
                        event={'error':'malformed game journal record','byte_offset':position}
                        tick=None; kind='journal_error'
                    key=f'{path}:{identity}:{generation}:{position}'
                    cursor=self.conn.execute('INSERT OR IGNORE INTO events VALUES(NULL,?,?,?,?,?,?)',
                        (time.time(),tick,kind,'factorio',encode(self.redact(event)),key))
                    count+=cursor.rowcount
                    offset=stream.tell()
                self.conn.execute('INSERT OR REPLACE INTO cursors VALUES(?,?,?,?,?)',
                    (str(path),identity,generation,offset,current_prefix))
        return count

    def snapshot(self,state):
        raw=encode(self.redact(state)).encode()
        with self.conn:
            cursor=self.conn.execute('INSERT INTO snapshots VALUES(NULL,?,?,?,?)',
                (time.time(),state.get('tick'),hashlib.sha256(raw).hexdigest(),zlib.compress(raw)))
        return cursor.lastrowid

    def load_snapshot(self,ident):
        row=self.conn.execute('SELECT state_zlib FROM snapshots WHERE id=?',(ident,)).fetchone()
        if row is None:
            raise KeyError(ident)
        return json.loads(zlib.decompress(row[0]))

    def decision(self,snapshot_id,decision,applied=False):
        with self.conn:
            cursor=self.conn.execute('INSERT INTO decisions VALUES(NULL,?,?,?,?,?,NULL)',
                (snapshot_id,time.time(),decision['phase'],encode(decision),int(applied)))
        return cursor.lastrowid

    def outcome(self,ident,result):
        with self.conn:
            self.conn.execute('UPDATE decisions SET outcome_json=? WHERE id=?',(encode(self.redact(result)),ident))

    def learn(self,action_key,success,reward):
        with self.conn:
            self.conn.execute('''INSERT INTO learning VALUES(?,1,?,?,?) ON CONFLICT(action_key)
                DO UPDATE SET attempts=attempts+1,failures=failures+excluded.failures,
                total_reward=total_reward+excluded.total_reward,updated_at=excluded.updated_at''',
                (action_key,int(not success),float(reward),time.time()))

    def experience(self):
        return {key:{'attempts':n,'failures':failures,'mean_reward':reward/n}
                for key,n,failures,reward in self.conn.execute('SELECT action_key,attempts,failures,total_reward FROM learning')}

    def recent_events(self,limit=30):
        return [{'tick':tick,'kind':kind,'source':source,'payload':json.loads(payload)} for tick,kind,source,payload
                in self.conn.execute('SELECT game_tick,kind,source,payload_json FROM events ORDER BY id DESC LIMIT ?',(limit,))]

    def count(self,table):
        if table not in {'events','snapshots','decisions','learning'}:
            raise ValueError('unknown table')
        return self.conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
