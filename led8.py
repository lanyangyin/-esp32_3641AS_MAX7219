from machine import Pin, SPI
import time

# 正确字典定义（键值对）
SEGMENT_CODE = {
    '0': 0b01111110, '1': 0b00110000, '2': 0b01101101, '3': 0b01111001,
    '4': 0b00110011, '5': 0b01011011, '6': 0b01011111, '7': 0b01110000,
    '8': 0b01111111, '9': 0b01111011, 'E': 0b01001111, 'r': 0b00000101,
    'o': 0b00011101, ' ': 0b00000000, '-': 0b00000001, '—': 0b00000001,
    'A': 0b01110111
}


class Led8_3641AS_Max7219:
    """
    驱动由两个4位的3641AS数码管和一个MAX7219寄存器组成的8位数码管元件
    """

    def __init__(self, pin_sck: int = 14, pin_mosi: int = 13, pin_cs: int = 15, n: int = 1):
        """
        初始化
        :param pin_sck: SPI时钟引脚
        :param pin_mosi: SPI数据引脚
        :param pin_cs: 片选引脚
        :param n: 这个8位数码管元件的数量，需要驱动几个八位数码管
        """
        self.spi = SPI(1, baudrate=500000, polarity=0, phase=0, sck=Pin(pin_sck), mosi=Pin(pin_mosi))
        self.cs = Pin(pin_cs, Pin.OUT)
        self.n = n

    def init_max7219(self):
        """
        初始化MAX7219
        """
        self.send_command([0x0C, 0x01] * self.n)  # 开启正常模式
        self.send_command([0x09, 0x00] * self.n)  # 禁用解码
        self.send_command([0x0B, 0x07] * self.n)  # 扫描8位
        self.send_command([0x0A, 0x0F] * self.n)  # 亮度, 范围0x00~0x0F
        self.send_command([0x0F, 0x00] * self.n)  # 关闭测试模式

    def send_command(self, rd: list):
        """
        发送命令
        :param rd: 命令列表
        """
        self.cs.value(0)
        self.spi.write(bytearray(rd))
        self.cs.value(1)

    def clear(self, methods: str = 'ML', direction: str = 'LR', interval: float = 0):
        """
        清除屏幕
        :param methods: 清除方法，'SL'表示逐行清除，'ML'表示整屏清除
        :param direction: 清除方向，'LR'表示从左到右，'RL'表示从右到左
        :param interval: 清除间隔，单位秒
        """
        if methods == 'SL':
            for i in range(self.n):
                for ni in range(8):
                    time.sleep(interval)
                    if direction == 'LR':
                        cmd = [0, 0] * (self.n - i - 1) + [8 - ni, SEGMENT_CODE[' ']] + [0, 0] * i
                        self.send_command(cmd)
                    elif direction == 'RL':
                        cmd = [0, 0] * i + [ni + 1, SEGMENT_CODE[' ']] + [0, 0] * (self.n - i - 1)
                        self.send_command(cmd)
        elif methods == 'ML':
            for ni in range(8):
                time.sleep(interval)
                if direction == 'LR':
                    cmd = [8 - ni, SEGMENT_CODE[' ']] * self.n
                    self.send_command(cmd)
                elif direction == 'RL':
                    cmd = [ni + 1, SEGMENT_CODE[' ']] * self.n
                    self.send_command(cmd)

    def display_singleLine_LR(self, text: str, clear: bool = True, interval: float = 0, brightness: int = 15):
        """
        单行显示文本，从左到右显示
        :param brightness 亮度
        :param interval: 每个字符显示间隔，单位秒
        :param clear: 是否清除屏幕
        :param text: 要显示的文本
        """
        # 清除屏幕
        if clear:
            self.clear()
        # 亮度, 范围0x00~0x0F
        self.send_command([0x0A, brightness] * self.n)
        # 显示文本
        # text = ''.join(reversed(str(text)))
        text = str(text) + (self.n * 8 - len(text.replace('.', ''))) * ' '  # 补齐空格
        for ib in range(self.n):
            for ni in range(8):
                time.sleep(interval)
                cmd = [0, 0] * (self.n - ib - 1) + [8 - ni, SEGMENT_CODE[text[ib * 8 + ni]]] + [0, 0] * ib  # 逆序显示
                self.send_command(cmd)


if __name__ == '__main__':
    L3M = Led8_3641AS_Max7219(n=2)  # 初始化并测试
    L3M.init_max7219()
    while True:
        L3M.display_singleLine_LR('5201314o114514 1', interval=0.1, brightness=15)
        time.sleep(2)
        L3M.display_singleLine_LR('98r05432109876AE', clear=True, brightness=2)
        time.sleep(2)
