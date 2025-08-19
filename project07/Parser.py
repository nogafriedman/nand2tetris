"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.lines = input_file.read().splitlines()  # saves every line as an element in a list
        self.num_lines = len(self.lines)
        self.cur_line_num = -1
        self.cur_line = ""

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_line_num < self.num_lines - 1  # True if the next potential line is within the list limits

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        while self.has_more_commands():
            self.cur_line_num += 1
            self.cur_line = self.lines[self.cur_line_num]

            self.cur_line = self.cur_line.replace('\t', '').replace('\n', '')  # removes all tabs and newlines
            self.cur_line = self.cur_line.split("//", 1)[0]  # removes everything from "//" onwards (comments)
            self.cur_line = self.cur_line.strip()  # removes all leading and trailing whitespaces

            if self.cur_line == "":
                continue
            break  # exits function if found a valid line

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.cur_line in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"]:
            return "C_ARITHMETIC"
        elif self.cur_line.startswith("push"):
            return "C_PUSH"
        elif self.cur_line.startswith("pop"):
            return "C_POP"
        elif self.cur_line.startswith("label"):
            return "C_LABEL"
        elif self.cur_line.startswith("goto"):
            return "C_GOTO"
        elif self.cur_line.startswith("if-goto"):
            return "C_IF"
        elif self.cur_line.startswith("function"):
            return "C_FUNCTION"
        elif self.cur_line.startswith("return"):
            return "C_RETURN"
        elif self.cur_line.startswith("call"):
            return "C_CALL"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.cur_line in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"]:
            return self.cur_line

        # two arguments commands:
        # first split returns a list of the form: ["command", " arg1 arg2"]
        # second split returns a list of the form: [" ", "arg1", "arg2"]
        elif self.cur_line.startswith("push"):
            return self.cur_line.split("push", 1)[1].split(" ", 2)[1]
        elif self.cur_line.startswith("pop"):
            return self.cur_line.split("pop", 1)[1].split(" ", 2)[1]
        elif self.cur_line.startswith("function"):
            return self.cur_line.split("function", 1)[1].split(" ", 2)[1]
        elif self.cur_line.startswith("call"):
            return self.cur_line.split("call", 1)[1].split(" ", 2)[1]

        # one argument commands:
        # first split returns a list of the form: ["command", " arg1"]
        # second split returns a list of the form: [" ", "arg1"]
        elif self.cur_line.startswith("label"):
            return self.cur_line.split("label", 1)[1].split(" ", 1)[1]
        elif self.cur_line.startswith("goto"):
            return self.cur_line.split("goto", 1)[1].split(" ", 1)[1]
        elif self.cur_line.startswith("if-goto"):
            return self.cur_line.split("if-goto", 1)[1].split(" ", 1)[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # first split returns a list of the form: ["command", " arg1 arg2"]
        # second split returns a list of the form: [" ", "arg1", "arg2"]

        if self.cur_line.startswith("push"):
            return int(self.cur_line.split("push", 1)[1].split(" ", 2)[2])
        elif self.cur_line.startswith("pop"):
            return int(self.cur_line.split("pop", 1)[1].split(" ", 2)[2])
        elif self.cur_line.startswith("function"):
            return int(self.cur_line.split("function", 1)[1].split(" ", 2)[2])
        elif self.cur_line.startswith("call"):
            return int(self.cur_line.split("call", 1)[1].split(" ", 2)[2])
