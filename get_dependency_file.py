from sys import exit as sys_exit
from sys import version_info
from os import listdir
from pathlib import Path


def get_python_version():
    return tuple(version_info)[:2]


def get_django_version():
    try:
        from django import VERSION

        return VERSION[:2]

    except (ImportError, ModuleNotFoundError):
        return max(get_django_versions(get_python_version()))


def get_python_versions():
    PYTHON = 6
    contents = listdir("requirements")
    without_prefix = map(lambda x: x[PYTHON:], contents)
    return tuple(sorted(map(to_version_tuple, without_prefix)))


def get_django_versions(python_version):
    DJANGO = 6
    TXT = -4

    s = "python" + ".".join(map(str, python_version))
    contents = listdir(str(Path("requirements") / s))
    breakpoint()
    without_prefix_suffix = map(lambda x: x[DJANGO:TXT], contents)
    return tuple(sorted(map(to_version_tuple, without_prefix_suffix)))


def to_version_tuple(version):
    return tuple(map(int, version.split(".")))


def to_version_string(version):
    return ".".join(map(str, version))


python_version = get_python_version()
python_version_verbose = to_version_string(python_version)
python_versions = get_python_versions()


if python_version not in python_versions:
    print(f"Python {python_version_verbose} not supported")
    sys_exit(1)

django_version = get_django_version()
django_version_verbose = to_version_string(django_version)
django_versions = get_django_versions(python_version)


if django_version not in django_versions:
    print(f"Django {django_version_verbose} not supported")
    sys_exit(1)

print(
    "requirements/python"
    + python_version_verbose
    + "/django"
    + django_version_verbose
    + ".txt"
)
