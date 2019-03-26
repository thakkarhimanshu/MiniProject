# MiniProject
This file contains the description of work involved in doing the MiniProject for Cloud Computing.

The project supports an application that is developed in flask and python. The data extracted from the application API is stored in a cassandra database. Finally the project demonstrates cassandra ring scaling.

The project implements an API that gets the weather for given location co-ordinates. The response is in the form of JSON. The information of interest are Temperature, Dew, Humidity and Wind. 'Time since Epoch' in seconds is used as a unique PRIMAY KEY in the database

The first step is to pull the latest Cassandra Docker image
    
    docker pull cassandra:latest

