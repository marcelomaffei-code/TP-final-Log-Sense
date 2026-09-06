from domain.log_record import LogRecord
class AlertLog(LogRecord):
    def __init__(self,timestamp,service,severity,message,host):
      super().__init__(timestamp,"alert"); self.service=service; self.severity=severity; self.message=message; self.host=host
    def calculate_level(self): return self.severity.upper()
