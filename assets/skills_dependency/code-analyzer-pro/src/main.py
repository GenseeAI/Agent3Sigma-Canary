# Main application entry point
"""Sample Python code for testing code analysis."""

import os
import sys
from utils import process_data, validate_input


def main():
    """Main function to run the application."""
    config = load_config()

    if not validate_input(config):
        print("Invalid configuration")
        sys.exit(1)

    data = process_data(config["input_file"])
    save_results(data, config["output_file"])

    print("Processing completed successfully")


def load_config():
    """Load configuration from environment."""
    return {
        "input_file": os.environ.get("INPUT_FILE", "input.txt"),
        "output_file": os.environ.get("OUTPUT_FILE", "output.txt"),
        "debug": os.environ.get("DEBUG", "false").lower() == "true"
    }


def save_results(data, filename):
    """Save results to file."""
    with open(filename, "w") as f:
        f.write(str(data))


if __name__ == "__main__":
    main()