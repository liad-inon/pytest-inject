from typing import Any, Union, List, Dict, Optional

from _pytest.mark import Mark
from _pytest.python import Metafunc

# Magic constants
PARAMETERIZE_MARKER_TAG = "parametrize"
ARG_NAMES_INDEX = 0
ARG_VALUES_INDEX = 1
COMMA_CHAR = ','


def inject_test_arguments(
        test_metafunc: Metafunc,
        injected_args: Dict[str, Any],
        allow_arg_values_duplication=False,
):
    """
    Injects arguments into the test function represented by test_metafunc,
    overriding existing parameterize markers arguments if needed, and adding
    new parameterization for non-parameterized injected arguments.
    Removes duplicated parameter sets on any parameterize marker with at least
    one argument injection, unless allow_arg_values_duplication is set to True.

    :param test_metafunc: The pytest Metafunc object of the injected test.
    :param allow_arg_values_duplication: Whether to allow duplicated parameter sets
            after injection.
    :param injected_args: A dictionary of argument names and their injected values.
    """
    left_injections = injected_args.copy()

    for marker in test_metafunc.definition.iter_markers(PARAMETERIZE_MARKER_TAG):
        _injected_parameterized_marker(
            marker,
            injected_args,
            allow_arg_values_duplication,
            test_metafunc,
        )

        marker_args_names = get_parameterize_arg_names(marker)
        for injection_name in marker_args_names:
            left_injections.pop(injection_name, None)

    relevant_left_injunctions = {
        argument_name: value for argument_name, value in left_injections.items()
        if argument_name in test_metafunc.fixturenames
    }

    if relevant_left_injunctions:
        test_metafunc.parametrize(
            list(relevant_left_injunctions.keys()),
            [tuple(relevant_left_injunctions.values())],
        )


def _injected_parameterized_marker(
        marker: Mark,
        injected_args: Dict[str, Any],
        allow_arg_values_duplication: bool,
        test_metafunc: Metafunc,
):
    """
        Injects arguments into a parameterize marker, by recreating it with
        the injected arguments overriding existing ones, deleting duplicates
        if needed, removing the old marker, and adding the new.
    """
    marker_arg_names = get_parameterize_arg_names(marker)
    injections_in_marker = {
        injected_argument: injected_value for injected_argument, injected_value in injected_args.items()
        if injected_argument in marker_arg_names
    }

    if not injections_in_marker:
        return

    old_marker_arg_values = marker.args[ARG_VALUES_INDEX]
    injected_arg_values = _inject_arg_values(
        old_marker_arg_values,
        marker_arg_names,
        injections_in_marker,
    )

    new_marker_indirect_arg = _adjust_indirect_arg_for_injection(
        marker.kwargs.get("indirect", False),
        marker_arg_names,
        injections_in_marker
    )

    new_marker_ids_arg = marker.kwargs.get("ids", None)
    new_marker_arg_values = injected_arg_values

    if not allow_arg_values_duplication:
        injected_arg_values_no_duplicates = [
            arg_value for index, arg_value in enumerate(injected_arg_values)
            if arg_value not in injected_arg_values[:index]
        ]
        new_marker_arg_values = injected_arg_values_no_duplicates

        # If duplicates were removed, reset the ids to None to avoid mismatches.
        # Because if duplicates were removed, the existing ids no longer
        # correspond correctly to the parameter sets, both in count and in meaning.
        duplicates_were_removed = len(injected_arg_values_no_duplicates) < len(injected_arg_values)
        if duplicates_were_removed:
            new_marker_ids_arg = None

    old_marker_index = test_metafunc.definition.own_markers.index(marker)
    _replace_parameterize_marker(
        marker_arg_names,
        new_marker_arg_values,
        new_marker_indirect_arg,
        new_marker_ids_arg,
        marker.kwargs.get("scope", None),
        test_metafunc,
        old_marker_index,
    )


def _inject_arg_values(
        arg_values: List[Any],
        arg_names: List[str],
        injections: Dict[str, Any],
) -> List[Any]:
    """
        Injects the given injections into the argument values list, returning
        a new list with the injected values.
    """
    arg_values_injected = []

    for arguments_values_set in arg_values:
        if isinstance(arguments_values_set, (list, tuple)):
            arg_values_set_injected = [arg_value for arg_value in arguments_values_set]

            for arg_index in range(len(arguments_values_set)):
                arg_name = arg_names[arg_index]

                if arg_name in injections.keys():
                    arg_values_set_injected[arg_index] = injections[arg_name]

            arg_values_injected.append(arg_values_set_injected)
        else:
            arg_name = arg_names[0]

            if arg_name in injections.keys():
                arg_values_injected.append(injections[arg_name])

    return arg_values_injected


def _adjust_indirect_arg_for_injection(
        old_indirect: Union[bool, List[str]],
        arg_names: List[str],
        injections_in_marker: Dict[str, Any]
) -> Union[bool, List[str]]:
    """
        returns an adjusts the 'indirect' argument of a parameterize marker
        that will not affect injected arguments, while keeping other indirect
        arguments indirect.
    """
    if old_indirect is True:
        return [
            arg_name for arg_name in arg_names
            if arg_name not in injections_in_marker.keys()
        ]
    elif isinstance(old_indirect, (list, tuple)):
        return [
            arg_name for arg_name in old_indirect
            if arg_name not in old_indirect
        ]
    else:
        return False


def get_parameterize_arg_names(parameterize_marker: Mark):
    """
        Helper to extract argument names from a parametrize marker.
        Handles both @pytest.mark.parametrize("a,b", ...) and (["a","b"], ...)
    """
    arg_names = parameterize_marker.args[ARG_NAMES_INDEX]
    if isinstance(arg_names, str):
        return [arg_name.strip() for arg_name in arg_names.split(",")]
    elif isinstance(arg_names, (list, tuple)):
        return list(arg_names)

    return []


def _replace_parameterize_marker(
        marker_arg_names: Union[List[str], str],
        marker_arg_values: List[Any],
        marker_indirect: Union[bool, List[str]],
        marker_ids: Optional[List[str]],
        marker_scope: Optional[str],
        test_metafunc: Metafunc,
        replacement_index: int,
):
    """
        replaces an existing parameterize marker in the test_metafunc with a new one
        created from the given arguments.
    """
    test_metafunc.parametrize(
        COMMA_CHAR.join(marker_arg_names),
        marker_arg_values,
        indirect=marker_indirect,
        ids=marker_ids,
        scope=marker_scope
    )

    new_marker = test_metafunc.definition.own_markers[-1]
    test_metafunc.definition.own_markers[replacement_index] = new_marker
    del test_metafunc.definition.own_markers[-1]
