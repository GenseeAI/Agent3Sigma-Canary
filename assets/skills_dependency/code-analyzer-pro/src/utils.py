# Utility functions
"""Utility module for data processing."""

import json
import logging
from typing import Any, Dict, List


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_data(input_file: str) -> Dict[str, Any]:
    """Process data from input file."""
    try:
        with open(input_file, "r") as f:
            data = json.load(f)

        result = {
            "processed": True,
            "count": len(data) if isinstance(data, list) else 1,
            "data": data
        }

        logger.info(f"Processed {result['count']} items")
        return result

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        return {"processed": False, "error": "file_not_found"}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in input file: {input_file}")
        return {"processed": False, "error": "invalid_json"}


def validate_input(config: Dict[str, Any]) -> bool:
    """Validate input configuration."""
    required_keys = ["input_file", "output_file"]

    for key in required_keys:
        if key not in config:
            logger.error(f"Missing required config key: {key}")
            return False

    return True


def transform_data(data: List[Any], operation: str) -> List[Any]:
    """Transform data based on operation type."""
    if operation == "uppercase":
        return [str(item).upper() for item in data]
    elif operation == "lowercase":
        return [str(item).lower() for item in data]
    else:
        return data