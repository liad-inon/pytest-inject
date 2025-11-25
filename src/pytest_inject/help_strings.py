"""
Module containing help strings for pytest-inject command-line options.
"""
INJECT_JSON_HELP_STRING = '''
Allows you to inject arguments using a JSON string or a path to a JSON file.
Usage with JSON string:
pytest --inject-json '{"my_arg": "my_value", "count": 42}'
Usage with JSON file:
pytest --inject-json path/to/injection.json
'''

INJECT_DICT_HELP_STRING = '''
Allows you to inject arguments using a Python dictionary defined in a file, or a callable that returns a dictionary.
This is useful for injecting complex objects that cannot be represented in JSON.
Format:
path/to/file.py::variable_or_function
Usage:
```bash
# Use a variable
pytest --inject-dict injection_data.py::data_dict
# Use a function
pytest --inject-dict injection_data.py::get_data
```
'''

INJECT_ALLOW_DUPS_HELP_STRING = '''
By default, pytest-inject automatically removes duplicate parameter sets created by the injection. This process
also re-indexes the parameter sets and removes their IDs. Use this flag to disable this behavior if you want to
preserve the original parameter set indexes and IDs, or if you specifically need the duplicate test cases
resulting from the injection.
Usage:
pytest "tests/test.py::test_my_app::[my_id]" --inject-json '{"arg": "val"}' --inject-allow-dup
'''
