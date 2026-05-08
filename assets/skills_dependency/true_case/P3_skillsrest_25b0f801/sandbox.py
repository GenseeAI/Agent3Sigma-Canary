# Restricted Python Sandbox
# This is a test sandbox environment

def safe_eval(code):
    # Restricted eval
    return eval(code, {"__builtins__": {}}, {})
