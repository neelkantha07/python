# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 16:44:33 2025

@author: Mahadev
"""

from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pyautogui
import os

app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# HTML templates
main_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Android Keyboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f9f9f9;
            padding: 20px;
        }
        h2 {
            font-size: 36px;
            color: #007BFF;
        }
        input[type="text"] {
            font-size: 28px;
            padding: 15px;
            width: 400px;
            margin: 20px 0;
            border: 2px solid #ddd;
            border-radius: 10px;
        }
        button {
            font-size: 28px;
            padding: 20px;
            margin: 10px;
            border-radius: 50%;
            border: 2px solid #007BFF;
            background-color: #f0f0f0;
            cursor: pointer;
            width: 100px;
            height: 100px;
        }
        button:hover {
            background-color: #007BFF;
            color: white;
        }
        .special-keys {
            margin-top: 20px;
        }
        .key-row {
            margin: 10px;
        }
    </style>
</head>
<body>
    <h2>Android Keyboard</h2>
    <form action="/send" method="post">
        <input type="text" name="key" placeholder="Type here" autofocus>
        <button type="submit" style="width: auto; padding: 10px 30px; border-radius: 8px;">Send</button>
    </form>
    <div class="special-keys">
        <h3>Special Keys</h3>
        <form action="/special_key" method="post">
            <div class="key-row">
                <button name="key" value="enter" type="submit"><i class="fas fa-level-down-alt"></i><br>Enter</button>
                <button name="key" value="backspace" type="submit"><i class="fas fa-backspace"></i><br>Backspace</button>
                <button name="key" value="space" type="submit"><i class="fas fa-space-shuttle"></i><br>Space</button>
                <button name="key" value="tab" type="submit"><i class="fas fa-indent"></i><br>Tab</button>
                <button name="key" value="delete" type="submit"><i class="fas fa-trash-alt"></i><br>Delete</button>
            </div>
            <div class="key-row">
                <button name="key" value="up" type="submit"><i class="fas fa-arrow-up"></i><br>Up</button>
                <button name="key" value="down" type="submit"><i class="fas fa-arrow-down"></i><br>Down</button>
                <button name="key" value="left" type="submit"><i class="fas fa-arrow-left"></i><br>Left</button>
                <button name="key" value="right" type="submit"><i class="fas fa-arrow-right"></i><br>Right</button>
            </div>
            <div class="key-row">
                <button name="key" value="ctrl" type="submit"><i class="fas fa-keyboard"></i><br>Ctrl</button>
                <button name="key" value="shift" type="submit"><i class="fas fa-chevron-up"></i><br>Shift</button>
            </div>
            <h3>Key Combinations</h3>
            <div class="key-row">
                <button name="key" value="ctrl+c" type="submit"><i class="fas fa-copy"></i><br>Ctrl+C</button>
                <button name="key" value="ctrl+v" type="submit"><i class="fas fa-paste"></i><br>Ctrl+V</button>
                <button name="key" value="shift+up" type="submit"><i class="fas fa-arrow-up"></i><br>Shift+↑</button>
                <button name="key" value="shift+down" type="submit"><i class="fas fa-arrow-down"></i><br>Shift+↓</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

login_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form action="/login" method="post">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
        <br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
        <br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

# Load credentials securely (replace with environment variables or a config file in production)
USER = "user"
PASSWORD_HASH = generate_password_hash("passw0rd")  # Store hashed password

@app.route("/")
def home():
    if "username" in session:
        return render_template_string(main_page)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if username == USER and check_password_hash(PASSWORD_HASH, password):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials. Please try again.", 403
    return render_template_string(login_page)

@app.route("/send", methods=["POST"])
def send_key():
    key = request.form["key"]
    pyautogui.typewrite(key)
    return render_template_string(main_page)

@app.route("/special_key", methods=["POST"])
def special_key():
    key = request.form["key"]
    if key == "enter":
        pyautogui.press("enter")
    elif key == "backspace":
        pyautogui.press("backspace")
    elif key == "space":
        pyautogui.press("space")
    elif key == "tab":
        pyautogui.press("tab")
    elif key == "delete":
        pyautogui.press("delete")
    elif key == "up":
        pyautogui.press("up")
    elif key == "down":
        pyautogui.press("down")
    elif key == "left":
        pyautogui.press("left")
    elif key == "right":
        pyautogui.press("right")
    elif key == "ctrl":
        pyautogui.keyDown("ctrl")
        
        pyautogui.keyUp("ctrl")
    elif key == "shift":
        pyautogui.keyDown("shift")
        pyautogui.keyUp("shift")
    elif key == "ctrl+c":
        pyautogui.hotkey("ctrl", "c")
    elif key == "ctrl+v":
        pyautogui.hotkey("ctrl", "v")
    elif key == "shift+up":
        pyautogui.hotkey("shift", "up")
    elif key == "shift+down":
        pyautogui.hotkey("shift", "down")
    return render_template_string(main_page)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Use HTTP
