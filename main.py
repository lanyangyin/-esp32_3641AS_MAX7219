import network
import time
from lib.led_3641AS_num8 import display_char, display_line  # 3641AS的LED数码管，用了MAX7219 寄存器
import ntptime
import _thread

TIMEZONE_OFFSET = 8  # 东八区


def sync_ntp_time(retries=30):
    """
    同步 NTP 时间
    """
    for _ in range(retries):
        try:
            ntptime.settime()  # 默认使用 pool.ntp.org
            print("NTP 时间同步成功!")
            return True
        except Exception as e:
            print("NTP 同步失败:", e)
            time.sleep(2)
    return False


def get_local_time():
    """
    获取本地时间（带时区调整）
    """
    # 计算时区偏移（秒）
    utc_offset = TIMEZONE_OFFSET * 3600
    # 获取当前时间戳并调整时区
    local_time = time.localtime(time.time() + utc_offset)
    # 格式化为字符串：YYYY-MM-DD HH:MM:SS
    # return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*local_time)
    return local_time


# 主程序
try:
    ntptime.host = "ntp.aliyun.com"
    sync_ntp_time()
    while True:
        year, month, day, hour, minut, second, week, day_of_year = get_local_time()
        print("当前时间:", get_local_time())
        display_line("{:02d}".format((hour)) + ". {:02d}".format((minut)) + ". {:02d}".format((second)))
        time.sleep(1)
except KeyboardInterrupt:
    print("程序已终止")
except Exception as e:
    print("运行错误:", e)
