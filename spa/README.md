# README Web App

The main reason to create this web application was to create an use case to demonstrate the advantages of a graph database. After we decided to use train data to create a graph database we've decided to create a web app, which enables to search for the fastest route (with some limitations).

## Start and requirements

This web app was created by using a JavaScript framework (Vue.js). Since this is just a use case application, there are some regulations regarding the JavaScript versions. There is no guarantee to run this app if you are using different versions.
 
Versions:

* NPM: 8.11.0
* Node.js: 17.7.1

To install the required modules, you need to run following command from command line:

`npm install`

This command will install all modules and dependencies from `package.json`. This may take a little time.

After all modules are installed, you can run the following command to start the web application. This command will start a development server.

`npm run serve`

The started application can be accessed from [localhost](http://localhost).

Furthermore, the application requires an installation of `Neo4j Desktop` and a running database.

* Database name: `deutschebahn`
* Database protocol: `bolt`
* Database host: `localhost`
* Database port: `7687`
* Database username: `neo4j`
* Database password: `admin`

