import json
import os
import runpy
from functools import lru_cache
from typing import Any, Dict

from pytest_inject.exceptions import PytestInjectError
from pytest_inject.injector import inject_test_arguments

# Magic constants
PYTHON_FILE_TO_DICT_TARGET_SEPERATOR = "::"


def pytest_addoption(parser):
    group = parser.getgroup("inject")
    group.addoption(
        "--inject-json",
        action="store",
        dest="inject_json",
        default=None,
        help="A file path or raw JSON string used to override "
             "test fixtures and parametrization arguments."
    )
    group.addoption(
        "--inject-allow-dup",
        action="store_true",
        dest="inject_allow_dup",
        default=None,
        help="Disable automatic deduplication of parameterized test cases. "
             "By default, duplicate parameter sets on markers effected by injection, "
             "are filtered to remove duplicates."
    )
    group.addoption(
        "--inject-dict",
        action="store",
        dest="inject_dict",
        default=None,
        help="A Python path to a dictionary or callable (format: 'path/module.py::attribute') "
             "used to override test fixtures and parametrization arguments."
    )


def pytest_generate_tests(metafunc):
    injection_json_raw_input = metafunc.config.getoption("inject_json", default=None)
    injection_dict_raw_input = metafunc.config.getoption("inject_dict", default=None)
    allow_parameter_set_duplication = metafunc.config.getoption("inject_allow_dup", default=False)

    if not injection_json_raw_input and not injection_dict_raw_input:
        return
    elif injection_json_raw_input and injection_dict_raw_input:
        raise PytestInjectError(
            "pytest-inject: --inject-json and --inject-dict arguments "
            "cannot be used together in the same test run. pytest-inject does not know "
            "how to fuse both inputs."
        )

    injected_args = {}
    if injection_json_raw_input:
        injected_args = _resolve_json_input(injection_json_raw_input)
    elif injection_dict_raw_input:
        injected_args = _resolve_python_dict_input(injection_dict_raw_input)

    inject_test_arguments(
        metafunc,
        injected_args,
        allow_parameter_set_duplication
    )


@lru_cache(maxsize=1)
def _resolve_json_input(raw_input: str) -> Dict[str, Any]:
    """
        Parses JSON input (file path or raw string) into a dictionary.
    """
    if os.path.isfile(raw_input):
        try:
            with open(raw_input, 'r') as file:
                return json.load(file)
        except Exception as exception:
            raise PytestInjectError(
                f"pytest-inject: Error reading file '{raw_input}'."
            ) from exception
    else:
        try:
            return json.loads(raw_input)
        except json.JSONDecodeError as exception:
            raise PytestInjectError(
                f"pytest-inject: Invalid JSON input, or a none existent "
                f"file path that is parsed as JSON."
            ) from exception


@lru_cache(maxsize=1)
def _resolve_python_dict_input(path: str) -> Dict[str, Any]:  # type: ignore
    """
    Loads a dict from a python file.
    Can load either a variable or a getter function/callable to get the dict from.

    Format: "path/to/file.py::variable_or_function"
    """
    if PYTHON_FILE_TO_DICT_TARGET_SEPERATOR in path:
        file_path, target_name = path.rsplit(PYTHON_FILE_TO_DICT_TARGET_SEPERATOR, 1)
    else:
        raise PytestInjectError(f"pytest-inject: No target specified in python input '{path}'.")

    if not os.path.isfile(file_path):
        raise PytestInjectError(f"pytest-inject: Python file not found: '{file_path}'")

    try:
        module_globals = runpy.run_path(file_path)
    except Exception as exception:
        raise PytestInjectError(
            f"pytest-inject: Error executing python script '{file_path}'."
        ) from exception

    if target_name not in module_globals:
        raise PytestInjectError(f"pytest-inject: '{target_name}' not found in '{file_path}'")

    obj = module_globals[target_name]

    if callable(obj):
        try:
            injections_dict = obj()
        except Exception as exception:
            raise PytestInjectError(
                f"pytest-inject: Error calling function '{target_name}'"
                f" in '{file_path}'."
            ) from exception
    else:
        injections_dict = obj

    if not isinstance(injections_dict, dict):
        raise PytestInjectError(
            f"pytest-inject: expected a dict from '{target_name}' in '{file_path}', "
            f"got {type(injections_dict)} instead."
        )

    for key in injections_dict:
        if not isinstance(key, str):
            raise PytestInjectError(
                f"pytest-inject: expected string keys in the dict from '{target_name}' "
                f"in '{file_path}', got key of type {type(key)} instead."
            )

    return injections_dict
