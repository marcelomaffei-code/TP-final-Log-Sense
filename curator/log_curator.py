from datetime import datetime
class LogCurator:
 def normalize_timestamp(self,ts):
  return datetime.fromisoformat(ts.replace('Z','+00:00')).isoformat()
