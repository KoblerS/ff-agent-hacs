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
    headers = {
      "Authorization": f"ACCESS-TOKEN {self.access_token}",
      "Content-Type": "application/json",
    }

    try:
      async with aiohttp.ClientSession() as session:
        # Fetch active mission status
        status_url = f"{BASE_URL}/app/v8/MobileService/activeMissionStatus?includeInfo=1"
        async with session.get(status_url, headers=headers) as resp:
          if resp.status != 200:
            raise UpdateFailed(f"Fehler beim Abruf der Daten: {resp.status}")
          data = await resp.json()

        # Fetch mission alarms if there's an active mission
        missions = (data or {}).get("missionStatus", [])
        alarms = []
        if missions:
          mission_guid = missions[0].get("mission", {}).get("guid")
          if mission_guid:
            alarms = await self._fetch_mission_alarms(session, headers, mission_guid)

        data["missionAlarms"] = alarms
        return data

    except UpdateFailed:
      raise
    except Exception as e:
      raise UpdateFailed(f"API Fehler: {e}")

  async def _fetch_mission_alarms(self, session, headers, mission_guid):
    """Hole die Alarmauslöser für eine Mission."""
    url = f"{BASE_URL}/app/v8/MobileService/missionAlarms?missionGuid={mission_guid}"
    try:
      async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
          _LOGGER.warning("Fehler beim Abruf der Alarmauslöser: %s", resp.status)
          return []
        return await resp.json()
    except Exception as e:
      _LOGGER.warning("Fehler beim Abruf der Alarmauslöser: %s", e)
      return []
