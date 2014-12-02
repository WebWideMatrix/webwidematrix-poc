#!/usr/bin/env python

import sys, os
import pytest

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    args = ["tests"]
    args.extend(sys.argv)
    pytest.main(args)
