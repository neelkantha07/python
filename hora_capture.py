import pyautogui
import time
import pyperclip
import pygetwindow as gw
import clippbor_to_csv as clip

day = 3285
# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False
# Function to perform the task


def perform_task(program_name):
    # Find the program's window
    program_window = gw.getWindowsWithTitle(program_name)

    if len(program_window) == 0:
        print(f"Window for '{program_name}' not found.")
        return

    # Activate and maximize the program's window
    program = program_window[0]
   # program.activate()
    program.maximize()
    time.sleep(1)  # Adjust sleep time as needed
    for i in range(day):
        # Move mouse to the right click
        screenWidth, screenHeight = pyautogui.size()
        # Adjust the coordinates as needed
        pyautogui.moveTo(screenWidth * .55, screenHeight * .55)

        # Right click
        pyautogui.click(button='right')
        time.sleep(0)  # Adjust sleep time as needed

        # Move mouse to the last option
        # Adjust the coordinates as needed
        pyautogui.moveTo(screenWidth * .65, screenHeight * .90)
        # time.sleep(1)
        # Left click the last option
        pyautogui.click()
        # time.sleep(1)  # Adjust sleep time as needed

        # Copy clipboard contents
        #pyautogui.hotkey('ctrl', 'c')
        # time.sleep(1)  # Adjust sleep time as needed

        # Write clipboard contents to a text file
        clipboard_text = pyperclip.paste()
        with open('clipboard_content.txt', 'a') as file:
            file.write(clipboard_text)
        # Adjust the coordinates as needed
        pyautogui.moveTo(screenWidth * .69, screenHeight * .05)
        pyautogui.click()
        # process the clipboard data
        clip.process_clipboard_data(
            "clipboard_dump.csv", "planet_total_values.csv")
        # store the navtara data
        clip.update_navtara_with_total_values(
            "navtara.csv", "planet_total_values.csv")

        # time.sleep(1)
# Call the function to perform the task
# Replace 'Jagannatha Hora' with the actual name of the program window
perform_task("Jagannatha Hora")
# =================================================================


# ------------------------------------------------------------------------------
