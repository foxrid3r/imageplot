"""Read coordinate-system metadata embedded by the PNG coordinate editor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

METADATA_KEY = "coordinate_systems_json"
SUPPORTED_SCHEMA = "png-coordinate-systems"


class MetadataError(ValueError):
    """Raised when PNG coordinate metadata is missing or invalid."""


def load_png_metadata(path: str | Path) -> tuple[Image.Image, dict[str, Any]]:
    """Load a PNG and parse its embedded coordinate-system JSON metadata."""
    image_path = Path(path)
    with Image.open(image_path) as opened:
        image = opened.convert("RGBA")
        raw = opened.info.get(METADATA_KEY)

    if raw is None:
        raise MetadataError(
            f"{image_path.name!r} does not contain the {METADATA_KEY!r} PNG metadata chunk."
        )

    try:
        payload = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError as exc:
        raise MetadataError(f"Invalid coordinate-system JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise MetadataError("Coordinate-system metadata must be a JSON object.")
    if payload.get("schema") != SUPPORTED_SCHEMA:
        raise MetadataError(
            f"Unsupported metadata schema {payload.get('schema')!r}; "
            f"expected {SUPPORTED_SCHEMA!r}."
        )
    systems = payload.get("coordinate_systems")
    if not isinstance(systems, list) or not systems:
        raise MetadataError("The PNG contains no coordinate systems.")

    return image, payload
