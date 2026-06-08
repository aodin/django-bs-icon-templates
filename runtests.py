#! /usr/bin/env python3
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    django.setup()
    runner = get_runner(settings)(verbosity=2)
    failures = runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
