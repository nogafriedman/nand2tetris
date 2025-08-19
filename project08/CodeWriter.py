"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.filename = ""
        self.ram0_to_ram4 = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        self.memory_segments = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT",
                                "pointer": 3, "temp": 5}
        self.label_counter = 0  # for labels in comparison operations
        self.address_counter = 0  # for return address in write_call
        self.current_function = ""  # updates in write_function

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename
        print("translating file:", filename + ".vm")

    def _write_init(self) -> None:  # function added by me (according to youtube lecture API)
        """Writes assembly code that intializes the VM code (bootstrap code).
         Must be placed at the beginning of the generated *.asm file.
        """
        self.output_stream.write("@256\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D\n")
        self.write_call("Sys.init", 0)

    def _binary_operation(self, operation: str) -> None:  # function added by me
        """Writes assembly code for binary operations.

        Args:
            operation (str): binary operation.
        """
        self.output_stream.write("@SP\n") # pop first value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@SP\n") # pop second value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=M" + operation + "D\n")  # perform operation (+, -, &, |)
        self.output_stream.write("@SP\n") # push result
        self.output_stream.write("M=M+1\n")

    def _comparison_operation(self, operation: str) -> None:  # function added by me
        """Writes assembly code for comparison operations.

        Args:
            operation (str): comparison operation.
        """
        self.label_counter += 1
        # could cause overflow if the values are large and one of the values is negative and the other is positive,
        # so in the case of different signs, the function checks who is the negative and who is the positive
        # and returns the appropriate result (instead of subtracting one from the other)
        self.output_stream.write("@SP\n")  # pop first value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@R13\n")  # store first value in R13
        self.output_stream.write("M=D\n")

        self.output_stream.write("@FIRST_POS" + str(self.label_counter) + "\n")  # check if first value is positive
        self.output_stream.write("D;JGT\n")

        self.output_stream.write("@SP\n")  # pop second value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")

        self.output_stream.write("@SECOND_POS" + str(self.label_counter) + "\n")  # check if second value is positive
        self.output_stream.write("D;JGT\n")

        self.output_stream.write("@R13\n")  # load first value from R13
        self.output_stream.write("D=D-M\n")  # perform operation to check if first value is greater than second value
        self.output_stream.write("@COMPARE" + str(self.label_counter) + "\n")  # (reached only if both negative/0)
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(FIRST_POS" + str(self.label_counter) + ")\n")  # if first value is positive
        self.output_stream.write("@SP\n")  # pop second value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")

        self.output_stream.write("@SECOND_NEG" + str(self.label_counter) + "\n")  # check if second value is negative
        self.output_stream.write("D;JLT\n")

        self.output_stream.write("@R13\n")
        self.output_stream.write("D=D-M\n")  # perform operation to check if first value is greater than second value
        self.output_stream.write("@COMPARE" + str(self.label_counter) + "\n")  # (reached only if both positive/0)
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(SECOND_POS" + str(self.label_counter) + ")\n")
        self.output_stream.write("D=1\n")      # reached if first value is negative and second value is positive
        self.output_stream.write("@COMPARE" + str(self.label_counter) + "\n")
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(SECOND_NEG" + str(self.label_counter) + ")\n")
        self.output_stream.write("D=-1\n")     # reached if first value is positive and second value is negative
        self.output_stream.write("@COMPARE" + str(self.label_counter) + "\n")
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(COMPARE" + str(self.label_counter) + ")\n")
        self.output_stream.write("@TRUE" + str(self.label_counter) + "\n")  # jump if operation result is true
        self.output_stream.write("D;" + operation + "\n")

        self.output_stream.write("D=0\n")
        self.output_stream.write("@END" + str(self.label_counter) + "\n")  # if operation result is false
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(TRUE" + str(self.label_counter) + ")\n")
        self.output_stream.write("D=-1\n")
        self.output_stream.write("@END" + str(self.label_counter) + "\n")
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(END" + str(self.label_counter) + ")\n")
        self.output_stream.write("@SP\n") # push result, D=0 if false and D=-1 if true
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

    def _unary_operation(self, operation: str) -> None:  # function added by me
        """Writes assembly code for unary operations.

        Args:
            operation (str): unary operation.
        """
        self.output_stream.write("@SP\n") # pop value
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        if operation == ">>" or operation == "<<":
            self.output_stream.write("M=M" + operation + "\n")  # perform operation (<<, >>)
        else:
            self.output_stream.write("M=" + operation + "M\n") # perform operation (-, !)
        self.output_stream.write("@SP\n") # push result
        self.output_stream.write("M=M+1\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # arithmetic operations:
        if command == "add":
            self._binary_operation("+")
        elif command == "sub":
            self._binary_operation("-")
        elif command == "neg":
            self._unary_operation("-")

        # comparison operations:
        elif command == "eq":
            self._comparison_operation("JEQ")
        elif command == "gt":
            self._comparison_operation("JGT")
        elif command == "lt":
            self._comparison_operation("JLT")

        # logical operations:
        elif command == "and":
            self._binary_operation("&")
        elif command == "or":
            self._binary_operation("|")
        elif command == "not":
            self._unary_operation("!")

        elif command == "shiftleft":
            self._unary_operation("<<")
        elif command == "shiftright":
            self._unary_operation(">>")

    def _push_D(self) -> None:  # function added by me
        """
        Writes assembly code that pushes the value in D onto the stack.
        """
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

    def write_push(self, segment: str, index: int) -> None:
        """Writes assembly code for the push command.

        Args:
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if segment == "constant":
            self.output_stream.write("@" + str(index) + "\n")  # load constant into D
            self.output_stream.write("D=A\n")
            self._push_D()  # push value onto stack

        elif segment in self.ram0_to_ram4:  # local, argument, this, that
            self.output_stream.write("@" + str(index) + "\n")  # load index into D
            self.output_stream.write("D=A\n")
            self.output_stream.write("@" + self.ram0_to_ram4[segment] + "\n")  # load base address into A
            self.output_stream.write("A=M+D\n")  # add index to base address
            self.output_stream.write("D=M\n")  # load value at address into D
            self._push_D()  # push value onto stack

        elif segment == "temp" or segment == "pointer":  # temp 0-7 = RAM 5-12, pointer 0 = RAM 3, pointer 1 = RAM 4
            self.output_stream.write("@" + str(index) + "\n")  # load index into D
            self.output_stream.write("D=A\n")
            self.output_stream.write("@" + str(self.memory_segments[segment]) + "\n")  # load base address into A
            self.output_stream.write("A=A+D\n")  # add index to base address
            self.output_stream.write("D=M\n")  # load value at address into D
            self._push_D()  # push value onto stack

        elif segment == "static":
            self.output_stream.write("@" + self.filename + "." + str(index) + "\n")
            self.output_stream.write("D=M\n")
            self._push_D()  # push value onto stack

    def write_pop(self, segment: str, index: int) -> None:
        """Writes assembly code for the pop command.

        Args:
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if segment == "static":
            self.output_stream.write("@SP\n")
            self.output_stream.write("M=M-1\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@" + self.filename + "." + str(index) + "\n")
            self.output_stream.write("M=D\n")

        else:  # local, argument, this, that, pointer, temp
            self.output_stream.write("@" + str(index) + "\n")  # load index into D
            self.output_stream.write("D=A\n")
            self.output_stream.write("@" + str(self.memory_segments[segment]) + "\n")
            if segment in self.ram0_to_ram4:
                self.output_stream.write("A=M\n")
            self.output_stream.write("D=A+D\n")  # add index to base address
            self.output_stream.write("@R13\n")  # store address in R13
            self.output_stream.write("M=D\n")
            self.output_stream.write("@SP\n")  # pop value into D
            self.output_stream.write("M=M-1\n")
            self.output_stream.write("A=M\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@R13\n")  # load address from R13
            self.output_stream.write("A=M\n")
            self.output_stream.write("M=D\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            self.write_push(segment, index)

        elif command == "C_POP":
            self.write_pop(segment, index)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write("(" + self.current_function + "$" + label + ")\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("@" + self.current_function + "$" + label + "\n")
        self.output_stream.write("0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write("@SP\n")  # pop value into D
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@" + self.current_function + "$" + label + "\n")
        self.output_stream.write("D;JNE\n")  # jump if D != 0

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        self.current_function = function_name
        self.output_stream.write("(" + function_name + ")\n")
        for i in range(n_vars):
            self.write_push("constant", 0)  # initializes the local variables to 0

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        self.address_counter += 1
        return_address = function_name + "$ret" + str(self.address_counter)

        self.output_stream.write("@" + return_address + "\n")
        self.output_stream.write("D=A\n")
        self._push_D()  # push return address onto stack

        for seg in ["LCL", "ARG", "THIS", "THAT"]:  # saves seg of the caller
            self.output_stream.write("@" + seg + "\n")
            self.output_stream.write("D=M\n")
            self._push_D()  # push seg onto stack

        self.output_stream.write("@5\n")
        self.output_stream.write("D=A\n")
        self.output_stream.write("@" + str(n_args) + "\n")  # reposition ARG
        self.output_stream.write("D=D+A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M-D\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("M=D\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@LCL\n")  # reposition LCL
        self.output_stream.write("M=D\n")

        self.output_stream.write("@" + function_name + "\n")  # transfer control to the callee
        self.output_stream.write("0;JMP\n")

        self.output_stream.write("(" + return_address + ")\n")  # inject return address label into the code

    def write_return(self) -> None:
        """Writes assembly code that affects the return command.
        """
        self.output_stream.write("@LCL\n")  # put return address in a temp var
        self.output_stream.write("D=M\n")
        self.output_stream.write("@R13\n")
        self.output_stream.write("M=D\n")

        self.output_stream.write("@5\n")
        self.output_stream.write("A=D-A\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@R14\n")
        self.output_stream.write("M=D\n")

        self.output_stream.write("@SP\n")  # reposition return value for the caller
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("@ARG\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")

        self.output_stream.write("@ARG\n")  # reposition SP for the caller
        self.output_stream.write("D=M+1\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=D\n")

        for seg in ["THAT", "THIS", "ARG", "LCL"]:
            self.output_stream.write("@R13\n")  # restore seg for caller
            self.output_stream.write("AM=M-1\n")
            self.output_stream.write("D=M\n")
            self.output_stream.write("@" + seg + "\n")
            self.output_stream.write("M=D\n")

        self.output_stream.write("@R14\n")  # go to return address
        self.output_stream.write("A=M\n")
        self.output_stream.write("0;JMP\n")

    def close(self) -> None:  # function added by me
        """Closes the output file.
        """
        self.output_stream.close()
