# android_device_oneplus_sm8850-common — agent carrier

<!-- rom-ops:carrier
project = "android_device_oneplus_sm8850-common"
seeded_at_ref = "oneplus/lineage-23.2"
seeded_at_oid = "0522cdc6164beb97711abc6f367032b021b5ca07"
date = "2026-08-15"
-->

## Upstream distillation

### Scope and placement

- This is the shared OnePlus SM8850/canoe board layer, not a selectable product: the pinned tree has no `AndroidProducts.mk`, product identity makefile, or `vendorsetup.sh`. A per-device tree is expected to include `BoardConfigCommon.mk` and inherit `common.mk`.
- Put a change here only when it is true for every consumer of the SM8850 common tree. Shared canoe architecture, partition/boot policy, Qualcomm and OPlus HAL wiring, common init and uevent behavior, common radio/audio/display properties, common overlays, common extraction rules, and shared phone-vs-tablet conditionals belong here.
- Keep model identity, product declarations, model-specific partition geometry (notably the `BOARD_SUPER_PARTITION_SIZE` consumed but not assigned in `BoardConfigCommon.mk`), panel/camera/sensor variants, and blobs or policy needed by only one product in that product's device tree. `common.mk` deliberately guards phone-only features with `TARGET_IS_TABLET`, and `extract-files.py` applies `proprietary-files-phone.txt` only when that variable is not `true`; do not defeat those boundaries by making a product exception common.
- `lineage.dependencies` names the source dependencies at `hardware/oplus`, `kernel/oneplus/sm8850`, `kernel/oneplus/sm8850-devicetrees`, and `kernel/oneplus/sm8850-modules`. `Android.bp` opens the local Soong namespace; `common.mk` also exposes `hardware/oplus`.
- Proprietary inventory is split between `proprietary-files.txt` (common) and `proprietary-files-phone.txt` (non-tablet). `extract-files.py` owns blob/library fixups and imports namespaces for this tree, OPlus, QCOM SM8850/WLAN, display, and data services; `setup-makefiles.py` regenerates makefiles through it.

### Board and product graph

- `BoardConfigCommon.mk` is the board half. It defines arm64/Oryon architecture, canoe boot configuration, boot/init-boot header v4, 4 KiB kernel pages, source-kernel and external-module wiring (unless `USE_PREBUILT_KERNEL=true`), dynamic partitions and filesystem types, A/B OTA partitions, recovery, AVB chains, WLAN, and property-file inputs. It finishes by including `vendor/oneplus/sm8850-common/BoardConfigVendor.mk`.
- The board uses GKI and, for source builds, `kernel/oneplus/sm8850` plus modules under `kernel/oneplus/sm8850-modules`; module load/block lists are read from those trees. `config.fs` supplies vendor AIDs and executable/file capabilities for security, Bluetooth, radio, diagnostics, firmware, and daemon paths.
- `common.mk` is the product half. Its inheritance chain is `hardware/qcom-caf/common/common.mk`, virtual A/B with vendor ramdisk, generic ramdisk, emulated storage, the Virtualization APEX package set, conditionally `hardware/oplus/oplus-fwk/oplus-fwk.mk`, and finally generated `vendor/oneplus/sm8850-common/sm8850-common-vendor.mk`.
- `common.mk` installs shared audio, Bluetooth, boot-control, camera, DRM, fastboot, health, IR, KeyMint, Lineage health/LiveDisplay/touch, memtrack, NFC/SE, power, QSPA, sensors, telephony, thermal, USB, Wi-Fi, update-engine, mount-point, and virtualization packages and permissions. Phone-only branches cover context hub, Doze, fingerprint, GPS, IR, NFC/SE, proximity, telephony, touch, and vibrator behavior.
- The A/B postinstall graph runs `otapreopt_script` on system, `checkpoint_gc` on vendor, and mandatory `xbl_config_arb_check` on ODM. `PRODUCT_BUILD_PVMFW_IMAGE` and dynamic partitions are enabled. `init/fstab.qcom` mounts logical system/product/vendor partitions, metadata and encrypted F2FS userdata, OPlus reserve/persist, removable storage, and modem/DSP/Bluetooth/QMCS/SPU/SoCCP firmware; `init/charger_fstab.qcom` limits charger-mode mounts to SoCCP and modem firmware.
- Source modules local to this tree are defined under `init/Android.bp` (vendor-init library, rc/fstab prebuilts, and shell binaries), `qcril-database/Android.bp` plus `qcril-database/config/Android.bp` (generated `qcrilNr.db` and SQL upgrade), and each RRO's `Android.bp`. `touch/include/TouchscreenGestureConfig.h` is exported to the OPlus Lineage touch HAL through a Soong config variable.

