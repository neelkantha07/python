# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 10:56:20 2023

@author: Programmer
"""
#infinite loop 
num=int(input("Enter the number "))
n=1
while (n<=10):
    r=num*n
    print ("%d * %d = %d" %(num,n,r) )
    n=n+1
     
print("Program has reached its end") 