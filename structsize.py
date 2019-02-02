#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import contextlib
import os
import re
import subprocess
import sys
import tempfile


TEMPLATE = """
%s

int main()
{
    switch (1)
    {
        case sizeof(%s): break;
        case sizeof(%s): break;
    }
}
"""

INCLUDE_TEMPLATE = "#include <%s>"

UNDECLARED_ID_REGEX = r"error C2065: '.+': undeclared identifier"

CASE_REGEX = r"error C2196: case value '(\d+)' already used"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("structure")
    parser.add_argument("--header")
    args = parser.parse_args()

    output = run_cl(args.structure, args.header)
    struct_size = parse_cl_output(output)

    print(struct_size)


def run_cl(structure, header=""):
    if header:
        include = INCLUDE_TEMPLATE % (header,)
    else:
        include = ""

    with named_temp_file(suffix=".cpp") as filename:
        with open(filename, mode="w") as f:
            f.write(TEMPLATE % (include, structure, structure))

        result = subprocess.run(("cl.exe", filename), capture_output=True)
        return result.stdout.decode("UTF-8")


def parse_cl_output(output):
    if re.search(UNDECLARED_ID_REGEX, output):
        print(output, file=sys.stderr)
        raise ValueError()

    match = re.search(CASE_REGEX, output)
    if match:
        return int(match.group(1))
    else:
        print(output, file=sys.stderr)
        raise RuntimeError()


@contextlib.contextmanager
def named_temp_file(suffix=None, prefix=None, delete=True):
    handle, filename = tempfile.mkstemp(suffix, prefix)
    os.close(handle)

    try:
        yield filename
    finally:
        if delete:
            os.remove(filename)


if __name__ == "__main__":
    main()