### Overlays

- `overlay-lineage/` is a compile-time overlay root added through `DEVICE_PACKAGE_OVERLAYS`: `frameworks/base/core/res/res/values/config.xml` requires proximity checking for long-press doze; `lineage-sdk/lineage/res/res/values/config.xml` enables wake proximity checks, high-aspect-ratio handling, assistant/volume hardware and wake keys (`72`), and recovery/bootloader/fastboot restart actions; `packages/apps/Settings/res/values/config.xml` exposes battery cycle count and peak-refresh settings.
- `overlay/CarrierConfigResCommon` is a product RRO for `com.android.carrierconfig` (priority 200); its `res/xml/vendor.xml` carries common APN, RAT, roaming, carrier, emergency-number, and signal-threshold policy. It is installed only for non-tablets.
- `overlay/FrameworksResTargetCommon` is a vendor `android` RRO (priority 250) for navigation-bar, suspend/audio-jack, and pinner policy. `overlay/FrameworksResTargetPhone` is the non-tablet vendor `android` RRO for AOD and QTI IWLAN service package selection.
- `overlay/OPlusFrameworksResCommon`, `overlay/OPlusSettingsResCommon`, and `overlay/OPlusSystemUIResCommon` are device-specific priority-300 RROs targeting `android`, Settings, and SystemUI. They carry shared OPlus haptics/lid/proximity, safe-volume, eUICC/5G/slot, DT2W, pinner and 120 Hz peak-refresh defaults; network scan timeout; and keyguard/vibration behavior. MCC/MNC resource directories under `OPlusFrameworksResCommon` provide Verizon-family MMS UA values.
- `overlay/OplusDozeResCommon` is a system-ext priority-300 OplusDoze RRO selecting the tilt detector. `overlay/SecureElement` is a non-tablet vendor priority-500 `com.android.se` RRO enabling VINTF-backed SE. `overlay/WifiResTarget` is a vendor priority-250 Wi-Fi customization RRO enabling 6 GHz/11ax, beamforming, partial scan, and restricted multi-STA policy.
- `common.mk` additionally inherits generic and QSSI overlays from `hardware/oplus/overlay`, enforces all RRO targets, and packages external `NcmTetheringOverlay` alongside the local modules.

### SELinux policy

- The pinned tree has no local `sepolicy/` directory and therefore declares no local SELinux domains, types, or contexts. Do not infer current-tree policy into this baseline.
- Its entire explicit policy graph is in `BoardConfigCommon.mk`: `device/qcom/sepolicy_vndr/SEPolicy.mk` and `hardware/oplus/sepolicy/qti/SEPolicy.mk`. A genuinely common SM8850 rule would need a common policy directory wired here; product- or subsystem-specific policy belongs at its narrow owning layer.
- SELinux labels referenced by local mount and uevent configuration (for example `firmware_file`, `bt_firmware_file`, `vendor_qmcs_file`, `vendor_spunvm_file`, and `vendor_soccp_file` in `init/fstab.qcom`) are supplied by those external/vendor policy sources, not declared locally.

### Init, recovery, and uevent behavior

