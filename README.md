# Sample backend project

This project serves a backend to manage users and file uploads. It's built using Django (ver 4.1), and GraphQL with Graphene for the API. Its purpose is to serve as an example of the backend we want to build, and the API is as close as the one we have in functionality.

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

### Uploading files through the API

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


### Using the paginations, search and filter params in read queries

Balam's read  _all_ queries have some common params which are used for filtering and changing the pagination of the items returned.

   * Pagination

   There are two special params for handling the pagination. One is **page_size** and the other is **page**. As the names suggest, **page_size** change the number of items retreived in each page, the default is 10, but you can increment or decrease that number to git your needs. On the other hand, **page** sets the number of the page we want to retrieve, the default value is 1. So, if this params are not in the query, the default is to return the first 10 items in the first page.

   * Search

   The search param performs a simple search in predefined fields that are normally used to identify an item in the queryset. For example the unique fields like username in the User model or the name field in the File model. Here's an example of how to use it:

      {
         allFiles(search: "wav") {
            pageInfo {
                  totalCount
            }
            items {
               id
               url
               name
               fileMetadata
               createdAt
            }
         }
      }

   this will return all files that contains wav in their names or urls. Note that the search is case insensitive.

   * Filter

   The filter param is a special param to make a more complex search. The filter param can take 4 arguments to apply a filter, which are:

   **field**: this is the field in the model where to apply the filter.

   **operator**: specifies the filter operator, and can be any of eq, neq, gt, gte, lt, lte, contains, notContains, OR, AND.

   **valueType** (optional): sets the conversion of the value to the specified type. If not set, takes the value as is was written.

   **value**: the value to filter with.

   An example of how to use it is the next one:

      
      allGroups(filters: {
            field: name,
            value: "annotators",
            operator: eq
      }) {
         items {
            id
            name
         }
      }
      

   Here we are filtering the results that are an exact match with the value `annotators` in the field `name` of the model Group.

   We can also make a more complex filter using AND/OR operators like so:

      
      allUsers(filters: {
         operator: AND,
         filters: [
            {
               field: can_login,
               valueType: Boolean,
               value: "true",
               operator: eq
            },
            {
               field: email,
               value: "biometrio.earth",
               operator: contains
            },
            
         ]
      }) {
         items {
            username
            firstName
            email
         }
      }
   
   Here we filter all users that the can_login field is set to True and its email contains "biometrio.earth".

   If we want to filter for items that its value is set to `null` in a field, we must omit the `valueType` argument:

      {
         allFiles(filters: {
            field: file_metadata,
            operator: eq,
            value: null
         }) {
            items {
                  id
                  fileMetadata
            }
         }
      }

   Finally, if the model has a JSON type field, the value of the filter needs to have a certain  syntax in order to work properly. The next example shows how to do it:

      {
         allFiles(filters: {
            field: file_metadata,
            operator: gt,
            value: "Duration:60"
         }) {
            items {
                  id
                  name
                  fileMetadata
            }
         }
      }

   Here the field `file_metadata` is of type `JSONField`, and in its properties it has a key called `Duration`, so we are filtering all files that have the key `Duration` in their json and that have a value in that property grater than 60.

      
