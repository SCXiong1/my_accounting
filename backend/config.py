import os
import yaml

_config: dict | None = None


def _load_config() -> dict:
    global _config
    if _config is not None:
        return _config

    config_path = os.environ.get("APP_CONFIG", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        _config = yaml.safe_load(f)
    return _config


def get(key: str, default=None):
    """获取配置值，支持点号路径如 'server.port'。
    环境变量 APP_<section>_<key> 可覆盖 YAML 配置。
    """
    cfg = _load_config()
    env_key = "APP_" + key.upper().replace(".", "_")
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val

    parts = key.split(".")
    val = cfg
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            return default
    return val if val is not None else default
