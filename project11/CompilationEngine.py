"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer
import SymbolTable
import VMWriter

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    def __init__(self, input_stream: "JackTokenizer", output_stream: VMWriter) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.vm_writer = output_stream
        self.symbol_table = SymbolTable.SymbolTable()
        self.class_name = None
        self.subroutine_name = None

    def compile_class(self) -> None:
        """Compiles a complete class.
         syntax: 'class' className '{' classVarDec* subroutineDec* '}'."""
        self.tokenizer.advance()  # class
        self.tokenizer.advance()  # className
        self.class_name = self.tokenizer.identifier()
        self.tokenizer.advance()  # {
        while self.tokenizer.next_token() in ["static","field"]:
            self.compile_class_var_dec()
        while self.tokenizer.next_token() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        self.tokenizer.advance()  # }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
        syntax: ('static' | 'field') type varName (',' varName)* ';'."""
        while self.tokenizer.next_token() in ["static", "field"]:
            self.tokenizer.advance()  # static | field
            kind = self.tokenizer.keyword()
            self.tokenizer.advance()   # type
            type = self.get_type()  # (int | char | boolean | className)
            self.tokenizer.advance()  # varName
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, kind)

            while self.tokenizer.next_token() == ",":  # (, varName)*
                self.tokenizer.advance()  # ,
                self.tokenizer.advance()  # varName
                name = self.tokenizer.identifier()
                self.symbol_table.define(name, type, kind)

            self.tokenizer.advance()  # ;

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        syntax: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        self.tokenizer.advance()  # constructor | function | method
        function_type = self.tokenizer.keyword()
        self.tokenizer.advance()  # void | type
        self.tokenizer.advance()  # subroutineName
        self.subroutine_name = self.class_name + "." + self.tokenizer.identifier()
        self.symbol_table.start_subroutine(self.subroutine_name)  # reset the subroutine's symbol table
        self.symbol_table.set_scope(self.subroutine_name)  # set the current scope to the current subroutine's scope
        self.tokenizer.advance()  # (
        self.compile_parameter_list(function_type)
        self.tokenizer.advance()  # )
        self.compile_subroutine_body(function_type)

    def compile_subroutine_body(self, function_type: str) -> None:
        """Compiles the body of a subroutine."""
        self.tokenizer.advance()  # {
        while self.tokenizer.next_token() == "var":
            self.compile_var_dec()
        num_vars = self.symbol_table.var_count("var")
        self.vm_writer.write_function(self.subroutine_name, num_vars)  # function name num_vars

        if function_type == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        elif function_type == "constructor":
            num_fields = self.symbol_table.globals_count("field")
            self.vm_writer.write_push("constant", num_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements()
        self.tokenizer.advance()  # }
        self.symbol_table.set_scope("class")  # reset the current scope to class scope

    def compile_parameter_list(self, function_type) -> None:
        """Compiles a (possibly empty) parameter list, not including the enclosing "()".
        syntax: (type varName (',' type varName)*)? """
        if function_type == "method":
            self.symbol_table.define("this", "self", "arg")

        while self.tokenizer.next_token_type() != "SYMBOL":  # while more parameters are left
            self.tokenizer.advance()  # type
            type = self.get_type()  # int | char | boolean | className
            self.tokenizer.advance()  # varName
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, "arg")

            if self.tokenizer.next_token() == ",":  # while more parameters are left
                self.tokenizer.advance()  # ,

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.
         syntax: 'var' type varName (',' varName)* ';'."""
        self.tokenizer.advance()  # var
        kind = self.tokenizer.keyword()
        self.tokenizer.advance()  # type
        type = self.get_type()  # int | char | boolean | className
        self.tokenizer.advance()  # varName
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, kind)

        while self.tokenizer.next_token() == ",":  # while more variables are left
            self.tokenizer.advance()  # ,
            self.tokenizer.advance()  # varName
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, kind)

        self.tokenizer.advance()  # ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing {}".
        syntax: statement*"""
        while self.tokenizer.next_token() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.next_token() == "let":
                self.compile_let()
            elif self.tokenizer.next_token() == "if":
                self.compile_if()
            elif self.tokenizer.next_token() == "while":
                self.compile_while()
            elif self.tokenizer.next_token() == "do":
                self.compile_do()
            elif self.tokenizer.next_token() == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement.
         syntax: 'do' subroutineCall ';'."""
        self.tokenizer.advance()  # do
        self.compile_subroutine_call()
        self.vm_writer.write_pop("temp", 0)
        self.tokenizer.advance() # ;

    def compile_let(self) -> None:
        """Compiles a let statement.
         syntax: 'let' varName ('[' expression ']')? '=' expression ';'."""
        array = False
        self.tokenizer.advance()  # let
        self.tokenizer.advance()  # varName
        name = self.tokenizer.identifier()

        if self.tokenizer.next_token() == "[":  # varName '[' expression ']'
            array = True
            self.tokenizer.advance()  # [
            self.compile_expression()
            self.tokenizer.advance()  # ]
            self.compile_array(name)
        self.tokenizer.advance()  # =
        self.compile_expression()
        if array:
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.pop_variable(name)
        self.tokenizer.advance()  # ;

    def compile_while(self) -> None:
        """Compiles a while statement.
         syntax: 'while' '(' 'expression' ')' '{' statements '}'."""
        count = self.symbol_table.index["while"]
        self.symbol_table.index["while"] += 1
        self.vm_writer.write_label("WHILE_EXP" + str(count))
        self.tokenizer.advance()  # while
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if("WHILE_END" + str(count))
        self.tokenizer.advance()  # )
        self.tokenizer.advance()  # {
        self.compile_statements()
        self.vm_writer.write_goto("WHILE_EXP" + str(count))
        self.vm_writer.write_label("WHILE_END" + str(count))
        self.tokenizer.advance()  # }

    def compile_return(self) -> None:
        """Compiles a return statement.
        syntax: 'return' expression? ';'"""
        self.tokenizer.advance()  # return
        empty = True
        if self.is_term():
            empty = False
            self.compile_expression()
        if empty:
            self.vm_writer.write_push("constant", 0)
        self.vm_writer.write_return()
        self.tokenizer.advance()  # ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause.
        syntax: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        self.tokenizer.advance()  # if
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.tokenizer.advance()  # )
        count = self.symbol_table.index["if"]
        self.symbol_table.index["if"] += 1
        self.vm_writer.write_if("IF_TRUE" + str(count))
        self.vm_writer.write_goto("IF_FALSE" + str(count))
        self.vm_writer.write_label("IF_TRUE" + str(count))
        self.tokenizer.advance()  # {
        self.compile_statements()
        self.tokenizer.advance()  # }
        if self.tokenizer.next_token() == "else":
            self.vm_writer.write_goto("IF_END" + str(count))
            self.vm_writer.write_label("IF_FALSE" + str(count))
            self.tokenizer.advance()  # else
            self.tokenizer.advance()  # {
            self.compile_statements()
            self.tokenizer.advance()  # }
            self.vm_writer.write_label("IF_END" + str(count))
        else:
            self.vm_writer.write_label("IF_FALSE" + str(count))

    def compile_expression(self) -> None:
        """Compiles an expression.
        syntax: term (op term)*"""
        self.compile_term()  # term
        while self.tokenizer.next_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self.tokenizer.advance()  # op
            op = self.tokenizer.symbol()
            self.compile_term()
            if op == "+":
                self.vm_writer.write_arithmetic("add")
            elif op == "-":
                self.vm_writer.write_arithmetic("sub")
            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)
            elif op == "&amp;":
                self.vm_writer.write_arithmetic("and")
            elif op == "|":
                self.vm_writer.write_arithmetic("or")
            elif op == "&lt;":
                self.vm_writer.write_arithmetic("lt")
            elif op == "&gt;":
                self.vm_writer.write_arithmetic("gt")
            elif op == "=":
                self.vm_writer.write_arithmetic("eq")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        syntax: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' |
         subroutineCall | '(' expression ')' | unaryOp term
        """
        array = False
        if self.tokenizer.next_token_type() == "INT_CONST":
            self.tokenizer.advance()
            value = str(self.tokenizer.int_val())  # integerConstant
            self.vm_writer.write_push("constant", value)

        elif self.tokenizer.next_token_type() == "STRING_CONST":
            self.tokenizer.advance()
            value = self.tokenizer.string_val()  # stringConstant
            self.vm_writer.write_push("constant", len(value))
            self.vm_writer.write_call("String.new", 1)
            for char in value:
                self.vm_writer.write_push("constant", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)

        elif self.tokenizer.next_token() in ["true", "false", "null", "this"]:
            self.tokenizer.advance()
            value = self.tokenizer.keyword()  # keywordConstant
            if value == "this":
                self.vm_writer.write_push("pointer", 0)
            else:
                self.vm_writer.write_push("constant", 0)
                if value == "true":
                    self.vm_writer.write_arithmetic("not")

        elif self.tokenizer.next_token() == "(":  # '(' expression ')'
            self.tokenizer.advance()  # (
            self.compile_expression()
            self.tokenizer.advance()  # )

        elif self.tokenizer.next_token() in ["-", "~", "^", "#"]:  # unaryOp term
            self.tokenizer.advance()
            op = self.tokenizer.symbol()  # unaryOp
            self.compile_term()
            if op == "-":
                self.vm_writer.write_arithmetic("neg")
            elif op == "~":
                self.vm_writer.write_arithmetic("not")
            elif op == "^":
                self.vm_writer.write_arithmetic("shiftleft")
            elif op == "#":
                self.vm_writer.write_arithmetic("shiftright")

        else:  # identifier: varName | varName '[' expression ']' | subroutineCall
            self.tokenizer.advance()  # varName | subroutineName
            name = self.tokenizer.identifier()
            num_args = 0

            if self.tokenizer.next_token() == "[":  # varName '[' expression ']'
                array = True
                self.tokenizer.advance()  # [
                self.compile_expression()
                self.tokenizer.advance()  # ]
                self.compile_array(name)

            if self.tokenizer.next_token() == "(":
                num_args += 1
                self.vm_writer.write_push("pointer", 0)
                self.tokenizer.advance()  # (
                num_args += self.compile_expression_list()
                self.tokenizer.advance()  # )
                self.vm_writer.write_call(self.class_name + "." + name, num_args)

            elif self.tokenizer.next_token() == ".":
                self.tokenizer.advance()
                self.tokenizer.advance()
                second_name = self.tokenizer.identifier()
                if name in self.symbol_table.cur_scope or name in self.symbol_table.class_scope:
                    self.push_variable(name)
                    full_name = self.symbol_table.type_of(name) + "." + second_name
                    num_args += 1
                else:
                    full_name = name + "." + second_name
                self.tokenizer.advance()  # (
                num_args += self.compile_expression_list()
                self.tokenizer.advance()  # )
                self.vm_writer.write_call(full_name, num_args)

            else:  # varName
                if array:
                    self.vm_writer.write_pop("pointer", 1)
                    self.vm_writer.write_push("that", 0)
                else:
                    self.push_variable(name)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions.

        Returns:
            int: The number of expressions in the list.
        """
        count = 0
        if self.is_term():
            self.compile_expression()
            count += 1
        while self.tokenizer.next_token() == ",":
            self.tokenizer.advance()  # ,
            self.compile_expression()
            count += 1
        return count

    def is_term(self) -> bool:  # added
        """Checks if the current token is a term.

        Returns:
            bool: True if the next token is a term, False otherwise.
        """
        return self.tokenizer.next_token_type() == "INT_CONST" or self.tokenizer.next_token_type() == "STRING_CONST" or\
            self.tokenizer.next_token_type() == "KEYWORD" or self.tokenizer.next_token_type() == "IDENTIFIER" or \
            self.tokenizer.next_token() in ["(", "-", "~"]

    def get_type(self) -> str:  # added
        """Gets the type of the current token.

        Returns:
            str: The type of the current token.
        """
        if self.tokenizer.token_type() == "KEYWORD":
            return self.tokenizer.keyword()  # int | char | boolean
        else:
            return self.tokenizer.identifier()  # className

    def compile_subroutine_call(self) -> None:  # added
        """Compiles a subroutine call. The function is called after the first identifier of the subroutine call.
        syntax: subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        """
        num_args = 0
        self.tokenizer.advance()  # subroutineName | className | varName
        first_name = self.tokenizer.identifier()

        if self.tokenizer.next_token() == ".":  # className | varName '.' subroutineName (chain of calls)
            self.tokenizer.advance()  # .
            self.tokenizer.advance()  # subroutineName
            second_name = self.tokenizer.identifier()
            if first_name in self.symbol_table.cur_scope or first_name in self.symbol_table.class_scope:
                self.push_variable(first_name)
                full_name = self.symbol_table.type_of(first_name) + "." + second_name
                num_args += 1
            else:
                full_name = first_name + "." + second_name

        else:  # subroutineName
            self.vm_writer.write_push("pointer", 0)
            full_name = self.class_name + "." + first_name
            num_args += 1

        self.tokenizer.advance()  # (
        num_args += self.compile_expression_list()
        self.vm_writer.write_call(full_name, num_args)
        self.tokenizer.advance()  # )

    def compile_array(self, name: str) -> None:  # added
        """Compiles an array by pushing the base address of the array and the index to the stack.
        """
        if name in self.symbol_table.cur_scope:
            if self.symbol_table.kind_of(name) == "var":
                self.vm_writer.write_push("local", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "arg":
                self.vm_writer.write_push("argument", self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == "field":
                self.vm_writer.write_push("this", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "static":
                self.vm_writer.write_push("static", self.symbol_table.index_of(name))
        self.vm_writer.write_arithmetic("add")

    def push_variable(self, name: str) -> None:  # added
        """Pushes the variable to the stack.

        Args:
            name (str): The name of the variable.
        """
        if name in self.symbol_table.cur_scope:
            if self.symbol_table.kind_of(name) == "var":
                self.vm_writer.write_push("local", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "arg":
                self.vm_writer.write_push("argument", self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == "field":
                self.vm_writer.write_push("this", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "static":
                self.vm_writer.write_push("static", self.symbol_table.index_of(name))

    def pop_variable(self, name: str) -> None:  # added
        """Pops the variable from the stack.

        Args:
            name (str): The name of the variable.
        """
        if name in self.symbol_table.cur_scope:
            if self.symbol_table.kind_of(name) == "var":
                self.vm_writer.write_pop("local", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "arg":
                self.vm_writer.write_pop("argument", self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == "field":
                self.vm_writer.write_pop("this", self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == "static":
                self.vm_writer.write_pop("static", self.symbol_table.index_of(name))
