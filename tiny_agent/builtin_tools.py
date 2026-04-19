import subprocess
import tempfile
import urllib.request
import os
from html.parser import HTMLParser
from tiny_agent.tools import tool


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())


@tool(
    name="execute_python",
    description="Executes Python code in a secure temporary environment and returns stdout/stderr. Do not use for infinite loops.",
)
def execute_python(code: str, timeout: int = 10) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python3", temp_path], capture_output=True, text=True, timeout=timeout
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out."
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


@tool(
    name="execute_shell",
    description="Executes a shell command (Bash) and returns the output. Useful for file listing, pip installs, or environment checks.",
)
def execute_shell(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + "\n" + result.stderr
        return output.strip() or "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."


@tool(
    name="fetch_webpage",
    description="Fetches a URL and returns clean text content without HTML tags. Useful for reading docs or searching the web.",
)
def fetch_webpage(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
            extractor = TextExtractor()
            extractor.feed(html)
            truncated_text = " ".join(extractor.text)[:5000]
            return truncated_text
    except Exception as e:
        return f"Failed to fetch URL: {str(e)}"


@tool(
    name="read_file",
    description="Reads the entire content of a file from the local file system.",
)
def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool(
    name="write_file",
    description="Writes content to a file on the local file system. Overwrites the file if it exists.",
)
def write_file(filepath: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


BUILTIN_TOOLS = [execute_python, execute_shell, fetch_webpage, read_file, write_file]
