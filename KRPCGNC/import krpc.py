import krpc
import threading
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

conn = krpc.connect()
vessel = conn.space_center.active_vessel

target_modules = [
    "TestFlightFailure_IgnitionFail",
    "TestFlightReliability_EngineCycle",
    "ModuleEnginesRF"
]

telemetry = {}
last_good_data = {}

def flatten_fields(fields):
    """Flatten a dict, unwrapping nested dicts under 'fields' and 'fields_by_id'."""
    result = {}
    for k, v in fields.items():
        if k in ("fields", "fields_by_id") and isinstance(v, dict):
            for inner_k, inner_v in v.items():
                result[inner_k] = inner_v
        else:
            result[k] = v
    return result

def gather_module_fields():
    data = {}
    for part in vessel.parts.all:
        for module in part.modules:
            if module.name in target_modules:
                fields = {}
                for attr in dir(module):
                    if attr.startswith('_') or attr in ['name', 'part', 'rpc']:
                        continue
                    try:
                        value = getattr(module, attr)
                        if not callable(value):
                            fields[attr] = value
                    except Exception:
                        fields[attr] = "ERR"
                flat_fields = flatten_fields(fields)
                data.setdefault(part.title, {})[module.name] = flat_fields
    return data

class TelemetryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(telemetry).encode())

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), TelemetryHandler)
    print("Telemetry server running on http://localhost:8080")
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

print("Starting engine static fire for 370 seconds...")
start_time = time.time()
while time.time() - start_time < 370:
    try:
        for engine in vessel.parts.engines:
            if not engine.active:
                engine.active = True
        new_data = gather_module_fields()
        if new_data:
            telemetry.clear()
            telemetry.update(new_data)
            last_good_data = new_data
        else:
            telemetry.clear()
            telemetry.update(last_good_data)
    except Exception as e:
        print("Error fetching data:", e)
        telemetry.clear()
        telemetry.update(last_good_data)
    time.sleep(1)

print("Static fire complete.")