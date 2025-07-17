# Django Interview

Welcome to the live‑coding stage of our hiring process.
You will work on a compact yet production‑style Django REST project. Issues reported by product, marketing, and finance have been turned into auto-tests.

**Your goal is to address those issues and keep all tests green.**

### What's included

- A ready‑to‑run Django application.
- Pre‑configured infrastructure (PostgreSQL, Redis, Docker, devcontainer).
- A comprehensive test suite. All tests should stay green.

## Business stories to address

[See the task list](docs/tasks.md)

## Getting started

- Select the prepared git branch `candidate`
- Go `Code` -> `Codespaces` -> `Create codespace on candidate`:

[<img src="docs/codespaces_example.png" width="560" />](docs/codespaces_example.png)

- You will find a ready-made, fully operational dedicated workspace to solve the interview. Take any action to solve the problem, keep the project working, and make sure that all the tests are passing.

## Requirements
- Commit each task separately.
- When all interview tests are done, open **one** Pull Request with your solution.
- All tests must be successfully passed. For `tests/interview/`, the removal of the decorator `@pytest.mark.xfail` is mandatory.
- Your solution will be evaluated externally. In addition to test results, the following aspects will be considered:
    - code quality and style
    - architectural and implementation decisions
    - adherence to industry best practices
    - the amount of time invested in completing the task
- Creative solutions are welcome if they meet quality standards.

### ⏱ Time‑box

The task is designed to be solved not more than **1 hour**. Focus on clear, incremental fixes.

### Helpful commands

Use the terminal to run:

- `make interview` to run interview tests to check your solutions.
- `make test` to run common project tests to ensure that common features are still working.
- `make lint` to run linters and formatters.
- see more useful commands in the `Makefile`.

Good luck and enjoy!

## About Project

### Tech Stack

- Python: 3.11
- Django: 4
- API: Django REST Framework
- Database: PostgreSQL 15
- Caching: Redis 7
- Testing: Pytest, Pytest-Django
- Architecture: Service Pattern, Resource-Based API
- Dependency Management: `requirements.txt`

---
Contact: [info@unicheck.ai ](mailto:info@unicheck.ai)
