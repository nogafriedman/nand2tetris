"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    symbol_table = SymbolTable()
    rom_address = 0
    ram_address = 16

    # first pass: add labels to symbol table
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "L_COMMAND":
            symbol_table.add_entry(parser.symbol(), rom_address)
        else:
            rom_address += 1

    # second pass: translate commands to binary and write to output file
    input_file.seek(0)  # reset file pointer to beginning of file
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "A_COMMAND":  # starts with @
            symbol = parser.symbol()  # either an integer or a variable name
            if symbol.isnumeric():
                output_file.write("0" + bin(int(symbol))[2:].zfill(15) + "\n")  ## TODO check
                continue
            elif not symbol_table.contains(symbol):
                symbol_table.add_entry(symbol, ram_address)
                ram_address += 1
            output_file.write("0" + bin(symbol_table.get_address(symbol))[2:].zfill(15) + "\n")  ## TODO check
        elif parser.command_type() == "C_COMMAND" or parser.cur_line == "0;JMP":
            if ">>" in parser.cur_line or "<<" in parser.cur_line:  # shift command
                output_file.write("101" + Code.comp(parser.comp()) + Code.dest(parser.dest()) + Code.jump(parser.jump()) + "\n")
            else:  # regualr commands
                output_file.write("111" + Code.comp(parser.comp()) + Code.dest(parser.dest()) + Code.jump(parser.jump()) + "\n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
