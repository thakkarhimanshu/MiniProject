# MiniProject - API to extract weather information
This README file contains the description of work involved in doing the MiniProject for Cloud Computing.
This was done simetimeback

The project supports an application that is developed in flask and python and is deployed on a docker. The data extracted from the application API is stored in a cassandra database. Three clusters of database is created and finally the project demonstrates cassandra ring scaling.

The project implements an API that gets the weather for given location co-ordinates. The response from the source is in the form of JSON but displayed in human readble HTML format. The information of interest are Temperature, Dew, Humidity and Wind. 'Time since Epoch' in seconds is used as a unique PRIMAY KEY for the cassandra database. The project assumes that a table already exists in the database ( The table currenttemp is created in KEYSPACE weatherdata using CQL)

The main application file is weather.py. It begins by importing required libraries. The time library provides the functions related to time. Cluster is imported from cassandra.cluster. This is needed to communicate with a cassandra database. The project also imports flask, request, render_template and jsonify. The project also needs an API key. The key being referenced from instance/config.py. Note that the key is valid until 30-03-2019. ( The project uses a temporary key provided by www.breezometer.com)

A connection to database is then made by executing

    cluster = Cluster(['cassandra'])
    
further a session is created by
    
    session = cluster.connect()

A variable template is created to prepare the session for inserting the data by

    insert_data = session.prepare("INSERT INTO weatherdata.currenttemp (time, temperature, dew, humidity, wind) VALUES(?,?,?,?,?)")

As detailed above, the KEYSPACE of cassandra is weatherdata while currenttemp is name of the table. This initialisation takes into consideration the fact that the table has been created (by CQLSH) in the cassandra keyspace. 

The final initialisation involves creating a weather_url that will be queried to achive data of interest

    weather_url_template = "https://api.breezometer.com/weather/v1/current-conditions?lat={lat}&lon={lng}&key={API_KEY}"
The GET method is mapped to the home page. As of now an location coordinates are of London. With a successul response the information is extracted by the following code
    
    json_data = requests.get(weather_url).json()
    #Extract the required values
    Temperature = json_data['data']['temperature']['value']
    Dew = json_data['data']['dew_point']['value']
    Humidity = json_data['data']['relative_humidity']
    Wind = json_data['data']['wind']['speed']['value'] 
 
The data is written into the cassandra database. Note that time.time() returns a float value in seconds; this is time in seconds since epoch i.e. 1st Jan 1970. 

    session.execute(insert_data,[time.time(),Temperature,Dew,Humidity,Wind])
 
The GET method returns with an object containing an HTML equivalent of JSON data returned by API.

With the application file coded. The Dockerfile is created to deploy the app on a docker.


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
 
 As the next step, check that the single container is running correctly:
 
    kubectl get pods -l name=cassandra
    
When the container is found to be working correctly then scale up the nodes via replication controller by using the following command

    kubectl scale rc cassandra --replicas=3

Nodetool status is an important tool to check whether a ring is formed between all of the Cassandra instances. This is done via followinf command
    
        kubectl exec -it cassandra-24bgm -- nodetool status

In the above command, cassandra-24bgm is the name of the one of the container created. This name varies between setup. Once a proper ring is created, roughly every node own 65% of load.

With successful creation of the ring, the next step involves creating a KEYSPACE on container. Connect to a container by executing following command

    kubectl exec -it cassandra-24bgm cqlsh

The above command launches CQL shell that facilitates creation of KEYSPACE. Use the following command to create KEYSPACE

    CREATE KEYSPACE weatherdata WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 2};
    
And create the table by using the following command

    CREATE TABLE weatherdata.currenttemp (Time float, Temperature float, Dew float, Humidity float, Wind float, PRIMARY KEY(Time));

Now build the image and push it to google repository:

    docker build -t gcr.io/${PROJECT_ID}/weather-app:v1 .
    docker push gcr.io/${PROJECT_ID}/weather-app:v1

Run the above as a service, exposing the deployment to get the external IP

    kubectl run pokemon-app --image=gcr.io/${PROJECT_ID}/weather-app:v1--port 8080
    kubectl expose deployment weather-app --type=LoadBalancer --port 80 --target-port 8080

Use the following command to check the IP address
    
    kubectl get services
  
Check the results on the IP address thus obtained  











 
