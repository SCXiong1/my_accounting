import os

import yaml

_config: dict | None = None

_DEFAULTS = {
    "server.host": "0.0.0.0",
    "server.port": 8080,
    "database.path": "./data/ezexpense.db",
    "security.jwt_secret": "change-me-in-production",
    "security.jwt_expire_days": 7,
    "cors.origins": ["*"],
}


def _load_config() -> dict:
    global _config
    if _config is not None:
        return _config

    config_path = os.environ.get("APP_CONFIG", "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        _config = yaml.safe_load(f) or {}
    return _config


def _dict_get(d: dict, path_parts: list[str]) -> object | None:
    for p in path_parts:
        if isinstance(d, dict):
            d = d.get(p)
        else:
            return None
    return d


def get(key: str, default: object = None) -> object:
    """获取配置值，支持点号路径如 'server.port'。

    优先级：环境变量 APP_<SECTION>_<KEY> > YAML 配置文件 > 内置默认值 > default 参数
    """
    env_key = "APP_" + key.upper().replace(".", "_")
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val

    parts = key.split(".")

    val = _dict_get(_load_config(), parts)
    if val is not None:
        return val

    builtin = _dict_get(_DEFAULTS, parts)
    if builtin is not None:
        return builtin

    return default
