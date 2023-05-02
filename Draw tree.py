# -*- coding: utf-8 -*-
"""
Created on Tue May  2 10:38:26 2023

@author: Mahadev
"""

import turtle

def draw_tree(t, branch_len):
    if branch_len > 5:
        t.forward(branch_len)
        t.right(20)
        draw_tree(t, branch_len-15)
        t.left(40)
        draw_tree(t, branch_len-15)
        t.right(20)
        t.backward(branch_len)

# Initialize Turtle
t = turtle.Turtle()
t.speed(0)
t.left(90)

# Draw the tree
draw_tree(t, 100)

# Exit the window
turtle.done()
