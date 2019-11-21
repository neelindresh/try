import pandas as pd
import numpy as np
import phonenumbers
from validate_email import validate_email
import pycountry
import os
import glob

path = 'flow/static/data/temporary/'

def removeExistingFiles():
    files = glob.glob(path+'*')
    for f in files:
        os.remove(f)
        
        
def getInfoData(data):
    columns=data.columns
    infoDict={}
    for i in columns:
        if data[i].dtype =='object':
            infoDict[i]= 'Categorical'
        elif len(data[i].unique()) <20:
            infoDict[i]= 'Categorical'
        else:
            infoDict[i]= 'Continious'
    return infoDict

def checkEmail(data, colName):
    removeExistingFiles()
    idx = []
    data[colName] = data[colName].fillna(' ')
    for i, email in enumerate(data[colName]):
        if(validate_email(str(email)) == False):
            idx.append(i)
    kf = data[['Dummy Loan Number', colName]].iloc[idx]
    kf.to_csv(path + colName.replace("/", "")+'.csv', index=False)
    return idx

def validPhone(df, colName):
    removeExistingFiles()
    invalid_pn_indices = []
    phone_numbers = df[colName]
    df[colName] = df[colName].astype('O')
    for i, pn in enumerate(phone_numbers):
        try:
            parsed_pn = phonenumbers.parse(str(pn))
        except phonenumbers.NumberParseException:
            invalid_pn_indices.append(i)
            continue
        except:
            return [-1]
        is_valid_num = phonenumbers.is_valid_number(parsed_pn)
        if is_valid_num == False:
            invalid_pn_indices.append(i)
    kf = df[['Dummy Loan Number', colName]].iloc[invalid_pn_indices]
    kf.to_csv(path + colName.replace("/", "")+'.csv', index=False)        
    return invalid_pn_indices

def ageCheck(df, colName):
    removeExistingFiles()
    idx = []
    try:
        df[colName] = df[colName].fillna(-1)
        df[colName] = df[colName].astype('float')
    except:
        return [-1]
    for i,age in enumerate(df[colName]):
        if(age<1 or age>100):
            idx.append(i)
    kf = df[['Dummy Loan Number', colName]].iloc[idx]
    kf.to_csv(path + colName.replace("/", "")+'.csv', index=False)     
    return idx

def validate_country(df, col_name):
    '''
    description : This function validates the country by their full names or short forms of two or three 
                  characters. for ex: India or Ind or In, and returns an array whose first value is the total number
                  of incorrect country names and second value is a list of incorrect country names
    Parameters  : Dataframe and column name which consists of country names.
    Returns     : Number of inconsistent country names
    '''
    removeExistingFiles()
    idx = []
    for i, country in enumerate(df[col_name]):
        try:
            name = pycountry.countries.lookup(country)
            
        except LookupError:
            idx.append(i)
            print(country)
    kf = df[['Dummy Loan Number', col_name]].iloc[idx]
    kf.to_csv(path + col_name.replace("/", "")+'.csv', index=False)
    return idx

def earth_movers_distance(df, col_a, col_b):
    '''
        This function calculates earth movers distance between two columns
    '''
    from scipy.stats import wasserstein_distance
    col_a_values = df[col_a].fillna(0).values
    col_b_values = df[col_b].fillna(0).values
    return wasserstein_distance(col_a_values, col_b_values)

'''
def getNullReport(data):
    return dict(data.isnull().sum())
'''

def getNullReport(data):
    removeExistingFiles()
    for colName in data.columns:
        Columns = ['Dummy Loan Number']
        Columns.append(colName)
        kf = data[Columns][data[colName].isnull() == True]
        kf.to_csv(path + colName.replace('/','') + '.csv',  index=False)
    return dict(data.isnull().sum())

def getMeanReport(data,info):
    meanReport={}
    for i in data.columns:
        if info[i]=='Continious':
            meanReport[i]=data[i].mean()
    return meanReport

def getMedianReport(data,info):
    meanReport={}
    for i in data.columns:
        if info[i]=='Continious':
            meanReport[i]=data[i].median()
    return meanReport

def getStdReport(data,info):
    meanReport={}
    for i in data.columns:
        if info[i]=='Continious':
            meanReport[i]=data[i].std()
    return meanReport

def getVarReport(data,info):
    meanReport={}
    for i in data.columns:
        if info[i]=='Continious':
            meanReport[i]=data[i].var()
    return meanReport

def CategoriacalStats(data,info):
    categorial_count={}
    for i in data.columns:
        if info[i]=='Categorical':
            
            categorial_count[i]=data[i].value_counts()
    return categorial_count

