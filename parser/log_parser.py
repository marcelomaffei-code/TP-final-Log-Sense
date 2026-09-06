import re
from domain.browser_log import BrowserLog
from domain.api_log import ApiLog
from domain.alert_log import AlertLog
from domain.audit_log import AuditLog
from exceptions.custom_exceptions import UnknownLogFormatError, InvalidTimestampError

class LogParser:
    BROWSER_PATTERN = re.compile(
        r'\[(?P<timestamp>[^\]]+)\]\s*BROWSER\s*\|\s*(?P<browser>[^|]+)\s*\|\s*(?P<method>\w+)\s+(?P<endpoint>\S+)\s*\|\s*(?P<status_code>\d+)\s*\|\s*(?P<response_time>\d+)ms\s*\|\s*session_id=(?P<session_id>\S+)'
    )
    
    API_PATTERN = re.compile(
        r'\[(?P<timestamp>[^\]]+)\]\s*API\s*\|\s*service=(?P<service>[^|]+)\s*\|\s*(?P<method>\w+)\s+(?P<endpoint>\S+)\s*\|\s*(?P<status_code>\d+)\s*\|\s*(?P<latency>\d+)ms\s*\|\s*trace_id=(?P<trace_id>\S+)\s*\|\s*msg="(?P<message>[^"]+)"'
    )
    
    ALERT_PATTERN = re.compile(
        r'\[(?P<timestamp>[^\]]+)\]\s*ALERT\s*\|\s*service=(?P<service>[^|]+)\s*\|\s*severity=(?P<severity>[^|]+)\s*\|\s*msg="(?P<message>[^"]+)"\s*\|\s*host=(?P<host>\S+)'
    )
    
    AUDIT_PATTERN = re.compile(
        r'\[(?P<timestamp>[^\]]+)\]\s*AUDIT\s*\|\s*user=(?P<user>[^|]+)\s*\|\s*action=(?P<action>[^|]+)\s*\|\s*target=(?P<target>[^|]+)\s*\|\s*ip=(?P<ip>\S+)'
    )
    
    def parse(self, line):
        line = line.strip()
        if not line:
            raise UnknownLogFormatError("Empty line")
        
        # Try browser log
        match = self.BROWSER_PATTERN.match(line)
        if match:
            return self._parse_browser_log(match)
        
        # Try API log
        match = self.API_PATTERN.match(line)
        if match:
            return self._parse_api_log(match)
        
        # Try alert log
        match = self.ALERT_PATTERN.match(line)
        if match:
            return self._parse_alert_log(match)
        
        # Try audit log
        match = self.AUDIT_PATTERN.match(line)
        if match:
            return self._parse_audit_log(match)
        
        raise UnknownLogFormatError(f"Unknown log format: {line}")
    
    def _parse_browser_log(self, match):
        timestamp = self._validate_timestamp(match.group('timestamp'))
        return BrowserLog(
            timestamp=timestamp,
            browser=match.group('browser').strip(),
            method=match.group('method'),
            endpoint=match.group('endpoint'),
            status_code=int(match.group('status_code')),
            response_time=int(match.group('response_time')),
            session_id=match.group('session_id')
        )
    
    def _parse_api_log(self, match):
        timestamp = self._validate_timestamp(match.group('timestamp'))
        return ApiLog(
            timestamp=timestamp,
            service=match.group('service').strip(),
            method=match.group('method'),
            endpoint=match.group('endpoint'),
            status_code=int(match.group('status_code')),
            latency=int(match.group('latency')),
            trace_id=match.group('trace_id'),
            message=match.group('message')
        )
    
    def _parse_alert_log(self, match):
        timestamp = self._validate_timestamp(match.group('timestamp'))
        return AlertLog(
            timestamp=timestamp,
            service=match.group('service').strip(),
            severity=match.group('severity').strip(),
            message=match.group('message'),
            host=match.group('host')
        )
    
    def _parse_audit_log(self, match):
        timestamp = self._validate_timestamp(match.group('timestamp'))
        return AuditLog(
            timestamp=timestamp,
            user=match.group('user').strip(),
            action=match.group('action'),
            target=match.group('target'),
            ip=match.group('ip')
        )
    
    def _validate_timestamp(self, timestamp_str):
        try:
            from datetime import datetime
            # Try to parse ISO 8601 format
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            datetime.fromisoformat(timestamp_str)
            return timestamp_str
        except ValueError:
            raise InvalidTimestampError(f"Invalid timestamp format: {timestamp_str}")
