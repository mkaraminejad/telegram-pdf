"""Temporary File and Storage Management Service.

Provides isolated workspace directories for each processing task,
prevents path traversal attacks, enforces 24-hour cleanup, and defines
an extensible storage interface for future S3/MinIO cloud backends.
"""
import os
import shutil
import time
import uuid
import re
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from pathlib import Path

from bot.config import settings

logger = logging.getLogger(__name__)


class BaseStorage(ABC):
    """Abstract interface for file persistence (Local filesystem or S3)."""

    @abstractmethod
    def create_task_workspace(self, task_id: str) -> str:
        pass

    @abstractmethod
    def save_file(self, task_id: str, filename: str, data: bytes) -> str:
        pass

    @abstractmethod
    def cleanup_task(self, task_id: str) -> None:
        pass

    @abstractmethod
    def purge_expired(self, max_age_hours: int) -> int:
        pass


class LocalStorageManager(BaseStorage):
    """Manages isolated local disk directories with automatic cleanup."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.STORAGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Strips path traversal attempts and dangerous characters from user filenames."""
        # Extract filename without directory path
        clean_name = os.path.basename(filename)
        # Remove any non-alphanumeric/farsi characters except dot, underscore, dash
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.\u0600-\u06FF]', '_', clean_name)
        if not clean_name.endswith(".pdf"):
            clean_name += ".pdf"
        return clean_name

    def create_task_workspace(self, task_id: Optional[str] = None) -> Tuple[str, Path]:
        """Creates an isolated directory for a specific conversion task."""
        task_uuid = task_id or str(uuid.uuid4())
        task_dir = (self.base_dir / task_uuid).resolve()

        # Security check: Ensure task_dir is strictly within base_dir
        if not str(task_dir).startswith(str(self.base_dir)):
            raise ValueError("Potential path traversal attempt detected.")

        task_dir.mkdir(parents=True, exist_ok=True)
        return task_uuid, task_dir

    def get_task_workspace(self, task_id: str) -> Path:
        """Resolves task workspace path with safety check."""
        task_dir = (self.base_dir / task_id).resolve()
        if not str(task_dir).startswith(str(self.base_dir)):
            raise ValueError("Invalid task directory.")
        return task_dir

    def save_file(self, task_id: str, filename: str, data: bytes) -> str:
        """Saves file into the task's isolated folder."""
        task_dir = self.get_task_workspace(task_id)
        safe_name = self.sanitize_filename(filename)
        target_path = task_dir / safe_name
        with open(target_path, "wb") as f:
            f.write(data)
        return str(target_path)

    def cleanup_task(self, task_id: str) -> None:
        """Immediately removes task temporary directory and all its files."""
        try:
            task_dir = self.get_task_workspace(task_id)
            if task_dir.exists() and task_dir.is_dir():
                shutil.rmtree(task_dir, ignore_errors=True)
                logger.info("Cleaned up temporary workspace for task %s", task_id)
        except Exception as e:
            logger.error("Error cleaning up task workspace %s: %s", task_id, e)

    def purge_expired(self, max_age_hours: Optional[int] = None) -> int:
        """Deletes all task folders older than the configured TTL (e.g. 24 hours).

        Returns:
            Number of purged directories.
        """
        ttl_seconds = (max_age_hours or settings.TEMP_FILE_TTL_HOURS) * 3600
        now = time.time()
        purged_count = 0

        if not self.base_dir.exists():
            return 0

        for item in self.base_dir.iterdir():
            if item.is_dir():
                try:
                    dir_age = now - item.stat().st_mtime
                    if dir_age > ttl_seconds:
                        shutil.rmtree(item, ignore_errors=True)
                        purged_count += 1
                        logger.info("Purged expired directory: %s (Age: %.1f hrs)", item.name, dir_age / 3600)
                except Exception as e:
                    logger.error("Failed to inspect/purge item %s: %s", item, e)

        return purged_count


storage = LocalStorageManager()
