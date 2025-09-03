# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 16:18:55 2023

@author: Mahadev
"""

from numpy import loadtxt


def growth(rate,invest_val):
    
    return rate*invest_val

#read text file into NumPy array
rate = loadtxt('rates.txt')
#printing the data into the list


sip=[10000,20000]
investment_val=[]
growth_val=[growth(rate[0],sip[0])]
# first growth 
investment_val.append(sip[0]+growth_val[0])
print(investment_val[0])
count=1
f=open("result.txt","w")
""" 
#for single 20k investment
for i in range(1,len(rate)):
    #print(growth(rate[i], sip[0]))
    sip_val=sip[0]*count
    investment_val.append(investment_val[i-1]+
                          round(growth(rate[i],investment_val[i-1]+sip_val)+ sip_val,1))
    print("val of i: "+str(i+1) +"  investment amount : "+str(investment_val[i]))
"""
print("i: 1 "+"sip:"+str(sip[0])+"  investment amount : "+str(investment_val[0]))
f.writelines (str(1) + ","+str(sip[1])+","+str(rate[0])+","+str(0)+","+str(investment_val[0])+"\n")


#for buying more in dips with multiple capital PLEDGING
for i in range(1,len(rate)):
    #print(growth(rate[i], sip[0]))
    #calculating investment by growth val
    if(growth_val[i-1]>0):
        sip_val=sip[0]
        count=count+1
    else:
        sip_val=sip[1] +(sip[0]*count)+(count*28)# adjusting the interest 
        #sip_val=sip[1] 
        count=0
    
    growth_val.append(round(growth(rate[i],(investment_val[i-1]+sip_val)),1))
    investment_val.append(investment_val[i-1]+growth_val[i]+sip_val)
    print("i: "+str(i+1) + " sip:"+str(sip_val)+" Growth "+str(growth_val[i])+"  investment amount : "+str(investment_val[i]))
    f.writelines (str(i+1) + ","+str(sip_val)+","+str(rate[i])+","+str(growth_val[i])+","+str(investment_val[i])+"\n")
f.close()

"""
#for buying only in dips
for i in range(1,len(rate)):
    #print(growth(rate[i], sip[0]))
    #calculating investment by growth val
    if(rate[i-1]>0):
        #sip_val=sip[0]
        sip_val=0
        count=count+1
    else:
        sip_val=sip[1] +(sip[1]*count)+(56*count) # adjusting the interest 
        #sip_val=sip[1] 
        count=0
    
    growth_val.append(round(growth(rate[i],(investment_val[i-1]+sip_val)),1))
    investment_val.append(investment_val[i-1]+growth_val[i]+sip_val)
    print("i: "+str(i+1) + " sip:"+str(sip_val)+" Growth "+str(growth_val[i])+"  investment amount : "+str(investment_val[i]))
    f.writelines (str(i+1) + ","+str(sip_val)+","+str(rate[i])+","+str(growth_val[i])+","+str(investment_val[i])+"\n")
f.close()
"""  
    