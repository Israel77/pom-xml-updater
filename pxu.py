#!/usr/bin/env python3
import os
from typing import List
from enum import Enum, auto
import re
import argparse
from dataclasses import dataclass

import xml.etree.ElementTree as ET


class UpdateType(Enum):
    PATCH = auto()
    MINOR = auto()
    MAJOR = auto()


@dataclass
class UpdateInfo:
    path_to_project: str
    update_type: UpdateType
    keep_suffix: bool
    verbose: bool


def main():
    update_info = parse_arguments()

    update(update_info)


def parse_arguments() -> UpdateInfo:
    parser = argparse.ArgumentParser(
        prog="Pom xml Updater",
        description="Atualiza a versão do arquivo pom.xml",
    )
    parser.add_argument("path_to_project",
        metavar="Project path",
        help="Caminho até o projeto Java",
        nargs="?",
        default=os.getcwd())

    update = parser.add_mutually_exclusive_group()
    update.add_argument(
        "--patch",
        "-p",
        help="Indica atualização do tipo patch, de acordo com o versionamento semântico",
        action="store_const",
        const=UpdateType.PATCH,
        dest="update_type",
    )
    update.add_argument(
        "--minor",
        "-m",
        help="Indica atualização do tipo minor, de acordo com o versionamento semântico",
        action="store_const",
        const=UpdateType.MINOR,
        dest="update_type",
    )
    update.add_argument(
        "--major",
        "-M",
        help="Indica atualização do tipo major, de acordo com o versionamento semântico",
        action="store_const",
        const=UpdateType.MAJOR,
        dest="update_type",
    )

    parser.add_argument(
        "--close-version",
        "-c",
        help="Fecha a versão para release (remove o sufixo)",
        action="store_false",
        dest="keep_suffix"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="verbose"
    )

    args = parser.parse_args()

    return UpdateInfo(args.path_to_project, args.update_type, args.keep_suffix, args.verbose)


def update(update_info: UpdateInfo):
    xmlNamespace =  "http://maven.apache.org/POM/4.0.0"
    ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
    file_tree = ET.parse(f"{update_info.path_to_project}/pom.xml")
    root = file_tree.getroot()

    # Encontra a versão do pom
    versionString = ""
    if (xmlVersion := root.find(f"{{{xmlNamespace}}}version")) is not None:
        versionString = xmlVersion.text
    else:
        raise ValueError("Não foi possível ler a versão do POM")

    # region Parsing da versão
    version = {"major": None, "minor": None, "patch": None, "suffix": None}

    # Versionamento com número único
    if match := re.match(r"([0-9]+)\.([0-9]+)\.([0-9]+)(-.+)?$", versionString):
        version["major"] = int(match.group(1))
        version["minor"] = int(match.group(2))
        version["patch"] = int(match.group(3))

    else:
        raise NotImplementedError(f"Padrão de string não suportado: {versionString}")

    if matchSuffix := re.search(r"(-.+)$", versionString):
        version["suffix"] = matchSuffix.group(1)

    # endregion

    newVersion = {
        "major": version["major"],
        "minor": version["minor"],
        "patch": version["patch"],
        "suffix": version["suffix"],
    }

    if update_info.update_type == UpdateType.MAJOR:
        newVersion["major"] += 1
        newVersion["minor"] = 0
        newVersion["patch"] = 0

    elif update_info.update_type == UpdateType.MINOR:
        newVersion["minor"] += 1
        newVersion["patch"] = 0

    elif update_info.update_type == UpdateType.PATCH:
        newVersion["patch"] += 1

    if not update_info.keep_suffix:
        newVersion["suffix"] = None

    newVersionString = f'{newVersion["major"]}.{newVersion["minor"]}.{newVersion["patch"]}{newVersion["suffix"] or ""}'

    xmlVersion.text = newVersionString

    file_tree.write(f"{update_info.path_to_project}/pom.xml")

    if update_info.verbose:
        print(f"[{update_info.path_to_project}]\npom.xml atualizado com sucesso: {versionString} -> {newVersionString}")


if __name__ == "__main__":
    # Chama a função principal
    main()
