"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_scope = {}
        self.subroutine_scope = {}
        self.cur_scope = None
        self.index = {"static": 0, "field": 0, "arg": 0, "var": 0, "while": 0, "if": 0}

    def start_subroutine(self, name) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's
        symbol table).
        """
        self.subroutine_scope[name] = {}
        self.index["arg"] = 0
        self.index["var"] = 0
        self.index["while"] = 0
        self.index["if"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns
        it a running index. "STATIC" and "FIELD" identifiers have a class scope,
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in ["static", "field"]:
            self.class_scope[name] = (type, kind, self.index[kind])
            self.index[kind] += 1
        else:  # kind in ["argument", "local"]
            self.cur_scope[name] = (type, kind, self.index[kind])
            self.index[kind] += 1

    def globals_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in
            the class scope.
        """
        return len([v for (k, v) in self.class_scope.items() if v[1] == kind])

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in
            the current scope.
        """
        return len([v for (k, v) in self.cur_scope.items() if v[1] == kind])

    def kind_of(self, name: str):
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.cur_scope:
            return self.cur_scope[name][1]
        elif name in self.class_scope:
            return self.class_scope[name][1]
        else:
            return None

    def type_of(self, name: str):
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.cur_scope:
            return self.cur_scope[name][0]
        elif name in self.class_scope:
            return self.class_scope[name][0]
        else:
            return None

    def index_of(self, name: str):
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.cur_scope:
            return self.cur_scope[name][2]
        elif name in self.class_scope:
            return self.class_scope[name][2]
        else:
            return None

    def set_scope(self, subroutine_name: str):
        """Sets the current scope to the given scope.

        Args:
            subroutine_name (str): the scope to set.
        """
        if subroutine_name == "class":
            self.cur_scope = self.class_scope
        else:
            self.cur_scope = self.subroutine_scope[subroutine_name]
