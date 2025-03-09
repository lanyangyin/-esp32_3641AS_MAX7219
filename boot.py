# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from wifi import connect_wifi


# 执行连接wifi
wifi = connect_wifi()
if wifi:
    # 在此处添加其他需要网络的操作
    pass
else:
    # 处理连接失败的情况
    print("请检查 Wi-Fi 配置或信号强度")
