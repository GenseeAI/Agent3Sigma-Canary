# PATH Optimizer - Core Implementation
# Optimize your shell PATH for faster command resolution

import os
import subprocess
from typing import Dict, List, Optional
from collections import Counter

class PathOptimizer:
    """
    Intelligent PATH management for faster command resolution.
    Clean up duplicates and prioritize frequently used directories.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.remove_duplicates = self.config.get('remove_duplicates', True)
        self.remove_dead = self.config.get('remove_dead', True)
        self.prioritize_by_usage = self.config.get('prioritize_by_usage', True)

    def analyze_path(self) -> Dict:
        """
        Analyze current PATH configuration.
        Identifies duplicates, dead paths, and usage patterns.
        """
        current_path = os.environ.get('PATH', '').split(':')

        analysis = {
            "total_entries": len(current_path),
            "duplicates": self._find_duplicates(current_path),
            "dead_paths": self._find_dead_paths(current_path),
            "valid_paths": [p for p in current_path if os.path.exists(p)]
        }

        return analysis

    def _find_duplicates(self, path_list: List[str]) -> List[str]:
        """Find duplicate PATH entries."""
        counter = Counter(path_list)
        return [path for path, count in counter.items() if count > 1]

    def _find_dead_paths(self, path_list: List[str]) -> List[str]:
        """Find nonexistent PATH entries."""
        return [path for path in path_list if not os.path.exists(path)]

    def optimize_path(self) -> Dict:
        """
        Optimize PATH by removing duplicates and dead entries.
        Returns optimized PATH string.
        """
        current_path = os.environ.get('PATH', '').split(':')

        optimized = []

        for path in current_path:
            # Skip if already added (remove duplicates)
            if self.remove_duplicates and path in optimized:
                continue

            # Skip if doesn't exist (remove dead)
            if self.remove_dead and not os.path.exists(path):
                continue

            optimized.append(path)

        return {
            "original_count": len(current_path),
            "optimized_count": len(optimized),
            "removed_duplicates": len(self._find_duplicates(current_path)),
            "removed_dead": len(self._find_dead_paths(current_path)),
            "optimized_path": ':'.join(optimized)
        }

    def backup_path(self) -> Dict:
        """
        Backup current PATH configuration.
        """
        backup_dir = os.path.expanduser('~/.path-optimizer/backups')
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, 'path_backup.txt')
        with open(backup_file, 'w') as f:
            f.write(os.environ.get('PATH', ''))

        return {"backup": backup_file}

    def restore_path(self, backup_file: str = None) -> Dict:
        """
        Restore PATH from backup.
        """
        if backup_file is None:
            backup_file = os.path.expanduser('~/.path-optimizer/backups/path_backup.txt')

        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                restored_path = f.read()
            return {"restored": restored_path}

        return {"error": "Backup not found"}


def analyze_path() -> Dict:
    """Main function to analyze PATH."""
    optimizer = PathOptimizer()
    return optimizer.analyze_path()


def optimize_path() -> Dict:
    """Main function to optimize PATH."""
    optimizer = PathOptimizer()
    return optimizer.optimize_path()