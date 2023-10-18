# Samuel Clear, Michael Piscione, Kyrill Serdyuk, Max Pursche
# CS 3050: Software Engineering
# Professor Hibbeler
# 09/24/2023

# query_parser.py holds the actual parser for the user's commands. Note that all string values
# should be enclosed in "" and quotation marks should never be present within the string itself.
# Ex: repo_name == "gitjk". repo_name is a string parameter but "gitjk" is a string value for that
# parameter.

from typing import List, Tuple
from query_classes import *

def parse_value(data: str) -> Value | None:
    if data.startswith('"') and data.endswith('"'):
        # Parse string value
        parsed = data.removeprefix('"')
        parsed = parsed.removesuffix('"')
        if not data.isascii():
            print("failed ascii")
            return None
        if '"' in parsed or "'" in parsed:
            return None
        return StrValue(parsed)
    else:
        #parse Int value
        try:
            parsed = int(data)
            return IntValue(parsed)
        except:
            return None
    
def try_parse_str_value(data: str) -> Tuple[StrValue, str] | None:
    # Don't bother trying to parse non StrValue data
    if not data.startswith('"'):
        return None
    
    # Check that there is a closing double quote to split on
    if '"' not in data[1:]:
        return None
    
    value_data, remainder = data[1:].split('"', 1)
    # The substring and split stripped the quotes of value_data
    # Parse value expects str values to be surrounded by quotes
    value = parse_value(f'"{value_data}"')
    match value:
        case None | IntValue(_):
            # We failed to parse
            return None
        case StrValue(_):
            pass
        case _:
            raise NotImplementedError
    # Chop off the leading space from remainder
    return value, remainder[1:]

def try_parse_int_value(data: str) -> Tuple[IntValue, str] | None:
    # Single case
    if ' ' not in data:
        value = parse_value(data)
        match value:
            case IntValue(_):
                return (value, '')
            case StrValue(_) | None:
                return None
    value_data, remainder = data.split(' ', 1)
    value = parse_value(value_data)
    match value:
            case IntValue(_):
                return (value, remainder)
            case StrValue(_) | None:
                return None


def parse_parameter(data: str) -> Parameter | None:
    # Check the restrictions on the parameter
    # Should not contain quotes
    if '"' in data or "'" in data:
        return None
    # Should only contain ascii characters
    if not data.isascii():
        return None
    # Should on contain letters
    if True in [x.isdigit() for x in data]:
        return None
    
    # Return the Parameter, differentiate between str and int parameters
    param_str = [
        "repo_name",
        "created",
        "description",
        "language",
        "topics",
        "parent_repository",
        "name",
        "type"
    ]

    param_int = [
        "forks",
        "id",
        "stars",
        "subscribers"
    ]

    if data in param_str:
        return StrParam(data)
    elif data in param_int:
        return IntParam(data)
    else:
        # This isn't a valid parameter :^)
        return None


def parse_equality(data: str) -> Equality | None:
    match data:
        case '==':
            return EqualTo()
        case '>': 
            return GreaterThan()
        case '<':
            return LessThan()
        case '>=':
            return GreaterThanOrEqualTo()
        case '<=':
            return LessThanOrEqualTo()
        # case '!=':
        #     return NotEqualTo()
        case _: return None


def try_parse_access_query(data: str) -> Access | None:
    if ' ' not in data:
        return None
    param_data, mod_data = data.split(' ', 1)
    parameter = parse_parameter(param_data)
    if parameter is None:
        return None 
    
    # Try to parse a StrValue for access query
    if mod_data.startswith('"'):
        # Check that there is a closing double quote to split on
        # Otherwise the query is malformed
        match try_parse_str_value(mod_data):
            case (value, remainder):
                if remainder != '':
                    # There is data after the second param
                    # This is a malformed query
                    return None
                # This is a valid access query
                return Access(parameter, value)
            case None | _:
                return None
            

def try_parse_comparison(data: str) -> Tuple[Comparison, str] | None:
    # Parse a parameter
    if ' ' not in data:
        return None
    param_data, remainder = data.split(' ', 1)
    parameter = parse_parameter(param_data)
    if parameter is None:
        return None 
    
    # Parse an equality
    if ' ' not in remainder:
        return None
    equality_data, remainder = remainder.split(' ', 1)

    equality = parse_equality(equality_data)
    if equality is None:
        return None
    
    # Parse a value
    match try_parse_str_value(remainder), try_parse_int_value(remainder):
        case (val, rem), None:
            # We successfully parsed a string
            return Comparison(equality, parameter, val), rem
        case None, (val, rem):
            # We successfully parsed a string
            return Comparison(equality, parameter, val), rem
        case None, None | _:
            # We failed to parse anything
            # Or we parsed both but reject because queries must be unambiguous :^)
            return None
    


