"""Side-effect-free domain behavior."""


def greeting(name: str) -> str:
    """Return a greeting for a non-blank name."""
    normalized_name = name.strip()
    if not normalized_name:
        msg = "name must not be blank"
        raise ValueError(msg)
    return f"Hello, {normalized_name}!"
