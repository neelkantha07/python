# -*- coding: utf-8 -*-
"""
Created on Mon 
Aug 19 22:41:19 2024

@author: Mahadev
"""

import pyautogui
import time
import pyperclip




# Copy data from clipboard
clipboard_data = pyperclip.paste()

# Split the data by spaces and store it in a list
data_list = clipboard_data.split()

screenWidth, screenHeight = pyautogui.size()
#sleep time to set the screen

time.sleep(10)

# Iterate over the list and print each element
for item in data_list:
    pyautogui.moveTo(screenWidth * .1, screenHeight * .18)
    pyautogui.click(button='left')
    pyautogui.typewrite(item)
    pyautogui.press("enter")  # Press 'Enter' after each item to paste in a new line
    time.sleep(0.5)  # Sleep to ensure the paste operation is registered
