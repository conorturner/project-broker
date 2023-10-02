from pathlib import Path
import os
from functools import cached_property


class UniqueWorker:
    def __init__(self, path):
        self.path = Path(path)
        self.id = str(os.getpid())
        self._set_id()

    def _set_id(self):
        """create the path to the pid file if it doesn't exist,
        write the pid to the file
        """
        if self.path.exists():
            self.path.parents[0].mkdir(parents=True, exist_ok=True)

        with open(self.path, "w") as f:
            f.write(self.id)

    @cached_property
    def is_assiged(self):
        """check if the worker in this process has been assigned
        as the unique worker
        """
        with open(self.path, "r") as f:
            assigned_worker = f.read()

        return assigned_worker == self.id


def by_one_worker(worker_pid_path):
    """Decorator to run startup function in only one worker from
    https://stackoverflow.com/questions/68547503/uvicorn-fastapi-execute-code-on-a-single-worker-only"""
    unique_worker = UniqueWorker(worker_pid_path)

    def deco(f):
        def wrapped(*args, **kwargs):
            if not unique_worker.is_assiged:
                return

            return f(*args, **kwargs)

        return wrapped

    return deco
