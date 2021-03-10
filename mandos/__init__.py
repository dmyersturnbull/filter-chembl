"""
Metadata for this project.
"""

import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import metadata as __load
from pathlib import Path

pkg = Path(__file__).absolute().parent.name
logger = logging.getLogger(pkg)
_metadata = None
try:
    _metadata = __load(Path(__file__).absolute().parent.name)
    __status__ = "Development"
    __copyright__ = "Copyright 2020–2021"
    __date__ = "2020-08-14"
    __uri__ = _metadata["home-page"]
    __title__ = _metadata["name"]
    __summary__ = _metadata["summary"]
    __license__ = _metadata["license"]
    __version__ = _metadata["version"]
    __author__ = _metadata["author"]
    __maintainer__ = _metadata["maintainer"]
    __contact__ = _metadata["maintainer"]
except PackageNotFoundError:  # pragma: no cover
    logger.error(f"Could not load package metadata for {pkg}. Is it installed?")


class MandosMetadata:
    version = __version__


if __name__ == "__main__":  # pragma: no cover
    if _metadata is not None:
        print(f"{pkg} (v{_metadata['version']})")
    else:
        print("Unknown project info")


__all__ = ["MandosMetadata"]
