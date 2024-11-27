import pickle
import logging
import socketserver
import struct

class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            print(f"{record.levelname} [{record.asctime}] {record.msg}")

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host='localhost', port=8700):
        super().__init__((host, port), LogRecordStreamHandler)

if __name__ == '__main__':
    tcpserver = LogRecordSocketReceiver()
    print('Starting logging server on port 8700...')
    tcpserver.serve_forever()