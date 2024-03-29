import socket, time
HOST = "192.168.16.2"  # The server's hostname or IP address
PORT = 6172  # The port used by the server
import numpy as np
from Utils import *
import logging
import time 





class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM,)
        else:
            self.sock = sock
        self.MSGLEN = 786432+8+262144+2400+8800

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
            logging.info(f"Connected to: HOST: {host},PORT:{port}")
            
            return True
        except Exception as e :

            print(e)
            logging.critical(f"Failed to connect to:{e}")
            return False
            
        

    def mysend(self, msg):
        totalsent = 0
        
        while totalsent <len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self,msg_length):
        stri = "DONE"
        chunks = []
        bytes_recd = 0
        while bytes_recd < msg_length:
            chunk = self.sock.recv(min(msg_length - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        
        return b''.join(chunks)
    def mains(self,queue):
        print("start")
        while True:
            data_info=self.myreceive(8)
            print(data_info[:4])
            length=int.from_bytes(data_info[4:8], byteorder="little", signed=False)
            
            queue.put(
                {
                    "type":data_info[:4],
                    "length":length,
                    "data":self.myreceive(length)

            })
    def terminate(self):
        self.mysend("GBYE".encode("utf-8"))
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        #self.sock.close()
        print("Closed socket")
    
        
def fetch_data(exit_event,data_queue,parameters,settings,debug=False):
    logging.info("Started client")
    time_arr = []
    debug_data = None
    if debug:
        debug_data = np.load("data/data_400_500.npy",mmap_mode="r")
        
    client_socket = MySocket()
    connection = client_socket.connect(host = HOST,port=PORT)
    if(not connection):
        exit_event.set()
    for key, val in parameters.items():
           client_socket.mysend(f"{key}".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+(int(val)).to_bytes(4, byteorder="little", signed=False))
    for key, val in settings.items():
           client_socket.mysend(f"{key}".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+(int(val)).to_bytes(4, byteorder="little", signed=False))

    #client_socket.mysend("PSPT".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+(1000).to_bytes(4, byteorder="little", signed=False))
        #client_socket.mains(queue=data_queue)
    client_socket.mysend("DSF1".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+"PPRM".encode("utf-8"))
    client_socket.mysend("DSF1".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+"RPRM".encode("utf-8"))
    first = True
    drop_count =1
    while not exit_event.is_set():
       
        try:
            
            data_info=client_socket.myreceive(8)
            length=int.from_bytes(data_info[4:8], byteorder="little", signed=False)
            data = client_socket.myreceive(length)
            if first: 
                #We wat to test of the correct tettogs was set
                if(data_info[:4].decode("utf-8")== "PPRM"):
                    read_PPRM(data)
                
                if(data_info[:4].decode("utf-8")== "RPRM"):
                    read_PPRM(data)
                first =False
           
            if(data_info[:4].decode("utf-8")== "RADC" and length >1):
                
                RADC_data = read_RADC(data,length, save =False)

                if data_queue.empty():
                    
                    data_queue.put((drop_count,RADC_data))
                    drop_count = 1
                else:
                    drop_count +=1
            
            
                
            #logging.critical(f"Client: Mean{np.mean(time_arr)},STD: {np.std(time_arr)}")   
        except Exception as e :
           logging.critical("Unexpected error, exiting:",e)
           exit_event.set()
           client_socket.terminate()
        
        
    if connection:
            client_socket.terminate()
                    
        
              
        
    return    










            
            
                
            
          
            
            
        
            
 
    
    