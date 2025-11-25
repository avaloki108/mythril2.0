"""This module contains various utility functions regarding unit conversion and
solc integration."""

import binascii
import json
import logging
import os
import platform
import re
import typing
from json.decoder import JSONDecodeError
from subprocess import PIPE, Popen
from typing import Tuple

import semantic_version as semver
import solcx
from pyparsing import Combine, Optional, Regex, Word
from requests.exceptions import ConnectionError

from mythril2.exceptions import CompilerError
from mythril2.support.support_args import args

log = logging.getLogger(__name__)


def safe_decode(hex_encoded_string):
    """

    :param hex_encoded_string:
    :return:
    """
    if hex_encoded_string.startswith("0x"):
        return bytes.fromhex(hex_encoded_string[2:])
    else:
        return bytes.fromhex(hex_encoded_string)


def get_solc_json(file, solc_binary="solc", solc_settings_json=None):
    """

    :param file:
    :param solc_binary:
    :param solc_settings_json:
    :return:
    """
    if args.solc_args is None:
        cmd = [solc_binary, "--standard-json", "--allow-paths", ".,/"]
    else:
        cmd = [solc_binary, "--standard-json"] + args.solc_args.split()

    settings = {}
    if solc_settings_json:
        with open(solc_settings_json) as f:
            settings = json.load(f)
    if "optimizer" not in settings:
        settings.update({"optimizer": {"enabled": False}})

    settings.update(
        {
            "outputSelection": {
                "*": {
                    "": ["ast"],
                    "*": [
                        "metadata",
                        "evm.bytecode",
                        "evm.deployedBytecode",
                        "evm.methodIdentifiers",
                    ],
                }
            },
        }
    )

    input_json = json.dumps(
        {
            "language": "Solidity",
            "sources": {file: {"urls": [file]}},
            "settings": settings,
        }
    )

    try:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(bytes(input_json, "utf8"))

    except FileNotFoundError:
        raise CompilerError(
            "Compiler not found. Make sure that solc is installed and in PATH, or set the SOLC environment variable."
        )

    out = stdout.decode("UTF-8")

    try:
        result = json.loads(out)
    except JSONDecodeError as e:
        log.error(f"Encountered a decode error.\n stdout:{out}\n stderr: {stderr}")
        raise e

    for error in result.get("errors", []):
        if error["severity"] == "error":
            raise CompilerError(
                "Solc experienced a fatal error.\n\n%s" % error["formattedMessage"]
            )

    return result


def get_random_address():
    """

    :return:
    """
    return binascii.b2a_hex(os.urandom(20)).decode("UTF-8")


def get_indexed_address(index):
    """

    :param index:
    :return:
    """
    return "0x" + (hex(index)[2:] * 40)


def solc_exists(version):
    """

    :param version:
    :return:
    """

    if platform.system() == "Darwin":
        solcx.import_installed_solc()
    solcx.install_solc("v" + version)
    solcx.set_solc_version("v" + version)
    solc_binary = solcx.install.get_executable()
    return solc_binary


def parse_pragma(solidity_code):
    lt = Word("<")
    gtr = Word(">")
    eq = Word("=")
    carrot = Word("^")
    version = Regex(r"\s*[0-9]+\s*\.\s*[0-9]+\s*(\.\s*[0-9]+)?")
    inequality = Optional(
        eq | (Combine(gtr + Optional(eq)) | Combine(lt + Optional(eq)))
    )
    min_version = Optional(carrot | inequality) + version
    max_version = Optional(inequality + version)
    pragma = Word("pragma") + Word("solidity") + min_version + Optional(max_version)
    result = pragma.parseString(solidity_code)
    min_inequality = result[2] if result[2] in [">", "<", ">=", "<=", "="] else ""
    min_carrot = result[2] if result[2] == "^" else ""
    min_version = result[3] if min_carrot != "" or min_inequality != "" else result[2]
    return {
        "min_carrot": min_carrot,
        "min_inequality": min_inequality,
        "min_version": min_version,
        "max_inequality": result[4] if len(result) > 4 else None,
        "max_version": result[5] if len(result) > 5 else None,
    }


try:
    all_versions = solcx.get_installable_solc_versions()
except ConnectionError:
    # No internet, trying to proceed with installed compilers
    all_versions = solcx.get_installed_solc_versions()


VOID_START = re.compile("//|/\\*|\"|'")
QUOTE_END = re.compile("(?<!\\\\)'")
DQUOTE_END = re.compile('(?<!\\\\)"')


def remove_comments_strings(program: str) -> str:
    """Return program without Solidity comments and strings

    :param str program: Solidity program with lines separated by \\n
    :return: program with strings emptied and comments removed
    :rtype: str
    """
    result = ""
    while True:
        match_start_of_void = VOID_START.search(program)
        if not match_start_of_void:
            result += program
            break
        else:
            result += program[: match_start_of_void.start()]
            if match_start_of_void[0] == "//":
                end = program.find("\n", match_start_of_void.end())
                program = "" if end == -1 else program[end:]
            elif match_start_of_void[0] == "/*":
                end = program.find("*/", match_start_of_void.end())
                result += " "
                program = "" if end == -1 else program[end + 2 :]
            else:
                if match_start_of_void[0] == "'":
                    match_end_of_string = QUOTE_END.search(
                        program[match_start_of_void.end() :]
                    )
                else:
                    match_end_of_string = DQUOTE_END.search(
                        program[match_start_of_void.end() :]
                    )
                if not match_end_of_string:  # unclosed string
                    break
                program = program[
                    match_start_of_void.end() + match_end_of_string.end() :
                ]
    return result


def extract_version_line(program: typing.Optional[str]) -> typing.Optional[str]:
    if not program:
        return None

    # normalize line endings
    if "\n" in program:
        program = program.replace("\r", "")
    else:
        program = program.replace("\r", "\n")

    # extract regular pragma
    program_wo_comments_strings = remove_comments_strings(program)
    for line in program_wo_comments_strings.split("\n"):
        if "pragma solidity" in line:
            return line.rstrip()

    # extract pragma from comments
    for line in program.split("\n"):
        if "pragma solidity" in line:
            return line.rstrip()

    return None


def extract_version(program: typing.Optional[str]) -> typing.Optional[str]:
    version_line = extract_version_line(program)
    if not version_line:
        return None

    assert "pragma solidity" in version_line
    if version_line[-1] == ";":
        version_line = version_line[:-1]
    version_line = version_line[version_line.find("pragma") :]
    pragma_dict = parse_pragma(version_line)

    min_inequality = pragma_dict.get("min_inequality", None)
    max_inequality = pragma_dict.get("max_inequality", None)
    min_version = pragma_dict.get("min_version", None)
    if min_version is not None:
        min_version = min_version.replace(" ", "").replace("\t", "")
    max_version = pragma_dict.get("max_version", None)
    if max_version is not None:
        max_version = max_version.replace(" ", "").replace("\t", "")

    version_spec = (
        f"{min_inequality}{min_version},{max_inequality}{max_version}"
        if max_version
        else min_version
    )
    version_constraint = semver.SimpleSpec(version_spec)

    for version in all_versions:
        semver_version = semver.Version(str(version))
        if semver_version in version_constraint:
            if "0.5.17" in str(semver_version):
                # Solidity 0.5.17 Does not compile in a lot of cases.
                continue
            return str(semver_version)


def extract_binary(file: str) -> Tuple[str, str]:
    program = None
    with open(file) as f:
        program = f.read()

    version = extract_version(program)

    if version is None:
        return os.environ.get("SOLC") or "solc", version
    return solc_exists(version), version
