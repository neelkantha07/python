from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pyautogui
import os

app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# HTML template
main_page = """
<html>
<head>
    <style>
        button {
            font-size: 24px;
            padding: 15px 30px;
            margin: 10px;
            border-radius: 8px;
            border: 2px solid #007BFF;
            background-color: #f0f0f0;
            cursor: pointer;
        }
        button:hover {
            background-color: #007BFF;
            color: white;
        }
        .special-key-row {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <h2>Android Keyboard</h2>
    <form action="/send" method="post">
        <input type="text" name="key" placeholder="Type here" autofocus 
               style="font-size: 24px; padding: 10px; width: 300px;">
        <button type="submit">Send</button>
    </form>
    <br>
    <h3>Special Keys</h3>
    <form action="/special_key" method="post">
        <div class="special-key-row">
            <button name="key" value="enter" type="submit">⏎ Enter</button>
            <button name="key" value="backspace" type="submit">⌫ Backspace</button>
            <button name="key" value="space" type="submit">␣ Space</button>
            <button name="key" value="tab" type="submit">⇥ Tab</button>
            <button name="key" value="delete" type="submit">🗑 Delete</button>
        </div>
        <div class="special-key-row">
            <button name="key" value="up" type="submit">↑ Up</button>
            <button name="key" value="down" type="submit">↓ Down</button>
            <button name="key" value="left" type="submit">← Left</button>
            <button name="key" value="right" type="submit">→ Right</button>
        </div>
        <div class="special-key-row">
            <button name="key" value="ctrl" type="submit">Ctrl</button>
            <button name="key" value="shift" type="submit">Shift</button>
        </div>
        <h3>Key Combinations</h3>
        <div class="special-key-row">
            <button name="key" value="ctrl+c" type="submit">Ctrl+C</button>
            <button name="key" value="ctrl+v" type="submit">Ctrl+V</button>
            <button name="key" value="shift+up" type="submit">Shift+↑</button>
            <button name="key" value="shift+down" type="submit">Shift+↓</button>
        </div>
    </form>
</body>
</html>
"""

login_page = """
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
PASSWORD_HASH = generate_password_hash("keyboard@2025")  # Store hashed password

@app.route("/")
def home():
    # Check if user is logged in
    if "username" in session:
        return render_template_string(main_page)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()  # Strip any extra whitespace
        password = request.form["password"].strip()  # Strip any extra whitespace
        
        # Validate username and password
        if username == USER and check_password_hash(PASSWORD_HASH, password):
            session["username"] = username  # Store username in session
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
    # Handle individual special keys
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
    # Handle combinations
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
    #app.run(host="0.0.0.0", port=5000, ssl_context='adhoc')  # Use SSL context for HTTPS
    app.run(host="0.0.0.0", port=5000)
