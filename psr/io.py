#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#  psr/io.py
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  software  : Kirmah    <http://kirmah.sourceforge.net/>
#  version   : 2.18
#  date      : 2014
#  licence   : GPLv3.0   <http://www.gnu.org/licenses/>
#  author    : a-Sansara <[a-sansara]at[clochardprod]dot[net]>
#  copyright : pluie.org <http://www.pluie.org/>
#
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  This file is part of Kirmah.
#
#  Kirmah is free software (free as in speech) : you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  Kirmah is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Kirmah.  If not, see <http://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module io ~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Io ~~

class Io:

    from io                 import SEEK_CUR
    from gzip               import compress as gzcompress, decompress as gzdecompress
    from bz2                import compress as bzcompress, decompress as bzdecompress
    from errno              import EEXIST
    from os                 import remove as removeFile, utime, rename
    from platform           import system
    if system() == 'Windows' :
        from mmap               import mmap, ACCESS_READ as PROT_READ
    else :
        from mmap               import mmap, PROT_READ

    def __init__(self):
        """"""

    @staticmethod
    def read_in_chunks(f, chsize=1024, utf8=False):
        """Lazy function (generator) to read a file piece by piece in
        Utf-8 bytes
        Default chunk size: 1k."""
        c = 0
        while True:
            data = f.read(chsize)
            if utf8 :
                p = f.tell()
                t = f.read(1)
                f.seek(p)
                if t!=b'' and not Io.is_utf8_start_sequence(ord(t)) :
                    delta = 0
                    for i in range(3) :
                        t = f.read(1)
                        if Io.is_utf8_start_sequence(ord(t)) :
                            delta += i
                            break
                    f.seek(p)
                    data += f.read(delta)
            if not data : break
            yield data, c
            c += 1


    @staticmethod
    def read_utf8_chr(f, chsize=0, p=0):
        """"""
        with Io.mmap(f.fileno(), chsize*p) as mmp:
            s, b, c = mmp.size(), b'', 0
            while mmp.tell() < s :
                b = mmp.read(1)
                c = Io.count_utf8_continuation_bytes(b)
                if c > 0 : b += mmp.read(c)
                yield str(b,'utf-8')


    @staticmethod
    def is_utf8_continuation_byte(b):
        """"""
        return b >= 0x80 and b <= 0xbf


    @staticmethod
    def is_utf8_start_sequence(b):
        """"""
        return (b >= 0x00 and b <= 0x7f) or (b>= 0xc2 and b <= 0xf4)


    @staticmethod
    def count_utf8_continuation_bytes(b):
        """"""
        c = 0
        try : d = ord(b)
        except : d = int(b)
        if d >= 0xc2 :
            if d < 0xe0 : c = 1
            elif d < 0xf0 : c = 2
            else : c = 3
        return c


    @staticmethod
    def get_data(path, binary=False, remove=False):
        """Get file content from `path`
        :Returns: `str`
        """
        d = ''
        with Io.rfile(path, binary) as f :
            d = f.read()
        if remove :
            Io.removeFile(path)
        return d


    @staticmethod
    def get_file_obj(path, binary=False, writing=False, update=False, truncate=False):
        """"""
        if not writing :                
            if not binary :
                f = open(path, encoding='utf-8', mode='rt')
            else :
                f = open(path, mode='rb')
        else :
            if update and not Io.file_exists(path):
                if binary :
                    f = open(path, mode='wb')
                else :
                    f = open(path, mode='wt', encoding='utf-8')
                return f
            m = ('w' if truncate else 'r')+('+' if update else '')+('b' if binary else 't')
            if not binary :
                f = open(path, mode=m, encoding='utf-8')
            else :
                f = open(path, mode=m)
        return f


    @staticmethod
    def wfile(path, binary=True):
        """"""
        return Io.get_file_obj(path, binary, True, True, True)


    @staticmethod
    def ufile(path, binary=True):
        """"""
        return Io.get_file_obj(path, binary, True, True, False)


    @staticmethod
    def rfile(path, binary=True):
        """"""
        return Io.get_file_obj(path, binary)


    @staticmethod
    def set_data(path, content, binary=False):
        """"""
        with Io.wfile(path, binary) as f:
            f.write(content)


    @staticmethod
    def readmmline(f, pos=0):
        """"""
        f.flush()
        with Io.mmap(f.fileno(), 0, prot=Io.PROT_READ) as mmp:
            mmp.seek(pos)
            for line in iter(mmp.readline, b''):
                pos = mmp.tell()
                yield pos, Io.str(line[:-1])


    @staticmethod
    def copy(fromPath, toPath):
        """"""
        if not fromPath == toPath :
            with Io.rfile(fromPath) as fi :
                with Io.wfile(toPath) as fo :
                    fo.write(fi.read())
        else : raise Exception('can\t copy to myself')


    @staticmethod
    def bytes(sdata, encoding='utf-8'):
        """"""
        return bytes(sdata,encoding)


    @staticmethod
    def str(bdata, encoding='utf-8'):
        """"""
        return str(bdata,encoding) if isinstance(bdata, bytes) else str(bdata)


    @staticmethod
    def printableBytes(bdata):
        """"""
        data = ''
        if isinstance(bdata,bytes) :
            try:
                data = Io.str(bdata)
            except Exception as e:
                hexv = []
                for i in bdata[1:] :
                    hexv.append(hex(i)[2:].rjust(2,'0'))
                data = ' '.join(hexv)
                pass
        else :
            data = bdata
        return bdata


    @staticmethod
    def is_binary(filename):
        """Check if given filename is binary."""
        done = False
        f = Io.get_file_obj(filename, True)
        try:
            CHUNKSIZE = 1024
            while 1:
                chunk = f.read(CHUNKSIZE)
                if b'\0' in chunk:  done = True # found null byte
                if done or len(chunk) < CHUNKSIZE: break
        finally:
            f.close()
        return done


    @staticmethod
    def file_exists(path):
        """"""
        exist = False
        try:
            if path is not None :
                with open(path) as f: exist = True
                f.close()
        except IOError as e: pass
        return exist


    @staticmethod
    def touch(fname, times=None):
        """ only existing files """
        if Io.file_exists(fname):
            Io.utime(fname, times)
