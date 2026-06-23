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

## Find `MIDEA_HOST`

`MIDEA_HOST` is the AC's local network IP address or hostname.

The easiest way is usually your router or Wi-Fi app. Open the connected devices, clients, or DHCP leases page and look for a Midea, NetHomePlus, MSmartHome, or AC-looking device. Use its IP address as `MIDEA_HOST`.

You can also use `msmart-ng` discovery after installing the requirements:

```powershell
.\.venv\Scripts\msmart-ng discover
```

Look for the `ip` field in the discovered device output.

If discovery does not show it, scan your local subnet for Midea's LAN port `6444`. Replace `<first-three-octets>` with your own subnet prefix:

```powershell
$prefix = "<first-three-octets>"
1..254 | ForEach-Object {
  $ip = "$prefix.$_"
  if (Test-NetConnection $ip -Port 6444 -InformationLevel Quiet) { $ip }
}
```

Then verify the candidate host:

```powershell
python .\midea_lan_demo.py status --host "<candidate-host>"
```

## Privacy

The demo source does not include device IDs, LAN addresses, serial numbers, tokens, or keys. Printed device state blanks common identifying fields before writing JSON output.
