# -*- coding: utf-8 -*-
"""
Created on Jan 18 23:25:57 2021

Для получения графика функции a(t) применяем таблицу, которая имитирует
поток данных от датчика ускорений

Интеграл вычисляем в потоке - по мере поступления новых данных
Метод прямоугольников. (Возможен метод трапеций или Симпсона)

В данном макете программы отработана реакция на событие останова состава.
Аналогично решается вопрос определения трогания состава с места.

@author:    ln.starmark@gmail.com
            ln.starmark@ekatra.io
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

###--- Можно графику отключить -----------------------------------------------
GRAPHICS_EN = 1 
PRINT_EN = 1

MAX_CNT = 1024 * 64

A_MIN = 0.4
A_EPS = 0.6         #--- предел зазора для ускорений 

V_MIN = 1.4
V_EPS = 1.5         #--- предел зазора для скоростей 

X_MIN = 2.1
X_EPS = 2.2        #--- предел зазора для перемещений 

dlt = 0.5             #--- интервал по оси времени 
###---------------------------------------------------------------------------
###--- Поток данных приходит от датчика --- Одна ось --- тест ----------------
###---------------------------------------------------------------------------

###--- Потоковый интеграл от каждого следующего значения функции ----
def intgr(cns, f , dlt):
    return (cns + (f * dlt))
###------------------------------------------------------------------   
    
###--- Все обнулить -------------------------------------------------
fnc = []        ###--- Для отрисовки данных потока по  оси X 
ingr0 = []      ###--- Для отрисовки ускорения
ingr1 = []      ###--- Для отрисовки 1-го интеграла от функции
ingr2 = []      ###--- Для отрисовки 2-го интеграла  

fl_Stop = 0     ###--- Сигнал останова состава  
fl_Start = 1    ###--- Сигнал трогания состава

###--- Организация пустого цикла для задержки, т.к. time.time() ----
###--- слишком быстро тикает ---------------------------------------
a = 0
def Delay(dt):
    global a
    for i in range(0,dt):
        a += 1
    a = 0    

def Reset_vars():
    global X
    global X_old   
    global Y
    global Y_old   
    global A_old
    X = 0
    X_old = 0    
    Y = 0
    Y_old = 0
    A_old = 0
       
def Graphics():
    if(GRAPHICS_EN == 1):
        df = pd.DataFrame(ingr0)
        df.plot(figsize=(20, 10))  
    
        df_V = pd.DataFrame(ingr1)
        df_V.plot(figsize=(20, 10))
    
        df_S = pd.DataFrame(ingr2)
        df_S.plot(figsize=(20, 10))         

###--- Основная рабочая функция -------------------------------------
###--- минимальное превышение X_epsilon при контроле остановки 
###--- минимальное превышение X_start_epsilon при старте состава
###--- tim_threshould контрольное время
def wrk(X_epsilon, X_start_epsilon, tim_threshould):
    A_old = 0           
    V = 0               ###--- Скорость
    V_old = 0
    X = 0               ###--- Перемещение
    X_old = 0

    CNT = 0

    global fl_Stop      ###--- Сигнал останова состава  
    global fl_Start     ###--- Сигнал трогания состава
    
    f = open("E:/GIT_Python/Python/test/channel1.txt", "r")
    
    timing = time.time()
    for line in f:
        
        ###--- Ускорение ax(t) получаем из датчика ------------------
        cax = float(line)
        cax = cax // 256
        if(abs(cax) < A_MIN):   ###--- незначащее значение ускорения 
            cax = 0.0
            A_old = 0.0
        else:
            if(abs(cax - A_old) > A_EPS):                
                A_old = cax     ###--- новое A значительно отличается
            else:
                cax = A_old     ###--- оставляем старое значение A
        
        if(GRAPHICS_EN == 1):ingr0.append(cax) ###--- для графика  
            
        ###--- Первый интеграл - скорость V -------------------------
        V = intgr(V, cax , dlt)
        if(abs(V) < V_MIN):
            V = 0.0
        else:    
            if(abs(V - V_old) < V_EPS):
                V = V_old
            else:
                V_old = V
        
        if(GRAPHICS_EN == 1):ingr1.append(V)   ###--- для графика
        
        ###--- Второй интеграл - перемещение X ----------------------
        X = intgr(X, V, dlt)
        if(abs(X) < X_MIN):
            X = 0.0
        else:    
            if(abs(X - X_old) < X_EPS):
                X = X_old
            else:
                X_old = X        
        
        if(GRAPHICS_EN == 1):ingr2.append(X)   ###--- для графика

        ###--- Контрольный вывод ------------------------------------
        if(PRINT_EN == 1):
            print(cax, V, X)    
 
        ###--- Принятие решения -------------------------------------
    
 
        '''
        if(fl_Stop == 0):
            if(abs(V - V_old) < X_epsilon):
                if ((time.time() - timing) > tim_threshould):
                    print("********* Train in stop status ", X)
                    fl_Stop = 1
                    fl_Start = 0
                    Reset_vars()
                    timing = time.time()
            else:
                timing = time.time()
                
        if(fl_Start == 0):
             if(abs(V - V_old) > X_start_epsilon):
                if ((time.time() - timing) < tim_threshould):
                    print("********* Train in start status ", X)
                    fl_Stop = 0
                    fl_Start = 1
                    Reset_vars()
                    timing = time.time()
             else:
                timing = time.time()                 
        
        X_old = X
        V_old = V
        '''
        
        CNT += 1
        if(CNT >= MAX_CNT):
            break
        
    f.close()
    

  
###=== Процесс пошел ================================================   
wrk(0.1, 0.1, 0.5)  
Graphics()  
###==================================================================