def parse(data: str) -> Query | None:
    # First, attempt to parse a Access Query
    # Since access queries are limited in size and complexity
    match try_parse_access_query(data):
        case Access(param, val):
            # We have an access query
            return Access(param, val)
        case None:
            # Now we should try to parse a Search query
            pass

    comparisons: List[Comparison] = []
    mod_data = data
    while True:
        # Try to parse a comparison
        match try_parse_comparison(mod_data):
            case Comparison(e, p, v), rem:
                match e, p, v:
                    case EqualTo(), StrParam(_), StrValue(_):
                        pass
                    case _, IntParam(_), IntValue(_):
                        pass
                    case _:
                        # Mismatch in param and value type
                        return None
                comparisons.append(Comparison(e, p, v))
                mod_data = rem
            case None:
                # Failure to parse means malformed query
                return None
        
        if mod_data == '':
            # We are done parsing
            break

        # Try to chop off the "and" and continue parsing
        if ' ' not in mod_data:
            # There is garbage on the end of my query >:(
            return None
        and_data, mod_data = mod_data.split(' ', 1)
        if and_data != 'and':
            # There is still garbage on the end of my query >:(
            return None
        
    
    # We have parsed all comparison
    return Search(comparisons)


def print_query(query: Query):
    match query:
        case Search(comparisons):
            output = 'Is '
            for cmp in comparisons:
                if output != 'Is ':
                    output += 'and '
                match cmp.parameter:
                    case StrParam(name):
                        output += f'[{name}: str] '
                    case IntParam(name):
                        output += f'[{name}: int] '
                    case _:
                        raise Exception('AAAAA')
                match cmp.equality:
                    case EqualTo():
                        output += 'equal to '
                    case GreaterThan():
                        output += 'greater than '
                    case LessThan():
                        output += 'less than '
                    case GreaterThanOrEqualTo():
                        output += 'greater than or equal to '
                    case LessThanOrEqualTo():
                        output += 'less than or equal to '
                    case _:
                        raise Exception("AA")
                match cmp.value:
                    case StrValue(val):
                        output += f'"{val}" '
                    case IntValue(val):
                        output += f'{val} '
                    case _:
                        raise Exception("AAA")
            print(f'Search Query: {output}')
        case Access(param, val):
            output = ''
            match param:
                    case StrParam(name):
                        output += f'[{name}: str] '
                    case IntParam(name):
                        output += f'[{name}: int] '
            output += 'of '
            match val:
                    case StrValue(val):
                        output += f'"{val}" '
                    case IntValue(val):
                        output += f'{val} '
            print(f'Access Query: {output}')     

        case None:
            print("Error: Bad Query")
        case _:
            print("Got an unknown query!")


def test():
    # Parsing parameter
    param_tests = {
        'Hello': None,
        '""hi': None,
        '129j': None,
        'stars': IntParam('stars'),
        'id': IntParam('id'),
        'description': StrParam('description'),
        'topics': StrParam('topics')
    }
    for val, result in param_tests.items():
        print(f"Testing: {val} == {result}")
        assert(parse_parameter(val) == result)

    # Parsing values
    value_tests = {
        '5': IntValue(5),
        '"I-love-programming"': StrValue('I-love-programming'),
        '2500': IntValue(2500),
    }
    for val, result in value_tests.items():
        print(f"Testing: {val} == {result}")
        assert(parse_value(val) == result)

    # Parse Access queries
    access_tests = {
        'stars "repo"': Access(IntParam('stars'), StrValue('repo')),
        'id "oop examples"': Access(IntParam('id'), StrValue('oop examples')),
        'id "oop examples" 1': None,
        'id "oop\'examples"' : None,
        'id "oop examples': None,
        # This maybe should be None
        'stars ""': Access(IntParam('stars'), StrValue('')),
    }
    for val, result in access_tests.items():
        print(f"Testing: {val} == {result}")
        assert(parse(val) == result)

    
    # Parse Search queries
    search_tests = {
        'stars == 5': Search([Comparison(EqualTo(), IntParam('stars'), IntValue(5))]),
        'stars > 5 and stars <= 100': Search([
            Comparison(GreaterThan(), IntParam('stars'), IntValue(5)),
            Comparison(LessThanOrEqualTo(), IntParam('stars'), IntValue(100)),
        ]),
        'topics == "level"': Search([Comparison(EqualTo(), StrParam('topics'), StrValue('level'))]),
        'type == "User"': Search([Comparison(EqualTo(), StrParam('type'), StrValue('User'))]),
    }
    for val, result in search_tests.items():
        print(f"Testing: {val} == {result}")
        assert(parse(val) == result)

    print("tests passed")


# For testing
# if __name__ == '__main__':
#     test()