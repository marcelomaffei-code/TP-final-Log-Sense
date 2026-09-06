from domain.log_record import LogRecord
class BrowserLog(LogRecord):
    def __init__(self,timestamp,browser,method,endpoint,status_code,response_time,session_id):
      super().__init__(timestamp,"browser"); self.browser=browser; self.method=method; self.endpoint=endpoint; self.status_code=status_code; self.response_time=response_time; self.session_id=session_id
    def calculate_level(self): return "ERROR" if self.status_code>=500 else ("WARN" if self.status_code>=400 else "INFO")
