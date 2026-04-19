# CHANGELOG


## v0.6.0 (2026-04-19)

### Features

* feat: add reasoning/thinking support to tiny-agent-py via litellm ([`9086c8b`](https://github.com/ksm0709/tiny-agent-py/commit/9086c8b9b63117f21321c9f04c0cf247bacbac89))


## v0.5.0 (2026-04-19)

### Features

* feat: support list of callables for custom hooks

- Allow injecting multiple hooks per event by passing a list of Callable in the hooks dictionary.
- Update type hinting for hooks parameter to Dict[str, Union[Callable, List[Callable]]].
- Ensure backward compatibility: return a single value if only one hook is registered, otherwise return a list of values. ([`4619e7c`](https://github.com/ksm0709/tiny-agent-py/commit/4619e7ce0bd6cd16095dc0d75100964a206d14b3))


## v0.4.0 (2026-04-19)

### Features

* feat: add turn_start and turn_stop lifecycle tools and hooks

- Introduce `turn_start` and `turn_stop` built-in tools to explicitly manage the agent's work cycle.
- Add `on_turn_start` and `on_turn_stop` hooks.
- Update system prompt to enforce their usage.
- Update documentation in docs/builtin_tools.md. ([`75151a6`](https://github.com/ksm0709/tiny-agent-py/commit/75151a6bd0e1f93879401343ee8fa13a641e4019))


## v0.3.0 (2026-04-19)

### Chores

* chore: remove obsolete CLAUDE.md file ([`2c44fb3`](https://github.com/ksm0709/tiny-agent-py/commit/2c44fb3c9ab208a2fa207e0a810b730b3019f8e1))

* chore: remove PyPI release step and update README installation instructions ([`66fdc8d`](https://github.com/ksm0709/tiny-agent-py/commit/66fdc8d5e9e0cc54a93708789df905b5fa92efa6))

### Features

* feat: change default max_iterations to infinity

Allow the agent loop to run indefinitely by default (float('inf')), instead of a hardcoded limit of 10. Users can still restrict iterations when needed. ([`09b9519`](https://github.com/ksm0709/tiny-agent-py/commit/09b9519311fb2549697ae6e837021875ade22f86))


## v0.2.0 (2026-04-19)

### Chores

* chore: add .omc/ to .gitignore

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`c3eca9f`](https://github.com/ksm0709/tiny-agent-py/commit/c3eca9f47014b972d717167b6a907484d75a7bb6))

* chore: sync uv.lock version to 0.1.2

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`be56ba0`](https://github.com/ksm0709/tiny-agent-py/commit/be56ba0b233156d2929f0e11c94f0f9a8567208e))

* chore: update uv.lock and add .pkm ([`4f3bb65`](https://github.com/ksm0709/tiny-agent-py/commit/4f3bb656f9e8781a6a696f61bdc1c15847290baa))

### Documentation

* docs: exclude hidden directories from AGENTS.md documentation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`6766b2f`](https://github.com/ksm0709/tiny-agent-py/commit/6766b2f1bfd0e68061ed682ecc5493f512c76779))

* docs: add hierarchical AGENTS.md documentation across codebase

Generated AI-readable AGENTS.md files for root, tiny_agent/, tests/, and
docs/ directories covering architecture, tool namespacing, memory design,
testing patterns, and agent workflow for AI agent navigation.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com> ([`a0261d4`](https://github.com/ksm0709/tiny-agent-py/commit/a0261d4fdb87032c7401264d02175b33a0bb0c74))

### Features

* feat: implement lazy loading for markdown skills

- Update `SkillLoader` to recursively scan skill directories and generate colon-separated skill IDs (e.g., `sub:nested_skill`).
- Modify `Agent._load_skills` to only inject skill metadata (ID, name, description) into the initial system prompt to save token usage.
- Introduce `load_skill` tool to allow the agent to fetch the full markdown instruction on demand.
- Update `README.md` and `docs/skills.md` to reflect the new lazy loading and nested directory support.
- Add test coverage for dynamic skill loading behavior and sub-directory picking. ([`af6e1bd`](https://github.com/ksm0709/tiny-agent-py/commit/af6e1bd94f86dec3f94f2c2ab061686f690d234e))


## v0.1.2 (2026-04-19)

### Bug Fixes

* fix: skip python-semantic-release internal build step to prevent permission errors ([`d440aad`](https://github.com/ksm0709/tiny-agent-py/commit/d440aad582867ddbae7c3cf4f86002d8140284ab))


## v0.1.1 (2026-04-19)

### Bug Fixes

* fix: use standard pip and python build in release workflow instead of uv ([`6b4c7af`](https://github.com/ksm0709/tiny-agent-py/commit/6b4c7afb40673384c624d6f6d34adb239018fb98))


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
