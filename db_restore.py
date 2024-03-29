import sys
import os
import subprocess
import platform
from getpass import getpass

os_type = platform.system()
SRV_IP="127.0.0.1"
WIN_SRV_TOSTOP=["1C:Enterprise 8.3 Server Agent (x86-64)"]
WIN_PG_BIN="C:\\Program Files\\PostgreSQL\\12.5-3.1C\\bin\\"
LIN_PG_BIN="//usr//bin"

def SrvStart():
    
    if (os_type == "Windows"):
        for srv in WIN_SRV_TOSTOP:
            print("Trying to start service: " + srv)
            response = os.system("sc start \"" + srv +  "\"")
            if (response != 0):
                print("Unable to start the service. Code: " + str(response))
                
    if (os_type == "Linux"):
         # todo for linux
         print("")

def SrvStop():
    
    if (os_type == "Windows"):
        for srv in WIN_SRV_TOSTOP:
            print("Trying to stop service: " + srv)
            response = os.system("sc stop \"" + srv +  "\"")
            if (response != 0 and response != 1062):
                print("Unable to stop the service. Code: " + str(response))
                sys.exit()
                
    if (os_type == "Linux"):
         # todo for linux
         print("")
            
def check_ping(host):
    response = os.system("ping -c 1 " + host)
    # and then check the response...
    return response


def GetFsig(file, count=10, seek=0):
    with open(file, 'rb') as file_object:

        # Reads only n bytes from the file
        file_object.seek(seek, 0)
        data = file_object.read(count)
        if  data:
            return data
        else:
            return 0       

def GetCreds(db_name_="", db_port_=""):
    creds=[]
    db_ip=input("Server IP/DNS: ")
    if (db_ip == ""):
        db_ip=SRV_IP
    print("Checking ip " + db_ip)
    if (check_ping(db_ip) != 0):
        print("The host is offline, exiting...")
        sys.exit()

    db_port=input("Server port " + db_port_ + ": ")
    if (db_port == ""):
        db_port=db_port_
    
    db_name=input("Database name (" + db_name_ +  "): ")
    if (db_name == ""):
        db_name = db_name_

    db_user=input("Database user: ")
    db_pass = getpass("Database password: ")
    if not ( len(db_pass.strip()) and  len(db_user.strip())):
        print("Emtpy db password or username, exiting... ")
        sys.exit()
    creds=[db_ip, db_name, db_user, db_pass, db_port]
    return creds

# PostgreSQL restore

def PostgreSQLRes(db_file=""):
    db_orig_name = str(GetFsig(db_file, 200, 56)).split('\\')[0].split('b\'')[1]
    creds = GetCreds(db_orig_name, "5432")
    print("--------\nRestoring\n--------\nDatabase: " + creds[1] + \
          "\nFile " + db_file + \
          "\nServer " + creds[0] + \
          "\nPort " + creds[4] + \
          "\nUser "+creds[2] + \
          "\nPassword *****\nProceed?")
    if input() == "y":
     
  

     sqlcmddrop = "DROP DATABASE " + creds[1] + ";"
     
     sqlcmdres = "CREATE DATABASE " + creds[1] + " \
          ENCODING 'UTF-8' \
          LC_COLLATE 'Russian_Russia.1251' \
          LC_CTYPE 'Russian_Russia.1251';"
      
     SrvStop()
     try:
         if (os_type == "Windows"):
             
             # Drop old db
             subprocess.call([WIN_PG_BIN+"psql", "-d", "postgresql://" + creds[2] + ":" + creds[3] + "@" + creds[0] + ":" + creds[4] +  "/" + creds[1], "-c", sqlcmddrop ])
             
             # And create new one
             subprocess.call([WIN_PG_BIN+"psql", "-d", "postgresql://" + creds[2] + ":" + creds[3] + "@" + creds[0] + ":" + creds[4] +  "/" + creds[1], "-c", sqlcmdres ])
             
     except FileNotFoundError:
      print('Cannot run postgres binaries.')
      sys.exit(-1)

     SrvStart()
def main():
    
  
    print("Detected os type " + os_type)
    db_file=input("Database file path: ")
    f_signature=GetFsig(db_file)
    print("File signature: " +  str(f_signature))
      
    # MsSql compressed db backup signature is b'MSSQLBAK\x02\x00'
    # PostgreSQL signature is b'PGDMP\x01\x0e\x00\x04\x08'

    if (f_signature[:5] == b'PGDMP'):
        print("PostgreSQL backup file detected, trying to restore.")
        PostgreSQLRes(db_file)
    elif (f_signature[:8] == b'MSSQLBAK'):
        print("mssqlfile")
    else:
        print("Unknown file type, exiting.")
        sys.exit()

 
if __name__ == "__main__":
        main()
