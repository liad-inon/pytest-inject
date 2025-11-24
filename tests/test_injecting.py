"""
    Tests here are injecting arguments into the tests defined
    in the "tests_injected" directory. These injected arguments are designed
    to make the injected tests pass. If the injected test failed, it means
    that the injection mechanism is not working as expected.
"""

import json
from os import path
from pathlib import Path

import pytest

from pytest_session_reporter import PytestSessionReporter
from tests_injected.argument_values import INJECTED

PLUGIN_TESTS_DIR = Path(__file__).resolve().parent
INJECTED_TESTS_DIR = path.join(PLUGIN_TESTS_DIR, "tests_injected")
TESTS_DATA_DIR = path.join(PLUGIN_TESTS_DIR, "data")

INJECT_1_STRING_JSON_PATH = path.join(TESTS_DATA_DIR, "inject_1_string.json")
INJECT_1_STRING_PYTHON_FILE_PATH = path.join(TESTS_DATA_DIR, "inject_1_string.py")
INJECT_1_STRING_DICT_TARGET = f"{INJECT_1_STRING_PYTHON_FILE_PATH}:injected_args"
INJECT_1_STRING_DICT_GETTER_FUNC_TARGET = f"{INJECT_1_STRING_PYTHON_FILE_PATH}:injected_args"

TEST_PASSED_CODE = 0


def test_inject_1_string_parameterize():
    """
        inject "injected_string_parameter"="injected" to make this test pass.
        Check that injection works with parameterized tests.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_parameterize",
            "--inject-json",
            json.dumps({"injected_string_parameter": INJECTED})
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_1_string_fixture():
    """
        Inject "injected_string_fixture"="injected" to make this test pass.
        Check that injection works with fixtures.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_fixture",
            "--inject-json",
            json.dumps({"injected_string_fixture": INJECTED})
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_and_override_indirect_for_indirect_true_while_not_effecting_other_indirect_arguments():
    """
        inject "injected_indirect_arg"="injected", while not effecting
        other_indirect_arg, which needs to stay indirect to pass the test.

        check that when injecting on indirect=True, none injected indirect
        arguments are not effected.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_and_override_indirect_for_indirect_true_while_not_effecting_other_indirect_arguments",
            "--inject-json",
            json.dumps({"injected_indirect_arg": INJECTED})
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_and_override_indirect_for_indirect_equal_list_with_all_test_arguments():
    """
        Inject "injected_string_fixture"="injected" to make this test pass, while not effecting
        other_indirect_arg, which needs to stay indirect to pass.
        Check that when injecting on indirect=["injected_indirect_arg", "other_indirect_arg"],
        none injected indirect arguments are not effected.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_and_override_indirect_for_indirect_equal_list_with_all_test_arguments",
            "--inject-json",
            json.dumps({"injected_indirect_arg": INJECTED})
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_parameterize_arguments_set_duplication_deletion():
    """
        Checking deletion of duplicated parameterize argument sets caused by
        injection.
        The test is preformed by overriding all injected test arguments, and
        verifying that the injected test was only run and collected one time.
    """
    injected_session_reporter = PytestSessionReporter()

    pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_general_duplication_deletion",
            "--inject-json",
            json.dumps({"a": INJECTED, "b": INJECTED, "c": INJECTED})
        ],
        [injected_session_reporter]
    )

    assert injected_session_reporter.tests_collected == 1


def test_parameterize_arguments_set_duplication_deletion_disabling():
    """
        Checking deletion of duplicated parameterize argument sets
        caused by injection not activating when --inject-allow-dup is used.
        The test is preformed by overriding all injected test arguments, and verifying that
        the injected test was only run and collected for each currently existing parameter set (3).
    """
    injected_session_reporter = PytestSessionReporter()

    pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_general_duplication_deletion",
            "--inject-json",
            json.dumps({"a": INJECTED, "b": INJECTED, "c": INJECTED}),
            "--inject-allow-dup"
        ],
        [injected_session_reporter]
    )

    assert injected_session_reporter.tests_collected == 3


def test_inject_using_json_string():
    """
        Inject "injected_string_parameter"="injected" to make this test pass.
        Use JSON string as input.
        Check that injection works with JSON strings.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_parameterize",
            "--inject-json",
            json.dumps({"injected_string_parameter": INJECTED})
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_using_json_file_path():
    """
        Inject "injected_string_parameter"="injected" to make this test pass.
        Use JSON file path as input.
        Check that injection works with JSON file paths.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_parameterize",
            "--inject-json",
            INJECT_1_STRING_JSON_PATH
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_using_python_dict_attribute():
    """
        Inject "injected_string_parameter"="injected" to make this test pass.
        Use Python dict from file target path.
        Check that injection works with Python dict.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_parameterize",
            "--inject-dict",
            INJECT_1_STRING_DICT_TARGET
        ]
    )

    assert exit_code == TEST_PASSED_CODE


def test_inject_using_python_dict_getter_function():
    """
        Inject "injected_string_parameter"="injected" to make this test pass.
        Use Python dict getter function from file target.
        Check that injection works with Python dict getter function.
    """
    exit_code = pytest.main(
        [
            INJECTED_TESTS_DIR,
            "-k",
            "test_inject_1_string_parameterize",
            "--inject-dict",
            INJECT_1_STRING_DICT_GETTER_FUNC_TARGET
        ]
    )

    assert exit_code == TEST_PASSED_CODE
