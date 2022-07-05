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

import importlib_metadata

metadata = importlib_metadata.metadata("Celeratas")


__title__ = metadata["name"]
__summary__ = metadata["summary"]
__url__ = metadata["home-page"]
__version__ = metadata["version"]
__author__ = metadata["author"]
__email__ = metadata["author-email"]
__license__ = metadata["license"]
