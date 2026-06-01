"""Trivial runnable entry point so `uv run` proves the toolchain works."""


def hello() -> str:
    """Return a health-check greeting."""
    return "Hello from todo_app! The uv toolchain works."


def main() -> None:
    print(hello())


if __name__ == "__main__":
    main()