def getQuatile(data,info,percent):
    quatileReport={}
    for i in data.columns:
        if info[i]=='Continious':
            quatileReport[i]=data[i].quantile(percent)
    return quatileReport

def getNumericalDf(data):
    info=getInfoData(data)
    nullReport=getNullReport(data)
    meanReport=getMeanReport(data,info)
    medianReport=getMedianReport(data,info)
    stdReport=getStdReport(data,info)
    varReport=getVarReport(data,info)
    quatileThird=getQuatile(data,info,.75)
    numericDf=pd.DataFrame()
    numericDf['Mean']=meanReport.values()
    numericDf['Median']=medianReport.values()
    numericDf['Variance']=varReport.values()
    numericDf['standardDevaition']=stdReport.values()
    numericDf['Quantile3rd']=quatileThird.values()
    numericDf['Quantile1st']=getQuatile(data,info,.25).values()
    contiNull={}
    for k,v in nullReport.items():
        if info[k]=='Continious':
            contiNull[k]=int(v)
    numericDf['NullCount']=contiNull.values()
    return numericDf

def getCategoriacalDF(data):
    info=getInfoData(data)
    cateStats=CategoriacalStats(data,info)
    catedf=pd.DataFrame(columns=['Top Feature-1','1_Count','Top Feature-2','2_Count','Top Feature-3','3_Count','Top Feature-4','4_Count','Top Feature-5','5_Count'])
    for k,v in cateStats.items():
        listOfRows=[]
        for i,j in v.to_dict().items():
            listOfRows.append(i)
            listOfRows.append(int(j))
        if len(listOfRows)<10:
            for i in range(10-len(listOfRows)):
                listOfRows.append(np.NaN)
                listOfRows.append(np.NaN)
        catedf.loc[k]=listOfRows[:10]
    return catedf

def genenateNullColumnReport(data,log):
    nullreport=getNullReport(data)
    actualSize=data.shape[0]
    for col,null in nullreport.items():
        percent=round((null/actualSize)*100,2)
        if percent>0:
            
            if percent>30:
                log.writeToLog(str(col+':'+str(percent)+'%'+ ' Warning :Null Values Exceeds standard percentile! May want to remove'))
            else:
                log.writeToLog(str(col+':'+str(percent)+'%'))
def getWrongClassified(data,log):
    
    for i in data.columns:
        if data[i].dtype =='object':
            if isinstance(data[i].loc[0], float) or data[i].loc[0].isdigit():
                count=0
                for d in data[i].loc[:6]:
                    if isinstance(data[i].loc[0], float) or d.isdigit():
                        count+=1
                if count>3:
                    
                    log.writeToLog('Warning! Seems that column "'+i+'" is wrongly classified as a Categorical variable')
                    
def robust_ratio(df, col_1, col_2, save_path='./robust_ratio_desc.csv', k1=1.5, k2=0.5):
    '''
        This function will find the outliers by comparing the ratios
        between two selected columns with the median rations computed
        from the same two columns.
        Robust_ratio_i = Median(column_1_val_i/column_2_val_i).
    '''
    df = pd.DataFrame(df, copy=True)
    ratios = []
    outliers_null = []
    for i, (col_1_val, col_2_val) in enumerate(zip(df[col_1].values, df[col_2].values)):
        if np.isnan(col_1_val) or np.isnan(col_2_val):
            outliers_null.append(i)
        elif col_2_val == 0:
            ratios.append((i, col_1_val/(col_2_val+1)))
        else:    
            ratios.append((i, col_1_val/(col_2_val)))
    
    only_ratios = [x[1] for x in ratios]
    ratios_arr = np.array(only_ratios)
    robust_ratio = np.median(ratios_arr)
    print(robust_ratio)
    outliers_value = []
    for i, ratio in ratios:
#         if ratio>1:
#             print(i, end=' ')
        if ratio > k1*robust_ratio or ratio < k2*robust_ratio:
            outliers_value.append(i)
#     print()
    #CREATING DESCRIPTION DATAFRAME TO DOWNLOAD
    description_null = 'Atleast one of the columns is NULL'
    description_value = 'Ratio too low/too high with respect to the robust ratio.'
    
    outlier_indices=outliers_value+outliers_null
    df_desc = df[['Dummy Loan Number', col_1, col_2]].iloc[outlier_indices]
#     df_desc['Dummy Loan Number'] = df['Dummy Loan Number'].loc[outlier_indices]
    df_desc['Description'] = [description_value]*len(outliers_value) + [description_null]*len(outliers_null)
#     print(df_desc.head())
    
    df_desc.to_csv(save_path, index=False)
            
#     return outliers_null, outliers_value
    return save_path, outliers_null+outliers_value
