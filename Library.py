#Library functions#
import struct #allows us to use struct.unpack()

## General Functions - Start ##

## The "<" included in the first argument of each struct.unpack function calls tells the function to assume little-endian byte order
## unpack returns a tuple even if it contains exactly one item. [0] returns the first item
def char_to_int(string):
    # Convert 1 byte (char) into an signed char (integer)
    # endian-ness is irrelevant as it is a one byte string but little endian is specified for consistency
    return struct.unpack("<b", string)[0]
    
def uchar_to_int(string):
    # Convert 1 byte (uchar) into an unsigned char (integer)
    # note that this conversion could be done using ord() but unpack has been used for consistency
    # also endian-ness is irrelevant as it is a one byte string but little endian is specified for consistency
    uchar = struct.unpack("<B", string)[0]
    return uchar

def short_to_int(string):
    # Convert 2 little endian bytes into a signed short (integer)
    return struct.unpack("<h", string) [0]

def ushort_to_int(string):
    # Convert 2 little endian bytes into an unsigned short (integer)
    return struct.unpack("<H", string)[0]

def ulong_to_int(string):
    # Convert 4 little endian bytes into an unsigned long (integer)
    return struct.unpack("<I", string)[0]

def long_to_int(string):
    # Convert 4 little endian bytes into a signed long (integer)
    return struct.unpack("<i", string) [0]

def float_to_float(string):
    # Convert 4 little endian bytes into a float
    return struct.unpack("<f", string) [0]

def double_to_float(string):
    # Convert 8 little endian bytes into a float
    return struct.unpack("<d", string) [0]
## General Functions - Finish ##

## File Handling functions - Start ##
def read_unsigned_char(filehandle):
    return uchar_to_int(filehandle.read(1))

def read_unsigned_short(filehandle):
    return ushort_to_int(filehandle.read(2))

def read_signed_short(filehandle):
    return short_to_int(filehandle.read(2))

def read_unsigned_long(filehandle):
    return ulong_to_int(filehandle.read(4))

def read_signed_long(filehandle):
    return long_to_int(filehandle.read(4))

def read_double(filehandle):
    return double_to_float(filehandle.read(8))
## File Handling functions - Finish ##
