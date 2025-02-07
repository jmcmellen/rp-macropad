# SPDX-FileCopyrightText: Copyright (c) 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Rainbow LED grid layout demo for MacroPad. Displays the key pressed in a grid matching the key
layout on the built-in display, and animates a rainbow the first time you press a key and turns it
off on the next press.
"""
import displayio
import terminalio
import time
import random
import bitmaptools
from adafruit_ticks import ticks_ms, ticks_add, ticks_less, ticks_diff
from rainbowio import colorwheel
from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_macropad import MacroPad
from adafruit_ducky import Ducky
#from adafruit_hid.mouse import Mouse
from adafruit_bitmap_font import bitmap_font
import math

def draw_cube(bitmap, display):
    r[0] = r[0] + pi / 180.0
    r[1] = r[1] + pi / 180.0
    r[2] = r[2] + pi / 180.0
    if (r[0] >= 360.0 * pi / 180.0):
        r[0] = 0
    if (r[1] >= 360.0 * pi / 180.0):
        r[1] = 0
    if (r[2] >= 360.0 * pi / 180.0):
        r[2] = 0

    for i in range(8):
        px2 = px[i]
        py2 = math.cos(r[0]) * py[i] - math.sin(r[0]) * pz[i]
        pz2 = math.sin(r[0]) * py[i] + math.cos(r[0]) * pz[i]

        px3 = math.cos(r[1]) * px2 + math.sin(r[1]) * pz2
        py3 = py2
        pz3 = -math.sin(r[1]) * px2 + math.cos(r[1]) * pz2

        ax = math.cos(r[2]) * px3 - math.sin(r[2]) * py3
        ay = math.sin(r[2]) * px3 + math.cos(r[2]) * py3
        az = pz3 - 150

        p2x[i] = width / 2 + ax * size / az
        p2y[i] = height / 2 + ay * size / az

    bitmap.fill(0)

    for i in range(3):
        bitmaptools.draw_line(bitmap, int(p2x[i]),   int(p2y[i]),   int(p2x[i+1]), int(p2y[i+1]), 1)
        bitmaptools.draw_line(bitmap, int(p2x[i+4]), int(p2y[i+4]), int(p2x[i+5]), int(p2y[i+5]), 1)
        bitmaptools.draw_line(bitmap, int(p2x[i]),   int(p2y[i]),   int(p2x[i+4]), int(p2y[i+4]), 1)

    bitmaptools.draw_line(bitmap, int(p2x[3]), int(p2y[3]), int(p2x[0]), int(p2y[0]), 1)
    bitmaptools.draw_line(bitmap, int(p2x[7]), int(p2y[7]), int(p2x[4]), int(p2y[4]), 1)
    bitmaptools.draw_line(bitmap, int(p2x[3]), int(p2y[3]), int(p2x[7]), int(p2y[7]), 1)
    display.refresh()

size = 600
width = 128
height = 64
pi = math.pi

d = 3
px = [-d,  d,  d, -d, -d,  d,  d, -d]
py = [-d, -d,  d,  d, -d, -d,  d,  d]
pz = [-d, -d, -d, -d,  d,  d,  d,  d]

p2x = [0,0,0,0,0,0,0,0]
p2y = [0,0,0,0,0,0,0,0]
r = [0,0,0]

macropad = MacroPad()
duck = Ducky('duckyscript.txt', macropad.keyboard, macropad.keyboard_layout)
macropad.red_led = True
red_led_deadline = ticks_add(ticks_ms(), 1000)
font = bitmap_font.load_font('fonts/PixelCarnageMonoTT-12.bdf')
main_group = displayio.Group()
blank_group = displayio.Group()
draw_group = displayio.Group()
macropad.display.bus.send(int(0xAF), b"")
macropad.display.show(main_group)
title = label.Label(
    y=2,
    font=font, #terminalio.FONT,
    color=0x0,
    text="      KEYPRESSES      ",
    background_color=0xFFFFFF,
)
layout = GridLayout(x=0, y=10, width=128, height=54, grid_size=(3, 4), cell_padding=5)
labels = []
for _ in range(12):
    labels.append(label.Label(font, text=""))# terminalio.FONT, text=""))

for index in range(12):
    x = index % 3
    y = index // 3
    layout.add_content(labels[index], grid_position=(x, y), cell_size=(1, 1))

main_group.append(title)
main_group.append(layout)

# Draw on the screen
bitmap = displayio.Bitmap(macropad.display.width, macropad.display.height, 2)
palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xffffff
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
draw_group.append(tile_grid)

lit_keys = [False] * 12
wheel_offset = 0
deadline = ticks_add(ticks_ms(), 10000)
last_encoder_pos = macropad.encoder

z = list(range(0, 12))
q = list()
while len(z) > 0:
    w = random.choice(z)
    z.remove(w)
    q.append(w)

while True:
    if not ticks_less(ticks_ms(), red_led_deadline):
        macropad.red_led = not macropad.red_led
        red_led_deadline = ticks_add(ticks_ms(), random.choice([10, 25, 40, 65, 75, 80, 100, 250, 300]))
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        break
        # macropad.display.show(main_group)
        macropad.display.bus.send(int(0xAF), b"")
        deadline = ticks_add(ticks_ms(), 5000)

    if macropad.encoder != last_encoder_pos:
        if macropad.encoder > last_encoder_pos:
            encoder_inc = True
        else:
            encoder_inc = False
        last_encoder_pos = macropad.encoder
        # macropad.display.show(main_group)
        macropad.display.bus.send(int(0xAF), b"")
        deadline = ticks_add(ticks_ms(), 5000)
        if encoder_inc:
            macropad.consumer_control.press(macropad.ConsumerControlCode.VOLUME_INCREMENT)
        else:
            macropad.consumer_control.press(macropad.ConsumerControlCode.VOLUME_DECREMENT)
        time.sleep(0.05)
        macropad.consumer_control.release()

    key_event = macropad.keys.events.get()
    if key_event:
        if key_event.pressed:
            #macropad.display.show(main_group)
            macropad.display.bus.send(int(0xAF), b"")
            labels[key_event.key_number].text = "KEY{}".format(key_event.key_number)
            print(labels[key_event.key_number].text)
            # Turn the LED on with the first press, and off with the second press.
            lit_keys[key_event.key_number] = not lit_keys[key_event.key_number]
            # time.sleep(0.5)
            deadline = ticks_add(ticks_ms(), 5000)
            if key_event.key_number == 0:
                result = True
                while result is not False:
                    result = duck.loop()
                duck = Ducky('duckyscript.txt', macropad.keyboard, macropad.keyboard_layout)
            if key_event.key_number == 1:
                macropad.mouse.move(-2, 0, 0)
            if key_event.key_number == 3:
                # macropad.keyboard.press(macropad.Keycode.LEFT_ALT, macropad.Keycode.A)
                time.sleep(0.05)
                # macropad.keyboard.release_all()
                for i in range(0,12):
                    lit_keys[i] = True
                deadline = ticks_add(ticks_ms(), 90000)
                macropad.display.show(draw_group)
            if key_event.key_number == 4:
                for i in range(0,12):
                    if i != 4:
                        lit_keys[i] = not lit_keys[i]
            if key_event.key_number == 9:
                macropad.consumer_control.press(macropad.ConsumerControlCode.SCAN_PREVIOUS_TRACK)
                time.sleep(0.05)
                macropad.consumer_control.release()
            if key_event.key_number == 10:
                macropad.consumer_control.press(macropad.ConsumerControlCode.PLAY_PAUSE)
                time.sleep(0.05)
                macropad.consumer_control.release()
            if key_event.key_number == 11:
                macropad.consumer_control.press(macropad.ConsumerControlCode.SCAN_NEXT_TRACK)
                time.sleep(0.05)
                macropad.consumer_control.release()
        else:
            labels[key_event.key_number].text = ""

    draw_cube(bitmap, macropad.display)
    wheel_offset += 2  # Glow thru the colorwheel.
    for pixel in range(12):
        if lit_keys[pixel]:  # Animate the specific LED.
            macropad.pixels[pixel] = colorwheel((q[pixel] / 12 * 256) + wheel_offset)
        else:
            macropad.pixels[pixel] = 0  # Otherwise, turn the LED off.
    if not ticks_less(ticks_ms(), deadline):
        macropad.display.show(main_group)
        macropad.display.bus.send(int(0xAE), b"")
    else:
        pass
    #break
macropad.display.bus.send(int(0xAF), b"")
macropad.display.auto_refresh = True
bitmap.fill(0)
macropad.display.show(draw_group)
bitmaptools.draw_line(bitmap, 1, 1, 100, 50, 1)
time.sleep(0.75)
bitmap.fill(0)
bitmaptools.draw_line(bitmap, 100, 1, 1, 50, 1)
time.sleep(1.0)
bitmap.fill(0)
macropad.display.auto_refresh = False
for x in range(1, 119):
    for y in range(30, 50):
        bitmap[x, y] = 1
    time.sleep(0.02)
    f = macropad.display.refresh()
time.sleep(5.0)

deadline = ticks_add(ticks_ms(), 90000)
#for y in range(32768):
while ticks_less(ticks_ms(), deadline):
    draw_cube(bitmap, macropad.display)
