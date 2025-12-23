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
        # 修改后的奖品设置 - 加入"谢谢参与"
        prizes = {
            "一等奖": {"name": "头戴式耳机", "count": 1, "weight": 5},
            "二等奖": {"name": "小风扇", "count": 1, "weight": 10},
            "三等奖": {"name": "笔记本", "count": 7, "weight": 20},
            "四等奖": {"name": "手机支架", "count": 3, "weight": 30},
            "谢谢参与": {"name": "谢谢参与", "count": 100, "weight": 35}  # 新增谢谢参与
        }

        phone = data.get('phone', '')
        name = data.get('name', '')

        if not name or not phone:
            return {"success": False, "message": "请输入姓名和手机号"}

        if len(phone) != 11:
            return {"success": False, "message": "请输入11位手机号"}

        # 创建加权抽奖池
        prize_pool = []
        for prize_name, prize_info in prizes.items():
            # 每个奖项根据权重添加相应次数
            prize_pool.extend([prize_name] * prize_info['weight'])

        # 随机抽奖
        selected_prize = random.choice(prize_pool)

        # 如果是实物奖品，检查库存
        if selected_prize != "谢谢参与":
            if prizes[selected_prize]['count'] <= 0:
                # 如果该奖品已抽完，自动转为谢谢参与
                selected_prize = "谢谢参与"
            else:
                # 减少实物奖品库存
                prizes[selected_prize]['count'] -= 1

        # 生成抽奖码
        lottery_code = hashlib.md5(f"{phone}{name}{datetime.now()}".encode()).hexdigest()[:8].upper()

        return {
            "success": True,
            "name": name,
            "phone": phone,
            "prize_name": selected_prize,
            "prize_item": prizes[selected_prize]["name"],
            "lottery_code": lottery_code,
            "is_prize": selected_prize != "谢谢参与"  # 新增字段，方便前端判断
        }

        }
