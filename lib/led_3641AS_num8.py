from machine import Pin
import time

# 定义引脚
DIN = Pin(13, Pin.OUT)  # 数据线
CLK = Pin(14, Pin.OUT)  # 时钟线
CS  = Pin(15, Pin.OUT)  # 片选线

# MAX7219 寄存器地址
REG_DECODE    = 0x09  # 0b00001001
REG_INTENSITY = 0x0A
REG_SCANLIMIT = 0x0B
REG_SHUTDOWN  = 0x0C
REG_DISPTEST  = 0x0F

# 自定义段码（共阴极数码管，格式：0bHABCDEFG → 对应段 dp,a,b,c,d,e,f,g）
# 共阴极段码表（二进制格式，最高位为小数点）
segments = {
    '0': 0b01111110,
    '1': 0b00110000,
    '2': 0b01101101,
    '3': 0b01111001,
    '4': 0b00110011,
    '5': 0b01011011,
    '6': 0b01011111,
    '7': 0b01110000,
    '8': 0b01111111,
    '9': 0b01111011,
    'E': 0b01001111,
    'r': 0b00000101,
    'o': 0b00011101,
    ' ': 0b00000000
}
segments_set = {'0','1','2','3','4','5','6','7','8','9','E','r','o',' '}


def has_element_not_in_list2(list1, list2):
    """
    判断 list1 中是否有元素不在 list2 中
    """
    if list1 is None or list2 is None:
        raise ValueError("list1 和 list2 不能为 None")
    set2 = set(list2)
    return any(e not in set2 for e in list1)


def reverse_str(text: str):
    """
    反转字符串
    """
    return ''.join(reversed(text))


def send_data(address, value):
    """
    向 MAX7219 发送 16 位数据（8位地址 + 8位数据）
    """
    # 组合地址和数据
    data = (address << 8) | value
    # 拉低片选以启动传输
    CS.off()
    # 逐位发送（高位先发）
    for i in range(15, -1, -1):
        bit = (data >> i) & 0x01
        DIN.value(bit)
        CLK.on()        # 时钟上升沿锁存数据
        CLK.off()
    # 拉高片选结束传输
    CS.on()

def init_max7219():
    """
    初始化 MAX7219 配置
    """
    send_data(REG_SHUTDOWN, 0x01)    # 退出省电模式（0x00=关机，0x01=开机）
    send_data(REG_DECODE, 0x00)      # 关闭所有解码模式（允许自定义段码）
    send_data(REG_SCANLIMIT, 0x07)   # 扫描全部 8 位数码管
    send_data(REG_INTENSITY, 0x04)   # 亮度设置（0x00~0x0F）
    send_data(REG_DISPTEST, 0x01)    # 显示测试
    time.sleep(0.5)
    send_data(REG_DISPTEST, 0x00)    # 关闭显示测试
    for i in range(8):
        send_data(i+1, 0x00)
    time.sleep(0.1)

def display_char(position, char_code):
    """
    在指定位置显示自定义字符
    :param position: 数码管位置（0~7，0=最右侧）
    :param char_code: 自定义段码（如 CHAR_F）
    """
    send_data(position, char_code)  # MAX7219 的位地址从 1 开始（1~8）

# 初始化 MAX7219
init_max7219()

def display_line(strs):
    if type(strs) == int or float:
        strs = str(strs)
    if has_element_not_in_list2(list(strs), list(segments_set|{'.'})) or '..' in strs or 0 > len(strs.replace('.','')) or 8 < len(strs.replace('.','')) or (strs.startswith('.') and strs.count(".") != 1):
        for n, i in enumerate('Error'):
            display_char(8-n, segments[i])
    else:
        display_str_list = []
        if strs.startswith('.'):
            strs = '0' + strs
        for t in strs:
            if t != '.':
                display_str_list.append(segments[t])
            else:
                display_str_list.append(display_str_list.pop()|0b10000000)
        for n, i in enumerate(display_str_list):
            display_char(8-n, i)
