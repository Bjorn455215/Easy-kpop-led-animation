#MIDZY 應援燈(成功)
from machine import Pin, SPI, I2C
import ssd1306
import time

# --- 常量定義 ---
DECODEMODE = const(9)
INTENSITY = const(10) 
SCANLIMIT = const(11) 
SHUTDOWN = const(12)  
DISPLAYTEST = const(15)

# --- 圖案資料庫 ---
ITZY_CHARS = {
    'I': (0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C),
    'T': (0xFF, 0xFF, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18),
    'Z': (0xFE, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x7F, 0x00),
    'Y': (0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0x18)
}

ICON_I     = (0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18)
ICON_HEART = (0x00, 0x66, 0xFF, 0xFF, 0xFF, 0x7E, 0x3C, 0x18)
ICON_SMALL_HEART = (0x00, 0x00, 0x24, 0x7E, 0x3C, 0x18, 0x00, 0x00)
ICON_U     = (0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x7E, 0x3C)

# --- 硬體設置 ---
# 使用 D0
touch_sensor = Pin(16, Pin.IN)

# OLED 初始化 (D1, D2)
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# 點陣屏初始化 (D5, D7, D8)
cs = Pin(15, Pin.OUT)
spi = SPI(1, baudrate=1000000)

# --- 副程式區 ---
def max7219(reg, data):
    cs.value(0)
    spi.write(bytes([reg, data]))
    cs.value(1)
    
def init():
    for reg, data in (
        (DISPLAYTEST, 0),
        (SCANLIMIT, 7),
        (INTENSITY, 2),
        (DECODEMODE, 0),
        (SHUTDOWN, 1)
    ):
        max7219(reg, data)
        
    for i in range(8):
        max7219(i + 1, 0)
        
    oled.fill(0)
    oled.show()
        
def display_pattern(pattern):
    for j in range(8):
        val = pattern[j] if pattern is not None else 0
        max7219(j + 1, val)
        
#動畫腳本
animation_script = [
    (ITZY_CHARS['I'], "I", 0.5), (ITZY_CHARS['T'], "IT", 0.5),
    (ITZY_CHARS['Z'], "ITZ", 0.5), (ITZY_CHARS['Y'], "ITZY", 1.0),
    (None, "ITZY", 0.5),
    (ICON_I, "I", 0.8),
    (ICON_HEART, "LOVE", 0.4), (ICON_SMALL_HEART, "LOVE", 0.3),
    (ICON_HEART, "LOVE", 0.4), (ICON_SMALL_HEART, "LOVE", 0.3),
    (ICON_HEART, "LOVE", 0.6),
    (ICON_U, "YOU", 1.5)
]    

#狀態變數
playing = False
step = 0
last_touch_state = 0  #上次狀態
next_frame_time = 0

#主程式 
init()
oled.text("ITZY TOUCH BOX", 10, 20)
oled.text("READY TO GLOW", 15, 40)
oled.show()
print("Touch Sensor Active on D6. Monitoring...")

while True:
    current_state = touch_sensor.value()
    
    # 偵測觸摸瞬間 (0 -> 1)
    if current_state != last_touch_state:
        # Debug 輸出
        print("Sensor Changed: {}".format(current_state))
        
        if current_state == 1 and last_touch_state == 0:
            playing = not playing
            if playing:
                print("ACTION: PLAY")
                next_frame_time = time.ticks_ms()
            else:
                print("ACTION: PAUSE")
            
            time.sleep(0.15) # 輕微防抖動
        last_touch_state = current_state

    # 播放邏輯
    if playing:
        now = time.ticks_ms()
        if time.ticks_diff(now, next_frame_time) >= 0:
            pattern, text, delay = animation_script[step]
            
            display_pattern(pattern)
            oled.fill(0)
            oled.text("FOR MY QUEEN:", 10, 10)
            oled.text(text, 45, 35)
            oled.show()
            
            next_frame_time = time.ticks_add(now, int(delay * 1000))
            
            step += 1
            if step >= len(animation_script):
                step = 0
                playing = False # 播完停止
                print("Animation Finished!")
                # 清除點陣屏
                display_pattern(None)
                oled.fill(0)
                oled.text("FINISHED!", 30, 25)
                oled.text("Touch to Restart", 5, 45)
                oled.show()

    time.sleep(0.01)
