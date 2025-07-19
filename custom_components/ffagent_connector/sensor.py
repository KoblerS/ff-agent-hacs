import aiohttp
import hashlib
import secrets
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ffagent_connector.coordinator import FFAgentDataCoordinator
from custom_components.ffagent_connector.sensor_entity import FFAgentStatusSensor
from .const import BASE_URL, USER_AGENT, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
  coordinator = FFAgentDataCoordinator(hass, entry)
  await coordinator.async_config_entry_first_refresh()
  async_add_entities([FFAgentStatusSensor(coordinator, entry)])

async def get_active_mission_status(hass: HomeAssistant, entry: ConfigEntry) -> dict:
  """Hole den Status der aktiven Mission von der FF-Agent API, erneuere Token automatisch bei Ablauf."""
  access_token = entry.data.get("access_token")
  username = entry.data.get(CONF_USERNAME)
  password = entry.data.get(CONF_PASSWORD)

  if not access_token or not username or not password:
    _LOGGER.error("Fehlende Zugangsdaten oder Zugriffstoken")
    return {}

  headers = {
    "User-Agent": USER_AGENT,
    "Content-Type": "application/json",
    "Authorization": f"ACCESS-TOKEN {access_token}",
  }

  url = f"{BASE_URL}/app/v8/MobileService/activeMissionStatus?includeInfo=1"

  async with aiohttp.ClientSession() as session:
    async with session.get(url, headers=headers) as response:
      if response.status == 200:
        return await response.json()

      elif response.status == 401:
        _LOGGER.warning("Zugriffstoken abgelaufen, fordere neues an...")
        new_token = await request_new_token(hass, username, password)
        if new_token:
          # Speichere neuen Token im ConfigEntry
          hass.config_entries.async_update_entry(entry, data={
            **entry.data,
            "access_token": new_token
          })
          # Neuer Versuch mit aktualisiertem Token
          headers["Authorization"] = f"ACCESS-TOKEN {new_token}"
          async with session.get(url, headers=headers) as retry_response:
            if retry_response.status == 200:
              return await retry_response.json()
            else:
              body = await retry_response.text()
              _LOGGER.error("Token-Erneuerung fehlgeschlagen: %s", body)
              return {}

      else:
        body = await response.text()
        _LOGGER.error("API-Anfrage fehlgeschlagen: %s %s", response.status, body)
        return {}

async def request_new_token(hass: HomeAssistant, username: str, password: str) -> str | None:
  """Fordere ein neues Zugriffstoken mit Benutzername und Passwort an."""
  def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

  token_url = f"{BASE_URL}/app/v8/MobileService/registerDevice"
  device_token = secrets.token_hex(16)

  body = {
    "debuggingDevice": 0,
    "deviceInfo": USER_AGENT,
    "deviceName": "HomeAssistant",
    "deviceToken": device_token,
    "deviceType": "ios",
    "password": hash_password(password),
    "pushEncryptionEnabled": 1,
    "username": username,
  }

  headers = {
    "User-Agent": USER_AGENT,
    "Content-Type": "application/x-www-form-urlencoded",
  }

  async with aiohttp.ClientSession() as session:
    async with session.post(token_url, headers=headers, data=body) as resp:
      if resp.status != 200:
        _LOGGER.error("Neues Token konnte nicht angefordert werden: %s", await resp.text())
        return None
      data = await resp.json()
      return data.get("accessToken")
