# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 19:36:29 2023

@author: Programmer
"""
num1 = input("enter the first no: ")
num2 = input("enter the second no ")

#oprators  < ,> , == , + , - .* ,/ ,% etc

# printing which is greater or smaller 
if (float(num1) > float(num2)) :
    print("Greater is ", num1)
else :
    print("Smaller no is ",num1)

print("*"*20)
    
print ("Sum of the numbers are ",float(num1)+float(num2))   
print("*"*20)
print ("Difference of the numbers are ",float(num1)-float(num2))   
print("*"*20)
print ("Multiplication  of the numbers are ",float(num1)*float(num2))   

print("*"*20)

if float(num2)==0:
    print("Cannot divide by zero")
else :
    print("Division of num1/num2", float(num1)/float(num2))


      
    