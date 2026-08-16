#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import pathlib
import re
import unittest

DEVICE_DIR = pathlib.Path(__file__).resolve().parents[1]
PRODUCT_PACKAGES = re.compile(r"^PRODUCT_PACKAGES\s*\+?=\s*(.*)$")


def composed_packages(makefile: pathlib.Path) -> set[str]:
    packages: set[str] = set()
    collecting = False
    for line in makefile.read_text(encoding="utf-8").splitlines():
        value = line.strip() if collecting else ""
        if not collecting:
            match = PRODUCT_PACKAGES.match(line)
            if match is None:
                continue
            value = match.group(1).strip()
        collecting = value.endswith("\\")
        packages.update(value.removesuffix("\\").split())
    return packages


class HealthCompositionTest(unittest.TestCase):
    def test_product_selects_oplus_lineage_health_and_keeps_health_images(self):
        packages = composed_packages(DEVICE_DIR / "common.mk")

        self.assertIn("vendor.lineage.health-service.oplus", packages)
        self.assertNotIn("vendor.lineage.health-service.default", packages)
        self.assertIn("android.hardware.health-service.qti", packages)
        self.assertIn("android.hardware.health-service.qti_recovery", packages)


if __name__ == "__main__":
    _ = unittest.main()
