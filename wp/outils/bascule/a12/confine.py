#!/usr/bin/env python3
"""Mandatory A12 launcher: Linux Landlock + disconnected container, no downloads."""
import ctypes
import os
import pathlib
import sys


def disjoint_output(parent, site, repository):
    return str(parent) != '/' and not any(parent == root or root in parent.parents or parent in root.parents
                                         for root in (site, repository))


def confine(write_root):
    if sys.platform != 'linux' or {p.name for p in pathlib.Path('/sys/class/net').iterdir()} != {'lo'}:
        raise RuntimeError('A12_DISCONNECTED_LINUX_REQUIRED')
    libc = ctypes.CDLL(None, use_errno=True)
    # Linux x86_64/aarch64/riscv use the generic Landlock syscall numbers.
    if os.uname().machine not in {'x86_64', 'aarch64', 'riscv64'}:
        raise RuntimeError('A12_LANDLOCK_ARCH_UNSUPPORTED')
    abi = libc.syscall(444, 0, 0, 1)
    if abi < 3:
        raise RuntimeError('A12_LANDLOCK_ABI_REQUIRED')
    # Handle every mutation right through ABI 3 (including truncate and refer).
    rights = ((1 << 15) - 1) & ~(1 | 4 | 8)

    class Ruleset(ctypes.Structure):
        _fields_ = [('handled_access_fs', ctypes.c_uint64)]

    class PathRule(ctypes.Structure):
        _pack_ = 1
        _fields_ = [('allowed_access', ctypes.c_uint64), ('parent_fd', ctypes.c_int)]

    attr = Ruleset(rights)
    ruleset = libc.syscall(444, ctypes.byref(attr), ctypes.sizeof(attr), 0)
    if ruleset < 0:
        raise RuntimeError('A12_LANDLOCK_CREATE_FAILED')
    parent = os.open(write_root, os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        rule = PathRule(rights, parent)
        if libc.syscall(445, ruleset, 1, ctypes.byref(rule), 0) != 0:
            raise RuntimeError('A12_LANDLOCK_RULE_FAILED')
        if libc.prctl(38, 1, 0, 0, 0) != 0 or libc.syscall(446, ruleset, 0) != 0:
            raise RuntimeError('A12_LANDLOCK_RESTRICT_FAILED')
    finally:
        os.close(parent)
        os.close(ruleset)
    return abi


def main():
    options = {}
    for arg in sys.argv[1:]:
        key, sep, value = arg.partition('=')
        if not sep or key not in {'--wp-path', '--output', '--audit'} or key in options:
            raise RuntimeError('A12_USAGE')
        options[key] = value
    if len(options) != 3:
        raise RuntimeError('A12_USAGE')
    site = pathlib.Path(options['--wp-path']).resolve(strict=True)
    parent = pathlib.Path(options['--output']).parent.resolve(strict=True)
    source = pathlib.Path(__file__).resolve().parent
    # Early checks before granting any output write rights. PHP repeats complete guards.
    candidate = source.parents[3] if len(source.parents) > 3 else source.parent
    repository = candidate if (candidate/'wp/outils/bascule/audit').is_file() else source.parent
    if not disjoint_output(parent, site, repository):
        raise RuntimeError('A12_OUTPUT_UNSAFE')
    import importlib.util
    spec = importlib.util.spec_from_file_location('stream_guard', source.parent/'stream_guard.py')
    guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
    guard.inventory('A12', source/'inventorier-contenus', options, fence=sys.modules[__name__])


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        import importlib.util
        spec=importlib.util.spec_from_file_location('stream_guard',pathlib.Path(__file__).resolve().parent.parent/'stream_guard.py')
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
        code=guard.public_error(error,'A12')
        print(code, file=sys.stderr)
        sys.exit(1)
