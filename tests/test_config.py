import pytest

from repotrust.config import ConfigError, load_config


def test_load_config_policy_and_weights(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[policy]
fail_under = 80

[weights]
readme_quality = 0.10
install_safety = 0.70
security_posture = 0.10
project_hygiene = 0.10
""",
        encoding="utf-8",
    )

    loaded = load_config(config)

    assert loaded.fail_under == 80
    assert loaded.weights == {
        "readme_quality": 0.10,
        "install_safety": 0.70,
        "security_posture": 0.10,
        "project_hygiene": 0.10,
    }


def test_load_config_rejects_unknown_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[remote]\nenabled = true\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Unknown config section"):
        load_config(config)


def test_load_config_rejects_partial_weights(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[weights]\nreadme_quality = 1.0\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="must define exactly"):
        load_config(config)


def test_load_config_rejects_weights_that_do_not_sum_to_one(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[weights]
readme_quality = 0.25
install_safety = 0.25
security_posture = 0.25
project_hygiene = 0.10
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="sum to 1.0"):
        load_config(config)


def test_load_config_rejects_invalid_fail_under(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 101\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="fail_under"):
        load_config(config)

