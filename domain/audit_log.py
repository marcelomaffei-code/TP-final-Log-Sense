from domain.log_record import LogRecord
class AuditLog(LogRecord):
    def __init__(self,timestamp,user,action,target,ip):
      super().__init__(timestamp,"audit"); self.user=user; self.action=action; self.target=target; self.ip=ip
    def calculate_level(self): return "INFO"
