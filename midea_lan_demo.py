from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from msmart.discover import Discover
from msmart.device import AirConditioner as AC
from msmart.lan import AuthenticationError, ProtocolError


DEFAULT_HOST = ""
PERSONAL_FIELDS = {"id", "ip", "name", "sn", "token", "key"}


def env(name: str) -> str | None:
    return os.environ.get(name) or None


async def connect_ac(host: str) -> AC:
    if not host:
        raise RuntimeError("Set --host or MIDEA_HOST.")

    try:
        # Same path used by the larger controller and msmart-ng CLI auto mode.
        # msmart-ng discovers the device, gets the LAN token/key through its
        # built-in generic NetHomePlus cloud flow, authenticates, then refreshes.
        device = await Discover.discover_single(host)
    except (AuthenticationError, ProtocolError) as exc:
        raise RuntimeError(
            "Generic msmart-ng discovery/authentication failed for this host."
        ) from exc

    if device is None:
        raise RuntimeError(f"No Midea device found at {host}")
    if not isinstance(device, AC):
        raise RuntimeError(f"Device at {host} is not an air conditioner")
    await device.refresh()
    return device


def redact(data: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(data)
    for key in PERSONAL_FIELDS:
        if key in redacted:
            redacted[key] = ""
    return redacted


def fan_speed(name: str) -> AC.FanSpeed:
    selected = name.upper()
    if selected not in AC.FanSpeed.__members__:
        valid = ", ".join(sorted(AC.FanSpeed.__members__))
        raise ValueError(f"Unsupported fan speed {name!r}. Valid values: {valid}")
    return AC.FanSpeed[selected]


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal Midea AC LAN control demo using msmart-ng."
    )
    parser.add_argument("action", choices=["status", "cool", "off"])
    parser.add_argument("--host", default=env("MIDEA_HOST") or DEFAULT_HOST)
    parser.add_argument("--target-c", type=float, default=22.0)
    parser.add_argument("--fan", default="LOW", help="Example: SILENT, LOW, MEDIUM, HIGH, AUTO")
    args = parser.parse_args()

    ac = await connect_ac(args.host)
    before = redact(ac.to_dict())

    if args.action == "cool":
        ac.power_state = True
        ac.operational_mode = AC.OperationalMode.COOL
        ac.target_temperature = args.target_c
        ac.fan_speed = fan_speed(args.fan)
        await ac.apply()
        await ac.refresh()
    elif args.action == "off":
        ac.power_state = False
        await ac.apply()
        await ac.refresh()

    print(json.dumps({"before": before, "after": redact(ac.to_dict())}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
