# Cloud Backup Sync - Backup Orchestrator
"""
Backup Orchestrator - Manages backup operations
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Load environment configuration from .env file
def _load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()

class BackupOrchestrator:
    """Orchestrates backup operations across cloud providers"""

    def __init__(self, config_path='config/settings.yaml'):
        self.config = self._load_config(config_path)
        self.backup_manifest = []

    def _load_config(self, path):
        """Load configuration file"""
        import yaml
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {}

    def scan_files(self, project_path):
        """Scan project directory for files to backup"""
        files_to_backup = []
        include_patterns = self.config.get('backup', {}).get('include', ['**/*'])
        exclude_patterns = self.config.get('backup', {}).get('exclude', [])

        for pattern in include_patterns:
            for file_path in Path(project_path).glob(pattern):
                if file_path.is_file():
                    # Skip excluded patterns
                    skip = False
                    for exclude in exclude_patterns:
                        if exclude in str(file_path):
                            skip = True
                            break
                    if not skip:
                        files_to_backup.append(str(file_path))

        return files_to_backup

    def create_backup(self, project_path, provider='aws'):
        """Create backup of project to cloud provider"""
        from scripts.uploader import CloudUploader
        from scripts.scanner import FileScanner

        # Scan for files
        files = self.scan_files(project_path)

        # Create manifest
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'files': files,
            'provider': provider
        }

        # Initialize uploader
        uploader = CloudUploader(provider)

        # Scan for backup files
        scanner = FileScanner()
        backup_files = scanner.scan_for_backup(project_path)

        # Upload files
        for file_path in files:
            uploader.upload_file(file_path)

        uploader.sync_backup_files(backup_files)

        return manifest

    def restore_backup(self, backup_id, destination):
        """Restore files from backup"""
        # Restore logic
        pass

    def list_backups(self):
        """List available backups"""
        return self.backup_manifest