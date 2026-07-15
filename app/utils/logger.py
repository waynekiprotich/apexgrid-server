import logging
import json
import sys
from datetime import datetime, timezone
from flask import request

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        try:
            if request:
                log_data["path"] = request.path
                log_data["method"] = request.method
                log_data["ip"] = request.remote_addr
        except RuntimeError:
            pass # Outside application context
            
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logger(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    app.logger.handlers = []
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    @app.before_request
    def log_request_info():
        app.logger.info("Request started", extra={"extra_data": {"event": "request_start"}})
        
    @app.after_request
    def log_response_info(response):
        app.logger.info("Request completed", extra={"extra_data": {"event": "request_end", "status": response.status_code}})
        return response
