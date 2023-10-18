# Samuel Clear, Michael Piscione, Kyrill Serdyuk, Max Pursche
# 09/24/2023

# Query.py is the file the houses exec_query. exec_query takes information from the parser (user input) and uses that information
# to query the firestore database. query.py also contains general helper functions used in exec_query.

from query_classes import *
from process import *

# Define constants
SINGLE_COMPARISON_LENGTH = 1

def format_output_docs(doc_names: list) -> str:
    """ format_output_docs simply takes a list of firbase document names and returns a clear and
    formatted list of those names. """

    # Create output string
    out_string = "-" * 10 + "DOCUMENT NAMES" + "-" * 10 + "\n"

    # Iterate through all the objects in the list
    for i in range(len(doc_names)):
        # Grab the document name at the current position
        doc_name = doc_names[i]

        # Check if it's a string (no reason for it not to be)
        if not isinstance(doc_name, str):
            return "NOPE"  # Deliver some kind of message if it isn't a string
        else:
            # Add it to a formatted output string
            out_string += "DOC " + str(i + 1) + ": " + doc_name + "\n"
    
    # Return the formatted output
    return out_string

def convert_equality(eq: Equality) -> str:
    """ convert_equality takes an instance of the Equality class as a parameter
     and returns the string representation of that instance. """

    # Return the string representation of the Equality instance
    # Ex: EqualTo() instance represents ==
    match eq:
        case EqualTo():
            return "=="
        case LessThan():
            return "<"
        case GreaterThan():
            return ">"
        case LessThanOrEqualTo():
            return "<="
        case GreaterThanOrEqualTo():
            return ">="
        case _:  # Return an error message if Equality instance unrecognized
            return "comparison not recognized"


def exec_query(query: Query) -> str:
    """ exec_query takes a query from the parser and returns a formatted string of information
    from firebase using the information in the query (comparison, value, parameter, etc). """
    
    # Otherwise match the query type
    match query:
        case Access(param, val):
            
            # Take the parameter from Acess object
            parameter = param.value

            # Take the repo_name from Access object
            repo_name = val.value

            # Check if valid repository name
            if repo_name not in database_document_names:
                return "Not a valid repository name"

            # This will either be string, int, or dictionary
            access_val = access_query(repo_name, parameter)

            # Format output dependent on input type
            match access_val:
                case str():  # Format return string based on str type
                    out_string = "-" * 10 + parameter + "-" * 10 + "\n"
                    out_string += access_val
                    return out_string
                case int():  # Format return string based on int type
                    out_string = "-" * 10 + parameter + "-" * 10 + "\n"
                    out_string += str(access_val)
                    return out_string
                case list():  # Format return string based on dict type
                    out_string = "-" * 10 + parameter + "-" * 10 + "\n"
                    for topic in access_val:
                        out_string += "Parent Repository: " + topic['parent_repository'] + " | Topic Name: " + topic['name'] + "\n"
                    return out_string
                case None:  # Can't do an access query on sub-collection fields 
                    return "Error: Terrible Query"
                case _:
                    return "ERROR in access_query return datatype"
                
        case Search(items):
            # Create a list of valid string comparison operators
            string_operators = ["=="]

            # Not a compound query
            if len(items) == SINGLE_COMPARISON_LENGTH:  
                # Grab the items from the list
                equality = convert_equality(items[0].equality)
                parameter = items[0].parameter.value
                value = items[0].value.value

                # Make sure appropriate comparisons are used
                if type(value) == str and equality not in string_operators:
                    return "Error: Terrible Query"

                # Call search_query using the parameters from the list
                search_vals = search_query(parameter, value, equality)
                
                # Return the formatted output string
                return format_output_docs(search_vals)
            
            # Compound query
            else:
                # Make a list to store similar elements
                intersections = []

                # Initializer a counter
                count = 0

                # Iterate through all Comparisons in items
                for cmp in items:
                    # Iterate count
                    count += 1

                    # Grab the fields of each instance of Comparison
                    equality= convert_equality(cmp.equality)
                    parameter = cmp.parameter.value
                    value = cmp.value.value

                    # Run a search query using these fields
                    search_vals = search_query(parameter, value, equality)

                    if count > 1:
                        # Intersect the known intersections list with the new set of search values
                        intersections = list(set(intersections) & set(search_vals))
                    else:  # Intersections should first be set to search_vals for the first search query (otherwise we'd be 
                           # intersecting with an empty set every time)
                        intersections = search_vals


                # Return the formatted output string
                return format_output_docs(intersections)
