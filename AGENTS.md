# PROJECT KNOWLEDGE BASE
**Project:** android_device_oneplus_sm8850-common
**Seeded-at-ref:** oneplus/lineage-23.2
**Seeded-at-oid:** 0522cdc6164beb97711abc6f367032b021b5ca07
**Seeded-at-date:** 2026-08-14
**Generated-policy-sha256:** 831fceec497e89cad3d18f57f71d7d9fbc2bf2498062efbc079821f326bd17f0

## UPSTREAM DISTILLATION

### Scope and ownership

This tree composes shared SM8850 OnePlus product policy for phone and tablet variants. It owns common board/product declarations, init selection, VINTF fragments, shared overlays, radio database assets, and device-facing Soong knobs. It is a consumer of audio, display, power, health, touch, IR, security, and other HAL implementations; those implementations remain in their hardware projects.

### Build graph and layout

- `common.mk` is the central product graph and inherits QCOM common plus A/B product definitions. Keep package and copy-file groups subsystem-labelled.
- `BoardConfigCommon.mk` defines board, partition, kernel, and sepolicy inputs.
- Root `Android.bp` exports the namespace. `init/Android.bp` builds init and fstab modules; `qcril-database/Android.bp` and its config graph own radio DB packaging; each overlay has a local `Android.bp`.
- `init/init_oplus.cpp` is the vendor-init implementation selected through `soong_config_set(libinit,vendor_init_lib,...)`; adjacent rc/shell/fstab files are boot-critical inputs.
- `vintf/` contains common device manifest fragments. A declaration here must match the service package selected in `common.mk` and its owner project.
- `configs/` carries audio and permission data. `overlay/` and `overlay-lineage/` alter framework/Lineage resource defaults.
- `proprietary-files*.txt`, extraction scripts, and generated `vendor/oneplus/sm8850-common` output form a paired extraction boundary.

### HAL, interface, and sepolicy boundaries

The base has no locally defined AIDL/HIDL API. `common.mk` selects standard or Lineage services including audio, Bluetooth audio, boot, camera provider, health, Lineage health, LiveDisplay, IR, and device-specific apps. The VINTF files declare consumed services; do not implement APIs in this configuration tree. SePolicy inputs are wired by `BoardConfigCommon.mk`; policy belongs at the narrowest device/vendor implementation boundary and must accompany any new init/VINTF service.

### Extension precedents

Prefer established typed Soong knobs (`lineage_health`, `libinit`, and owner-specific HAL namespaces), package selection, and resource overlays. `common.mk` demonstrates the crDroid/Lineage pattern: expose a standard or Lineage service and configure it here, rather than publishing Oplus IDs, sysfs paths, or opaque vendor calls to apps.

### Conventions and verification

Upstream subjects use `sm8850-common: <imperative description>` with scoped forms such as `sm8850-common: init: ...`. Preserve SPDX headers and sorted, backslash-continued lists. Boot changes require graph, init, VINTF, and policy review together; overlay changes require checking target package and resource existence; proprietary list changes require regeneration of the paired blob tree rather than editing generated payload bytes.

## OUR DELTAS

None at seed. Later entries must name topic commit OIDs and must not rewrite upstream truth.
