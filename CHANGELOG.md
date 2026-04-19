# CHANGELOG


## v0.1.0 (2026-04-19)

### Bug Fixes

* fix: change build_command in pyproject.toml to use pip instead of uv for semantic release ([`f200fdd`](https://github.com/ksm0709/tiny-agent-py/commit/f200fdd4c33e8051ba20cb732c83d190f60b32f0))

* fix: update example.py and README to handle streaming correctly ([`17a6f8e`](https://github.com/ksm0709/tiny-agent-py/commit/17a6f8eacbd9d91d862e398c1a3544601880b416))

* fix: configure hatchling to find tiny_agent package ([`a915071`](https://github.com/ksm0709/tiny-agent-py/commit/a915071f45fee210f8b15df39872bbb6032ffc56))

### Chores

* chore: remove __pycache__ and .coverage from git tracking and add .gitignore ([`c3e78cf`](https://github.com/ksm0709/tiny-agent-py/commit/c3e78cf64f7916f3aeebfef67ae42e2c5a94610a))

* chore: remove pkm specific docs ([`1304a96`](https://github.com/ksm0709/tiny-agent-py/commit/1304a9661d420014afb4135b2fce3cfa00f4d40b))

* chore: copy docs infrastructure from pkm ([`1b357dd`](https://github.com/ksm0709/tiny-agent-py/commit/1b357dd9c499526c37b05b0b4c9c004b2586b78c))

* chore: copy pkm infrastructure (docs, claude stop hook, context check) ([`144c4a3`](https://github.com/ksm0709/tiny-agent-py/commit/144c4a3b69ad0b5d241c7fb19c45167703b607f4))

### Continuous Integration

* ci: update workflow triggers to use master branch ([`2f151e6`](https://github.com/ksm0709/tiny-agent-py/commit/2f151e6bf06bc123e2f52cdf25417723d8154e87))

### Features

* feat: add essential native builtin tools

- Researched and implemented essential native tools for AI agents
- Added execute_python, execute_shell, fetch_webpage, read_file, and write_file tools
- Tools are automatically loaded into the Agent by default (can be disabled via load_builtin_tools=False)
- Added tests in tests/test_builtin_tools.py
- Updated documentation and README.md ([`e4b75c4`](https://github.com/ksm0709/tiny-agent-py/commit/e4b75c4f40bc03214ff677bc5d7e9265aadf5dc3))

* feat: implement dynamic context window based on model token size

- Replaced fixed message count with token size calculation using `litellm.token_counter`
- Added `context_window_ratio` parameter to `Agent` and `SessionMemory` (default 0.8)
- Updated tests to mock `litellm.token_counter`
- Updated README.md, docs/memory.md, and example.py to reflect new dynamic context window ([`c73ef45`](https://github.com/ksm0709/tiny-agent-py/commit/c73ef45579e6e61e4e21a8b4dc8ab02e12c66080))

* feat: Add tests for tiny_agent, CI coverage checks, and documentation

- Wrote comprehensive pytest cases achieving 100% coverage
- Configured CI GitHub Actions workflow to enforce 80% coverage
- Added robust README and modular documentation in docs/
- Fixed formatting and linting errors across codebase ([`d947d76`](https://github.com/ksm0709/tiny-agent-py/commit/d947d76f568cecfb9af9197f989112007a401189))

* feat: initial release setup with uv and github actions ([`8d86c9f`](https://github.com/ksm0709/tiny-agent-py/commit/8d86c9fe87bd4c494f8701250c23d21a50ddc187))

### Refactoring

* refactor: remove ai slops and clean up imports in agent.py ([`dbd1e76`](https://github.com/ksm0709/tiny-agent-py/commit/dbd1e767a10a337e538c63db7058e7fa0bce0d49))

### Testing

* test: add comprehensive end-to-end test (test_e2e.py) ([`a247a0f`](https://github.com/ksm0709/tiny-agent-py/commit/a247a0fe981aa559edf9ad16fecc95421f765b7b))

* test: split test_all.py into appropriate modular test files ([`77670c6`](https://github.com/ksm0709/tiny-agent-py/commit/77670c682b85e09146ff88bc1aee15f5db26e6c1))

* test: add comprehensive test suite for tiny_agent ([`5c6135f`](https://github.com/ksm0709/tiny-agent-py/commit/5c6135f628b084b5c00d995df9e713ddd4628a62))

* test: add comprehensive test suite for tiny_agent ([`8b98b54`](https://github.com/ksm0709/tiny-agent-py/commit/8b98b54cc0eb737f3b953f9f64ba93e3c5d08630))
