from http.server import BaseHTTPRequestHandler
import json
import random
import hashlib
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/lottery':
            self.handle_lottery()
        else:
            self.send_error(404)

    def handle_lottery(self):
        # 允许跨域
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            result = self.process_lottery(data)
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            error_result = {"success": False, "message": "系统错误"}
            self.wfile.write(json.dumps(error_result).encode())

    def process_lottery(self, data):
        # 奖品设置
        prizes = {
            "一等奖": {"name": "头戴式耳机", "count": 1, "issued": 0},
            "二等奖": {"name": "小风扇", "count": 1, "issued": 0},
            "三等奖": {"name": "笔记本", "count": 7, "issued": 0},
            "四等奖": {"name": "手机支架", "count": 3, "issued": 0}
        }

        phone = data.get('phone', '')
        name = data.get('name', '')

        if not name or not phone:
            return {"success": False, "message": "请输入姓名和手机号"}

        if len(phone) != 11:
            return {"success": False, "message": "请输入11位手机号"}

        # 简化的抽奖逻辑
        available_prizes = []
        for prize_name, prize_info in prizes.items():
            available_prizes.append(prize_name)

        if not available_prizes:
            return {"success": False, "message": "所有奖品都已抽完"}

        selected_prize = random.choice(available_prizes)
        lottery_code = hashlib.md5(f"{phone}{name}{datetime.now()}".encode()).hexdigest()[:8].upper()

        return {
            "success": True,
            "name": name,
            "phone": phone,
            "prize_name": selected_prize,
            "prize_item": prizes[selected_prize]["name"],
            "lottery_code": lottery_code
        }
