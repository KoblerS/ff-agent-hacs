from datetime import timedelta
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import aiohttp

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class FFAgentDataCoordinator(DataUpdateCoordinator):
  """Koordinator für FF-Agent API."""

  def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
    self.hass = hass
    self.entry = entry
    self.username = entry.data["username"]
    self.access_token = entry.data["access_token"]

    super().__init__(
      hass,
      _LOGGER,
      name="FF-Agent Coordinator",
      update_interval=timedelta(seconds=30),
    )

  async def _async_update_data(self):
    """Hole Daten von der FF-Agent API."""
    url = f"{BASE_URL}/app/v8/MobileService/activeMissionStatus?includeInfo=1"
    headers = {
      "Authorization": f"ACCESS-TOKEN {self.access_token}",
      "Content-Type": "application/json",
    }

    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
          if resp.status != 200:
            raise UpdateFailed(f"Fehler beim Abruf der Daten: {resp.status}")
          return await resp.json()
    except Exception as e:
      raise UpdateFailed(f"API Fehler: {e}")
