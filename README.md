# pytest-inject

**pytest-inject** is a pytest plugin that allows you to inject arguments into fixtures and parametrized tests using
pytest command-line options, effectively transforming your existing test suite into a set of dynamic debugging tools,
without the need to modify or copy any test code.

**pytest-inject** is the solution when you temporarily modify tests to debug your application, or when your debugging
scripts are based on existing tests.

## Installation

You can install `pytest-inject` via pip:

```bash
pip install pytest-inject
```

## Usage Docs

`pytest-inject` provides main command-line options:

- **`--inject-json`**

  Allows you to inject arguments using a JSON string or a path to a JSON file.

  **Usage with JSON string:**
  ```bash
  pytest --inject-json '{"my_arg": "my_value", "count": 42}'
  ```

  **Usage with JSON file:**
  ```bash
  pytest --inject-json path/to/injection.json
  ```

- **`--inject-dict`**

  Allows you to inject arguments using a Python dictionary defined in a file, or a callable that returns a dictionary.
  This is useful for injecting complex objects that cannot be represented in JSON.

  **Format:** `path/to/file.py::variable_or_function`

  **Example `injection_data.py`:**
  ```python
  def get_data():
      return {"complex_obj": SomeClass(), "timestamp": 123456789}

  data_dict = {"simple_arg": "value"}
  ```

  **Usage:**
  ```bash
  # Use a variable
  pytest --inject-dict injection_data.py::data_dict

  # Use a function
  pytest --inject-dict injection_data.py::get_data
  ```

- **`--inject-allow-dup`**

  By default, pytest-inject automatically removes duplicate parameter sets created by the injection. This process
  also re-indexes the parameter sets and removes their IDs. Use this flag to disable this behavior if you want to
  preserve the original parameter set indexes and IDs, or if you specifically need the duplicate test cases
  resulting from the injection.

  **Usage:**
  ```bash
  pytest "tests/test.py::test_my_app::[my_id]" --inject-json '{"arg": "val"}' --inject-allow-dup
  ```

## Contributions

Contributions in the form of bug reports, feature requests, and pull requests are most welcome!

### Development Installation

To install the project for development purposes:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pytest-inject.git
   cd pytest-inject
   ```

2. Install dependencies (assuming you are using a virtual environment):
   ```bash
   pip install -e .
   ```
   Or if you are using `hatch`:
   ```bash
   hatch env create
   ```

### Running Tests

To run the project's own tests after installing for development, execute pytest from the project root pointing to the
`tests/` directory:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License.