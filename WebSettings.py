from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread

class WebSettings:
    def __init__(self, port=5000, on_settings_changed=None):
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.server_thread = None
        self.on_settings_changed = on_settings_changed

        self.enabled = False
        self.pomodoro_work = 25
        self.pomodoro_break = 5
        self.proximity = 50
        self.volume = 70
        self.sensitivity = 'medium'

        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/api/settings', methods=['POST'])
        def update_settings():
            data = request.get_json()

            if 'enabled' in data:
                self.enabled = data['enabled']
            if 'pomodoro_work' in data:
                self.pomodoro_work = data['pomodoro_work']
            if 'pomodoro_break' in data:
                self.pomodoro_break = data['pomodoro_break']
            if 'proximity' in data:
                self.proximity = data['proximity']
            if 'volume' in data:
                self.volume = data['volume']
            if 'sensitivity' in data:
                self.sensitivity = data['sensitivity']

            print(f"Settings updated: enabled={self.enabled}, "
                  f"pomodoro={self.pomodoro_work}/{self.pomodoro_break}min, "
                  f"sensitivity={self.sensitivity}")

            if self.on_settings_changed:
                self.on_settings_changed(self.get_settings())

            return jsonify({'status': 'ok', 'settings': self.get_settings()})

        @self.app.route('/api/settings', methods=['GET'])
        def get_settings_route():
            return jsonify(self.get_settings())

        @self.app.route('/')
        def index():
            return jsonify({'status': 'running', 'message': 'WebSettings server is active'})

    def get_settings(self):
        """Return current settings as a dictionary."""
        return {
            'enabled': self.enabled,
            'pomodoro_work': self.pomodoro_work,
            'pomodoro_break': self.pomodoro_break,
            'proximity': self.proximity,
            'volume': self.volume,
            'sensitivity': self.sensitivity,
        }

    def start(self):
        """Start the Flask server in a background thread."""
        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, threaded=True, use_reloader=False)

        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"WebSettings server started on port {self.port}")

    def is_enabled(self):
        """Check if the robot is enabled via web interface."""
        return self.enabled