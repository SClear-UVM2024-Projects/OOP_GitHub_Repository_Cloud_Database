# Samuel Clear, Michael Piscione, Kyrill Serdyuk, Max Pursche
# 09/24/2023

# interface.py is the main function for the program. The program should be run out of interface.py. It initializes the database and starts
# a loop to collect user input.

from query import exec_query
from query_parser import *
from process import *

def print_help():
    print(
    '''
    This is an interface for querying a database of github repos.
    It supports two different types of queries:
     - Access Queries:
        usage: key "reponame"
        ex: stars "my favorite repo"
     - Search Queries:
        usage: key equality value [and ...]
        ex: stars >= 50 and language == "C++"
    
    Access queries can only be preformed by using the repositories name.
    The repository name, and all string values, need to be surronded by double quotes ("").
    String values only support comparison (==).
    Search queries can optionaly take additional search values and intersect the result with and.
    The type of the key and the value must match, i.e. when searching by stars a valid query
    will have a comparison with an integer value.
    
    Parameters:
     - String:
        - created
        - language
        - name
        - repo_name
        - topics
        - type
     - Int:
        - forks
        - id
        - stars
        - subscribers
     - Optional String:
        - description
        - language
        - parent_repository
    
    Bad Query:
        - Self Explanatory :^)
    '''
    )


if __name__ == '__main__':
    ### IMPORTANT DATABASE NAMES CREATION LOOP
    document_list = db.collection(DATABASE_NAME).get()
    iterator = 0
    while iterator < DOCUMENT_LIST_LENGTH:

    # Find the name of the first document in the database
        document_fields = document_list[iterator].to_dict()

        # Record the name in the document list
        database_document_names.append(document_fields['repo_name'])

        # Increment iterator
        iterator += 1

    # Get user input
    exit = False
    while not exit:  # While they don't want to exit
        try:
            user_input = input("> ")  # Collect user input after '>
            if user_input == "exit" or user_input == "quit":  # They want to exit
                exit = True
            elif user_input == "help":
                # Print the help query
                print_help()
            else:
                query = parse(user_input)  # Parse the command
                if query == None:
                    print("Error: Bad Query")
                else:
                    print(exec_query(query))  # Print the data found in firestore
        # User broke out of input
        except EOFError:
            exit = True
