# SPDX-License-Identifier: Apache-2.0

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON_SOURCE_LIST = ROOT / "proprietary-files-phone.txt"
CAMERA_OWNED_TA_DESTINATIONS = {
    f"odm/firmware/secure_ta/{name}.{suffix}"
    for name in ("cryptoeng", "fidoctap", "fidotap")
    for suffix in (*[f"b0{index}" for index in range(9)], "mdt")
}
COMMON_ONLY_FIDO_DESTINATIONS = {
    "system_ext/etc/permissions/vendor-oplus-hardware-biometrics-fido.xml",
    "system_ext/etc/permissions/vendor-oplus-hardware-biometrics-fido2.xml",
    "system_ext/framework/vendor.oplus.hardware.fido.fido2ca-V1-java.jar",
    "system_ext/framework/vendor.oplus.hardware.fido.fidoca-V1-java.jar",
}
DUPLICATE_ODM_FIDO_REGISTRATIONS = {
    "odm/etc/permissions/vendor-oplus-hardware-biometrics-fido.xml",
    "odm/etc/permissions/vendor-oplus-hardware-biometrics-fido2.xml",
}


def declaration_destinations(source_list: Path) -> set[str]:
    destinations: set[str] = set()
    for raw_line in source_list.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        declaration = line.split(";", 1)[0].removeprefix("-")
        destination = declaration.split(":", 1)[-1]
        if destination in destinations:
            raise AssertionError(
                f"duplicate destination in {source_list}: {destination}"
            )
        destinations.add(destination)
    return destinations


def camera_source_list() -> Path:
    configured = os.environ.get("CAMERA_SOURCE_LIST")
    if configured:
        source_list = Path(configured)
    else:
        source_list = (
            ROOT.parents[2]
            / "vendor/oneplus/camera-sm8850-common/proprietary-files.txt"
        )
    if not source_list.is_file():
        raise AssertionError(
            "camera source declaration list not found; set CAMERA_SOURCE_LIST"
        )
    return source_list


class ExtractionOwnershipTest(unittest.TestCase):
    def test_camera_owned_trust_tas_have_one_source_owner(self) -> None:
        common = declaration_destinations(COMMON_SOURCE_LIST)
        camera = declaration_destinations(camera_source_list())

        self.assertEqual(
            CAMERA_OWNED_TA_DESTINATIONS,
            CAMERA_OWNED_TA_DESTINATIONS & camera,
        )
        self.assertEqual(set(), CAMERA_OWNED_TA_DESTINATIONS & common)
        self.assertEqual(set(), common & camera & CAMERA_OWNED_TA_DESTINATIONS)

    def test_nonduplicate_common_fido_inputs_remain_common(self) -> None:
        common = declaration_destinations(COMMON_SOURCE_LIST)
        camera = declaration_destinations(camera_source_list())

        self.assertEqual(
            COMMON_ONLY_FIDO_DESTINATIONS,
            COMMON_ONLY_FIDO_DESTINATIONS & common,
        )
        self.assertEqual(set(), COMMON_ONLY_FIDO_DESTINATIONS & camera)
        self.assertEqual(set(), DUPLICATE_ODM_FIDO_REGISTRATIONS & common)
        self.assertEqual(set(), DUPLICATE_ODM_FIDO_REGISTRATIONS & camera)


if __name__ == "__main__":
    _ = unittest.main()
