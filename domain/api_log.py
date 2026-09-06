from domain.log_record import LogRecord
class ApiLog(LogRecord):
    def __init__(self,timestamp,service,method,endpoint,status_code,latency,trace_id,message):
      super().__init__(timestamp,"api"); self.service=service; self.method=method; self.endpoint=endpoint; self.status_code=status_code; self.latency=latency; self.trace_id=trace_id; self.message=message
    def calculate_level(self): return "ERROR" if self.status_code>=500 else ("WARN" if self.status_code>=400 else "INFO")
