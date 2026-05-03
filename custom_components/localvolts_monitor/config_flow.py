"""Config flow for Localvolts Energy Monitor."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_API_KEY, CONF_PARTNER_ID, CONF_NMI_ID
from . import validate_api_key, validate_partner_id, validate_nmi_id

_LOGGER = logging.getLogger(__name__)


def build_data_schema(existing_data):
    return vol.Schema({
        vol.Required(CONF_API_KEY, default=existing_data.get(CONF_API_KEY, "")): cv.string,
        vol.Required(CONF_PARTNER_ID, default=existing_data.get(CONF_PARTNER_ID, "")): cv.string,
        vol.Required(CONF_NMI_ID, default=existing_data.get(CONF_NMI_ID, "")): cv.string,
    })


class LocalvoltsMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        existing_entry = next(iter(self._async_current_entries()), None)
        existing_data = existing_entry.data if existing_entry else {}

        if user_input is not None:
            if not validate_api_key(user_input[CONF_API_KEY]):
                errors[CONF_API_KEY] = "invalid_api_key"
            elif not validate_partner_id(user_input[CONF_PARTNER_ID]):
                errors[CONF_PARTNER_ID] = "invalid_partner_id"
            elif not validate_nmi_id(user_input[CONF_NMI_ID]):
                errors[CONF_NMI_ID] = "invalid_nmi_id"

            if not errors:
                title = f"Localvolts NMI {user_input[CONF_NMI_ID]}"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=build_data_schema(existing_data), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return LocalvoltsMonitorOptionsFlowHandler(config_entry)


class LocalvoltsMonitorOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options = self.config_entry.options
        return self.async_show_form(
            step_id="user", data_schema=build_data_schema(options), errors=errors
        )
