from uplaybook import internals


def test_platform_info_does_not_require_id_like(monkeypatch):
    monkeypatch.setattr(internals.platform, "system", lambda: "Linux")
    monkeypatch.setattr(
        internals.platform,
        "freedesktop_os_release",
        lambda: {
            "NAME": "Example Linux",
            "ID": "example",
            "VERSION_ID": "1",
            "VERSION_CODENAME": "example",
        },
    )

    info = internals.PlatformInfo()

    assert info.release_name == "Example Linux"
    assert not hasattr(info, "release_like")
