AshesOS — Master TODO Specification
0. Core Concept

AshesOS is a hypervisor‑first mobile OS for Google Pixel devices.
It provides isolated Boxes (VMs) that can run Android or Linux, each with configurable hardware and network permissions.
!!this should be able to be put on any pixel device, altho preferrably more compatibility on ANY grapheneOS or android phone with a single app or script to transform their phone!!
1. Base System
1.1 Hypervisor Layer

    Implement or integrate hypervisor at EL2 (pKVM or custom).

    Ensure support for:

        VM creation/destruction

        VM resource limits (CPU/RAM)

        Virtual NICs

        Virtual storage devices

        Virtual camera/USB interfaces

1.2 Control OS (dom0 equivalent)

    Build minimal OS responsible for:

        Boot menu

        Box management UI

        Permission enforcement

        Network routing

        Storage routing

        VM lifecycle control

1.3 Verified Boot

    Extend Pixel verified boot to:

        Validate hypervisor image

        Validate Control OS image

        Validate Box templates

2. Boot Flow
2.1 Boot Sequence

    Bootloader → Hypervisor → Control OS → Box Menu

2.2 Box Menu

    Display list of Boxes

    Options:

        Start Box

        Stop Box

        Create Box

        Delete Box

        Edit Box Permissions

3. Box System
3.1 Box Types

    Android Box

    Linux Box

    Disposable Box

3.2 Box Templates

    Personal Android

    Banking Android

    Work Android

    Dev Linux

    Disposable

3.3 Box Configuration Schema

Each Box must define:

    name

    os_type (android/linux)

    template

    cpu_limit

    ram_limit

    permissions (see section 4)

    storage_mounts

    network_profile

4. Permission System
4.1 Network Permissions

    internet

    2g

    3g

    4g

    5g

    sim_card_1

    sim_card_2

    wifi

    bluetooth

4.2 Hardware Permissions

    camera

    microphone

    usb

    nfc

    sensors (accelerometer, gyroscope, GPS)

4.3 Storage Permissions

    read/write specific folders

    read-only folders

    shared folders

    isolated storage

4.4 Enforcement

    All permissions enforced by Control OS

    Boxes receive only virtualized devices

    Network VM handles radio access

5. Networking Architecture
5.1 Network VM

    Owns:

        modem (2G/3G/4G/5G)

        VoLTE stack

        Wi‑Fi

        Bluetooth

    Provides virtual NICs to Boxes

    Enforces per-Box network policies

5.2 Routing

    NAT or direct passthrough depending on Box policy

    Optional VPN per Box

6. Storage Architecture
6.1 Storage VM

    Owns physical storage

    Exposes virtual volumes to Boxes

    Enforces:

        read-only

        read-write

        shared folders

        isolated volumes

7. UI System
7.1 Boot Menu UI

    List Boxes

    Buttons:

        Start

        Stop

        Edit

        Delete

        Create

7.2 Box Creation UI

    Choose OS type

    Choose template

    Set name

    Set CPU/RAM limits

    Configure permissions

7.3 Box Permission Editor

    Toggle hardware/network/storage permissions

8. OS Images
8.1 Android Guest Image

    Based on GrapheneOS or AOSP

    Must support:

        running inside VM

        virtual NIC

        virtual camera

        virtual storage

8.2 Linux Guest Image

    Minimal distro (Alpine, Debian, Arch)

    VM‑friendly kernel

8.3 Disposable Image

    Stateless template

    Auto‑destroy on exit

9. Developer Tools
9.1 Box Manager CLI

Commands:

    ashes box create

    ashes box delete

    ashes box start

    ashes box stop

    ashes box edit

    ashes box list

9.2 Logs

    Hypervisor logs

    Control OS logs

    Box logs

10. Security Requirements
10.1 Isolation

    Boxes cannot access each other’s memory

    Boxes cannot access hardware directly

    All hardware mediated by Control OS

10.2 Integrity

    Signed Box templates

    Signed hypervisor

    Signed Control OS

10.3 Networking

    No Box can bypass Network VM

11. Milestones
Phase 1 — Foundation

    Hypervisor booting

    Control OS running

    Basic Box creation

    Android guest booting

Phase 2 — Networking

    Network VM functional

    Virtual NICs working

    Per-Box network policies

Phase 3 — Storage

    Storage VM functional

    Virtual volumes working

Phase 4 — Permissions

    Hardware permissions enforced

    Camera/mic/USB virtualization

Phase 5 — UI

    Full Box Manager UI

Phase 6 — Templates

    Android templates

    Linux templates

    Disposable templates

Phase 7 — Polishing

    Performance tuning

    Battery optimization

    Security audits
