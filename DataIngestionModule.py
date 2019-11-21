import paramiko
import sys


def connect(host,username,key):
    '''
    CONNECTING TO REMOTE SERVER
    :param host: host address
    :param username: AWS user name
    :param key: PATH to the .pem file
    :return: NONE
    '''
    print('Connecting to host ',host)
    try:
        key=key
        k = paramiko.RSAKey.from_private_key_file(key)
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            session.connect(hostname=host, username=username, pkey=k)
        except Exception as e:
            print(e)
            print('Please Check the HOST NAME OR USER NAME')
            sys.exit(0)
    except Exception as e:
        print(e)
        print('Cannot be connected')
        sys.exit(0)
    print('Connected')
    return session

def get_file_list(host,username,key,options=None):
    '''
    GIVE US THE LIST OF FILES IN REMOTE LOCATION
    :param options: [LIST] of parameters -a ,-l <Optional>
    :return:[LIST] of files
    '''
    session=connect(host,username,key)
    command='ls'
    if options is not None:
        for option in options:
            command+=option
    stdin_, stdout_, stderr_ = session.exec_command("ls")
    # time.sleep(2)    # Previously, I had to sleep for some time.
    stdout_.channel.recv_exit_status()
    if len(stderr_.readlines()) is 0:
        lines=stdout_.readlines()
        return lines
    else:
        print(stderr_.readlines())
        #close()
        sys.exit(0)

def get_parquet_file_from_S3(host,username,key,local,remote):
    '''
    SAVES DATA FROM REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    session=connect(host,username,key)
    sftp = session.open_sftp()
    print('Getting parquet data...')
    try:
        localpath = local
        remotepath = remote
        sftp.get(localpath, remotepath)
        print('File saved to local')
    except Exception as e:
        print(e)
        print('FILE NOT FOUND')

    sftp.close()
def get_csv_file_from_S3(host,username,key,local,remote):
    '''
    SAVES DATA FROM REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    session=connect(host,username,key)
    sftp = session.open_sftp()
    print('Getting csv data...')
    try:
        localpath = local
        remotepath = remote
        sftp.get(localpath, remotepath)
        print('File saved to local')
    except Exception as e:
        print(e)
        print('FILE NOT FOUND')

    sftp.close()
def get_json_file_from_S3(host,username,key,local,remote):
    '''
    SAVES DATA FROM REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    session=connect(host,username,key)
    sftp = session.open_sftp()
    print('Getting json data...')
    try:
        localpath = local
        remotepath = remote
        sftp.get(localpath, remotepath)
        print('File saved to local')
    except Exception as e:
        print(e)
        print('FILE NOT FOUND')

    sftp.close()
def save_data_remote(host,username,key,local,remote):
    '''
    SAVES DATA TO REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    print('Saving data...')
    session=connect(host,username,key)
    sftp = session.open_sftp()
    try:
        sftp.put(local, remote)
        fileName=remote.split('/')[-1]
        print('Data saved remotely to ',host,' as ', create_URL(host,fileName))
    except Exception as e:
        print(e)
        print('FILE NOT FOUND')

    sftp.close()
def create_URL(host,fileName):
    fileName=host+'/'+fileName
    return fileName
def save_dir_remote(host,username,key,local,remote):
    '''
    SAVES Directory TO REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    import os
    pwd=os.getcwd()
    session=connect(host,username,key)
    try:
        list_of_remote_dir=get_file_list(host,username,key)
        list_of_remote_dir=[l.strip('\n') for l in list_of_remote_dir]
        if remote.split('/')[-1] not in list_of_remote_dir:
            print('not there',remote.split('/')[-1])
            session.exec_command(str('mkdir '+str(remote.split('/')[-1])))

        sftp = session.open_sftp()
        print('Saving data...')    
        sftp.chdir(str(remote.split('/')[-1]))
        os.chdir(local)
        for file in os.listdir():
            if file != '.ipynb_checkpoints':
                print('Saving File-->',file)
                sftp.put(file,file)
    except Exception as e:
        print(e)
    finally:
        os.chdir(pwd)
        sftp.close()
def get_parquet_folder_from_s3(host,username,key,local,remote):
    '''
    Gets Directory from REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    import os
    session=connect(host,username,key)
    pwd=os.getcwd()
    try:
        local_dir=os.listdir()

        if local.split('/')[-1] not in local_dir:
            os.mkdir(local.split('/')[-1])

        sftp = session.open_sftp()
        sftp.chdir(str(remote.split('/')[-1]))
        os.chdir(local)
        print('Getting data...')
        stdin_, stdout_, stderr_ = session.exec_command("cd "+str(remote.split('/')[-1])+" \n ls")
        list_of_remote=stdout_.readlines()
        list_of_remote=[l.strip('\n') for l in list_of_remote]
        for file in list_of_remote:
            print('Getting File-->',file)
            sftp.get(file,file)
    except Exception as e:
        print(e)
    finally:
        print('Data Ingestion Completed')
        os.chdir(pwd)
        sftp.close()
def get_csv_folder_from_s3(host,username,key,local,remote):
    '''
    Gets Directory from REMOTE SERVER
    :param local: LOCAL file name
    :param remote: Remote file name
    :return: NONE
    '''
    import os
    session=connect(host,username,key)
    pwd=os.getcwd()
    try:
        local_dir=os.listdir()

        if local.split('/')[-1] not in local_dir:
            os.mkdir(local.split('/')[-1])

        sftp = session.open_sftp()
        sftp.chdir(str(remote.split('/')[-1]))
        os.chdir(local)
        print('Getting data...')
        stdin_, stdout_, stderr_ = session.exec_command("cd "+str(remote.split('/')[-1])+" \n ls")
        list_of_remote=stdout_.readlines()
        list_of_remote=[l.strip('\n') for l in list_of_remote]
        for file in list_of_remote:
            print('Getting File-->',file)
            sftp.get(file,file)
    except Exception as e:
        print(e)
    finally:
        print('Data Ingestion Completed')
        os.chdir(pwd)
        sftp.close()
def get_data_mongoDb(host,port,db,table):
    from pymongo import MongoClient
    import pandas as pd
    uri='mongodb://'+host+':'+str(port)
    cli=MongoClient(uri)
    tab=cli[db][table]
    df = pd.DataFrame(list(tab.find()))
    
    df=df.drop('_id',axis=1)
    df.to_csv('flow/static/data/'+table+'.csv',index=False)
def get_data_MySql(host,port,user,password,db,table):
    import sqlalchemy as sql
    import pandas as pd
    import pymysql
    uri="mysql+pymysql://"+user+':'+password+'@'+host+':'+str(port)+'/'+db
    engine = sql.create_engine(uri)
    data = pd.read_sql('select * from '+table, con=engine)
    data.to_csv('flow/static/data/'+table+'.csv',index=False)