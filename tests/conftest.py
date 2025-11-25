pytest_plugins = ["pytest_inject"]

# Disable collection of the injected tests to avoid running them without injection
collect_ignore = ["tests_injected"]
