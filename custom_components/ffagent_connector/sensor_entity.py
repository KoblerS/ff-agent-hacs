# sensor_entity.py
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

class FFAgentStatusSensor(CoordinatorEntity, SensorEntity):
  def __init__(self, coordinator, entry):
    super().__init__(coordinator)
    self.entry = entry
    self._attr_name = f"FF-Agent - {entry.data['username']}"
    self._attr_unique_id = f"ffagent_{entry.data['username']}"

  @property
  def native_value(self):
    data = self.coordinator.data or {}
    mission_list = data.get("missionStatus", [])
    if not mission_list:
      return "Kein Einsatz"
    # Zeige ersten Status im UI
    return mission_list[0].get("status", "Unbekannt")

  @property
  def extra_state_attributes(self):
    data = self.coordinator.data or {}
    missions = data.get("missionStatus", [])
    status_list = []

    for m in missions:
      mission = m.get("mission", {})
      status_list.append({
        "status": m.get("status"),
        "auto_reply": m.get("isAutoReply"),
        "mission_guid": mission.get("guid"),
        "alarm_time": mission.get("alarmDate"),
        "message": mission.get("message"),
        "details": mission.get("details"),
        "caller": mission.get("caller"),
        "location": mission.get("location"),
        "district": mission.get("district"),
        "object": mission.get("object"),
        "division": mission.get("division", {}).get("title"),
        "type": mission.get("type", {}).get("label"),
        "opener_info": mission.get("openerInformation"),
      })

    return {
      "einsatzanzahl": len(missions),
      "alarmierungen": status_list,
    }
