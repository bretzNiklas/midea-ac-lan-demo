# Midea AC LAN Demo

Minimal Python demo for controlling a Midea-compatible AC over LAN with `msmart-ng`.

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

Set your local values before running commands:

```powershell
$env:MIDEA_HOST = ""
$env:MIDEA_DEVICE_ID = ""
$env:MIDEA_TOKEN = ""
$env:MIDEA_KEY = ""
```

The script also supports:

```powershell
python .\midea_lan_demo.py status --host ""
```

If `controller_state.json` exists, the script can read cached local credentials from it. Keep that file local only.

## Privacy

The demo source does not include device IDs, LAN addresses, serial numbers, tokens, or keys. Printed device state blanks common identifying fields before writing JSON output.
