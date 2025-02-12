#!/usr/bin/env python3
import logging
import os
import re
import subprocess
import sys


def check_print_statements():
    print_found = False
    diff_cmd = ["git", "diff", "--name-only", "HEAD"]
    modified_files = subprocess.check_output(diff_cmd).decode("utf-8").splitlines()
    logging.basicConfig(level=logging.INFO)
    for file in modified_files:
        if file.endswith(".py"):
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    for line_number, line in enumerate(f, start=1):
                        absolute_file_path = os.path.abspath(file)
                        if re.search(r"\bprint\s*\(", line):
                            logging.info(
                                f"Error: Declaracion de print en {absolute_file_path}:{line_number}"
                            )
                            logging.info(f"  {line.strip()}")
                            print_found = True
    return print_found


if __name__ == "__main__":
    if check_print_statements():
        sys.exit(1)
