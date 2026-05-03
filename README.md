# Localvolts Energy Monitor for Home Assistant

Real-time energy pricing, emissions, and interval data from your Localvolts electricity plan – directly inside Home Assistant.

This integration creates 22 sensors grouped under a single device, giving you live import/export costs, demand, emissions, and data quality for your NMI. You can use these sensors to automate batteries, EV charging, or simply monitor your electricity rates.

---

## Features

- **Flex pricing:** Live export and import prices per kWh (up & down flex)
- **Demand monitoring:** Peak demand used for network charges
- **Energy totals:** Exports, imports, earnings, and costs per 5‑minute interval
- **Variable & fixed components:** See how your bill is built up
- **Emissions & renewables:** CO₂e and zero‑emission energy percentages
- **Data quality:** Know whether the data is `Act`(ual), `Exp`(ected), or `Fcst`(forecast)
- **Automatic polling** every 20 seconds

All sensors are prefixed with `LV` and appear under one device named **Localvolts NMI xxxx**.

---

## Requirements

- An active account with [Localvolts](https://localvolts.com) (Australian electricity retailer)
- API key, Partner ID, and NMI ID (request from Localvolts)
- Home Assistant 2023.12 or newer

---

## Installation

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/localvolts_monitor` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

### HACS (coming soon)

(Once available, you will be able to add this repository as a custom integration in HACS.)

---

## Configuration

After installation, add the integration via the Home Assistant UI:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Localvolts Energy Monitor**.
3. Enter your **API Key**, **Partner ID**, and **NMI ID** (10‑character identifier, without checksum).

The integration will validate your inputs and create all sensors automatically.

---

## Sensors

| Sensor name                          | Description                                            | Unit        |
|--------------------------------------|--------------------------------------------------------|-------------|
| `LV Export Price (flex up)`          | Extra earnings per kWh if you export more            | $/kWh       |
| `LV Export Price (flex down)`        | Earnings lost per kWh if you reduce exports          | $/kWh       |
| `LV Import Cost (flex up)`           | Extra cost per kWh if you import more                | $/kWh       |
| `LV Import Cost (flex down)`         | Savings per kWh if you reduce imports                | $/kWh       |
| `LV Peak Demand`                     | Peak average demand over the demand window           | kW (or kVA) |
| `LV Total Exports`                   | Energy exported during the interval                  | kWh         |
| `LV Total Imports`                   | Energy imported during the interval                  | kWh         |
| `LV Total Earnings`                  | Total earnings in the interval                       | $           |
| `LV Variable Earnings`               | Variable portion of earnings                         | $           |
| `LV Fixed Earnings`                  | Fixed portion of earnings                            | $           |
| `LV Total Costs`                     | Total costs in the interval                          | $           |
| `LV Variable Costs`                  | Variable portion of costs                            | $           |
| `LV Fixed Costs`                     | Fixed portion of costs                               | $           |
| `LV Variable Export Rate`            | Variable earnings rate (N/A when no exports)         | $/kWh       |
| `LV Variable Import Rate`            | Variable cost rate (N/A when no imports)             | $/kWh       |
| `LV Export Emissions`                | Emissions associated with grid‑injected energy       | gCO₂e       |
| `LV Import Emissions`                | Emissions associated with energy drawn from the grid  | gCO₂e       |
| `LV Export Renewables %`             | Share of zero‑emission energy in exports             | %           |
| `LV Import Renewables %`             | Share of zero‑emission energy in imports             | %           |
| `LV Data Lag`                        | Seconds between interval start and last data refresh | s           |
| `LV Interval End`                    | UTC timestamp marking the end of the current interval| datetime    |
| `LV Last Update`                     | When the data was last fetched from Localvolts       | datetime    |
| `LV Data Quality`                    | `Act`, `Exp`, or `Fcst`                               | –           |

All sensors update every 20 seconds.

---

## Automation ideas

Charge a battery only when the export price is low and import cost is high:

```yaml
alias: "Battery charging on cheap import"
trigger:
  - platform: numeric_state
    entity_id: sensor.lv_import_cost_flex_up
    below: 0.15
condition:
  - condition: numeric_state
    entity_id: sensor.lv_data_quality
    state: "Exp"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.battery_charger
```

Avoid exporting when you'd lose money:

```yaml
alias: "Stop exporting when price negative"
trigger:
  - platform: numeric_state
    entity_id: sensor.lv_export_price_flex_up
    below: 0
action:
  - service: switch.turn_off
    target:
      entity_id: switch.grid_export
```

---

## Troubleshooting

### No sensors appear

- Verify your API key, Partner ID, and NMI are correct.
- Check Home Assistant logs for error messages – likely "Invalid API key (401)" or "Forbidden (403)".

### Sensors show "unknown"

- Wait up to 30 seconds after integration startup; the first data fetch might be delayed.
- Ensure your internet connection allows access to `api.localvolts.com`.

### Some sensors show 0 or N/A

- `Variable Export Rate` and `Variable Import Rate` become `unavailable` when there is no energy flow – this is normal.
- Historical data will only show `Act` quality; live data is usually `Exp`.

### Reconfiguration

Go to the integration's card in HA, click the three‑dot menu, and choose **Configure** to update your credentials.

---

## License

MIT (or your preferred license – please insert the appropriate license text)

---

## Credits

This integration is not affiliated with Localvolts Pty Ltd, but uses their public API.  
API documentation: [Localvolts API Guide](https://api.localvolts.com) (see table 5 for field details).
