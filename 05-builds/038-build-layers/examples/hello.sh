#!/bin/sh
echo "curl is $(curl --version | head -1 | cut -d" " -f1-2)"
