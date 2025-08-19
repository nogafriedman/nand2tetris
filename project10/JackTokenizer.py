"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = list(input_stream.read().splitlines())  # read lines into list
        self.clean_list()  # clean list to prepare for parsing
        self.line_tokens = []  # the tokens found in the current line
        self.cur_token = None  # the current token we are translating to the output stream

    def clean_list(self) -> None:  # added
        """Cleans and prepares the input_lines list for parsing. Removes comments, trailing whitespaces and empty lines.
        """
        self.remove_comments()  # remove all comments from the input
        self.input_lines = [line.strip() for line in self.input_lines]  # remove leading and trailing whitespace
        self.input_lines = [line for line in self.input_lines if line not in [" ", ""]]  # remove empty lines

    def remove_comments(self) -> None:  # added
        """Removes all comments from the input lines list unless the comment is inside a double quotes string.
        """
        clean_lines = []
        inside_double_quotes = False
        inside_multi_line_comment = False

        for line in self.input_lines:
            cleaned_line = ""
            i = 0
            while i < len(line):
                char = line[i]

                if char == '"':
                    if inside_multi_line_comment:  # if inside a multi-line comment, ignore double quotes
                        i += 1
                        continue
                    inside_double_quotes = not inside_double_quotes
                    cleaned_line += char
                    i += 1
                    continue

                if not inside_double_quotes:
                    if char == '/' and i + 1 < len(line) and line[i + 1] == '/':  # single-line comment, skip the rest
                        break
                    elif char == '/' and i + 1 < len(line) and line[i + 1] == '*':  # start of multi-line comment
                        inside_multi_line_comment = True
                        i += 2
                        continue
                    elif char == '*' and i + 1 < len(line) and line[i + 1] == '/':  # end of multi-line comment
                        inside_multi_line_comment = False
                        i += 2
                        continue
                    if not inside_multi_line_comment:  # if not inside a comment, add the character to the cleaned line
                        cleaned_line += char

                else:
                    cleaned_line += char
                i += 1

            clean_lines.append(cleaned_line)

        self.input_lines = clean_lines

    def parse_line(self) -> None:  # added
        """Parses the current line into tokens and saves them in a list.
        """
        re_keyword = "\b(?:class|constructor|function|method|field|static|var|int|char|boolean" \
                     "|void|true|false|null|this|let|do|if|else|while|return)\b"
        re_symbol = "[\\&\\*\\+\\(\\)\\.\\/\\,\\-\\]\\;\\~\\}\\|\\{\\>\\=\\[\\<]"
        re_int = "[0-9]+"
        re_str = "\"[^\"\n]*\""
        re_identifier = r"[a-zA-Z_]\w*"

        self.line_tokens = re.compile(re_keyword + "|" + re_symbol + "|" + re_int + "|" + re_str + "|" + re_identifier)
        self.line_tokens = self.line_tokens.findall(self.input_lines[0])

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # check if there are more tokens in the current line or if there are more lines to parse
        return self.line_tokens != [] or self.input_lines != []

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():

            while self.line_tokens == []:  # parse lines until a line with tokens is found
                self.parse_line()
                self.input_lines.pop(0)

            self.cur_token = self.line_tokens.pop(0)  # get the next token from the list and remove it

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in ["class", "constructor", "function", "method",
                              "field", "static", "var", "int", "char", "boolean",
                              "void", "true", "false", "null", "this", "let",
                              "do", "if", "else", "while", "return"]:
            return "KEYWORD"
        if self.cur_token in ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                             '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']:
            return "SYMBOL"
        if self.cur_token.isdigit():
            return "INT_CONST"
        if  self.cur_token.startswith('"') and self.cur_token.endswith('"'):
            return "STRING_CONST"
        return "IDENTIFIER"  # if none of the above

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.cur_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.cur_token == '<':
            return '&lt;'
        if self.cur_token == '>':
            return '&gt;'
        if self.cur_token == '&':
            return '&amp;'
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.cur_token[1:-1]
