"""Coordinator for Localvolts Energy Monitor."""
import datetime
import logging
from dateutil import parser, tz
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

import aiohttp

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(seconds=20)


class LocalvoltsMonitorCoordinator(DataUpdateCoordinator):
    """Manages fetching data from Localvolts API."""

    def __init__(
        self, hass: HomeAssistant, api_key: str, partner_id: str, nmi_id: str
    ) -> None:
        self.api_key = api_key
        self.partner_id = partner_id
        self.nmi_id = nmi_id
        self.interval_end: Optional[datetime.datetime] = None
        self.last_update: Optional[datetime.datetime] = None
        self.time_past_start: datetime.timedelta = datetime.timedelta(0)
        self.data: Dict[str, Any] = {}

        super().__init__(
            hass,
            _LOGGER,
            name="Localvolts Monitor",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        # Request the interval that is just starting (real-time data)
        from_time = now_utc
        to_time = now_utc + datetime.timedelta(minutes=5)

        url = (
            "https://api.localvolts.com/v1/customer/interval?"
            f"NMI={self.nmi_id}"
            f"&from={from_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            f"&to={to_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        headers = {
            "Authorization": f"apikey {self.api_key}",
            "partner": self.partner_id,
        }

        # Add a timeout to fail quickly if the server is unresponsive
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, headers=headers, timeout=timeout) as resp:
                if resp.status == 401:
                    raise UpdateFailed("Invalid API key (401)")
                if resp.status == 403:
                    raise UpdateFailed("Invalid Partner ID (403)")
                resp.raise_for_status()
                raw_data = await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"API communication error: {err}") from err

        if not isinstance(raw_data, list) or not raw_data:
            _LOGGER.warning("Empty response, keeping previous data")
            return self.data

        # Use the first (most relevant) interval returned
        self.data = raw_data[0]
        self._process_timestamps(self.data)
        return self.data

    def _process_timestamps(self, item: Dict[str, Any]) -> None:
        try:
            ie_str = item["intervalEnd"]
            lu_str = item["lastUpdate"]
            ie = parser.isoparse(ie_str)
            lu = parser.isoparse(lu_str)
            if ie.tzinfo is None:
                ie = ie.replace(tzinfo=tz.UTC)
            if lu.tzinfo is None:
                lu = lu.replace(tzinfo=tz.UTC)
            self.interval_end = ie
            self.last_update = lu
            interval_start = ie - datetime.timedelta(minutes=5)
            self.time_past_start = lu - interval_start
        except (KeyError, ValueError) as err:
            _LOGGER.error("Timestamp parsing error: %s", err)
