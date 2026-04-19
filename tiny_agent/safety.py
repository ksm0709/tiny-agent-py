import os


def is_safe_path(filepath: str) -> bool:
    """
    Checks if the given path is safe to access.
    - Must be under the user's home directory.
    - Must not be a sensitive file/directory.
    """
    try:
        abs_path = os.path.abspath(filepath)
        home_dir = os.path.expanduser("~")

        if not abs_path.startswith(home_dir):
            return False

        sensitive_patterns = [
            ".env",
            ".bashrc",
            ".ssh",
            ".git/config",
            "/etc/",
            "/var/",
        ]

        for pattern in sensitive_patterns:
            if pattern in abs_path:
                return False

        return True
    except Exception:
        return False


def is_safe_command(command: str) -> bool:
    """
    Checks if the given shell command is safe.
    - Blocks commands that try to access sensitive files/directories.
    """
    sensitive_patterns = [
        "/etc/",
        "/var/",
        "~/.ssh",
        "~/.env",
        "~/.bashrc",
        ".git/config",
    ]

    for pattern in sensitive_patterns:
        if pattern in command:
            return False

    return True