- `init/init_oplus.cpp` builds `libinit_oplus`; `common.mk` selects it as the vendor-init library. It maps kernel `oplus_region` IDs 27/68/151/161/167 to `IN`/`EU`/`CN`/`NA`/`ROW` in `ro.boot.hardware.revision`.
- `init/init.qcom.rc` is the vendor hardware entry point. It imports QTI UFS, USB, test, target, and factory rc files and handles early boot, MTE, post-fs/data setup, subsystem restart/ramdump controls, radio, Wi-Fi, CHRE, GPU/media properties, charger behavior, and class scripts. It declares these services: `nqnfcinfo`, `iop`, `qcomsysd`, `vendor.ssr_setup`, `vendor.ss_ramdump`, `qcom-c_core-sh`, `qcom-c_main-sh`, `irsc_util`, `qmiproxy`, `ptt_socket_app`, `ptt_ffbm`, `wifi_ftmd`, `cnss-daemon`, `ssgqmigd`, `mlid`, `qcom-sh`, `qcom-post-boot`, `qti-testscripts`, `wifi-sdio-on`, `wifi-crda`, `qvop-daemon`, `vendor.atfwd`, `hostapd_fst`, `battery_monitor`, `vendor.ril-daemon2`, `vendor.ril-daemon3`, `profiler_daemon`, `vendor.ssr_diag`, `diag_mdlog_start`, `diag_mdlog_stop`, `vm_bms`, three `vendor.msm_irqbalance` variants, `vendor.LKCore-dbg`, `vendor.LKCore-rel`, `qseeproxydaemon`, `esepmdaemon`, `poweroffhandler`, `vendor.power_off_alarm`, `vendor.hbtp`, `chre`, and `bugreport`.
- `init/init.target.rc` imports `init.qti.kernel.rc`, drives fstab stages, persist setup, WLAN calibration, camera/audio cpusets, trusted-touch/hypervisor permissions, charger startup, PCIe boot options, and remoteproc shutdown. Its declared services are `vendor.pd_mapper`, `vendor.per_mgr`, disabled `vendor.per_proxy` (started when the manager runs), and one-shot `vendor.cnss_diag`.
- `init/init.oplus.rc` creates ADSP dump storage, grants Audio HAL feedback access, mirrors project name and serial boot properties, and installs the Widevine license after boot. It declares no service. `init/init.qcom.recovery.rc` configures recovery backlight/USB, firmware mounting, ADSP boot, and fastbootd cleanup; it also declares no service.
- `init/init.class_main.sh`, `init/init.qcom.sh`, `init/init.qcom.early_boot.sh`, `init/init.qcom.post_boot.sh`, and `init/init.kernel.post_boot-memory.sh` provide QCOM class setup, modem-config/RIL completion and printk policy, density/permissions, platform post-boot tuning, and zram/read-ahead/THP/VM memory tuning. Their install definitions are in `init/Android.bp`.
- `init/ueventd.qcom.rc` is the broad QCOM device/sysfs ownership map and firmware search path; `init/ueventd.oplus.rc` adds OPlus ADF, camera, charging, display firmware, DDR, and reserve-node handling. Both install as partition-specific `ueventd.rc` files. Keep a node rule at the narrowest layer matching the hardware that actually exposes it.

### VINTF and properties

- `common.mk` uses `vintf/manifest_canoe.xml` as the device manifest; at target level `202504` it is intentionally empty and acts as the canoe manifest anchor. Framework compatibility comes from `hardware/oplus/vintf/device_framework_matrix.xml` and `hardware/qcom-caf/common/vendor_framework_compatibility_matrix.xml`; the device matrix is `hardware/qcom-caf/common/compatibility_matrix_aidl.xml`.
- For non-tablets, `vintf/network_manifest.xml` adds dual-slot AIDL Android radio data/messaging/modem/network/SAP/SIM/voice plus QTI data, IWLAN, IMS, LPA, OEM hook, QTI radio, UIM, and remote-UIM interfaces. `vintf/network_manifest_odm.xml`, installed through `ODM_MANIFEST_FILES`, adds dual-instance OPlus app-radio, IMS, radio, and subsystem-radio HALs.
- `BoardConfigCommon.mk` routes `odm.prop`, `product.prop`, `system_ext.prop`, and `vendor.prop` to their matching partitions. Preserve that ownership: do not move a property merely to make it visible sooner.
- `odm.prop` holds OPlus audio/engineering/FTM, radio carrier/virtual communication, and stock SVN (`49`) values. `product.prop` holds framework-facing audio, Bluetooth vendor ID, and Assistant model ID. `system_ext.prop` covers framework-side audio/Bluetooth, CNE/DPM, brightness, GPS/Horae, IMS, media, rmnet/data, dual-SIM telephony, sensors, and QTI voice-assistant support.
- `vendor.prop` is the hardware-facing bulk: AIDL audio and codecs, Bluetooth profiles/offload, camera, canoe board identity, crypto, display/HWC, DRM, graphics/SurfaceFlinger/Vulkan, media, MTE, performance, radio/RCS, secure processor, sensors, USB/UVC, VM, Widevine, Wi-Fi, and zygote policy. Notable shared contracts include `ro.hardware.camera=oemlayer.v2`, `ro.vendor.board.family=f-canoe`, 165-fps SurfaceFlinger game override, dual-SIM defaults, and USB controller `a600000.dwc3`.

