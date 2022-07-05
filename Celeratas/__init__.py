import importlib_metadata

from . import _version

__all__ = (
    "__title__",
    "__summary__",
    "__url__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
)

__copyright__ = "Copyright 2022 Finn Mattis"

metadata = importlib_metadata.metadata("Celeratas")

__title__ = metadata["name"]
__summary__ = metadata["summary"]
__url__ = metadata["home-page"]
__author__ = metadata["author"]
__email__ = metadata["author-email"]
__license__ = metadata["license"]

__version__ = _version.get_versions()['version']
