import numpy as np
import pandas as pd
import operator
from . import VerificationFunctions as vf


'''
    parser.py Starts With The Function
    
    MainFunction(input_filename, data_filename, output_filename)
    
    where input_filename is path of the file which consists of Commands
          data_filename is path of the file which contains the data that should be analized
          output_filename: path to the output file
          Three files should be in CSV format
'''

def MainFunction(input_filename, data_filename, output_filename):
    '''
    Traverse through the 'Command' Column in input_filename and calls the function parser(data_df, Command, ops) for each command
    '''
    path = 'flow/static/data/temporary/'
    
    ops = {'>': operator.gt, '>=': operator.ge,'<': operator.lt,'<=': operator.le,'==': operator.eq,'!=': operator.ne}
    try:
        data_df=pd.read_csv(data_filename)
        input_df=pd.read_csv(input_filename)
    except FileNotFoundError as ff: 
        print(getattr(ff, 'message', repr(ff)))
        return
    data, count = [], 1
    for Command,Threshold in zip(input_df['Command'], input_df['Threshold']):
        
        try:
            if(pd.isnull(Command) or not(isinstance(Command,str))):
                raise Exception('Command not exist: {}'.format(Command))
            if(pd.isnull(Threshold) or not(isinstance(Threshold,float))):
                raise Exception('Threshold is Null or not a float Value: {}'.format(Command))    
            Command=Command.strip('\n')
            ValidList, InValidList, Columns = Parser(data_df, Command, ops)
            Columns = list(set(Columns))
            Columns.insert(0, 'Dummy Loan Number')
            kf = data_df[Columns].iloc[InValidList]
            if(len(InValidList)<=float(Threshold)*(len(ValidList)+len(InValidList))):
                data.append([len(ValidList),len(InValidList),"Pass"])
            else:
                data.append([len(ValidList),len(InValidList),"Fail"])
        except KeyError as k:
            kf = pd.DataFrame()
            for column in list(set(Columns)):
                kf[column] = []
            data.append([-1,-1,"Error: "+"Wrong Column Name ('"+str(k)+"')"])
        except IndexError as i:
            kf = pd.DataFrame()
            for column in list(set(Columns)):
                kf[column] = []
            data.append([-1,-1,"Error: "+"Length MisMatch in instruction ('"+str(i)+"')"])
        except Exception as e:
            kf = pd.DataFrame()
            for column in list(set(Columns)):
                kf[column] = []
            data.append([-1,-1,"Error: "+getattr(e, 'message', repr(e))])
        kf.to_csv(path + str(count)+'.csv', index=False)
        count+=1
    input_df['Valid']=np.array(data)[:,0]
    input_df['Invalid']=np.array(data)[:,1]
    input_df['Result']=np.array(data)[:,2]
    input_df.to_csv(output_filename, index=False)

def Parser(df,string, ops):
    '''
    Parse through the Command Given and divide it into parts make a list of keyWords
        and Calls a Function FindCase(df, ops, KeyWords_List)
    '''
    keywordsList,andorList,ansList=[],[],[]
    AllColumns = []
    keywordsList=string.split('|')
    for Word in keywordsList:
        if Word in [' ','','\n']:
            keywordsList.remove(Word)
    
    for index in range(0,len(keywordsList),4):
        validList, inValidList, TempColumns = FindCase(df, ops, keywordsList[index:index+3])
        AllColumns = AllColumns + TempColumns
        if(isinstance(validList,int) and validList==-1 and inValidList==-1):
            return -1,-1
        andorList.append([validList,inValidList])
        if(len(keywordsList)>index+3):
            andorList.append(keywordsList[index+3])
    index=0       
    while(index<len(andorList)):
        if(isinstance(andorList[index],list)):
            ansList.append(andorList[index])
        elif(andorList[index].lower()=='and'):
            index+=1
            Temp=ansList.pop()
            validListTemp=np.intersect1d(Temp[0],andorList[index][0])
            invalidListTemp=np.union1d(np.union1d(Temp[1],andorList[index][1]),np.setdiff1d(Temp[0],andorList[index][0]))
            ansList.append([validListTemp,invalidListTemp])
        elif(andorList[index].lower()=='or'):
            index+=1
            Temp=ansList.pop()
            validListTemp=np.union1d(Temp[0],andorList[index][0])
            invalidListTemp=np.setdiff1d(np.union1d(Temp[1],andorList[index][1]),validListTemp)
            ansList.append([validListTemp,invalidListTemp])
        elif(andorList[index]!='?' and andorList[index]!=':'):
            raise Exception('Unknown Contidion: {}'.format(andorList[index]))
        index+=1
    if(len(ansList) == 3):
        validList = np.append(np.intersect1d(ansList[0][0],ansList[1][0]),np.intersect1d(ansList[0][1],ansList[2][0]))
        inValidList = np.setdiff1d(np.append(ansList[0][0],ansList[0][1]),validList)                          
    elif(len(ansList) == 2):
        validList = np.intersect1d(ansList[0][0],ansList[1][0])
        inValidList = np.setdiff1d(ansList[0][0],validList)
    else:
        validList = ansList[0][0]
        inValidList = ansList[0][1]
    
    return np.array(validList),np.array(inValidList), AllColumns

    
