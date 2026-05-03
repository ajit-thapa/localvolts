"""Constants for Localvolts Energy Monitor."""

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

ENTITY_PREFIX = "LV "

# Sensor definitions: (api_key, name, unit, device_class, conversion_factor)
# conversion_factor multiplies raw API value (cents, Wh, etc.) into display unit ($, kWh, etc.)
SENSOR_DEFINITIONS = [
    # Flex pricing
    ("earningsFlexUp", "Export Price (flex up)", "$/kWh", None, 0.01),
    ("earningsFlexDown", "Export Price (flex down)", "$/kWh", None, 0.01),
    ("costsFlexUp", "Import Cost (flex up)", "$/kWh", None, 0.01),
    ("costsFlexDown", "Import Cost (flex down)", "$/kWh", None, 0.01),
    # Demand
    ("demandMain", "Peak Demand", "kW", None, 1),
    # Energy totals
    ("exportsAll", "Total Exports", "kWh", None, 0.001),
    ("importsAll", "Total Imports", "kWh", None, 0.001),
    # Earnings & Costs
    ("earningsAll", "Total Earnings", "$", None, 0.01),
    ("earningsAllVar", "Variable Earnings", "$", None, 0.01),
    ("earningsAllFixed", "Fixed Earnings", "$", None, 0.01),
    ("costsAll", "Total Costs", "$", None, 0.01),
    ("costsAllVar", "Variable Costs", "$", None, 0.01),
    ("costsAllFixed", "Fixed Costs", "$", None, 0.01),
    # Rates
    ("earningsAllVarRate", "Variable Export Rate", "$/kWh", None, 0.01),
    ("costsAllVarRate", "Variable Import Rate", "$/kWh", None, 0.01),
    # Emissions
    ("exportsAllEmissions", "Export Emissions", "gCO2e", None, 1),
    ("importsAllEmissions", "Import Emissions", "gCO2e", None, 1),
    # Green energy share
    ("exportsAllZeroEE", "Export Renewables %", "%", None, 1),
    ("importsAllZeroEE", "Import Renewables %", "%", None, 1),
]
