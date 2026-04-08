from sys import exit as sys_exit
from sys import version_info

python_version = tuple(version_info)[:2]
python_version_verbose = str(python_version[0]) + "." + str(python_version[1])

supported_dependencies = {
    (3, 8): ["django4.2.txt", "latest.txt"],
    (3, 9): ["django4.2.txt", "latest.txt"],
    (3, 10): [
        "django4.2.txt",
        "django5.0.txt",
        "django5.1.txt",
        "django5.2.txt",
        "latest.txt",
    ],
    (3, 10): [
        "django4.2.txt",
        "django5.0.txt",
        "django5.1.txt",
        "django5.2.txt",
        "latest.txt",
    ],
    (3, 11): [
        "django4.2.txt",
        "django5.0.txt",
        "django5.1.txt",
        "django5.2.txt",
        "latest.txt",
    ],
    (3, 12): [
        "django4.2.txt",
        "django5.0.txt",
        "django5.1.txt",
        "django5.2.txt",
        "latest.txt",
    ],
    (3, 13): [
        "django5.1.txt",
        "django5.2.txt",
        "latest.txt",
    ],
}

try:
    from django import VERSION

    django_version = f"django{VERSION[0]}.{VERSION[1]}.txt"
except (ImportError, ModuleNotFoundError):
    django_version = "latest.txt"

if python_version not in supported_dependencies:
    print(f"Python {python_version_verbose} not supported")
    sys_exit()

if django_version not in supported_dependencies[python_version]:
    print(f"Django {VERSION[:2]} not supported")
    sys_exit()

print("requirements/python" + python_version_verbose + "/" + django_version)
