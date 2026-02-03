# Map each attribute to a Material Design icon
MISSION_SENSOR_ICONS = {
  "status": "mdi:alert-circle-outline",
  "auto_reply": "mdi:robot",
  "mission_guid": "mdi:identifier",
  "alarm_time": "mdi:clock-outline",
  "message": "mdi:message-text-outline",
  "details": "mdi:file-document-outline",
  "caller": "mdi:account-voice",
  "location": "mdi:map-marker",
  "district": "mdi:city",
  "object": "mdi:cube-outline",
  "division": "mdi:account-group-outline",
  "type": "mdi:shape-outline",
  "opener_info": "mdi:information-outline",
}
# sensor_entity.py
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


# List of mission attributes to expose as separate sensors
MISSION_SENSOR_ATTRIBUTES = [
  ("status", "Status"),
  ("auto_reply", "Auto Reply"),
  ("mission_guid", "Mission GUID"),
  ("alarm_time", "Alarm Time"),
  ("message", "Message"),
  ("details", "Details"),
  ("caller", "Caller"),
  ("location", "Location"),
  ("district", "District"),
  ("object", "Object"),
  ("division", "Division"),
  ("type", "Type"),
  ("opener_info", "Opener Info"),
]

def get_first_mission(data):
  missions = (data or {}).get("missionStatus", [])
  if not missions:
    return None, None
  m = missions[0]
  mission = m.get("mission", {})
  return m, mission


class FFAgentMissionSensor(CoordinatorEntity, SensorEntity):
  def __init__(self, coordinator, entry, attribute, display_name):
    super().__init__(coordinator)
    self.entry = entry
    self.attribute = attribute
    self._attr_name = f"FF-Agent - {entry.data['username']} {display_name}"
    self._attr_unique_id = f"ffagent_{entry.data['username']}_{attribute}"
    self._attr_icon = MISSION_SENSOR_ICONS.get(attribute, "mdi:alert-circle-outline")

  @property
  def native_value(self):
    data = self.coordinator.data or {}
    m, mission = get_first_mission(data)
    if m is None:
      return None
    # Map attribute to correct value source
    if self.attribute == "status":
      return m.get("status")
    elif self.attribute == "auto_reply":
      return m.get("isAutoReply")
    elif self.attribute == "mission_guid":
      return mission.get("guid")
    elif self.attribute == "alarm_time":
      return mission.get("alarmDate")
    elif self.attribute == "message":
      return mission.get("message")
    elif self.attribute == "details":
      return mission.get("details")
    elif self.attribute == "caller":
      return mission.get("caller")
    elif self.attribute == "location":
      return mission.get("location")
    elif self.attribute == "district":
      return mission.get("district")
    elif self.attribute == "object":
      return mission.get("object")
    elif self.attribute == "division":
      return mission.get("division", {}).get("title")
    elif self.attribute == "type":
      return mission.get("type", {}).get("label")
    elif self.attribute == "opener_info":
      return mission.get("openerInformation")
    return None

  @property
  def extra_state_attributes(self):
    # Optionally, add more context if needed
    return {}

# Factory to create all sensors for a user
def create_ffagent_sensors(coordinator, entry):
  return [
    FFAgentMissionSensor(coordinator, entry, attr, display_name)
    for attr, display_name in MISSION_SENSOR_ATTRIBUTES
  ]
