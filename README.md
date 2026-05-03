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

### HACS (Recommended)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

1. Make sure [HACS](https://hacs.xyz) is installed in your Home Assistant.
2. In the Home Assistant sidebar, go to **HACS**.
3. Click the **three dots** menu in the top right corner and select **Custom repositories**.
4. Paste the repository URL:  
   `https://github.com/ajit-thapa/localvolts`
5. Choose **Integration** as the category and click **Add**.
6. Still in HACS, search for "Localvolts Energy Monitor" and click **Download**.
7. Restart Home Assistant.

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/localvolts_monitor` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

---

## Configuration

After installation, add the integration via the Home Assistant UI:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Localvolts Energy Monitor**.
3. Enter your **API Key**, **Partner ID**, and **NMI ID** (10‑character identifier, without checksum).

The integration will validate your inputs and create all sensors automatically.

---

## Sensors

All sensors follow the pattern `sensor.nmi_<NMI_ID>_<sensor_key>`.  
Example for NMI `4103XXXXXX`:
- `sensor.nmi_4103xxxxxx_export_price_flex_up`
- `sensor.nmi_4103xxxxxx_data_lag`

| Sensor name (user‑friendly)                | Entity ID example (NMI=4103xxxxxx)                       | Description                                            | Unit        |
|--------------------------------------------|----------------------------------------------------------|--------------------------------------------------------|-------------|
| Export Price (flex up)           | `sensor.nmi_4103xxxxxx_export_price_flex_up`             | Extra earnings per kWh if you export more            | $/kWh       |
| Export Price (flex down)         | `sensor.nmi_4103xxxxxx_export_price_flex_down`           | Earnings lost per kWh if you reduce exports          | $/kWh       |
| Import Cost (flex up)            | `sensor.nmi_4103xxxxxx_import_cost_flex_up`              | Extra cost per kWh if you import more                | $/kWh       |
| Import Cost (flex down)          | `sensor.nmi_4103xxxxxx_import_cost_flex_down`            | Savings per kWh if you reduce imports                | $/kWh       |
| Peak Demand                      | `sensor.nmi_4103xxxxxx_peak_demand`                      | Peak average demand over the demand window           | kW (or kVA) |
| Total Exports                    | `sensor.nmi_4103xxxxxx_total_exports`                    | Energy exported during the interval                  | kWh         |
| Total Imports                    | `sensor.nmi_4103xxxxxx_total_imports`                    | Energy imported during the interval                  | kWh         |
| Total Earnings                   | `sensor.nmi_4103xxxxxx_total_earnings`                   | Total earnings in the interval                       | $           |
| Variable Earnings                | `sensor.nmi_4103xxxxxx_variable_earnings`                | Variable portion of earnings                         | $           |
| Fixed Earnings                   | `sensor.nmi_4103xxxxxx_fixed_earnings`                   | Fixed portion of earnings                            | $           |
| Total Costs                      | `sensor.nmi_4103xxxxxx_total_costs`                      | Total costs in the interval                          | $           |
| Variable Costs                   | `sensor.nmi_4103xxxxxx_variable_costs`                   | Variable portion of costs                            | $           |
| Fixed Costs                      | `sensor.nmi_4103xxxxxx_fixed_costs`                      | Fixed portion of costs                               | $           |
| Variable Export Rate             | `sensor.nmi_4103xxxxxx_variable_export_rate`             | Variable earnings rate (N/A when no exports)         | $/kWh       |
| Variable Import Rate             | `sensor.nmi_4103xxxxxx_variable_import_rate`             | Variable cost rate (N/A when no imports)             | $/kWh       |
| Export Emissions                 | `sensor.nmi_4103xxxxxx_export_emissions`                 | Emissions associated with grid‑injected energy       | gCO₂e       |
| Import Emissions                 | `sensor.nmi_4103xxxxxx_import_emissions`                 | Emissions associated with energy drawn from the grid  | gCO₂e       |
| Export Renewables %              | `sensor.nmi_4103xxxxxx_export_renewables_pct`            | Share of zero‑emission energy in exports             | %           |
| Import Renewables %              | `sensor.nmi_4103xxxxxx_import_renewables_pct`            | Share of zero‑emission energy in imports             | %           |
| Data Lag                         | `sensor.nmi_4103xxxxxx_data_lag`                         | Seconds between interval start and last data refresh | s           |
|  Interval End                     | `sensor.nmi_4103xxxxxx_interval_end`                     | UTC timestamp marking the end of the current interval| datetime    |
| Last Update                      | `sensor.nmi_4103xxxxxx_last_update`                      | When the data was last fetched from Localvolts       | datetime    |
| Data Quality                     | `sensor.nmi_4103xxxxxx_data_quality`                     | `Act`, `Exp`, or `Fcst`                               | –           |

All sensors update every 20 seconds.

---

## Automation ideas

Charge a battery only when the export price is low and import cost is high:

```yaml
alias: "Battery charging on cheap import"
trigger:
  - platform: numeric_state
    entity_id: sensor.nmi_4103xxxxxx_import_cost_flex_up
    below: 0.15
condition:
  - condition: numeric_state
    entity_id: sensor.nmi_4103xxxxxx_data_quality
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
    entity_id: sensor.nmi_4103xxxxxx_export_price_flex_up
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

MIT

---

## Credits

Original concept and initial codebase by [gurrier](https://github.com/gurrier).  
This rewrite is a community effort and is not affiliated with Localvolts Pty Ltd, but uses their public API.

API documentation: [Localvolts API Guide](https://api.localvolts.com) (see table 5 for field details).
