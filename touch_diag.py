import lvgl as lv
import waveshare as board
import time

lv.init()
board.init()

print("Touch Diagnostic Active.")
print("Tap the screen to see coordinates...")

while True:
    t = board.read_touch()
    if t:
        print("Raw Touch:", t)
    time.sleep_ms(50)
