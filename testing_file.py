# Samuel Clear, Max Pursche, Michael Piscione, Kyrill Serdyuk
# CS 3050: Software Engineering
# Professor Hibbeler
# 09/24/2023

# testing_file.py: Testing Suite for access_query(), search_query(), and compound_search_query()
# This file contains a test suite for each of the back-end query functions.

# Readying Firestore for use on our document, along with additional imports
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import db
import json
import os
import string

from process import access_query
from process import search_query
from process import compound_search_query

# This import statement was retrieved from the following GitHub repository:
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/faa2232086c3bb70866f3f87e782e9f95fa9e467/firestore/cloud-client/snippets.py#L241-L249
from google.cloud.firestore_v1.base_query import FieldFilter

# FOR ALL: Determining how receiving and inputting data into Google Firestore: https://www.youtube.com/watch?v=WBWOuvKTjvM
db = firestore.client()

# Constants for the Database
DATABASE_NAME = "github_repos_oops"
DOCUMENT_LIST_LENGTH = len(db.collection(DATABASE_NAME).get())
AGGREGATE_FUNCTIONS = ("<", ">", "<=", ">=", "==", "!=")
FIELD_NAMES = ("repo_name", "created", "description", "forks", "id", "language", "stars", "subscribers", "topics")
PARENT_REPOSITORIES = ("low-level", "devices", "prog_langs", "oop", "software", "miscellaneous", "event")
SUBCOLLECTION_FIELD_NAMES = ("parent_repository", "name")

# Global list containing database names
database_document_names = []

# Testing Suite for access_query, search_query, and compound_search_query
if __name__ == "__main__":

    ### IMPORTANT DATABASE NAMES CREATION LOOP
    document_list = db.collection(DATABASE_NAME).get()
    iterator = 0
    while iterator < DOCUMENT_LIST_LENGTH:

    # Find the name of the first document in the database
        document_fields = document_list[iterator].to_dict()

        # Record the name in the document list
        database_document_names.append(document_fields['repo_name'])

        iterator += 1
    
    # First test case for Access Query, generic
    try:
        assert access_query("DevOops", "id") == 89589066
        print("PASSED First Access Query Test Case")
    except:
        print("FAILED First Access Query Test Case")

    # Second test case for Access Query, subcollections
    try:
        assert access_query("ParkingLot", "topics") == [{"parent_repository": "miscellaneous", "name": "parking-lot"}, {"parent_repository": "prog_langs","name": "nodejs"},{"parent_repository": "prog_langs","name": "javascript"}]
        print("PASSED Second Access Query Test Case")
    except:
        print("FAILED Second Access Query Test Case")

    # Third test case for Access Query, different field
    try:
        assert access_query("gitjk", "subscribers") == 12
        print("PASSED Third Access Query Test Case")
    except:
        print("FAILED Third Access Query Test Case")
    
    # First and Second Test Cases for search_query(), generic
    try:
        assert search_query("id", 89589066, "==") == ["DevOops"]
        print("PASSED First Search Query Test Case")
    except:
        print("FAILED First Search Query Test Case")
    try:
        assert search_query("repo_name", "oops", "==") == ["oops"]
        print("PASSED Second Search Query Test Case")
    except:
        print("FAILED Second Search Query Test Case")

    # Third Test Case, checking for specific parent repository names
    try:
        assert search_query("parent_repository", "miscellaneous", "==") == ["8085-Emulator", "DataStructures-Algorithms", "Learn-Java-with-Implementation-Professional-Level-1", "Oopsilon", "ParkingLot", "cljs-oops", "low-level-design-even-odd-java-threading", "oops-android-kt", "oops.js", "shivneri"]
        print("PASSED Third Search Query Test Case")
    except:
        print("FAILED Third Search Query Test Case")

    # First Test Case for compound_search_query(), generic
    try:
        assert compound_search_query("id", 20174993, "==", "stars", 828, "==") == ["gitjk"]
        print("PASSED First Compound Search Query Test Case")
    except:
        print("FAILED First Compound Search Query Test Case")

    # Second Test Case for compound_search_query(), subcollection objects fields
    try:
        assert compound_search_query('parent_repository', "oop", "==", "name", "oops", "==") == ["2-Player-Ninja-Fight-Game-in-Java", "8085-Emulator", "Data-Structure-and-Algorithms-with-JavaScript", "SnakeGame", "Technical-Subjects", "Zuber", "gitjk"]
        print("PASSED Second Compound Search Query Test Case")
    except:
        print("FAILED Second Compound Search Query Test Case")