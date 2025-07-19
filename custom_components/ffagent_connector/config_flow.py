import aiohttp
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries, core
from .const import CONF_USERNAME, CONF_PASSWORD, BASE_URL, USER_AGENT, DOMAIN
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

import hashlib
import secrets

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

AUTH_SCHEMA = vol.Schema(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_PASSWORD): TextSelector(
      TextSelectorConfig(
        type=TextSelectorType.PASSWORD
      )
    )}
)

def hash_password(pw):
  return hashlib.sha256(pw.encode()).hexdigest()

async def validate_auth(username: str, password: str, hass: core.HomeAssistant) -> None:
    """Validiert ein GitHub Zugriffstoken.

    Wirft einen ValueError, wenn das Authentifizierungstoken ungültig ist.
    """
    url = f"{BASE_URL}/app/v8/MobileService/registerDevice"
    headers = {
      "User-Agent": USER_AGENT,
      "Content-Type": "application/x-www-form-urlencoded",
    }
    device_token = secrets.token_hex(16)
    body = {
      "debuggingDevice": 0,
      "deviceInfo": USER_AGENT,
      "deviceName": "HomeAssistant",
      "deviceToken": device_token,
      "deviceType": "ios",
      "password": password,
      "pushEncryptionEnabled": 1,
      "username": username,
    }
    async with aiohttp.ClientSession() as session:
      resp = await session.post(url, headers=headers, data=body)
      async with resp:
        if resp.status != 200:
          body_text = await resp.text()
          _LOGGER.error("HTTP-Fehler: %s %s", resp.status, body_text)
          raise ValueError(f"HTTP Fehler! Status: {resp.status}, Antwort: {body_text}")
        data = await resp.json()
        if not data.get("accessToken"):
          raise ValueError("Zugriffstoken wurde in der Antwort nicht gefunden")
        return data["accessToken"]

class FFAgentConnectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  """FFAgent Connector Konfigurationsablauf."""

  data: Optional[Dict[str, Any]]

  async def async_step_user(
      self, user_input: Dict[str, Any] = None
  ) -> Dict[str, Any]:
    errors: Dict[str, str] = {}

    if user_input is not None:
      try:
        hashed_password = hash_password(user_input[CONF_PASSWORD])
        access_token = await validate_auth(user_input[CONF_USERNAME], hashed_password, self.hass)
        data = {
            "access_token": access_token,
            "username": user_input[CONF_USERNAME],
            "password": hashed_password,
        }
        return self.async_create_entry(title=user_input[CONF_USERNAME], data=data)
      except ValueError as e:
        errors["base"] = "Authentifizierung fehlgeschlagen: " + str(e)
      except Exception as e:
        _LOGGER.exception("Unerwarteter Fehler im Config Flow: %s", e)
        errors["base"] = "unknown"

    return self.async_show_form(
      step_id="user", data_schema=AUTH_SCHEMA, errors=errors
    )
