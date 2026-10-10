import pytest

from cloud_assessment_lab.config import Settings


def test_defaults_from_empty_env():
    s = Settings.from_env({})
    assert s.port == 8080 and s.frame_ancestors == "'none'" and s.ttl_minutes == 120 and s.max_items == 200
    assert s.rate_limit_posts == 10 and s.rate_limit_window_minutes == 10 and s.max_concurrent == 2
    assert not s.trust_proxy and not s.allow_no_turnstile and s.turnstile_secret is None
    assert s.turnstile_enforced and not s.turnstile_required, (
        "fail closed: no secret and no override means uploads answer 503"
    )
    assert s.static_dir.name == "web" and s.samples_dir.name == "samples"


def test_full_env():
    s = Settings.from_env(
        {
            "PORT": "9000",
            "CA_ALLOWED_ORIGINS": "https://a.example, https://b.example/ https://a.example",
            "CA_FRAME_ANCESTORS": "https://hybridcloudworks.com https://www.hybridcloudworks.com",
            "CA_SITE_ORIGINS": "https://hybridcloudworks.com",
            "TURNSTILE_SECRET": " s3 ",
            "CA_TURNSTILE_SITE_KEY": "k",
            "CA_ALLOW_NO_TURNSTILE": "true",
            "CA_TTL_MINUTES": "5",
            "CA_MAX_ITEMS": "3",
            "CA_RATE_LIMIT_POSTS": "2",
            "CA_RATE_LIMIT_WINDOW_MINUTES": "1",
            "CA_MAX_CONCURRENT": "1",
            "CA_TRUST_PROXY": "1",
            "CA_LOG_SILENT": "yes",
            "CA_STATIC_DIR": "/tmp/web",
            "CA_SAMPLES_DIR": "/tmp/samples",
        }
    )
    assert s.port == 9000 and s.allowed_origins == ("https://a.example", "https://b.example")
    assert s.site_origins == ("https://hybridcloudworks.com",) and s.turnstile_secret == "s3" and s.turnstile_required
    assert s.turnstile_enforced and s.trust_proxy and s.log_silent and str(s.static_dir) == "/tmp/web"
    assert "s3" not in repr(s), "the secret never appears in repr"


def test_override_only_applies_without_secret():
    s = Settings.from_env({"CA_ALLOW_NO_TURNSTILE": "1"})
    assert not s.turnstile_enforced and not s.turnstile_required


@pytest.mark.parametrize(
    "env",
    [
        {"PORT": "abc"},
        {"PORT": "0"},
        {"CA_TTL_MINUTES": "-1"},
        {"CA_TTL_MINUTES": "9" * 400},
        {"CA_RATE_LIMIT_POSTS": "1000000001"},
        {"CA_MAX_CONCURRENT": "1.5"},
        {"CA_ALLOWED_ORIGINS": "example.com"},
        {"CA_FRAME_ANCESTORS": "'self'; script-src *"},
    ],
)
def test_invalid_values_raise(env):
    with pytest.raises(ValueError):
        Settings.from_env(env)
