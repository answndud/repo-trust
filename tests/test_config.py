import pytest
from pathlib import Path

from repotrust.config import ConfigError, load_config


def test_load_config_policy_fail_under(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[policy]
fail_under = 80
""",
        encoding="utf-8",
    )

    loaded = load_config(config)

    assert loaded.fail_under == 80


def test_example_ci_policy_config_loads():
    loaded = load_config(Path("examples/repotrust.toml"))

    assert loaded.fail_under == 85


def test_load_config_rejects_unknown_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[remote]\nenabled = true\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Unknown config section"):
        load_config(config)


def test_load_config_rejects_removed_weights_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[weights]\nreadme_quality = 1.0\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Unknown config section"):
        load_config(config)


def test_load_config_rejects_removed_policy_profiles(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[policy.profiles]
install = "usable_after_review"
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Unknown \\[policy\\] key"):
        load_config(config)


def test_load_config_rejects_invalid_fail_under(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 101\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="fail_under"):
        load_config(config)
