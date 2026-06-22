import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.ffagent_connector.sensor import async_setup_entry
from custom_components.ffagent_connector.sensor import get_active_mission_status
from custom_components.ffagent_connector.sensor import request_new_token
from custom_components.ffagent_connector.sensor_entity import FFAgentMissionSensor, get_first_mission
from types import SimpleNamespace

@pytest.mark.asyncio
async def test_async_setup_entry_adds_entity():
  hass = MagicMock()
  entry = MagicMock()
  async_add_entities = AsyncMock()

  with patch("custom_components.ffagent_connector.sensor.FFAgentDataCoordinator") as MockCoordinator, \
    patch("custom_components.ffagent_connector.sensor.create_ffagent_sensors") as MockFactory:
    coordinator_instance = AsyncMock()
    MockCoordinator.return_value = coordinator_instance
    sensor_instances = [MagicMock(), MagicMock()]
    MockFactory.return_value = sensor_instances

    await async_setup_entry(hass, entry, async_add_entities)

    MockCoordinator.assert_called_once_with(hass, entry)
    coordinator_instance.async_config_entry_first_refresh.assert_awaited_once()
    MockFactory.assert_called_once_with(coordinator_instance, entry)
    async_add_entities.assert_called_once_with(sensor_instances)

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


# --- Tests for opener_info extra_state_attributes ---

def _make_opener_sensor(coordinator_data):
  """Helper to create an opener_info sensor with given coordinator data."""
  coordinator = MagicMock()
  coordinator.data = coordinator_data
  entry = MagicMock()
  entry.data = {"username": "testuser"}
  sensor = FFAgentMissionSensor(coordinator, entry, "opener_info", "Opener Info")
  return sensor


def test_opener_info_extra_attributes_with_multiple_openers():
  """Test that openerInformation is split into individual entries."""
  data = {
    "missionStatus": [{
      "status": "REQUESTED",
      "isAutoReply": False,
      "mission": {
        "openerInformation": "eMID - FF Musterstadt (Dienststelle)\neMID - Schleife 10001\nTETRA Callout - FW MUSTER_1 - FR"
      }
    }]
  }
  sensor = _make_opener_sensor(data)
  attrs = sensor.extra_state_attributes

  assert attrs["openers"] == [
    "eMID - FF Musterstadt (Dienststelle)",
    "eMID - Schleife 10001",
    "TETRA Callout - FW MUSTER_1 - FR",
  ]
  assert attrs["openers_count"] == 3
  assert attrs["last_opener"] == "TETRA Callout - FW MUSTER_1 - FR"
  assert attrs["openers_filtered"] == [
    "eMID - FF Musterstadt (Dienststelle)",
    "eMID - Schleife 10001",
    "TETRA Callout - FW MUSTER_1 - FR",
  ]


def test_opener_info_extra_attributes_filters_tetra_sds():
  """Test that TETRA SDS entries are filtered from openers_filtered."""
  data = {
    "missionStatus": [{
      "status": "REQUESTED",
      "isAutoReply": False,
      "mission": {
        "openerInformation": "TETRA SDS - Funkmelder\neMID - Schleife 10001\nTETRA SDS - Dienststelle"
      }
    }]
  }
  sensor = _make_opener_sensor(data)
  attrs = sensor.extra_state_attributes

  assert attrs["openers_count"] == 3
  assert attrs["openers"] == [
    "TETRA SDS - Funkmelder",
    "eMID - Schleife 10001",
    "TETRA SDS - Dienststelle",
  ]
  assert attrs["openers_filtered"] == ["eMID - Schleife 10001"]


def test_opener_info_extra_attributes_no_mission():
  """Test attributes when no mission is active."""
  data = {"missionStatus": []}
  sensor = _make_opener_sensor(data)
  attrs = sensor.extra_state_attributes

  assert attrs == {"openers": [], "openers_count": 0, "openers_filtered": [], "last_opener": None}


def test_opener_info_extra_attributes_empty_opener_info():
  """Test attributes when openerInformation is empty."""
  data = {
    "missionStatus": [{
      "status": "REQUESTED",
      "isAutoReply": False,
      "mission": {
        "openerInformation": ""
      }
    }]
  }
  sensor = _make_opener_sensor(data)
  attrs = sensor.extra_state_attributes

  assert attrs == {"openers": [], "openers_count": 0, "openers_filtered": [], "last_opener": None}


def test_opener_info_extra_attributes_single_opener():
  """Test attributes with a single opener entry."""
  data = {
    "missionStatus": [{
      "status": "REQUESTED",
      "isAutoReply": False,
      "mission": {
        "openerInformation": "eMID - FF Musterstadt (Dienststelle)"
      }
    }]
  }
  sensor = _make_opener_sensor(data)
  attrs = sensor.extra_state_attributes

  assert attrs["openers"] == ["eMID - FF Musterstadt (Dienststelle)"]
  assert attrs["openers_count"] == 1
  assert attrs["last_opener"] == "eMID - FF Musterstadt (Dienststelle)"
  assert attrs["openers_filtered"] == ["eMID - FF Musterstadt (Dienststelle)"]


def test_non_opener_sensor_has_empty_attributes():
  """Test that non-opener_info sensors return empty attributes."""
  coordinator = MagicMock()
  coordinator.data = {
    "missionStatus": [{
      "status": "ACTIVE",
      "isAutoReply": False,
      "mission": {"openerInformation": "something"}
    }]
  }
  entry = MagicMock()
  entry.data = {"username": "testuser"}
  sensor = FFAgentMissionSensor(coordinator, entry, "status", "Status")
  assert sensor.extra_state_attributes == {}
