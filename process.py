# Samuel Clear, Michael Piscione, Kyrill Serdyuk, Max Pursche
# CS 3050: Software Engineering
# Professor Hibbeler
# 09/24/2023

# process.py: Querying functions and Firebase Initializer Function
# This file contains the file to set up the back-end of the repository. When the main function is utilized, it sets up 
# all of the current data from the database file into Google Firebase. Then we have the comparison, access query, and 
# search query functions for accessing the cloud database from the query.py front_end interface. 

# Readying Firestore for use on our document, along with additional imports
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import db
import json
import os
import string

# This import statement was retrieved from the following GitHub repository:
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/faa2232086c3bb70866f3f87e782e9f95fa9e467/firestore/cloud-client/snippets.py#L241-L249
from google.cloud.firestore_v1.base_query import FieldFilter

# Initializing the Google Firebase client, connected to the original site
cred_object = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred_object)

# Originally the reference is set to be a database within portion of the Cloud Firebase.
db = firestore.client()

# Constants for the Database
DATABASE_NAME = "github_repos_oops"
DOCUMENT_LIST_LENGTH = len(db.collection(DATABASE_NAME).get())
AGGREGATE_FUNCTIONS = ("<", ">", "<=", ">=", "==", "!=")
FIELD_NAMES = ("repo_name", "created", "description", "forks", "id", "language", "stars", "subscribers", "topics", "type")
PARENT_REPOSITORIES = ("low-level", "devices", "prog_langs", "oop", "software", "miscellaneous", "event")
SUBCOLLECTION_FIELD_NAMES = ("parent_repository", "name")

# This import statement was retrieved from the following GitHub repository:
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/faa2232086c3bb70866f3f87e782e9f95fa9e467/firestore/cloud-client/snippets.py#L241-L249
from google.cloud.firestore_v1.base_query import FieldFilter

# Initializing a reference to interact with the database on the cloud.
database_document_names = []

### IMPORTANT DATABASE NAMES CREATION LOOP
document_list = db.collection(DATABASE_NAME).get()
iterator = 0
while iterator < DOCUMENT_LIST_LENGTH:

# Find the name of the first document in the database
    document_fields = document_list[iterator].to_dict()

    # Record the name in the document list
    database_document_names.append(document_fields['repo_name'])

    iterator += 1

    
# initialize_database Function
# Creates the files in Google Firebase to be accessed through the query functions below
# Parameters:
#   json_db: String variable for name of the JSON file for the repository
#   db_name: Given database name
# Return:
#   None, database is initialized into Google Firebase
def initialize_database(json_db: str, db_name: str):
    # Reference individual documents in this by referencing each instance within the 
    # collection, like indexing into a list (write_ref[0], write_ref.last(), etc.)

    # Then, set all of the data in the database to be this given data from 
    # the .JSON file from earlier.
    json_file_contents = json.load(open(json_db, "r"))
    for document in json_file_contents:
        db.collection(db_name).document(document['repo_name']).set(document)

    # Finally, all of the data should be initialized! (It was initialized!)
    print("All data has been initialized")


# Comparison Function
# Given a field, value, and conditional variable, checks if the relationship is true or false
# Parameters:
#   field: Given field variable value
#   value: Checked value against the field
#   cond_var: Given conditional variable to compare both the field and the value
# Return:
#   Boolean value indicating whether the variable and the value are comparable.
def compare(field: str, value: any, cond_var: str) -> bool:
    match cond_var:
        case "==":
            if field == value:
                return True
            else:
                return False
        case "<=":
            if field <= value:
                return True
            else:
                return False
        case ">=":
            if field >= value:
                return True
            else:
                return False
        case "<":
            if field < value:
                return True
            else:
                return False
        case ">":
            if field > value:
                return True
            else:
                return False
            

# Access Query Function
# Finds the information of the given field for the given repository by name, returns the field's value
# Parameters: 
#   repo_name: String variable for the given name of the repository
#   field_name: String variable for the field to search for
# Return:
#   Value/s in string list format contained in the given field for the given repository
def access_query (repo_name: str, field_name: str):
    # Input validation: if field not in field_names, return None to signify that an invalid query was recieved
    if field_name not in FIELD_NAMES:
        return None
    
    # Find the document with the given repository name
    document_found = db.collection(DATABASE_NAME).document(repo_name).get()
    
    # FOR MAX: This process in finds all of the fields and their values, and compiles them into a 
    # dictionary. This can be used alongside the .JSON file reader below to find every repository's 
    # field variables to perform each search (Need a for-loop running through a list of all the 
    # repo_names). This should work for just this function, but it can be expanded to the other 
    # functions with a bit of extra implementation.

    # Find value at given field
    field_document = document_found.to_dict()

    # If one of the subcollection's fields are searched for in access query, it is considered an invalid 
    # query for searching more than one identifiable value.
    if field_name in SUBCOLLECTION_FIELD_NAMES:
        return None
    
    # If an optional field is not present, return an error message
    if field_name not in field_document.keys():
        return "Optional Field: No Value Available"
    elif field_document[field_name] == None:
        return "Optional Field: No Value Available"
    else:
        # Finally, return the given field found all of the field of the given document.
        # return str(fields_of_document[field_name])
        return field_document[field_name]


# Search Query Function
# Finds the names of the repositories that satisfy the given field condition
# Parameters: 
#   field: Given String variable for the field to search for
#   value: Given flexible-typed variable for the given value searched for from a variable
#   cond_var: Given string variable representing the conditional relationship between the value and the field
# Return:
#   Names of the repositories in string list format that satisfy the given query
def search_query (field: str, value: str | int, cond_var: str):
    # Input validation: if field not in field_names, return None to signify that an invalid query was recieved
    if field not in FIELD_NAMES and field not in SUBCOLLECTION_FIELD_NAMES:
        return None
    
    # Create a list to contain each of the repositories that satisfy the given conditon
    return_list = []
    
    # If a field in the subcollections is searched for, then each subcollection of each document must be checked. Currently, this is a bit tedious...
    if field in SUBCOLLECTION_FIELD_NAMES:
        for doc_name in database_document_names:

            # Find the document info, then find the dictionaries in the document
            document_info = db.collection(DATABASE_NAME).document(doc_name).get().to_dict()
            if "topics" in document_info.keys():
                topics = document_info['topics']

                # Going by topic, find the field value of the given field. If any of the topics in the field share a 
                # conditional relationship with the given topic, then add the document to the results list.
                for topic in topics:
                    if compare(topic[field], value, cond_var) and doc_name not in return_list:
                        return_list.append(doc_name)

    # If not, then search for the fields with a Google Firebase query function
    else:
        # Input validation: if field not in field_names, return None to signify that an invalid query was recieved
        if field not in FIELD_NAMES:
            return None
        
        # FieldFilter was not previously accessible without an import statement from the following GitHub Document:
        # https://github.com/GoogleCloudPlatform/python-docs-samples/blob/faa2232086c3bb70866f3f87e782e9f95fa9e467/firestore/cloud-client/snippets.py#L241-L249
        # Query the Google Firebase database for the given filters
        query_results_list = db.collection(DATABASE_NAME).where(filter=FieldFilter(field, cond_var, value)).stream()
    

        # Loop through each of the documents found to satisfy the query
        for query_result in query_results_list:

            # Find the repository name of the given query, enter into the return list
            doc = query_result.to_dict()
            doc_name = doc['repo_name']
            return_list.append(doc_name)

    # Finally, return all of the repositories that had the given value!
    return return_list

# Main for Initializing Database
# if __name__ == __main__:
#     initialize_database("oop_repository_descriptions.json", "github_repos_oops")