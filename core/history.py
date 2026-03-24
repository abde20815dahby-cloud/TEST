import os
import shutil
import time
from typing import Dict, List, Tuple, Optional, Callable

from core.config import USER_DOCS


class ActionHistoryManager:
    def __init__(self):
        self.history_dir: str = os.path.join(USER_DOCS, "ANCFCC_Action_History")
        os.makedirs(self.history_dir, exist_ok=True)
        self.undo_stack: List[Dict] = []
        self.redo_stack: List[Dict] = []
        self.current_batch: Optional[Dict] = None

    def start_batch(self, name: str) -> None:
        if self.current_batch:
            self.commit_batch()
        self.current_batch = {
            "name": name,
            "id": str(int(time.time() * 1000)),
            "changes": {},
        }

    def _record_state(self, path: str, state_key: str) -> None:
        if not self.current_batch:
            return
        if path not in self.current_batch["changes"]:
            self.current_batch["changes"][path] = {"before": None, "after": None}

        if os.path.exists(path):
            safe_path = os.path.join(
                self.history_dir,
                f"{os.path.basename(path)}_{self.current_batch['id']}_{state_key}.bak",
            )
            try:
                shutil.copy2(path, safe_path)
                self.current_batch["changes"][path][state_key] = safe_path
            except Exception:
                pass

    def record_before(self, path: str) -> None:
        self._record_state(path, "before")

    def record_after(self, path: str) -> None:
        self._record_state(path, "after")

    def commit_batch(self, callback: Optional[Callable] = None) -> None:
        if self.current_batch and self.current_batch["changes"]:
            self.undo_stack.append(self.current_batch)
            self.redo_stack.clear()
            self.current_batch = None
            if callback:
                callback()
        else:
            self.current_batch = None

    def undo(self) -> Tuple[bool, str]:
        if not self.undo_stack:
            return False, "لا توجد عمليات للتراجع"
        batch = self.undo_stack.pop()
        for path, states in batch["changes"].items():
            self._restore_file(states.get("before"), path)
        self.redo_stack.append(batch)
        return True, batch["name"]

    def redo(self) -> Tuple[bool, str]:
        if not self.redo_stack:
            return False, "لا توجد عمليات للإعادة"
        batch = self.redo_stack.pop()
        for path, states in batch["changes"].items():
            self._restore_file(states.get("after"), path)
        self.undo_stack.append(batch)
        return True, batch["name"]

    def _restore_file(self, source_bak: Optional[str], target_path: str) -> None:
        if source_bak and os.path.exists(source_bak):
            target_dir = os.path.dirname(target_path)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
            try:
                shutil.copy2(source_bak, target_path)
            except Exception:
                pass
        else:
            if os.path.exists(target_path):
                os.remove(target_path)
