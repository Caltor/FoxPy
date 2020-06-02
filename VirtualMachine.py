import sys  #needed for sys.stdout.write
import math
import operator #allows operator.add, operator.mul etc
import Library  # Must prefix function calls with "Library."
#from numpy.py import npv

def ltrim(*args):
    mystring = args[0]
    if len(args) == 1:
        return mystring.lstrip()
    elif len(args) == 2:
        return mystring.lstrip(args[1])
    elif len(args) >= 3:
        if type(args[1] == type(1)):
            #second parameter is nFlags
            nFlags = args[1]
            stripchars = ''.join(args[2:])
        else:
            # nFlags is ommitted
            nFlags = 0
            stripchars = ''.join(args[1:])
           
        if nFlags == 0:
            #case sensitive
            return mystring.lstrip(stripchars)
        else:
            #case insensitive
            return mystring.lower().lstrip(stripchars.lower()) 

def rtrim(*args):
    mystring = args[0]
    if len(args) == 1:
        return mystring.rstrip()
    elif len(args) == 2:
        return mystring.rstrip(args[1])
    elif len(args) >= 3:
        if type(args[1] == type(1)):
            #second parameter is nFlags
            nFlags = args[1]
            stripchars = ''.join(args[2:])
        else:
            # nFlags is omitted
            nFlags = 0
            stripchars = ''.join(args[1:])
           
        if nFlags == 0:
            #case sensitive
            return mystring.rstrip(stripchars)
        else:
            #case insensitive
            return mystring.lower().rstrip(stripchars.lower()) 

def alltrim(*args):
    mystring = args[0]
    if len(args) == 1:
        return mystring.strip()
    elif len(args) == 2:
        return mystring.strip(args[1])
    elif len(args) >= 3:
        if type(args[1] == type(1)):
            #second parameter is nFlags
            nFlags = args[1]
            stripchars = ''.join(args[2:])
        else:
            # nFlags is ommitted
            nFlags = 0
            stripchars = ''.join(args[1:])
           
        if nFlags == 0:
            #case sensitive
            return mystring.strip(stripchars)
        else:
            #case insensitive
            return mystring.lower().strip(stripchars.lower())   

def left(my_string, num_chars):
    return my_string[:num_chars]

def right(my_string, num_chars):
    return my_string[len(my_string)-num_chars:]

def string(number, length=10, decimalplaces=0):
    # equivalent of STR() in VFP
    #this routine should round up but doesn't do any rounding at the moment
    #this routine should padl with spaces if the specified "length" is greater than the length of the value
    format_string = "{:."+str(decimalplaces)+"f}"
    return left(format_string.format(number), length)

def substr(mystring, startingpos, numchars=-1):
    startingpos = startingpos-1   #Python is zero indexed but VFP is 1 indexed
    
    if numchars == -1:
        # numchars has not been specified so return the whole string
        return mystring[startingpos:]
    else:
        return mystring[startingpos:startingpos+numchars]

