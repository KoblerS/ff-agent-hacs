import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.ffagent_connector.sensor import async_setup_entry
from custom_components.ffagent_connector.sensor import get_active_mission_status
from custom_components.ffagent_connector.sensor import request_new_token
from types import SimpleNamespace

@pytest.mark.asyncio
async def test_async_setup_entry_adds_entity():
  hass = MagicMock()
  entry = MagicMock()
  async_add_entities = AsyncMock()

  with patch("custom_components.ffagent_connector.sensor.FFAgentDataCoordinator") as MockCoordinator, \
    patch("custom_components.ffagent_connector.sensor.FFAgentStatusSensor") as MockSensor:
    coordinator_instance = AsyncMock()
    MockCoordinator.return_value = coordinator_instance
    sensor_instance = MagicMock()
    MockSensor.return_value = sensor_instance

    await async_setup_entry(hass, entry, async_add_entities)

    MockCoordinator.assert_called_once_with(hass, entry)
    coordinator_instance.async_config_entry_first_refresh.assert_awaited_once()
    MockSensor.assert_called_once_with(coordinator_instance, entry)
    async_add_entities.assert_called_once_with([sensor_instance])

# TODO: Fix test
# @pytest.mark.asyncio
# async def test_get_active_mission_status_success():
#   hass = MagicMock()
#   entry = MagicMock()
#   entry.data = {
#     "access_token": "token123",
#     "username": "user",
#     "password": "pass"
#   }

#   response_json = {"status": "active"}

#   # Mocked Response
#   mock_response = AsyncMock()
#   mock_response.status = 200
#   mock_response.json = AsyncMock(return_value=response_json)

#   # Mocked aiohttp session
#   mock_session = AsyncMock()
#   mock_session.get = AsyncMock(return_value=mock_response)

#   # aiohttp.ClientSession context manager
#   class MockClientSession:
#     async def __aenter__(self):
#       return mock_session
#     async def __aexit__(self, exc_type, exc, tb):
#       pass

#   with patch("aiohttp.ClientSession", return_value=MockClientSession()):
#     result = await get_active_mission_status(hass, entry)

#   assert result == response_json

@pytest.mark.asyncio
async def test_get_active_mission_status_missing_credentials():
  hass = MagicMock()
  entry = MagicMock()
  entry.data = {}

  with patch("aiohttp.ClientSession"):
    result = await get_active_mission_status(hass, entry)
    assert result == {}

@pytest.mark.asyncio
async def test_get_active_mission_status_token_expired_and_refresh_failed():
  hass = MagicMock()
  hass.config_entries.async_update_entry = AsyncMock()
  entry = MagicMock()
  entry.data = {
    "access_token": "expired_token",
    "username": "user",
    "password": "pass"
  }

  response_401 = AsyncMock()
  response_401.status = 401
  response_401.text = AsyncMock(return_value="Unauthorized")

  response_403 = AsyncMock()
  response_403.status = 403
  response_403.text = AsyncMock(return_value="Forbidden")

  mock_session = AsyncMock()
  mock_session.get = AsyncMock(side_effect=[response_401, response_403])

  mock_client_session = AsyncMock()
  mock_client_session.__aenter__.return_value = mock_session

  with patch("aiohttp.ClientSession", return_value=mock_client_session), \
    patch("custom_components.ffagent_connector.sensor.request_new_token", AsyncMock(return_value="new_token")):
    result = await get_active_mission_status(hass, entry)
    assert result == {}

@pytest.mark.asyncio
async def test_get_active_mission_status_api_error():
  hass = MagicMock()
  entry = MagicMock()
  entry.data = {
    "access_token": "token123",
    "username": "user",
    "password": "pass"
  }

  response_error = AsyncMock()
  response_error.status = 500
  response_error.text = AsyncMock(return_value="Internal Server Error")

  mock_session = AsyncMock()
  mock_session.get = AsyncMock(return_value=response_error)

  mock_client_session = AsyncMock()
  mock_client_session.__aenter__.return_value = mock_session

  with patch("aiohttp.ClientSession", return_value=mock_client_session):
    result = await get_active_mission_status(hass, entry)
    assert result == {}