def FindCase(df,ops,KeyWords_List):
    
    '''
    Finds Which case the given String Belongs to and calls that case_Function()
    '''
    x, y, z =[], [], []
    KeyWords_List[1]=KeyWords_List[1].strip()
    if(KeyWords_List[2].upper()=='NULL'):
        x,y,z=case_4(df, KeyWords_List)
    elif(KeyWords_List[1].lower()=='in'):
        x,y,z=case_3(df, KeyWords_List)
    elif(KeyWords_List[1] in ops.keys() and FindNum(KeyWords_List[2])):
        x,y,z=case_1(df, ops, KeyWords_List)
    elif(KeyWords_List[1] in ops.keys() and not(FindNum(KeyWords_List[2]))):
        x,y,z=case_2(df, ops, KeyWords_List)
    else:
         raise Exception('Unknown Contidion: {}'.format(KeyWords_List[1]))
    return x,y,z
    
    
def case_1(df, ops, KeyWords_List):
    
    '''
    Command:  |Name Of The Column||Operator||Number|
    Calls the funtion check_column(df, ops, mul, col_name, operator, number)
    returns:  list of Valid Rows and Invalid Rows
    '''
    
    col_name,operator,number,mul=KeyWords_List[0],KeyWords_List[1],float(KeyWords_List[2]),1
    if '*' in col_name:
        mul=float(col_name.split("*")[0])
        col_name=col_name.split("*")[1]
    
    x,y=vf.check_column(df, ops, mul, col_name, operator, number)
    return x,y,[col_name]

def case_2(df, ops, KeyWords_List):
    
    '''
    Command:  |Number * Name Of The Column||Operator||Number * Another Column Name|
    Calls the funtion vf.compare_columns(df, ops, col_name1, col_name2, KeyWords_List[1], mul1, mul2)
    returns:  list of Valid Rows and Invalid Rows
    '''
    
    col_name1,col_name2=KeyWords_List[0],KeyWords_List[2]
    mul1,mul2=1,1
        
    if '*' in col_name1:
        mul1=float(col_name1.split("*")[0])
        col_name1=col_name1.split("*")[1]
        
    if '*' in col_name2:
        mul2=float(col_name2.split("*")[0])
        col_name2=col_name2.split("*")[1]
       
    x,y=vf.compare_columns(df, ops, col_name1, col_name2, KeyWords_List[1], mul1, mul2)
    
    return x,y,[col_name1, col_name2]

def case_3(df, KeyWords_List):
    
    '''
    Command:  |Name Of The Column||in||[x,y,z]|
    Calls the funtion vf.values_in(df, col_name, Element_List)
    returns:  list of Valid Rows and Invalid Rows
    '''
    
    Element_List=KeyWords_List[2].strip('][').split(',')
    col_name=KeyWords_List[0]
       
    x,y=vf.values_in(df, col_name, Element_List)
    return x,y,[col_name]

def case_4(df, KeyWords_List):
    
    '''
    Command:  |Name Of The Column||!=||NULL|
    Calls the funtion vf.check_not_null(df, KeyWords_List[1], col_name)
    returns:  list of Valid Rows and Invalid Rows
    '''
   
    col_name=KeyWords_List[0]    
    x,y=vf.check_not_null(df, KeyWords_List[1], col_name)
    return x,y,[col_name]
       
    
def FindNum(num):
    '''
    Returns True if the Function is Number else False
    '''
    try:
        num=float(num)
        return True
    except:
        return False
    
    
#MainFunction('Test_Case.csv','April_Sheet.csv','Output_File.csv')