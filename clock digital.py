from tkinter import *
import time
import math

def create_clock():
    global canvas, hour_hand, minute_hand, second_hand
    clock_window = Tk()
    clock_window.title('Analog Clock')
    canvas = Canvas(clock_window, width=400, height=400, bg='white')
    canvas.pack(expand=YES, fill=BOTH)
    draw_dials()
    hour_hand = canvas.create_line(200, 200, 200, 150, width=5, arrow=LAST, fill='blue')
    minute_hand = canvas.create_line(200, 200, 200, 100, width=3, arrow=LAST, fill='green')
    second_hand = canvas.create_line(200, 200, 200, 50, width=2, arrow=LAST, fill='red')
    update_clock()
    clock_window.mainloop()

def draw_dials():
    global canvas
    center_x, center_y = 200, 200
    for i in range(12):
        angle = math.radians(30*i)
        x1 = center_x + 150 * math.sin(angle)
        y1 = center_y - 150 * math.cos(angle)
        x2 = center_x + 130 * math.sin(angle)
        y2 = center_y - 130 * math.cos(angle)
        canvas.create_line(x1, y1, x2, y2, width=2)
        label_x = center_x + 170 * math.sin(angle)
        label_y = center_y - 170 * math.cos(angle)
        canvas.create_text(label_x, label_y, text=str(i+1), font=('Arial', 12))

def update_clock():
    global canvas, hour_hand, minute_hand, second_hand
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    second = current_time.tm_sec
    hour_angle = math.radians((hour % 12) * 30 + minute / 2)
    minute_angle = math.radians(minute * 6)
    second_angle = math.radians(second * 6)
    canvas.coords(hour_hand, 200, 200, 200+70*math.sin(hour_angle), 200-70*math.cos(hour_angle))
    canvas.coords(minute_hand, 200, 200, 200+100*math.sin(minute_angle), 200-100*math.cos(minute_angle))
    canvas.coords(second_hand, 200, 200, 200+120*math.sin(second_angle), 200-120*math.cos(second_angle))
    canvas.after(1000, update_clock)

create_clock()
