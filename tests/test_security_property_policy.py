#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import pathlib
import unittest
from typing import ClassVar, override

DEVICE_DIR = pathlib.Path(__file__).resolve().parents[1]
PROPERTY_FILES = ("odm.prop", "product.prop", "system_ext.prop", "vendor.prop")

COMMON_POLICY = {
    "remote_provisioning.enable_rkpd": "true",
    "remote_provisioning.hostname": "remoteprovisioning.googleapis.com",
    "remote_provisioning.connect_timeout_millis": "2000",
    "remote_provisioning.strongbox.rkp_only": "true",
    "avf.remote_attestation.enabled": "true",
    "vendor.keymint.retry_timer": "5",
}

# These values differ between stock projects, or have not been proven for every
# consumer of this common tree. They must stay in a project carrier so an
# unknown project cannot inherit a permissive common default.
PROJECT_SCOPED_PROPERTIES = {
    "remote_provisioning.tee.rkp_only",
    "ro.strongbox.manufacturer",
    "ro.strongbox.model",
    "ro.vendor.oplus.provision.pki",
    "sys.oplus.ifaa.model",
    "vendor.wv.oemcrypto.debug.enable_prov40",
}


def read_properties(path: pathlib.Path) -> dict[str, str]:
    properties: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in properties:
            raise AssertionError(f"duplicate property {key} in {path.name}")
        properties[key] = value
    return properties


class SecurityPropertyPolicyTest(unittest.TestCase):
    by_partition: ClassVar[dict[str, dict[str, str]]]
    resolved: ClassVar[dict[str, str]]

    @classmethod
    @override
    def setUpClass(cls):
        cls.by_partition = {
            name: read_properties(DEVICE_DIR / name) for name in PROPERTY_FILES
        }
        cls.resolved = {
            key: value
            for properties in cls.by_partition.values()
            for key, value in properties.items()
        }

    def test_common_rkpd_avf_and_keymint_policy_resolves_exact_values(self):
        self.assertEqual(
            COMMON_POLICY,
            {key: self.resolved.get(key) for key in COMMON_POLICY},
        )

    def test_common_policy_has_one_property_owner(self):
        for key in COMMON_POLICY:
            owners = [
                name for name, properties in self.by_partition.items() if key in properties
            ]
            self.assertEqual(1, len(owners), f"{key} owners: {owners}")

    def test_unknown_project_does_not_inherit_project_scoped_policy(self):
        inherited = PROJECT_SCOPED_PROPERTIES.intersection(self.resolved)
        self.assertEqual(set(), inherited)

    def test_existing_generic_rkpd_properties_are_positive_controls(self):
        product = self.by_partition["product.prop"]
        self.assertEqual("true", product["remote_provisioning.enable_rkpd"])
        self.assertEqual(
            "remoteprovisioning.googleapis.com",
            product["remote_provisioning.hostname"],
        )
        self.assertEqual(
            "2000", product["remote_provisioning.connect_timeout_millis"]
        )


if __name__ == "__main__":
    _ = unittest.main()
