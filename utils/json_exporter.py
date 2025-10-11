"""
JSON export utilities for serializing Pydantic models.
Handles datetime serialization and pretty formatting.
"""

import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel

from utils.logger import setup_logger

logger = setup_logger(__name__)


class JSONExporter:
    """Exports Pydantic models to JSON files."""
    
    @staticmethod
    def export(
        data: BaseModel,
        output_path: Path,
        indent: int = 2
    ) -> None:
        """
        Export Pydantic model to JSON file.
        
        Args:
            data: Pydantic model instance
            output_path: Destination file path
            indent: JSON indentation level
        
        Raises:
            IOError: If file write fails
        """
        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize to JSON with proper datetime handling
            json_data = data.model_dump_json(indent=indent, exclude_none=False)
            
            # Write to file
            output_path.write_text(json_data, encoding="utf-8")
            
            logger.info(f"✓ Exported data to {output_path}")
        
        except Exception as e:
            logger.error(f"Failed to export JSON to {output_path}: {str(e)}")
            raise IOError(f"JSON export failed: {str(e)}") from e
    
    @staticmethod
    def export_dict(
        data: dict[str, Any],
        output_path: Path,
        indent: int = 2
    ) -> None:
        """
        Export dictionary to JSON file.
        
        Args:
            data: Dictionary to export
            output_path: Destination file path
            indent: JSON indentation level
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, default=str)
            
            logger.info(f"✓ Exported data to {output_path}")
        
        except Exception as e:
            logger.error(f"Failed to export JSON to {output_path}: {str(e)}")
            raise IOError(f"JSON export failed: {str(e)}") from e


if __name__ == "__main__":
    # Example usage
    from data.github_models import PullRequest, PRState
    from datetime import datetime
    
    pr = PullRequest(
        number=1,
        title="Test PR",
        state=PRState.OPEN,
        author="testuser",
        created_at=datetime.utcnow(),
        url="https://github.com/test/repo/pull/1"
    )
    
    exporter = JSONExporter()
    exporter.export(pr, Path("./test_output.json"))
    
    print("✓ Export test complete")