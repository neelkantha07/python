# -*- coding: utf-8 -*-
"""
Created on Thu May  4 09:41:04 2023

@author: Programmer
"""

# Example of for loop in Python

# # Iterating over a range of numbers
# for i in range(1,11):
#     print(i)




# Iterating over a string
mystring= "Jai ma "
for char in mystring:
    print(char)
    
    
    
    
    
# Iterating over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)


# # Using the enumerate function to iterate over a list with index
# for i, fruit in enumerate(fruits):
#     print(f"Index {i}: {fruit}")

# # Using the zip function to iterate over multiple lists simultaneously
# numbers = [1, 2, 3]
# letters = ["a", "b", "c"]
# for number, letter in zip(numbers, letters):
#     print(f"{number}: {letter}")

# # Using a for loop with a conditional statement
# for i in range(10):
#     if i % 2 == 0:
#         print(f"{i} is even")
#     else:
#         print(f"{i} is odd")

# # Using a nested for loop to iterate over multiple lists
# colors = ["red", "green", "blue"]
# sizes = ["small", "medium", "large"]
# for color in colors:
#     for size in sizes:
#         print(f"{color} {size}")
