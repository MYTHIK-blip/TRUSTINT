import pytest
import yaml

from core.lattice import validate_all


# Test missing trustee
def test_missing_trustee(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "trusts.yaml").write_text(
        yaml.dump([{"slug": "test-trust", "name": "Test Trust", "jurisdiction": "NZ"}])
    )
    (config_dir / "roles.yaml").write_text(
        yaml.dump(
            [{"trust": "test-trust", "role": "beneficiary", "party": "Test Party"}]
        )
    )
    (config_dir / "assets.yaml").touch()
    (config_dir / "laws.yaml").touch()

    with pytest.raises(
        ValueError, match=r"Rule violation: trusts without a trustee: \['test-trust'\]"
    ):
        validate_all(config_dir)


# Test air asset missing jurisdiction
def test_air_asset_missing_jurisdiction(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "trusts.yaml").write_text(
        yaml.dump([{"slug": "test-trust", "name": "Test Trust", "jurisdiction": "NZ"}])
    )
    (config_dir / "roles.yaml").write_text(
        yaml.dump([{"trust": "test-trust", "role": "trustee", "party": "Test Party"}])
    )
    (config_dir / "assets.yaml").write_text(
        yaml.dump([{"trust": "test-trust", "class": "air", "descriptor": "test"}])
    )
    (config_dir / "laws.yaml").touch()

    with pytest.raises(ValueError, match=r"Air asset must specify jurisdiction: .*"):
        validate_all(config_dir)


# Test air asset missing bounds
def test_air_asset_missing_bounds(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "trusts.yaml").write_text(
        yaml.dump([{"slug": "test-trust", "name": "Test Trust", "jurisdiction": "NZ"}])
    )
    (config_dir / "roles.yaml").write_text(
        yaml.dump([{"trust": "test-trust", "role": "trustee", "party": "Test Party"}])
    )
    (config_dir / "assets.yaml").write_text(
        yaml.dump(
            [
                {
                    "trust": "test-trust",
                    "class": "air",
                    "descriptor": "test",
                    "jurisdiction": "NZ",
                }
            ]
        )
    )
    (config_dir / "laws.yaml").touch()

    with pytest.raises(
        ValueError, match=r"Air asset descriptor should indicate bounds/altitude: .*"
    ):
        validate_all(config_dir)
