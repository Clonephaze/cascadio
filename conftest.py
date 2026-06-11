"""
conftest.py - pytest configuration for local development on Windows.

On Windows, Python 3.8+ no longer searches PATH for DLL dependencies of
extension modules.  In a released wheel, delvewheel places the OCCT DLLs next
to _core.pyd so they are found automatically.  During local development the
DLLs live in occt_cache/win64/vc14/bin, pointed to by CASCADIO_OCCT_LIB
(which is the *lib* dir; we derive *bin* from it).

This file is not shipped in the wheel and has no effect in CI or on other
platforms.
"""

import os
import sys


def pytest_configure(config):
    if sys.platform != "win32":
        return
    occt_lib = os.environ.get("CASCADIO_OCCT_LIB", "")
    if not occt_lib:
        return
    occt_bin = os.path.join(os.path.dirname(occt_lib), "bin")
    if os.path.isdir(occt_bin):
        os.add_dll_directory(occt_bin)
