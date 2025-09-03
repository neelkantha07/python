import asyncio
import websockets
import json
import pyautogui
import socket
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController, Button

# Initialize keyboard and mouse controllers
keyboard = KeyboardController()
mouse = MouseController()
screen_width, screen_height = pyautogui.size()
sensitivity = 2.990

async def handler(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            #print(f"Received message: {message}")
            data = json.loads(message)

            if data['type'] == 'mouse':
                if data['command'] == 'move':
                    dx = data['dx']*sensitivity
                    dy = data['dy']* sensitivity
                    # Ensure the mouse stays within screen boundaries
                    mouse_x, mouse_y = pyautogui.position()  # Get current mouse position
                    new_x = max(0, min(mouse_x + dx, screen_width - 1))
                    new_y = max(0, min(mouse_y + dy, screen_height - 1))

                    pyautogui.moveTo(new_x, new_y)
                    
                elif data['command'] == 'click':
                    button = data['button']
                    if button == 'left':
                        mouse.click(Button.left, 1)
                    elif button == 'right':
                        mouse.click(Button.right, 1)

            elif data['type'] == 'keyboard':
                text = data['text']
                if text == 'backspace':
                    pyautogui.press("backspace")
                elif text == 'enter':
                    pyautogui.press("enter")
                elif text=="escape":
                    pyautogui.press('esc')
                elif text == "ctrl+c":
                    pyautogui.hotkey("ctrl", "c")
                elif text == "ctrl+v":
                    pyautogui.hotkey("ctrl", "v")
                elif text == "ctrl+a":
                    pyautogui.hotkey("ctrl", "a")
                elif text == "ctrl+a":
                     pyautogui.hotkey("ctrl", "a")
                elif text == "ctrl+z":
                      pyautogui.hotkey("ctrl", "z")
                elif text == "ctrl+y":
                  pyautogui.hotkey("ctrl", "y")
                elif text == "up":
                    pyautogui.press("up")
                elif text == "down":
                    pyautogui.press("down")
                elif text == "left":
                    pyautogui.press("left")
                elif text == "right":
                    pyautogui.press("right")
                elif text == "space":
                    pyautogui.press("space")
                elif text == "tab":
                    pyautogui.press("tab")
                elif text == "delete":
                    pyautogui.press("delete")    
                else:
                    keyboard.type(text)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Client disconnected")

async def main():
    # Set ping_interval and ping_timeout to None to disable the ping-pong mechanism
    server = await websockets.serve(handler, "0.0.0.0", 7000, ping_interval=None, ping_timeout=None)
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"WebSocket server running on ws://{ip_address}")

   # print("Server running on ws://0.0.0.0:7000",server)
    await server.wait_closed()

# Check if an event loop is running, and use it accordingly
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        # If no event loop is running, use asyncio.run
        if str(e) == "This event loop is already running":
            print("Using existing event loop")
            asyncio.ensure_future(main())
        else:
            raise