### Upstream commit conventions

- The pinned history overwhelmingly uses `sm8850-common: <imperative description>`; subsystem-scoped subjects add another token, for example `sm8850-common: init: ...`, `overlay: ...`, or `audio: ...`. Preserve that prefix and use the narrow subsystem when it improves searchability.
- Subjects are concise action statements such as `Build`, `Set`, `Drop`, `Switch`, `Update`, `Restore`, or `Decommonize`; stock refreshes use `sm8850-common: Update from OOS <version>`. Reverts retain Git's `Revert "..."` form.
- The 20 commits ending at the pin all carry a Gerrit `Change-Id:` trailer. Keep commits single-purpose and retain that trailer convention; do not combine extraction refreshes, init behavior, overlays, and unrelated policy in one change.

## Our deltas

Against `0522cdc6164beb97711abc6f367032b021b5ca07`, the topic tree adds the following grouped changes:

- Camera/display integration: `BoardConfigCommon.mk` optionally includes the camera-port board flags; `common.mk` enables DeviceAsWebcam, camera timestamp compatibility, the OPlus UDFPS SurfaceFlinger hook, LiveDisplay anti-flicker/display modes, and `folio-daemon`. `overlay/DeviceAsWebcamResTarget/` ignores `/dev/video0` and `/dev/video1`, while the common OPlus framework peak-refresh cap rises from 120 to 165 Hz. `init/init.target.rc` grants system access to the ADFR sysfs control.
- Media/audio/security features: Dolby Vision properties, extraction fixups, payloads, an optional framework matrix declaration, and the new `dvs_aidl_default` SELinux domain/service are added. AudioX is selected through `product.prop`/`vendor.prop`; remote key provisioning is enabled; duplicate dynamic-head-tracker permission copying is removed. `init/init.qcom.rc` now propagates the media profile variant.
- Local policy now exists at `sepolicy/vendor/`, wired by `BOARD_VENDOR_SEPOLICY_DIRS`: besides the Dolby DVS domain/types/contexts it grants GameBar stats reads, fsck access to custom A/B block devices, and `vendor_qms` access to the SSR property.
- Product/runtime support: `common.mk` declares a 4096-byte maximum page size, installs `oplus_radio_probe` on debug builds, and installs `keylayout/touchpanel.kl` for wake/power/sleep events. `overlay-lineage/packages/apps/Settings/res/xml/satellite_settings_apps_list.xml` restores the Settings search-index resource expected by the app.
- Extraction changes add Dolby Vision, display, ShareBuffer, sensor, charger, radio, and related closure pieces; patch OxygenOS-only `/my_product` and `/my_bigball` paths; enforce key 735 as `ASSIST`; and remove source-replaced or camera-port-owned duplicate display, FIDO, cryptoeng, and VINTF payloads. The final net diff modifies both proprietary lists and substantially extends `extract-files.py`.

## Known defects

### DEF-PAIR-01 — declared AudioX effect proxy was absent
The common proprietary list declared `vendor/lib64/soundfx/libeffectproxy.so` while the paired vendor repository carried no payload, leaving the configured spatializer without its backing effect. Done means the declaration, payload, generated module, and package row all agree and declaration coherence passes. See `docs/history/DEFECTS-2026-08.md` for the full investigation.

### DEF-RRO-01 — a device overlay referenced a private Settings resource
The satellite Settings overlay failed at Ninja because its RRO-local `@string/title_satellite_supported_app_list_page` could not resolve, while qualifying the target resource exposed its private visibility. Done means the dependency is fixed in the Settings app and this overlay copy is removed, preserving all localized target strings. See `docs/history/DEFECTS-2026-08.md` for the full investigation.

## Owner rulings

### Select one principal vibrator (2026-08-13)
Common product composition must preserve our standard vibrator as the sole principal writer. OPLUS linear-motor compatibility is only a named camera/gallery re-stub and cannot become a second product API. See `docs/history/DIRECTIVES-2026-08.md`.