class VirtualMachine:
    # Note any properties/members instantiated here will be shared by ALL INSTANCES of this class.
    # See https://docs.python.org/3/tutorial/classes.html for details
    
    def __init__(self):
        #Instantiate the instance variable
        self.code = "" #Code block to execute
        self.ip = 0 # Instruction Pointer

        ## could we make these classes static or class members rather than instance
        self.COMMAND_DICT = {
            0x02: self.QuestionMark,
            0x03: self.QuestionMarkDouble,
            0x54: self.Assignment
        }
        self.OPERATOR_DICT = {
            0x04: operator.mul,
            0x05: operator.pow,
            0x06: operator.add,
            0x08: operator.sub,
            0x0C: operator.truediv,
            0x19: abs,
            0x1C: ord,
            0x20: chr,
            0x3D: left,
            0x3E: len,
            0x40: lambda my_string: my_string.lower(),  #lower
            0x41: ltrim,
            0x44: max,
            0x46: min,
            0x47: operator.mod,
            0x52: right,
            0x56: rtrim,   # this seems to be a duplicate of 0x60
            0x5A: string, ## STR() in VFP
            0x5C: substr,
            0x60: rtrim,  # this seems to be a duplicate of 0x56
            0x66: lambda my_string: my_string.upper(),  #upper
            #0x75: npv,   ## needs install and import of numpy
            0x9B: alltrim,
            0xB1: lambda my_string, length: my_string.rjust(length),  #padl - equivalent of right justify
            0xB2: lambda my_string, length: my_string.rjust(length),  #padr - equivalent of left justify
            0xEA: self.extended
        }
        self.TERM_DICT = {
            0xD9: self.ReadString,
            0xE9: self.Int32,
            0xF7: self.GetVariable,
            0xF8: self.Int8,
            0xF9: self.Int16,
            0xFA: self.Double,
            0xFC: self.Expression
        }
        self.locations = []  #List to hold variables (maximum 65536)

    def extended(self, *params):
        EXTENDED_FUNCTIONS = {
            0x43: math.cos,
            0x44: math.sin,
            0x45: math.tan,
            0x46: math.acos,
            0x47: math.asin,
            0x48: math.atan,
            0x4C: math.exp
        }
 
        next_char = self.read_byte()
        f = EXTENDED_FUNCTIONS[next_char]
        return f(*params)

    def interpret(self):
        size_code_area = len(self.code)
        while self.ip+3 < size_code_area:
            self.codeline()

    def codeline(self):
        size_line = self.read_ushort() #Find out how long this line of code is
        next_line = self.ip + size_line
        self.command()
        self.match(0xFE)    ## end of code line
        # self.ip = next_line - 2
        
    def command(self):
        # Can this be combined with Expression()?
        opcode = self.read_byte()
        if opcode in self.COMMAND_DICT:
            command = self.COMMAND_DICT[opcode]
            command()
        else:
            print("opcode " + str(opcode) + " 0x" + hex(opcode) + " is not recongised")

    def consume(self, hexcode):
        #Consume the expected character
        num = self.code[self.ip]
        if num == hexcode:
            self.move_pointer(1)
        else:
            print("Position in code section: ", hex(self.ip))
            print("Expected: ", hex(hexcode))
            print("Got: ", hex(num))

    def consumeCC(self):
        #For an unknown reason a Double is sometimes followed by 0xCC which needs to be consumed if present
        self.consume(0xCC)
    

    def match(self, expected):
        cur_pos = self.ip
        got = self.code[self.ip]
        self.move_pointer(1)
        if got != expected:
            print("File pos: ",cur_pos)
            print("Expected: ", hex(expected))
            print("Got: ", hex(got))

    def move_pointer(self, numbytes):
        self.ip = self.ip+numbytes

    def read_byte(self):
        mybyte = self.code[self.ip]
        self.move_pointer(1)
        return mybyte

    def read_double(self):
        mydouble = Library.double_to_float(self.code[self.ip:self.ip+8])
        self.move_pointer(8)
        return mydouble

    def read_short(self):
        myshort = Library.short_to_int(self.code[self.ip:self.ip+2])
        self.move_pointer(2) #Move the ip on 2 bytes
        return myshort

    def read_ushort(self):
        #mycode = self.code[self.ip:self.ip+2]
        myshort = Library.ushort_to_int(self.code[self.ip:self.ip+2])
        self.move_pointer(2) #Move the ip on 2 bytes
        return myshort

    def read_long(self):
        mylong = Library.long_to_int(self.code[self.ip:self.ip+4])
        self.move_pointer(4)
        return mylong

    def read_ulong(self):
        mylong = Library.ulong_to_int(self.code[self.ip:self.ip+4])
        self.move_pointer(4)
        return mylong

    ## VFP Commands ##
    def Assignment(self):
        self.consume(0xF7)
        location=self.read_ushort()
        self.consume(0x10)  ## not sure what this is for! Maybe data type?
        next_byte = self.read_byte()
        self.locations.insert(location, self.term(next_byte))


    def Double(self):
        #Doubles are stored using N(10.3) format the same as numeric fields in tables.
        #The value is stored in IEEE 754 double-precision binary floating-point format: binary64
        #see http://en.wikipedia.org/wiki/Double-precision_floating-point_format
        digits = self.read_byte()
        decimals = self.read_byte()
        mydouble = self.read_double()
        self.consumeCC() #For an unknown reason the double is sometimes followed by 0xCC which needs to be consumed if present
        return mydouble

    def Expression(self):
        # Expression := Term [Term Operand] (BNF format)

        stack = []  # initialise the stack

        #loop for each element until end of expression
        while True: ## Look <> "\xFD":
        
            next_byte = self.read_byte()

            if next_byte == 0xFD:
                ##print "End Expression"
                break
            
            if next_byte in self.OPERATOR_DICT:
                #This is an OPERATOR opcode
                f = self.OPERATOR_DICT[next_byte]    ##Get function reference
                params = []
                # while len(stack) > 0:
                #     ## interate through the stack popping the last value into a parameter list
                #     a = stack.pop() ##POP value off the stack
                #     if a == 0x43:   ##end of parameter list opcode
                #         break
                #     params.insert(0,a) ## Insert at start of parameter list (The stack is in reverse order to the parameter list)

                ## Pop the last two items off the stack into the params list (The stack is in reverse order to the parameter list)
                if len(stack):
                    params.insert(0, stack.pop())
                
                if len(stack):
                    item = stack.pop()
                    if item != 0x43:
                        params.insert(0, item)

                stack.append(f(*params))    ##execute the function and push the result onto the stack
            elif next_byte != 0x03: ## seems to sometimes have 0x03 in middle of expression for some reason!??
                #push value onto stack
                stack.append(self.term(next_byte))

        #print "Pos before match 0xFD",progfile.tell()
        #MatchNum(0xFD) #consume expression terminator
        #pop and return last value off stack
        return stack.pop()

    def term(self, next_byte):
        if next_byte in self.TERM_DICT:
            func = self.TERM_DICT[next_byte]
            return func()
        else:
            return next_byte

    def GetVariable(self):
        location = self.read_ushort()
        return self.locations[location]

    def Int8(self):
        digits = self.read_byte()
        return self.read_byte()

    def Int16(self):
        digits = self.read_byte()
        return self.read_short()

    def Int32(self):
        digits = self.read_byte()
        return self.read_long()

    def QuestionMark(self):
        #print("Question Mark")
        sys.stdout.write('\n')  ##writes new line
        self.QuestionMarkDouble()

    def QuestionMarkDouble(self):
        #print("Double Question Mark")
        self.move_pointer(2)    #Skip the F8 03 bytes which are part of the 02 F8 03 code for the ? statement
        number_params = self.read_byte()
        ## mytext = self.Expression() #.decode("ascii") #decodes bytes into a string
        next_byte = self.read_byte()
        mytext = self.term(next_byte)
        sys.stdout.write(str(mytext))

    def ReadBytes(self, numbytes):
        mybytes=self.code[self.ip:self.ip+numbytes]
        self.ip=self.ip+numbytes
        return mybytes
        
    def String(self):
        string_length = self.read_ushort()
        return self.ReadBytes(string_length)

    def ReadString(self):
        string_length = self.read_ushort()
        bytestring = self.ReadBytes(string_length)
        return bytestring.decode()  # default encoding is 'ascii'
