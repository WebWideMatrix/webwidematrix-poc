#!/usr/bin/env python

import sys, os
import pytest

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    args = []
    args.extend(sys.argv[1:])
    if not args:
        print "Tip: to run only unit-tests, add option: tests/unit"
        args.append("tests")
    pytest.main(args)
