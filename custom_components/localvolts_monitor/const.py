"""Constants for Localvolt HA Integration."""

DOMAIN = "localvolts_monitor"


def validate_api_key(key: str) -> bool:
    return bool(key.strip())


def validate_partner_id(pid: str) -> bool:
    return bool(pid.strip())


def validate_nmi_id(nmi: str) -> bool:
    nmi = nmi.strip().upper()
    return len(nmi) == 10 and nmi.isalnum()


CONF_API_KEY = "api_key"
CONF_PARTNER_ID = "partner_id"
CONF_NMI_ID = "nmi_id"

# Sensor definitions: (api_key, name_suffix, unit, device_class, conversion_factor, icon)
SENSOR_DEFINITIONS = [
    # Flex pricing
    ("earningsFlexUp", "Export Price (flex up)", "$/kWh", None, 0.01, "mdi:cash-plus"),
    ("earningsFlexDown", "Export Price (flex down)", "$/kWh", None, 0.01, "mdi:cash-minus"),
    ("costsFlexUp", "Import Cost (flex up)", "$/kWh", None, 0.01, "mdi:cash-plus"),
    ("costsFlexDown", "Import Cost (flex down)", "$/kWh", None, 0.01, "mdi:cash-minus"),
    # Demand
    ("demandMain", "Peak Demand", "kW", None, 1, "mdi:flash"),
    # Energy totals
    ("exportsAll", "Total Exports", "kWh", None, 0.001, "mdi:transmission-tower-export"),
    ("importsAll", "Total Imports", "kWh", None, 0.001, "mdi:transmission-tower-import"),
    # Earnings & Costs
    ("earningsAll", "Total Earnings", "$", None, 0.01, "mdi:cash-multiple"),
    ("earningsAllVar", "Variable Earnings", "$", None, 0.01, "mdi:cash-multiple"),
    ("earningsAllFixed", "Fixed Earnings", "$", None, 0.01, "mdi:cash-lock"),
    ("costsAll", "Total Costs", "$", None, 0.01, "mdi:cash-multiple"),
    ("costsAllVar", "Variable Costs", "$", None, 0.01, "mdi:cash-multiple"),
    ("costsAllFixed", "Fixed Costs", "$", None, 0.01, "mdi:cash-lock"),
    # Rates
    ("earningsAllVarRate", "Variable Export Rate", "$/kWh", None, 0.01, "mdi:currency-usd"),
    ("costsAllVarRate", "Variable Import Rate", "$/kWh", None, 0.01, "mdi:currency-usd"),
    # Emissions
    ("exportsAllEmissions", "Export Emissions", "gCO2e", None, 1, "mdi:leaf"),
    ("importsAllEmissions", "Import Emissions", "gCO2e", None, 1, "mdi:leaf"),
    # Green energy share
    ("exportsAllZeroEE", "Export Renewables %", "%", None, 1, "mdi:wind-power"),
    ("importsAllZeroEE", "Import Renewables %", "%", None, 1, "mdi:wind-power"),
]
