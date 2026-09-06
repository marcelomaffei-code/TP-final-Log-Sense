from domain.log_record import LogRecord
class AlertLog(LogRecord):
    def __init__(self,timestamp,service,severity,message,host):
      super().__init__(timestamp,"alert"); self.service=service; self.severity=severity; self.message=message; self.host=host
    def calculate_level(self):
      severity = self.severity.strip().lower()
      if severity in {"high", "critical", "alta", "critica", "crítica"}:
        return "ERROR"
      if severity in {"medium", "warning", "warn", "media"}:
        return "WARN"
      return "INFO"
