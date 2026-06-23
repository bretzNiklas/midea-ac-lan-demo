# Midea AC LAN Demo

Minimal Python demo for controlling a Midea-compatible AC over LAN with `msmart-ng`.

It uses the same generic `msmart-ng` discovery/authentication path as the larger controller: `msmart-ng` discovers the device, fetches the per-device LAN token/key through its built-in generic NetHomePlus cloud flow, authenticates locally, then sends commands over LAN.

The script supports three actions:

```powershell
python .\midea_lan_demo.py status
python .\midea_lan_demo.py cool --target-c 22 --fan LOW
python .\midea_lan_demo.py off
```

`status` only reads the device state. `cool` turns the AC on in cooling mode, sets the target temperature, and sets the fan speed. `off` turns the AC off.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Configure

Set your AC LAN host before running commands:

```powershell
$env:MIDEA_HOST = ""
```

The script also supports:

```powershell
python .\midea_lan_demo.py status --host ""
```

## Privacy

The demo source does not include device IDs, LAN addresses, serial numbers, tokens, or keys. Printed device state blanks common identifying fields before writing JSON output.
