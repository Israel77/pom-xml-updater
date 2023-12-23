#!/usr/bin/env python3
import os
from typing import List
from enum import Enum

import xml.etree.ElementTree as ET

UpdateType = Enum("UpdateType", ["PATCH", "MINOR", "MAJOR"])



def main(*args: List[str]):
    update("pom.xml", UpdateType.PATCH)


def update(path_to_project: str, update_type: UpdateType, pomVersion="4.0.0"):
    mavenUrlTemplate = f"{{http://maven.apache.org/POM/{pomVersion}}}"
    file_tree = ET.parse(path_to_project)
    root = file_tree.getroot()

    # Encontra a versão do pom
    versionString = ""
    if root.find(f"{mavenUrlTemplate}version") == None:
        raise ValueError("Não foi possível ler a versão do POM")
    else:
        versionString = root.find(f"{mavenUrlTemplate}version").text
    
    version = {
        "major": None,
        "minor": None,
        "patch": None,
        "suffix": None
    }


if __name__ == "__main__":
    main()
