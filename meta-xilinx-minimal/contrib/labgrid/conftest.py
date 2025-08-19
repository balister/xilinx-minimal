import pytest


@pytest.fixture(scope="session")
def command(target):
    strategy.transition("shell")
    shell = target.get_driver("ShellDriver")
    target.activate(shell)
    return shell
