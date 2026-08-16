from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCE_PACKAGES = {
    "android.hardware.graphics.mapper@4.0-impl-qti-display",
    "init.qti.display_boot.rc",
    "init.qti.display_boot.sh",
    "libfilefinder",
    "mapper.qti",
    "vendor.qti.hardware.display.allocator-service",
    "vendor.qti.hardware.display.composer-service",
    "vendor.qti.hardware.display.demura-service",
    "vendor.qti.hardware.display.snapalloc-impl",
}

SOURCE_OWNED_PAYLOADS = {
    "vendor/bin/hw/vendor.qti.hardware.display.allocator-service",
    "vendor/bin/hw/vendor.qti.hardware.display.composer-service",
    "vendor/bin/hw/vendor.qti.hardware.display.demura-service",
    "vendor/bin/init.qti.display_boot.sh",
    "vendor/etc/init/init.qti.display_boot.rc",
    "vendor/etc/init/vendor.qti.hardware.display.allocator-service.rc",
    "vendor/etc/init/vendor.qti.hardware.display.composer-service.rc",
    "vendor/etc/init/vendor.qti.hardware.display.demura-service.rc",
    "vendor/etc/vintf/manifest/vendor.qti.hardware.display.allocator-service.xml",
    "vendor/etc/vintf/manifest/vendor.qti.hardware.display.composer-service3_v4.xml",
    "vendor/etc/vintf/manifest/vendor.qti.hardware.display.demura-service.xml",
    "vendor/etc/vintf/manifest/mapper.qti.xml",
    "vendor/lib64/hw/android.hardware.graphics.mapper@4.0-impl-qti-display.so",
    "vendor/lib64/hw/mapper.qti.so",
    "vendor/lib64/libdisplayconfig.qti.so",
    "vendor/lib64/libdisplaydebug.so",
    "vendor/lib64/libdrmutils.so",
    "vendor/lib64/libfilefinder.so",
    "vendor/lib64/libgpu_tonemapper.so",
    "vendor/lib64/libgralloc.qti.so",
    "vendor/lib64/libgralloccore.so",
    "vendor/lib64/libgrallocutils.so",
    "vendor/lib64/libhistogram.so",
    "vendor/lib64/libmapperutils.so",
    "vendor/lib64/libqdMetaData.so",
    "vendor/lib64/libqdutils.so",
    "vendor/lib64/libqservice.so",
    "vendor/lib64/libsdedrm.so",
    "vendor/lib64/libsdmclient.so",
    "vendor/lib64/libsdmcore.so",
    "vendor/lib64/libsdmdal.so",
    "vendor/lib64/libsdmutils.so",
    "vendor/lib64/vendor.qti.hardware.display.snapalloc-impl.so",
}

PROPRIETARY_EXTENSIONS = {
    "odm/lib64/libpwirisfeature.so",
    "vendor/bin/qdcmss",
    "vendor/lib64/libdemura_oem_plugin.so",
    "vendor/lib64/libhdrvivid.so",
    "vendor/lib64/libqdcm-algo.so",
    "vendor/lib64/libsdm-color.so",
}


def test_source_display_packages_are_selected() -> None:
    common = (ROOT / "common.mk").read_text(encoding="utf-8")

    missing = sorted(package for package in SOURCE_PACKAGES if package not in common)

    assert not missing, f"source display packages are not selected: {missing}"


def test_canoe_selects_composer3_v4() -> None:
    board_config = (ROOT / "BoardConfigCommon.mk").read_text(encoding="utf-8")

    assert "SOONG_CONFIG_qtidisplay_composer_version := v3_4" in board_config


def test_source_owned_display_payloads_are_not_extracted() -> None:
    rows = {
        line.split(";", maxsplit=1)[0]
        for line in (ROOT / "proprietary-files.txt").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }

    retained = sorted(SOURCE_OWNED_PAYLOADS & rows)

    assert not retained, f"source-owned display payloads remain proprietary: {retained}"


def test_device_specific_display_extensions_remain_proprietary() -> None:
    rows = {
        line.split(";", maxsplit=1)[0]
        for line in (ROOT / "proprietary-files.txt").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }

    missing = sorted(PROPRIETARY_EXTENSIONS - rows)

    assert not missing, f"device-specific display extensions were over-deblobbed: {missing}"
