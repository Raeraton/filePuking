import os

class RFile:

    def __init__(self, path):
        self.file = open( path, "rb" )

        self.file.seek(0, os.SEEK_END)
        self.size = self.file.tell()

    def get_bytes( self, start, end ) -> bytes:
        if start < 0 : start = 0
        if start > self.size-1: start = self.size-1
        if end > self.size : end = self.size
        if end < 0 : end = 0

        self.file.seek(start, os.SEEK_SET)
        out = self.file.read(end-start)
        return out

    def __del__(self):
        self.file.close()


class WFile:

    def __init__(self, path, size:int):
        self.file = open( path, "wb" )
        self.file.write( bytes(size) )

        self.size = size

    def set_bytes( self, data: bytes, start: int ) -> bytes:
        self.file.seek(start, os.SEEK_SET)
        dl = len(data)
        rd = self.size-start
        if rd < dl: dl = rd
        self.file.write( data[:dl] )

    def __del__(self):
        self.file.close()
