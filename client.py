import socket, time
HOST = "192.168.16.2"  # The server's hostname or IP address
PORT = 6172  # The port used by the server
import numpy as np
from scipy.signal import detrend


def read_RADC(data,length):
    length = data["length"]
                    
    data_RADC = data["data"][8:8+length]
    data_RADC = np.frombuffer(data_RADC,dtype=np.uint16)
    data_RADC = data_RADC.reshape(3,256,512)
    data_RADC_I_raw = data_RADC[:,:,::2]
    data_RADC_Q_raw = data_RADC[:,:,1::2]
    data_RADC_I = detrend(data_RADC_I_raw, axis=2)
    data_RADC_Q = detrend(data_RADC_Q_raw, axis=2)
                    
    data_RADC_I_mean = data_RADC_I
    data_RADC_Q_mean = data_RADC_Q
    return data_RADC_I_mean[:,:,:] + 1j*data_RADC_Q_mean[:,:,:]
    
    


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
            print("Connected to:")
            print("HOST: ", host)
            print("PORT:",port,"\n")
            return True
        except Exception as e :
            print(e)
            print("Failed to connect to:")
            print("HOST: ", host)
            print("PORT:",port,"\n")
            exit()
            
        

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
        #self.sock.close()
        print("Closed socket")
    
        
def fetch_data(data_queue):
    print("Started client")
    client_socket = MySocket()
    connection = client_socket.connect(host = HOST,port=PORT)
    client_socket.mysend("PSPT".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+(1000).to_bytes(4, byteorder="little", signed=False))
        #client_socket.mains(queue=data_queue)
    client_socket.mysend("DSF1".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+"PPRM".encode("utf-8"))
    client_socket.mysend("DSF1".encode("utf-8")+(4).to_bytes(4, byteorder="little", signed=False)+"RPRM".encode("utf-8"))
    while True:
        try:
            
            data_info=client_socket.myreceive(8)
            length=int.from_bytes(data_info[4:8], byteorder="little", signed=False)
        
            if(data_info[:4].decode("utf-8")== "RADC" and length >1 ):
                data_RADC = read_RADC( client_socket.myreceive(length), length)
                data_queue.put(data_RADC)
        
        except KeyboardInterrupt:
            if connection:
                    client_socket.terminate()
                    
            print("Exiting client")      
            break
        if not connection:
            break
    return    










            
            
                
            
          
            
            
        
            
 
    
    
