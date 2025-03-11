from machine import Pin, SPI
import time

# 正确字典定义（键值对）
SEGMENT_CODE = {
    '0': 0b01111110, '1': 0b00110000, '2': 0b01101101, '3': 0b01111001,
    '4': 0b00110011, '5': 0b01011011, '6': 0b01011111, '7': 0b01110000,
    '8': 0b01111111, '9': 0b01111011, 'E': 0b01001111, 'r': 0b00000101,
    'o': 0b00011101, ' ': 0b00000000, '-': 0b00000001, '—': 0b00000001}


class Led8_3641AS_Max7219:

    def __init__(self, pin_sck: int = 14, pin_mosi: int = 13, pin_cs: int = 15, n: int = 1):
        self.spi = SPI(1, baudrate=500000, polarity=0, phase=0, sck=Pin(pin_sck), mosi=Pin(pin_mosi))
        self.cs = Pin(pin_cs, Pin.OUT)
        self.n = n

    def send_command(self, rd):
        self.cs.value(0)
        self.spi.write(bytearray(rd))
        self.cs.value(1)

    def init_max7219(self):
        self.send_command([0x0C, 0x01] * self.n)  # 开启正常模式
        self.send_command([0x09, 0x00] * self.n)  # 禁用解码
        self.send_command([0x0B, 0x07] * self.n)  # 扫描8位
        self.send_command([0x0A, 0x0F] * self.n)  # 亮度
        self.send_command([0x0F, 0x00] * self.n)  # 关闭测试模式

    def display_singleLine_LR(self, text: str):
        text = str(text) + (self.n * 8 - len(text.replace('.', ''))) * ' '
        for i in range(self.n):
            for ni in range(8):
                cmd = [0, 0] * (self.n - i - 1) + [8 - ni, SEGMENT_CODE[' ']] + [0, 0] * i
                self.send_command(cmd)
        # text = ''.join(reversed(str(text)))
        print(text)
        for ib in range(self.n):
            for ni in range(8):
                time.sleep_ms(80)
                print((ib+1) * 8 + ni)
                cmd = [0, 0] * (self.n - ib - 1) + [8 - ni, SEGMENT_CODE[text[ib * 8 + ni]]] + [0, 0] * ib
                self.send_command(cmd)


if __name__ == '__main__':
    L3M = Led8_3641AS_Max7219(n=2)
    # 初始化并测试
    L3M.init_max7219()
    while True:
        L3M.display_singleLine_LR('5201314 11451451')
        time.sleep(2)
        L3M.display_singleLine_LR('98 0543210987654')
        time.sleep(2)
