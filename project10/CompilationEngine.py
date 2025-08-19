"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.input_stream.advance()  # start reading the first token

    def compile_class(self) -> None:
        """Compiles a complete class.
         syntax: 'class' className '{' classVarDec* subroutineDec* '}'."""
        self.output_stream.write("<class>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # class
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # className
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # {
        self.input_stream.advance()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["static", "field"]:
            self.compile_class_var_dec()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["constructor", "function", "method"]:
            self.compile_subroutine()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # }
        self.output_stream.write("</class>\n")
        self.input_stream.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
        syntax: ('static' | 'field') type varName (',' varName)* ';'."""
        self.output_stream.write("<classVarDec>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # static | field
        self.input_stream.advance()
        self.write_type()  # type (int | char | boolean | className)
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
        self.input_stream.advance()
        while self.input_stream.symbol() == ",":  # (, varName)*
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ,
            self.input_stream.advance()
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
            self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ;
        self.output_stream.write("</classVarDec>\n")
        self.input_stream.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        syntax: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        self.output_stream.write("<subroutineDec>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # constructor | function | method
        self.input_stream.advance()
        self.write_type()  # void | type (int | char | boolean | className)
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # subroutineName
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # (
        self.input_stream.advance()
        self.compile_parameter_list()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # )
        self.input_stream.advance()
        self.output_stream.write("<subroutineBody>\n")
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # {
        self.input_stream.advance()
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # }
        self.output_stream.write("</subroutineBody>\n")
        self.output_stream.write("</subroutineDec>\n")
        self.input_stream.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the enclosing "()".
        syntax: (type varName (',' type varName)*)? """
        self.output_stream.write("<parameterList>\n")
        if self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ")":
            self.output_stream.write("</parameterList>\n")
            return  # empty parameter list
        self.write_type()  # type (int | char | boolean | className)
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
        self.input_stream.advance()
        while self.input_stream.symbol() == ",":  # (, type varName)*
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ,
            self.input_stream.advance()
            self.write_type()  # type (int | char | boolean | className)
            self.input_stream.advance()
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
            self.input_stream.advance()
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.
         syntax: 'var' type varName (',' varName)* ';'."""
        self.output_stream.write("<varDec>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # var
        self.input_stream.advance()
        self.write_type()  # type (int | char | boolean | className)
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
        self.input_stream.advance()
        while self.input_stream.symbol() == ",":
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ,
            self.input_stream.advance()
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
            self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ;
        self.output_stream.write("</varDec>\n")
        self.input_stream.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing {}".
        syntax: statement*"""
        self.output_stream.write("<statements>\n")
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["let", "if", "while", "do", "return"]:
            if self.input_stream.keyword() == "let":
                self.compile_let()
            elif self.input_stream.keyword() == "if":
                self.compile_if()
            elif self.input_stream.keyword() == "while":
                self.compile_while()
            elif self.input_stream.keyword() == "do":
                self.compile_do()
            elif self.input_stream.keyword() == "return":
                self.compile_return()
        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement.
         syntax: 'do' subroutineCall ';'."""
        self.output_stream.write("<doStatement>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # do
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # subroutineName | className | varName
        self.input_stream.advance()
        self.subroutine_call()  # subroutineCall
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ;
        self.output_stream.write("</doStatement>\n")
        self.input_stream.advance()

    def compile_let(self) -> None:
        """Compiles a let statement.
         syntax: 'let' varName ('[' expression ']')? '=' expression ';'."""
        self.output_stream.write("<letStatement>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # let
        self.input_stream.advance()
        self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName
        self.input_stream.advance()
        if self.input_stream.symbol() == "[":
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # [
            self.input_stream.advance()
            self.compile_expression()  # expression
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ]
            self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # =
        self.input_stream.advance()
        self.compile_expression()  # expression
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ;
        self.output_stream.write("</letStatement>\n")
        self.input_stream.advance()

    def compile_while(self) -> None:
        """Compiles a while statement.
         syntax: 'while' '(' 'expression' ')' '{' statements '}'."""
        self.output_stream.write("<whileStatement>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # while
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # (
        self.input_stream.advance()
        self.compile_expression()  # expression
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # )
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # {
        self.input_stream.advance()
        self.compile_statements()  # statements
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # }
        self.output_stream.write("</whileStatement>\n")
        self.input_stream.advance()

    def compile_return(self) -> None:
        """Compiles a return statement.
        syntax: 'return' expression? ';'"""
        self.output_stream.write("<returnStatement>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # return
        self.input_stream.advance()
        if self.input_stream.symbol() != ";":
            self.compile_expression()  # expression
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ;
        self.output_stream.write("</returnStatement>\n")
        self.input_stream.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause.
        syntax: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        self.output_stream.write("<ifStatement>\n")
        self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # if
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # (
        self.input_stream.advance()
        self.compile_expression()  # expression
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # )
        self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # {
        self.input_stream.advance()
        self.compile_statements()  # statements
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # }
        self.input_stream.advance()
        if self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() == "else":
            self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # else
            self.input_stream.advance()
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # {
            self.input_stream.advance()
            self.compile_statements()  # statements
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # }
            self.input_stream.advance()
        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression.
        syntax: term (op term)*"""
        self.output_stream.write("<expression>\n")
        self.compile_term()  # term
        while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # op
            self.input_stream.advance()
            self.compile_term()  # term
        self.output_stream.write("</expression>\n")

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
        self.output_stream.write("<term>\n")
        if self.input_stream.token_type() == "INT_CONST":
            self.output_stream.write("<integerConstant> " + str(self.input_stream.int_val()) + " </integerConstant>\n")  # integerConstant
            self.input_stream.advance()
        elif self.input_stream.token_type() == "STRING_CONST":
            self.output_stream.write("<stringConstant> " + self.input_stream.string_val() + " </stringConstant>\n")  # stringConstant
            self.input_stream.advance()
        elif self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["true", "false", "null", "this"]:
            self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # keywordConstant
            self.input_stream.advance()
        elif self.input_stream.symbol() == "(":  # '(' expression ')'
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # (
            self.input_stream.advance()
            self.compile_expression()  # expression
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # )
            self.input_stream.advance()
        elif self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() in ["-", "~"]:  # unaryOp term
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # unaryOp
            self.input_stream.advance()
            self.compile_term()  # term

        else:  # identifier, one of three options: varName | varName '[' expression ']' | subroutineCall
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # varName | subroutineName
            self.input_stream.advance()
            if self.input_stream.symbol() == "[":  # varName '[' expression ']'
                self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # [
                self.input_stream.advance()
                self.compile_expression()  # expression
                self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ]
                self.input_stream.advance()
            elif self.input_stream.symbol() in ["(", "."]:  # subroutineCall
                self.subroutine_call()
            # else: varName (already written)
        self.output_stream.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if self.input_stream.token_type() != "SYMBOL" or self.input_stream.symbol() != ")":
            self.compile_expression()
            while self.input_stream.symbol() == ",":
                self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # ,
                self.input_stream.advance()
                self.compile_expression()
        self.output_stream.write("</expressionList>\n")

    def write_type(self) -> None:  # added
        """Writes the type of the current token to the output stream."""
        if self.input_stream.token_type() == "KEYWORD":
            self.output_stream.write("<keyword> " + self.input_stream.keyword() + " </keyword>\n")  # int | char | boolean
        else:
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # className

    def subroutine_call(self) -> None:  # added
        """Compiles a subroutine call. The function is called after the first identifier of the subroutine call.
        syntax: subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'"""
        while self.input_stream.symbol() == ".":  # used while instead of if to allow chaining of subroutine calls
            self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # .
            self.input_stream.advance()
            self.output_stream.write("<identifier> " + self.input_stream.identifier() + " </identifier>\n")  # subroutineName
            self.input_stream.advance()
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # (
        self.input_stream.advance()
        self.compile_expression_list()  # expressionList
        self.output_stream.write("<symbol> " + self.input_stream.symbol() + " </symbol>\n")  # )
        self.input_stream.advance()
