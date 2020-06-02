import Library  # Must prefix function calls with "Library."
from VirtualMachine import VirtualMachine

#Instantiate the VirtualMachine
myVM = VirtualMachine()

#Load the VM with the code from the FXP
sourcefile = "helloworld.fxp"
progfile = open(sourcefile,"rb")    ## rb = Readonly Binary mode
progfile.seek(0x4e) #from beginning of file (0)
code_area_size = Library.read_unsigned_short(progfile)

myVM.code = progfile.read(code_area_size)

#Close the FXP
progfile.close()

myVM.interpret()

