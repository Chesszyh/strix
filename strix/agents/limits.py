from strix.config import Config


_DEFAULT_ROOT_ITERATIONS = {
    "quick": 50,
    "standard": 120,
    "deep": 180,
}

_DEFAULT_CHILD_ITERATIONS = {
    "quick": 30,
    "standard": 60,
    "deep": 90,
}


def _int_config(name: str, default: int, minimum: int = 1) -> int:
    raw_value = Config.get(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default
    return max(minimum, value)


def resolve_max_iterations(scan_mode: str, *, child: bool = False) -> int:
    defaults = _DEFAULT_CHILD_ITERATIONS if child else _DEFAULT_ROOT_ITERATIONS
    default = defaults.get(scan_mode, defaults["deep"])
    config_name = "strix_child_max_iterations" if child else "strix_max_iterations"
    return _int_config(config_name, default)
