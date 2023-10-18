# Samuel Clear, Michael Piscione, Kyrill Serdyuk, Max Pursche
# CS 3050: Software Engineering
# Professor Hibbeler
# 09/24/2023

# query_classes.py just holds all the dataclasses used in parsing a user's query. The classes help represent what a parsed query looks
# like in a human-readable form. For example, a query of the form 'stars "gitjk"' would be handled in the Access class (which is a child of
# the Query class), which holds the parameter to be looked for and the repo_name (value as it is seen in the class). The data held in each
# of these fields are also represented by classes as well. 

from dataclasses import dataclass
from typing import List

@dataclass(frozen=True, eq=True)
class Parameter():
    pass

# Seperate between str and int param? i.e only str param can have str value
@dataclass(frozen=True, eq=True)
class StrParam(Parameter):
    value: str

@dataclass(frozen=True, eq=True)
class IntParam(Parameter):
    value: str


# Values
@dataclass(frozen=True, eq=True)
class Value():
    pass

@dataclass(frozen=True, eq=True)
class StrValue(Value):
    value: str

@dataclass(frozen=True, eq=True)
class IntValue(Value):
    value: int

# Equality
@dataclass(frozen=True, eq=True)
class Equality():
    pass

@dataclass(frozen=True, eq=True)
class EqualTo(Equality):
    pass

@dataclass(frozen=True, eq=True)
class LessThan(Equality):
    pass

@dataclass(frozen=True, eq=True)
class GreaterThan(Equality):
    pass

@dataclass(frozen=True, eq=True)
class LessThanOrEqualTo(Equality):
    pass

@dataclass(frozen=True, eq=True)
class GreaterThanOrEqualTo(Equality):
    pass

@dataclass(frozen=True, eq=True)
class Comparison():
    equality: Equality
    parameter: StrParam
    value: Value

# Query
@dataclass(frozen=True, eq=True)
class Query():
    pass

@dataclass(frozen=True, eq=True)
class Search(Query):
    items: List[Comparison]

@dataclass(frozen=True, eq=True)
class Access(Query):
    parameter: StrParam
    value: StrValue