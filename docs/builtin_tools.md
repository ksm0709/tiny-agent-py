# Built-in Native Tools

`tiny-agent-py` ships with a powerful set of default native tools out-of-the-box. These tools allow the agent to interact with its environment and self-correct, giving it a Turing-complete action space without requiring expensive external API keys or bloated dependencies.

By default, these tools are loaded automatically. You can disable this by passing `load_builtin_tools=False` when instantiating the `Agent`.

## 1. Python Code Executor (`execute_python`)
Executes Python code in a secure temporary environment and returns `stdout` and `stderr`.
This acts as a "REPL" for the agent. Instead of struggling with complex math, logic, or data parsing, the agent can write a script, run it, read the output, and fix any errors.

## 2. Shell Command Executor (`execute_shell`)
Executes shell (Bash) commands and returns the output. 
This allows the agent to navigate the filesystem, install packages (e.g., via `pip`), run tests (`pytest`), and use tools like `git`.

## 3. Web Page Fetcher (`fetch_webpage`)
Fetches a URL and returns clean text content with HTML tags stripped. 
This gives the agent real-time access to the web to read API documentation, GitHub issues, or current events.

## 4. File Operations (`read_file`, `write_file`)
Provides read and write access to the local filesystem.
The agent uses these tools to edit source code, manage configuration files, and persist its work securely.

## 5. Turn Lifecycle Hooks (`turn_start`, `turn_stop`)
These implicit tools explicitly delimit the agent's work cycle:
- `turn_start(goal: str)`: Signals the start of the task execution and the current target.
- `turn_stop(result: str)`: Signals the completion of the task and outputs the result.
The framework exposes hooks (`on_turn_start`, `on_turn_stop`) so integrating applications can track agent progress.

## 6. Task Management (`manage_tasks`)
Provides an agent context window manager that pins tasks directly to the system prompt.
The tool maintains a task/todo list containing `status`, `title`, and `description`. To prevent the context window from getting cluttered via standard standard output, the tool only prints the checkbox status and title to the stdout, while keeping the full rich descriptions securely attached to the agent's "static memory" system prompt so that they never slide out of context.
