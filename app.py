import ujson
import urequests
import network
import usocket
import utime
import random
from machine import Pin


# 预定义函数示例（需与config.json中的name对应）
def led_control(state, brightness):
    print(f"Setting LED: {state} at {brightness}%")
    # 实际硬件控制代码


def get_temperature():
    return f"{random.uniform(20, 30):.1f}°C"  # 示例温度值


# 加载配置文件
with open('config.json') as f:
    config = ujson.load(f)


# 网页生成函数
def generate_html():
    html = """<html><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { 
            background: #f0f2f5; 
            margin: 0;
            padding: 20px;
        }
        .group { 
            background: white;
            border-left: 4px solid #1890ff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            margin: 15px 0;
            padding: 20px;
            transition: transform 0.2s;
        }
        .group:hover {
            transform: translateY(-2px);
        }
        h3 {
            color: #1890ff;
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
            font-size: 1.2em;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            border-color: #1890ff;
            outline: none;
        }
        input[type="submit"], button {
            background: #1890ff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            transition: opacity 0.3s;
        }
        input[type="submit"]:hover, button:hover {
            opacity: 0.9;
        }
        .output {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            font-size: 1.1em;
            color: #333;
            min-height: 40px;
        }
        .form-group {
            margin-bottom: 15px;
        }
    </style>
    <script>
        function updateShow(id) {{
            fetch('/show/' + id)
            .then(r => r.text())
            .then(t => document.getElementById(id).innerHTML = t)
        }}
    </script></head><body>"""
    
    for group_id, group in config.items():
        html += f'<div class="group"><h3>🔹 {group["name"].upper()}</h3>'
        
        if group['type'] == 'function':
            html += f'<form action="/{group_id}" method="post">'
            for i, param in enumerate(group['data']):
                html += f'<input type="text" name="arg{i}" placeholder="{param}"><br>'
            html += '<input type="submit" value="Run"></form>'
            
        elif group['type'] == 'show':
            html += f'<div class="output" id="{group_id}">Loading...</div>'
            html += f'<script>setInterval(() => updateShow("{group_id}"), 1000)</script>'
            
        html += '</div>'
    return html + "</body></html>"

# 网络服务
def start_webserver():
    wlan = network.WLAN(network.STA_IF)
    print('IP:', wlan.ifconfig()[0])

    s = usocket.socket()
    s.bind(('0.0.0.0', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        
        # 路由处理
        if request.startswith('GET /'):
            if request.startswith('GET /show/'):
                group_id = request.split('/show/')[1].split()[0]
                func = globals()[config[group_id]['name']]
                result = str(func())
                conn.send('HTTP/1.1 200 OK\nContent-Type: text/plain; charset=utf-8\n\n' + result)
            else:
                conn.send('HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\n\n' + generate_html())
        
        # 修改后的POST处理部分
        elif request.startswith('POST /'):
            group_id = request.split()[1].split('/')[1]
            
            # 分离headers和body
            header_body = request.split('\r\n\r\n', 1)
            body = header_body[1] if len(header_body) > 1 else ''
            
            # 解析POST参数
            params = {}
            if body:
                pairs = body.split('&')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)  # 只分割第一个等号
                        params[key] = value
            
            # 构建参数列表（带默认值）
            expected_args = len(config[group_id]['data'])
            args = [params.get(f'arg{i}', '') for i in range(expected_args)]
            
            # 执行对应函数
            func = globals()[config[group_id]['name']]
            try:
                func(*args)
            except TypeError as e:
                print("参数错误:", e)
            
            conn.send('HTTP/1.1 303 See Other\nLocation: /\n\n')        
        conn.close()

start_webserver()