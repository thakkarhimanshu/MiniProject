# MiniProject
This file contains the description of work involved in doing the MiniProject for Cloud Computing.

The project supports an application that is developed in flask and python. The data extracted from the application API is stored in a cassandra database. Finally the project demonstrates cassandra ring scaling.

The project implements an API that gets the weather for given location co-ordinates. The response is in the form of JSON. The information of interest are Temperature, Dew, Humidity and Wind. 'Time since Epoch' in seconds is used as a unique PRIMAY KEY in the database

The first step is to pull the latest Cassandra Docker image
    
    docker pull cassandra:latest

The second step is to run a Cassandra instance within docker
    
    docker run --name cassandra-test -d cassandra:latest
  
In the third step a 3 node cluster named cassandra is creared. If an error is encountered prompting that google container api is not enabled the same can be achieved by executing following command

    glcoud services enable container.googleapis.com
    
(Note: It takes several minutes for clusters to create)

To run Kubernetes service, three files are needed. The first is a Headless service that allow peer discovery i.e. cassandra pods will be able to find each other and form a ring. To run the headless service, execute the following command

    kubectl create -f cassandra-peer-service.yml
 
 The next step is to run service itself. It is executed with the following command
 
    kubectl create -f cassandra-service.yml
    
 Finally the replication controller is run ( the replication controller allows the scale up and scale down of the containers as needed)
 
    kubectl create -f cassandra-replication-controller.yml
 
 
