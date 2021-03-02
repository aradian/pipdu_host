
import BaseHTTPServer as http
import re
import os
import relayboard as r
import logging
import json

class WebInterface(http.BaseHTTPRequestHandler):
    data_path = None
    meter_ctrl = None
    relay_state = None
    logger = logging.getLogger('webif')

    _cors_origin = 'http://pipdu.lan:8080'

    _prom_mapping = [
            ['voltage{meter="1"}',  1, 'gauge'],
            ['voltage{meter="2"}', 17, 'gauge'],
            ['current{meter="1",channel="1"}',  2, 'gauge'],
            ['current{meter="1",channel="2"}',  3, 'gauge'],
            ['current{meter="1",channel="3"}',  4, 'gauge'],
            ['current{meter="2",channel="4"}', 18, 'gauge'],
            ['current{meter="2",channel="5"}', 19, 'gauge'],
            ['current{meter="2",channel="6"}', 20, 'gauge'],
            ['power_active{meter="1",channel="1"}',  5, 'gauge'],
            ['power_active{meter="1",channel="2"}',  6, 'gauge'],
            ['power_active{meter="1",channel="3"}',  7, 'gauge'],
            ['power_active{meter="2",channel="4"}', 21, 'gauge'],
            ['power_active{meter="2",channel="5"}', 22, 'gauge'],
            ['power_active{meter="2",channel="6"}', 23, 'gauge'],
            ['power_reactive{meter="1",channel="1"}',  8, 'gauge'],
            ['power_reactive{meter="1",channel="2"}',  9, 'gauge'],
            ['power_reactive{meter="1",channel="3"}', 10, 'gauge'],
            ['power_reactive{meter="2",channel="4"}', 24, 'gauge'],
            ['power_reactive{meter="2",channel="5"}', 25, 'gauge'],
            ['power_reactive{meter="2",channel="6"}', 26, 'gauge'],
            ['power_apparent{meter="1",channel="1"}', 11, 'gauge'],
            ['power_apparent{meter="1",channel="2"}', 12, 'gauge'],
            ['power_apparent{meter="1",channel="3"}', 13, 'gauge'],
            ['power_apparent{meter="2",channel="4"}', 27, 'gauge'],
            ['power_apparent{meter="2",channel="5"}', 28, 'gauge'],
            ['power_apparent{meter="2",channel="6"}', 29, 'gauge'],
            ['power_factor{meter="1",channel="1"}', 14, 'gauge'],
            ['power_factor{meter="1",channel="2"}', 15, 'gauge'],
            ['power_factor{meter="1",channel="3"}', 16, 'gauge'],
            ['power_factor{meter="2",channel="4"}', 30, 'gauge'],
            ['power_factor{meter="2",channel="5"}', 31, 'gauge'],
            ['power_factor{meter="2",channel="6"}', 32, 'gauge'],
            ['temperature_celcius', 33, 'gauge'],
            ['frequency_hz', 34, 'gauge'],
            ['measurement_time_seconds', 35, 'gauge'],
            ]

    #                          1    2 3            4 5
    _pathparse = re.compile('^/(\w*)(/([\w\._-]+))?(/(\w+))?')

    def do_GET(self):
        if self.data_path is None:
            self.logger.error('Received GET while not configured: ' + self.path)
            self.send_error(500, 'Not Configured')
            return

        pathmatch = self._pathparse.match(self.path)

        # if unrecognizable
        if not pathmatch:
            self.logger.debug('Received GET with unknown path: ' + self.path)
            self.send_error(404, 'Not Found')
            return

        if pathmatch.group(1) == 'log':
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            fh = None
            try:
                fh = open(self.data_path + 'log/activity.log', 'r')
                for line in fh:
                    self.wfile.write(line)
            finally:
                if fh:
                    fh.close()
            return

        # if Prometheus exporter
        if pathmatch.group(1) == 'metrics' and pathmatch.group(2) is None:
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            for line in self._get_prometheus_data():
                self.wfile.write(line + "\n")
            return

        # if data API
        if pathmatch.group(1) == 'api':
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/json')
            self.send_header('Access-Control-Allow-Origin', self._cors_origin)
            self.send_header('Vary', 'Origin')
            self.end_headers()
            self.wfile.write(self._get_json_data())
            return

        self.logger.debug('Received GET unhandled: ' + self.path)
        self.send_error(404, 'Not Found')

    def do_OPTIONS(self):
        options_list = []
        pathmatch = self._pathparse.match(self.path)
        self.send_response(204, 'No Content')
        self.send_header('Access-Control-Allow-Origin', self._cors_origin)
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Vary', 'Origin')
        if not pathmatch:
            self.end_headers()
            return
        if pathmatch.group(1) == '':
            self.send_header('Access-Control-Allow-Methods', 'OPTIONS, GET')
            self.end_headers()
            return
        if pathmatch.group(1) == 'api':
            self.send_header('Access-Control-Allow-Methods', 'OPTIONS, GET, POST')
            self.end_headers()
            return

        self.send_header('Access-Control-Allow-Methods', 'OPTIONS')
        self.end_headers()

    def do_POST(self):
        if self.data_path is None:
            self.logger.error('Received POST while not configured: ' + self.path)
            self.send_error(500, 'Not Configured')
            return

        pathmatch = self._pathparse.match(self.path)

        if pathmatch.group(1) == 'api' and pathmatch.group(3):
            self.logger.debug('Received POST at: ' + self.path)
            if pathmatch.group(3) == 'relay':
                relay_num = int(pathmatch.group(5))
                if not (relay_num >= 1 and relay_num <= 6):
                    self.send_response(400, 'Bad Request')
                    self.send_header('Access-Control-Allow-Origin', self._cors_origin)
                    self.send_header('Vary', 'Origin')
                    self.end_headers()
                    return
                post_len = int(self.headers.getheader('Content-Length'))
                if post_len > 5:
                    post_len = 5
                relay_state = int(json.loads(self.rfile.read(post_len)))
                self.logger.info('Set relay ' + str(relay_num) + ': ' + str(relay_state))
                r.set_relay(relay_num, relay_state)
                self.relay_state[relay_num - 1] = relay_state

                self.send_response(200, 'OK')
                self.send_header('Access-Control-Allow-Origin', self._cors_origin)
                self.send_header('Vary', 'Origin')
                self.end_headers()
                return

        self.logger.debug('Received POST unhandled: ' + self.path)
        self.send_error(405, 'Method Not Allowed')

    def _fetch_latest_data(self):
        if not self.meter_ctrl:
            return []
        return self.meter_ctrl.get_last_data()

    def _get_prometheus_data(self):
        data = self._fetch_latest_data()
        prom_lines = [
                '# TYPE channel_id gauge',
                '# TYPE channel_name gauge',
                '# TYPE relay_state gauge',
                '# TYPE voltage gauge',
                '# TYPE current gauge',
                '# TYPE power_active gauge',
                '# TYPE power_reactive gauge',
                '# TYPE power_apparent gauge',
                '# TYPE power_factor gauge',
                '# TYPE temperature_celcius gauge',
                '# TYPE frequency_hz gauge',
                '# TYPE measure_time_seconds gauge',
                '# TYPE energy_active_forward_kWh counter',
                '# TYPE energy_active_reverse_kWh counter',
                '# TYPE energy_reactive_forward_kWh counter',
                '# TYPE energy_reactive_reverse_kWh counter',
                'channel_id{meter="1",channel="1"} 1',
                'channel_id{meter="1",channel="2"} 2',
                'channel_id{meter="1",channel="3"} 3',
                'channel_id{meter="2",channel="4"} 4',
                'channel_id{meter="2",channel="5"} 5',
                'channel_id{meter="2",channel="6"} 6',
                'channel_name{meter="1",channel="1"} 1',
                'channel_name{meter="1",channel="2"} 2',
                'channel_name{meter="1",channel="3"} 3',
                'channel_name{meter="2",channel="4"} 4',
                'channel_name{meter="2",channel="5"} 5',
                'channel_name{meter="2",channel="6"} 6',
                ]
        if len(data):
            for i in range(0,6):
                prom_lines.append('relay_state{channel="' + str(i) + '"} ' + str(int(self.relay_state[i])))
            for stat in self._prom_mapping:
                prom_lines.append(stat[0] + " " + str(data[stat[1]]))
            for (meter, channels) in self.meter_ctrl.getclear_energy_data().iteritems():
                for (channel, values) in channels.iteritems():
                    for (name, value) in values.iteritems():
                        prom_lines.append(name + '{meter="' + str(meter) + '",channel="' + str(channel) + '"} ' + str(value))

        return prom_lines

    def _get_json_data(self):
        data = self._fetch_latest_data()
        return json.dumps({
                'timestamp': data[0],
                'channel1': {
                    'voltage': data[1],
                    'current': data[2],
                    'power_active': data[5],
                    'power_reactive': data[8],
                    'power_apparent': data[11],
                    'power_factor': data[14],
                    'relay': self.relay_state[0],
                    },
                'channel2': {
                    'voltage': data[1],
                    'current': data[3],
                    'power_active': data[6],
                    'power_reactive': data[9],
                    'power_apparent': data[12],
                    'power_factor': data[15],
                    'relay': self.relay_state[1],
                    },
                'channel3': {
                    'voltage': data[1],
                    'current': data[4],
                    'power_active': data[7],
                    'power_reactive': data[10],
                    'power_apparent': data[13],
                    'power_factor': data[16],
                    'relay': self.relay_state[2],
                    },
                'channel4': {
                    'voltage': data[17],
                    'current': data[18],
                    'power_active': data[21],
                    'power_reactive': data[24],
                    'power_apparent': data[27],
                    'power_factor': data[30],
                    'relay': self.relay_state[3],
                    },
                'channel5': {
                    'voltage': data[17],
                    'current': data[19],
                    'power_active': data[22],
                    'power_reactive': data[25],
                    'power_apparent': data[28],
                    'power_factor': data[31],
                    'relay': self.relay_state[4],
                    },
                'channel6': {
                    'voltage': data[17],
                    'current': data[20],
                    'power_active': data[23],
                    'power_reactive': data[26],
                    'power_apparent': data[29],
                    'power_factor': data[32],
                    'relay': self.relay_state[5],
                    },
                'temperature': data[33],
                'frequency': data[34],
                'measurement_time': data[35],
                })

