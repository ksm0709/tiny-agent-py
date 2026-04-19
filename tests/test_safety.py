import os
from tiny_agent.safety import is_safe_path, is_safe_command


def test_is_safe_path():
    home = os.path.expanduser("~")

    # Safe paths
    assert is_safe_path(os.path.join(home, "test.txt")) is True
    assert is_safe_path(os.path.join(home, "subdir/test.txt")) is True

    # Unsafe paths
    assert is_safe_path("/etc/passwd") is False
    assert is_safe_path("/var/log/syslog") is False
    assert is_safe_path(os.path.join(home, ".ssh/id_rsa")) is False
    assert is_safe_path(os.path.join(home, ".env")) is False
    assert is_safe_path(os.path.join(home, ".git/config")) is False


def test_is_safe_command():
    # Safe commands
    assert is_safe_command("ls") is True
    assert is_safe_command("echo 'hello'") is True

    # Unsafe commands
    assert is_safe_command("cat /etc/passwd") is False
    assert is_safe_command("ls /var/log") is False
    assert is_safe_command("cat ~/.ssh/id_rsa") is False
    assert is_safe_command("cat ~/.env") is False
