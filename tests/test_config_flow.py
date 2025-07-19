import pytest
from custom_components.ffagent_connector.config_flow import hash_password
import hashlib
from unittest.mock import patch, AsyncMock, MagicMock
from custom_components.ffagent_connector.config_flow import validate_auth
from custom_components.ffagent_connector.config_flow import FFAgentConnectorConfigFlow, CONF_USERNAME, CONF_PASSWORD

def test_hash_password_returns_correct_sha256():
  password = "mysecretpassword"
  expected_hash = hashlib.sha256(password.encode()).hexdigest()
  assert hash_password(password) == expected_hash

def test_hash_password_empty_string():
  password = ""
  expected_hash = hashlib.sha256(password.encode()).hexdigest()
  assert hash_password(password) == expected_hash

def test_hash_password_unicode():
  password = "pässwörd😊"
  expected_hash = hashlib.sha256(password.encode()).hexdigest()
  assert hash_password(password) == expected_hash

def test_hash_password_consistency():
  password = "repeatable"
  hash1 = hash_password(password)
  hash2 = hash_password(password)
  assert hash1 == hash2

@pytest.mark.asyncio
async def test_validate_auth_success():
  username = "testuser"
  password = "hashedpassword"
  hass = MagicMock()

  mock_response = AsyncMock()
  mock_response.status = 200
  mock_response.json = AsyncMock(return_value={"accessToken": "token123"})
  mock_response.text = AsyncMock(return_value="OK")

  mock_session = AsyncMock()
  mock_session.post = AsyncMock(return_value=mock_response)

  mock_client_session = AsyncMock()
  mock_client_session.__aenter__.return_value = mock_session

  with patch("aiohttp.ClientSession", return_value=mock_client_session):
    token = await validate_auth(username, password, hass)
    assert token == "token123"
    mock_session.post.assert_called_once()

@pytest.mark.asyncio
async def test_validate_auth_http_error():
  username = "testuser"
  password = "hashedpassword"
  hass = MagicMock()

  mock_response = AsyncMock()
  mock_response.status = 401
  mock_response.text = AsyncMock(return_value="Unauthorized")
  mock_response.json = AsyncMock(return_value={})

  mock_session = AsyncMock()
  mock_session.post = AsyncMock(return_value=mock_response)

  mock_client_session = AsyncMock()
  mock_client_session.__aenter__.return_value = mock_session

  with patch("aiohttp.ClientSession", return_value=mock_client_session):
    with pytest.raises(ValueError) as excinfo:
      await validate_auth(username, password, hass)
    assert "HTTP Fehler!" in str(excinfo.value)
    mock_session.post.assert_called_once()

@pytest.mark.asyncio
async def test_validate_auth_missing_access_token():
  username = "testuser"
  password = "hashedpassword"
  hass = MagicMock()

  mock_response = AsyncMock()
  mock_response.status = 200
  mock_response.text = AsyncMock(return_value="OK")
  mock_response.json = AsyncMock(return_value={})  # Kein accessToken

  mock_session = AsyncMock()
  mock_session.post = AsyncMock(return_value=mock_response)

  mock_client_session = AsyncMock()
  mock_client_session.__aenter__.return_value = mock_session

  with patch("aiohttp.ClientSession", return_value=mock_client_session):
    with pytest.raises(ValueError) as excinfo:
      await validate_auth(username, password, hass)
    assert "Zugriffstoken wurde in der Antwort nicht gefunden" in str(excinfo.value)
    mock_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_async_step_user_auth_failure():
  flow = FFAgentConnectorConfigFlow()
  flow.hass = MagicMock()
  user_input = {CONF_USERNAME: "user", CONF_PASSWORD: "pass"}

  with patch("custom_components.ffagent_connector.config_flow.hash_password", return_value="hashedpass"), \
      patch("custom_components.ffagent_connector.config_flow.validate_auth", AsyncMock(side_effect=ValueError("invalid"))) as mock_validate, \
      patch.object(flow, "async_show_form", return_value={"form": "shown"}) as mock_show_form:
    result = await flow.async_step_user(user_input)
    mock_validate.assert_awaited_once()
    mock_show_form.assert_called_once()
    assert result == {"form": "shown"}

@pytest.mark.asyncio
async def test_async_step_user_unknown_exception():
  flow = FFAgentConnectorConfigFlow()
  flow.hass = MagicMock()
  user_input = {CONF_USERNAME: "user", CONF_PASSWORD: "pass"}

  with patch("custom_components.ffagent_connector.config_flow.hash_password", return_value="hashedpass"), \
      patch("custom_components.ffagent_connector.config_flow.validate_auth", AsyncMock(side_effect=Exception("unexpected"))), \
      patch.object(flow, "async_show_form", return_value={"form": "shown"}) as mock_show_form:
    result = await flow.async_step_user(user_input)
    mock_show_form.assert_called_once()
    assert result == {"form": "shown"}

@pytest.mark.asyncio
async def test_async_step_user_no_input():
  flow = FFAgentConnectorConfigFlow()
  with patch.object(flow, "async_show_form", return_value={"form": "shown"}) as mock_show_form:
    result = await flow.async_step_user(None)
    mock_show_form.assert_called_once()
    assert result == {"form": "shown"}
