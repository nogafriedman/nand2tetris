"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

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
        return self.cur_line_num + 1 <= self.num_lines - 1  # True if the next potential line is within the list limits

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        while self.has_more_commands():
            self.cur_line_num += 1
            self.cur_line = self.lines[self.cur_line_num]

            self.cur_line = self.cur_line.replace(" ", "")  # removes whitespaces from the beginning and end of the line
            self.cur_line = self.cur_line.split("//", 1)[0]  # removes everything from "//" onwards

            # if self.cur_line.startswith("//"):
            #     continue
            if self.cur_line == "":
                continue
            break  # exits function if found a valid line

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.cur_line.startswith("@"):
            return "A_COMMAND"
        elif self.cur_line.startswith("M") or self.cur_line.startswith("D") or self.cur_line.startswith("A") or self.cur_line.startswith("0"):
            return "C_COMMAND"
        elif self.cur_line.startswith("("):
            return "L_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "A_COMMAND":
            return str(self.cur_line[1:])
        elif self.command_type() == "L_COMMAND":
            return self.cur_line[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if "=" in self.cur_line:
            return self.cur_line.split("=")[0]  # commmand is of the form dest=comp
        else:
            return ""  # no dest

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if "=" in self.cur_line:
            return self.cur_line.split("=")[1]  # commmand is of the form dest=comp
        elif ";" in self.cur_line:
            return self.cur_line.split(";")[0]  # command is of the form comp;jump

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if ";" in self.cur_line:
            return self.cur_line.split(";")[1]  # command is of the form comp;jump
        else:
            return ""  # no jump
