import numpy as np
import pandas as pd
import operator


def check_column(df, ops, first_mul, col_name, oper, value):
    '''
        This function will return the list of valid and invalid rows list after performing the operation
        first_mul * df[col_name] oper value ex: [ 1*df['age'] >= 25 ].
    '''
    valid_rows_list = []
    invalid_rows_list = []
    
    for i, row in enumerate(df[col_name]):
        
        if ops[oper](first_mul*row, value):
            valid_rows_list.append(i)
        else:
            invalid_rows_list.append(i)             
    return valid_rows_list, invalid_rows_list



def values_in(df,col_name, inp_list):
    '''
        This function will iterate the df[col_name] and checks if all the values in df[col_name] are in inpu_list.
        This returns the valid_rows_list which contains indexes of all rows which are in inp_list and 
        invalid_rows_list which contains indexes of all rows which are not in inp_list
    '''
    valid_rows_list = []
    invalid_rows_list = []
    
    if 'float' in str(df[col_name].dtype):
        inp_list = list(map(float, inp_list))
    
    elif 'int' in str(df[col_name].dtype):
        inp_list = list(map(int, inp_list))
        
    for i, value in enumerate(df[col_name]):
        
        if value in inp_list:
            valid_rows_list.append(i)
        else:
            invalid_rows_list.append(i) 
            
    return valid_rows_list, invalid_rows_list



def compare_columns(df,ops,col_name1, col_name2, oper, first_mul=1, sec_mul=1):
    '''
        This function returns the list of indexes of rows which satisfy and doesn't satisfy the condition
        [first_mul*col_name1 op1 sec_mul*col_name2] ex: [1*mayRevenue >= 1.5*aprilRevenue].
    '''    

    valid_rows_list = []
    invalid_rows_list = []
    
    for i in range(len(df[col_name1])):
        
        if ops[oper](first_mul*df[col_name1][i], sec_mul*df[col_name2][i]):
            valid_rows_list.append(i)
        else:
            invalid_rows_list.append(i)
            
    return valid_rows_list, invalid_rows_list



def check_not_null(df, oper, col_name):
    '''
        This function will check for the null in df[col_name] and returns the list of indexes which is not equal to null
        and the list of list of indexes which is equal to null
    '''
        
    valid_rows_list = []
    invalid_rows_list = []
    
    for i, value in enumerate(df[col_name]):
        
        if oper=='!=' and not(pd.isnull(value)):
            valid_rows_list.append(i)
        elif oper=='==' and pd.isnull(value):
            valid_rows_list.append(i)
        else:
            invalid_rows_list.append(i)
    return valid_rows_list, invalid_rows_list

