# Sample backend project

This project serves a backend to manage users and file uploads. It's built using Django (ver 4.1), and GraphQL with Graphene for the API. Its pupose is to serve as an example of the backend we want to build, and the API is as close as the one we have in functionality.

## Requirements

To run this project, you'll need to have installed:

 - docker (^20.10.18)
 - docker-compose (^1.29.2)
 - yarn (^1.22)
    
## First steps

Before anything, you'll need to create an `.env` file. You can use `.env.example` to create it. This are the contents of the file:

      #Django
      DEBUG=1
      SECRET_KEY="mysecretkey" # define a different secret key for your project
      DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1] * # change to your desired allowed hosts

      # database access credentials
      # change as needed
      TEST_DATABASE_NAME=example_test_db
      TEST_DATABASE_USER=postgres
      TEST_DATABASE_PASSWORD=postgres
      TEST_DATABASE_HOST=test_db
      TEST_DATABASE_PORT=5432
      DEV_EXPOSE_DB_PORT=5433 # this port is used to expose the database to the host, maybe try a different one than 5432

      # docker app port
      # with this one we expose the app, you can change it to any other port you want
      TEST_APP_PORT=7070

      # default superuser
      # needed!
      # with this you'll define the default superuser in the platform
      TEST_SUPERUSER="admin"
      TEST_SUPERUSER_PASS="somepassword"
    
once created, you can run the containers to start using this project.

## Useful commands

There are some useful commands to easily handle the containers in this project. We use yarn to manage this commands, that's why it's needed as a requirement. The commands are the following: 

      $ yarn start # starts all containers in the background, can use it also to build them for the first time.

      $ yarn stop # stops the containers

      $ yarn restart <service name> # restarts the service specified

      $ yarn logs <service name> # shows logs for the desired service

But if you don't want to use yarn, that's ok! You can always use the docker-compose `up`, `down`, `restart` commands.

## Run the project

To build and start the containers you can use `yarn start` command. Once build and up, you can access to the default endpoints in this routes:

 - graphql: 
    * _graphql endpoint, it also serves the graphiql interface_
    * http://localhost:<TEST_APP_PORT>/graphql/
 - admin:
    * _default django admin site_
    * http://localhost:<TEST_APP_PORT>/admin/
 - postgres: 
    * _is exposed on the port you specified with DEV_EXPOSE_DB_PORT in you `.env` file_
   
## How to use the API

All requests to the API must be authenticated, to authenticate requests we use a JWT token. To obtain this token you can make a request to the graphql endpoint using the mutation:

      mutation {
         tokenAuth(
            username: "<some_user>",
            password: "<some_password>"
         ) {
            token
         }
      }

this will return the following response:

      {
         "data": {
            "tokenAuth": {
                  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjc4ODE1NjA0LCJvcmlnSWF0IjoxNjc4ODE1MzA0fQ.EjBY_CBjvOG570vt1dBUyjFOqd6VGENu43xbZ-AeTMc"
            }
         }
      }

use that token in your requests, setting the `Authentication` header like so:

      "Authentication": "JWT <token>"

just remember that the token has an expiry time.

### Uploading file through the API

To upload files, make a multipart/form request to the graphql endpoint, and create 3 parameters:

   - operations
   - map
   - 0

**operations** (text) is the query mutation, **map** contains a mapping to the file variable, ans **0** is the file to be uploaded.

for example, a mutation to upload a file would look like:

      operations: {
                     "query" : "mutation($name: String!,$mimeType: String!,$file: Upload!) { createFile(name: $name,mimeType: $mimeType,file: $file) {id}}",
                     "variables" : {
                        "name": "test.png",
                        "mimeType": "image/png",
                        "file": null 
                     }
                  }

      map: {"0": ["variables.file"]}

      0: file_to_upload.png

you can check [this link](https://davidkg.medium.com/uploading-images-using-django-graphene-django-and-graphene-file-upload-9f2e9bfc949d) for more info
