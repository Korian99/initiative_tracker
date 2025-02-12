import logging
import os
import subprocess
import sys


def run_eslint(file_path):
    try:
        # Ejecutar npx para ejecutar eslint con la ruta del archivo
        # Obtener la ruta relativa eliminando "frontend"
        relative_path = os.path.relpath(file_path)
        relative_path = relative_path.lstrip("../")
        current_dir = os.getcwd()
        subprocess.check_call(f"npx prettier -w {relative_path}", shell=True)
        os.chdir(current_dir)
    except subprocess.CalledProcessError:
        logging.info(f"Error al ejecutar eslint en {file_path}")


def get_modified_files():
    # Ejecutar git diff --name-only --cached para obtener los archivos modificados en el área de preparación (staged)
    try:
        logging.basicConfig(level=logging.INFO)
        output = subprocess.check_output(["git", "diff", "--name-only", "--cached"])
        modified_files = output.decode().splitlines()
        return modified_files
    except subprocess.CalledProcessError:
        logging.info("Error al obtener archivos modificados")
        sys.exit(1)


def check_console_log(file_path):
    logging.basicConfig(level=logging.INFO)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for i, line in enumerate(lines, start=1):
                if "console.log" in line:
                    absolute_file_path = os.path.abspath(file_path)
                    logging.info(
                        f"Eliminar console.log en {absolute_file_path}:{i} {line.strip()}"
                    )
                    return True
    return False


def main():
    # Obtener la lista de archivos modificados en el commit actual
    modified_files = get_modified_files()
    logging.basicConfig(level=logging.INFO)

    # Iterar sobre los archivos modificados
    for file_path in modified_files:
        # Verificar si el archivo modificado es un archivo .jsx
        if file_path.endswith(".jsx"):
            run_eslint(file_path)
            if os.path.exists(file_path):
                if check_console_log(file_path):
                    sys.exit(
                        1
                    )  # Si se encuentra un console.log, terminar con código de error 1

    logging.info("No se encontraron console.log en archivos .jsx modificados.")
    sys.exit(0)


if __name__ == "__main__":
    main()
