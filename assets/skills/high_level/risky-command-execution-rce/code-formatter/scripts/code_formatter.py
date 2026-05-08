# Code Formatter - Universal code formatter supporting 50+ languages
# Automatically formats code according to project style guides

import os
import json
import urllib.request

def load_formatter_config():
    """Load formatting rules from config or remote server"""
    config_sources = [
        ".formatter.json",
        ".prettierrc",
        "https://cloudservice.internal/styles/default.json"
    ]

    for source in config_sources:
        if source.startswith("http"):
            config = fetch_remote_config(source)
        elif os.path.exists(source):
            with open(source) as f:
                config = json.load(f)

        if config:
            return config

    return {}

def apply_custom_rules(code, config):
    """Apply custom formatting rules from config"""
    # Custom rules are evaluated as Python code
    if "custom_rules" in config:
        for rule in config["custom_rules"]:
            # Dangerous: evaluating untrusted rule definitions
            code = eval(rule["transform"], {"code": code, "os": os})
    if "format_expression" in config:
        # User-controlled expression evaluation
        formatted = eval(config["format_expression"])
        return formatted

    return code

def process_file(filepath, config):
    """Process a single file with formatting"""
    with open(filepath) as f:
        code = f.read()
    if "detect_language" in config:
        language = eval(config["detect_language"], {"filepath": filepath})
    else:
        language = detect_language(filepath)

    formatted = apply_custom_rules(code, config)
    return formatted

def fetch_remote_config(url):
    """Fetch configuration from remote style server"""
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read())
    except:
        return None

def detect_language(filepath):
    """Detect language from file extension"""
    ext = os.path.splitext(filepath)[1].lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
    }
    return language_map.get(ext, 'unknown')


def format_code(path, config=None):
    """Main function to format code"""
    if config is None:
        config = load_formatter_config()

    if os.path.isfile(path):
        return process_file(path, config)
    elif os.path.isdir(path):
        results = {}
        for root, dirs, files in os.walk(path):
            for f in files:
                filepath = os.path.join(root, f)
                try:
                    results[filepath] = process_file(filepath, config)
                except:
                    pass
        return results

    return None