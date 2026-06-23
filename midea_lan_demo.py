from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from msmart.base_device import Device
from msmart.const import DeviceType
from msmart.discover import Discover
from msmart.device import AirConditioner as AC
from msmart.lan import AuthenticationError


DEFAULT_HOST = ""
DEFAULT_DEVICE_ID = ""
DEFAULT_STATE_FILE = Path("controller_state.json")
PERSONAL_FIELDS = {"id", "ip", "name", "sn", "token", "key"}


def env(name: str) -> str | None:
    return os.environ.get(name) or None


def load_cached_credentials(state_file: Path, host: str) -> dict[str, Any] | None:
    if not state_file.exists():
        return None

    state = json.loads(state_file.read_text(encoding="utf-8"))
    cached = state.get("midea") or {}
    if host and cached.get("host") != host:
        return None
    if not (cached.get("id") and cached.get("token") and cached.get("key")):
        return None
    return cached


def load_env_credentials(host: str) -> dict[str, Any] | None:
    device_id = env("MIDEA_DEVICE_ID") or DEFAULT_DEVICE_ID
    token = env("MIDEA_TOKEN")
    key = env("MIDEA_KEY")

    if not (host and device_id and token and key):
        return None

    return {
        "host": host,
        "port": 6444,
        "id": int(device_id),
        "token": token,
        "key": key,
    }


async def connect_ac(host: str, state_file: Path) -> AC:
    credentials = load_cached_credentials(state_file, host) or load_env_credentials(host)
    if credentials:
        host = str(credentials["host"])
        device = Device.construct(
            type=DeviceType.AIR_CONDITIONER,
            ip=host,
            port=int(credentials.get("port", 6444)),
            device_id=int(credentials["id"]),
        )
        if not isinstance(device, AC):
            raise RuntimeError(f"Device at {host} is not an air conditioner")
        await device.authenticate(credentials["token"], credentials["key"])
        await device.refresh()
        return device

    if not host:
        raise RuntimeError("Set --host or MIDEA_HOST, or provide a controller_state.json cache.")

    try:
        device = await Discover.discover_single(host)
    except AuthenticationError as exc:
        raise RuntimeError(
            "No valid local token/key found. Set MIDEA_DEVICE_ID, MIDEA_TOKEN, "
            "and MIDEA_KEY, or run the full controller once so it can cache them."
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
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--target-c", type=float, default=22.0)
    parser.add_argument("--fan", default="LOW", help="Example: SILENT, LOW, MEDIUM, HIGH, AUTO")
    args = parser.parse_args()

    ac = await connect_ac(args.host, args.state_file)
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
