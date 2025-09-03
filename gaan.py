# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 23:14:43 2024

@author: Mahadev
"""

import tkinter as tk
from tkinter import messagebox
import numpy as np
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def generate_gann_square(final_number, start_value, increment_value):
    size = int(final_number ** 0.5) + 1  # Determine the size of the matrix
    matrix = [[0] * size for _ in range(size)]
    
    num = start_value
    x, y = size // 2, size // 2  # Start from the center
    matrix[x][y] = num
    num += increment_value  # Increment by the specified value
    
    # Directions: left, up, right, down (clockwise)
    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    dir_index = 0
    steps = 1
    
    while num < start_value + final_number * increment_value:
        for _ in range(2):
            for _ in range(steps):
                x += directions[dir_index][0]
                y += directions[dir_index][1]
                if 0 <= x < size and 0 <= y < size:
                    matrix[x][y] = num
                    num += increment_value  # Increment by the specified value
            dir_index = (dir_index + 1) % 4
        steps += 1
    
    return matrix, size

def plot_gann_square(matrix, size, user_angle, figsize):
    fig, ax = plt.subplots(figsize=figsize)  # Use user-defined figure size
    
    # Plot the Gann Square
    cax = ax.matshow(np.array(matrix), cmap='Blues', vmin=0, vmax=size**2, alpha=0.6)
    
    # Draw the circle outside the matrix
    circle_radius = size * 0.7  # Adjust radius to ensure circle is outside the box
    circle = plt.Circle((size // 2, size // 2), circle_radius, color='red', fill=False)
    ax.add_artist(circle)
    
    # Center of the square
    x_center, y_center = size // 2, size // 2
    
    # Plot the predefined angles and the user-defined angle
    predefined_angles = [60, 120, 180, -60, -120, -360, 45, -45, 90, -90, -30,30]
    new_angles = [user_angle + shift for shift in predefined_angles]
    
    # Combine angles and plot
    all_angles = new_angles + [user_angle]

    # Function to plot a line for a given angle
    def plot_angle_line(angle, line_color, label=None):
        theta = np.radians(-angle)
        x_end1 = x_center + circle_radius * np.cos(theta)
        y_end1 = y_center + circle_radius * np.sin(theta)
        x_end2 = x_center - circle_radius * np.cos(theta)
        y_end2 = y_center - circle_radius * np.sin(theta)
        ax.plot([x_end1, x_end2], [y_end1, y_end2], color=line_color, linestyle='--')
        
        if label:
            ax.text(x_end1, y_end1, label, fontsize=10, color=line_color)
    
    # Plot predefined angles in blue
    for angle, shift in zip(new_angles, predefined_angles):
       plot_angle_line(angle, 'blue', label=f"{shift*-1}°")
    
    # Plot the user-defined angle in green
    plot_angle_line(user_angle, 'green', label=f"{user_angle}° (User)")
    
    # Annotate the values in the Gann square
    for i in range(size):
        for j in range(size):
            value = matrix[i][j]
            if value != 0:
                ax.text(j, i, str(value), ha='center', va='center', color='black')
    
    # Format the plot
    ax.set_xlim(-circle_radius, size + circle_radius)
    ax.set_ylim(size + circle_radius, -circle_radius)
    ax.set_xticks(range(size))
    ax.set_yticks(range(size))
    ax.set_xticklabels(range(1, size+1))
    ax.set_yticklabels(range(1, size+1))
    plt.grid(True)

    return fig


def display_gann_square():
    try:
        final_number = float(entry_number.get())
        angle = float(entry_angle.get())
        start_value =float(entry_start.get())
        subplot_x = int(entry_subplot_x.get())
        subplot_y = int(entry_subplot_y.get())
        increment_value = float(entry_increment.get())
        
        # Compute n2 based on the formula
        n1 = float(entry_comp.get())
        n2 = (math.sqrt(n1) + angle / 180) ** 2
        
        if final_number < 1 or angle < 0 or angle >= 360 or start_value < 1 or subplot_x < 1 or subplot_y < 1:
            raise ValueError
        
        matrix, size = generate_gann_square(final_number, start_value, increment_value)
        
        # Clear previous plot if any
        for widget in canvas_frame.winfo_children():
            widget.destroy()
        
        # Plot the Gann Square with the user-defined subplot size
        fig = plot_gann_square(matrix, size, angle, (subplot_x, subplot_y))
        
        # Create the plot canvas
        fig_canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        fig_canvas.draw()
        
        # Add the plot to the canvas
        canvas_widget = fig_canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Update canvas scroll region
        canvas_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Compute n2 values for predefined angles and display them
        predefined_angles = [60, 120, 180, -60, -120, -360, 45, -45, 90, -90, -30,30]
        
        n2_values = {theta: (math.sqrt(n1) + theta / 180) ** 2 for theta in predefined_angles}
        
        n2_text = "Predefined n2 values:\n"
        for theta, n2 in n2_values.items():
            n2_text += f"θ = {theta}°: n2 = {n2:.2f}\n"
        
        messagebox.showinfo("Computed n2 Values", n2_text)
        info_list.insert(tk.END, n2_text + "\n")
    
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid positive integer values for number and subplot size.")


def angle_calc():
    
    n1 = float(val1.get())
    n2 = float(val2.get())
    messagebox.showinfo("Computed Angle", ((math.sqrt(n1) - math.sqrt(n2)) * 180) % 360)
    
    
# GUI setup
root = tk.Tk()
root.title("Gann Square Generator with Angle Line and n2 Calculation")

# Create a frame to hold the canvas with scrollbars
scroll_frame = tk.Frame(root)
scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

info_frame = tk.Frame(root)
info_frame.grid(row=0, column=2, padx=1, pady=1, sticky='nse')

info_list = tk.Text(info_frame)
info_list.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

tk.Label(info_frame, text="Enter 1val").grid(row=1, column=0, sticky='nsw')
val1 = tk.Entry(info_frame)  # Create the Entry widget and store its reference
val1.grid(row=2, column=0, sticky='nsw')  # Then position it using grid

tk.Label(info_frame, text="Enter val2").grid(row=3, column=0, sticky='nsw')
val2 = tk.Entry(info_frame)
val2.grid(row=4, column=0, sticky='nsw')

tk.Button(info_frame, text="Angle cal", command=angle_calc).grid(row=5, column=0, sticky='nsw')

# Create the canvas with scrollbars
canvas = tk.Canvas(scroll_frame, width=1200, height=600)  # Increase canvas size
scroll_y = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(scroll_frame, orient="horizontal", command=canvas.xview)
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

canvas_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=canvas_frame, anchor="nw")

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

# Create the input fields
tk.Label(root, text="Enter the final number (n1):").grid(row=1, column=0, sticky='nsw')
entry_number = tk.Entry(root)
entry_number.grid(row=1, column=1, sticky='nsw')

tk.Label(root, text="Enter the starting value:").grid(row=2, column=0, sticky='nsw')
entry_start = tk.Entry(root)
entry_start.grid(row=2, column=1, sticky='nsw')

tk.Label(root, text="Enter the increment value:").grid(row=3, column=0, sticky='nsw')
entry_increment = tk.Entry(root)
entry_increment.grid(row=3, column=1, sticky='nsw')

tk.Label(root, text="Enter the angle in degrees:").grid(row=4, column=0, sticky='nsw')
entry_angle = tk.Entry(root)
entry_angle.grid(row=4, column=1, sticky='nsw')

tk.Label(root, text="Enter the subplot x-size:").grid(row=5, column=0, sticky='nsw')
entry_subplot_x = tk.Entry(root)
entry_subplot_x.grid(row=5, column=1, sticky='nsw')

tk.Label(root, text="Enter the subplot y-size:").grid(row=6, column=0, sticky='nsw')
entry_subplot_y = tk.Entry(root)
entry_subplot_y.grid(row=6 , column=1, sticky='nsw')

tk.Label(root, text="Enter the n1 Value:").grid(row=7, column=0, sticky='nsw')
entry_comp = tk.Entry(root)
entry_comp.grid(row=7, column=1, sticky='nsw')

# Add the generate button
generate_button = tk.Button(root, text="Generate Gann Square", command=display_gann_square)
generate_button.grid(row=8, column=0, pady=10)

# Start the GUI event loop
root.mainloop()
