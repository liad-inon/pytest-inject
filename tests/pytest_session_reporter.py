from _pytest.main import Session


class PytestSessionReporter:
    def __init__(self):
        self.tests_collected = 0

    def pytest_sessionfinish(self, session: Session):
        self.tests_collected = session.testscollected
