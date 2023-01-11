from pytanis.config import get_cfg


def test_get_cfg(tmp_config):
    cfg = get_cfg()
    assert cfg.Google.client_secret_json.is_absolute()
