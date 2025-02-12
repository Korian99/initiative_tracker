#!/usr/bin/env python
import subprocess
import sys

# Obtener archivos modificados relacionados con el commit actual
changed_files = (
    subprocess.check_output(["git", "diff", "--name-only", "HEAD"])
    .decode()
    .splitlines()
)

# Ejecutar pre-commit solo en los archivos modificados
pre_commit_command = ["pre-commit", "run", "--files"] + changed_files
try:
    subprocess.run(pre_commit_command, check=True)
except subprocess.CalledProcessError as e:
    sys.exit(e.returncode)
