This is an event scheduling API that can be used as a backend for event organizing or get toghter application.


## Installation

Download repository


Make sure you have pip installed.
```
$ sudo apt-get install python3-pip
```
Installing virtualenvwrapper 
```
$ sudo pip3 install virtualenvwrapper
```
Open bashrc by –
```
$ sudo gedit ~/.bashrc
```
After opening it, add the following  lines to it :
```
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
Save the bashrc file.
```

In project folder:

### Create virtualenv

```
mkvirtualenv --python=`which python3` nameofEnviroment
```

To work on an existing virtual environment,
```
$ workon nameofEnviroment
```
### Install requirements

```
pip install -r requirements.txt
```

### Run server

```
./manage.py runserver
or
python manage.py runserver
```

***

## Usage:
In order to use the API we need to create a user and API token to authenticate.


### Create super user

```
./manage.py createsuperuser
```

If you have your server tunning you should be able to accsess the admin panel from  url: "localhost:8000/admin"

### Create token

User argument would in this case be the user id of the super user you created in the step before (usually is 1)

```
./manage.py create token --user_id=<user_id>
```


For users to authenticate, the token key should be included in the Authorization HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```
To use the API you can either user the browsable API via local "localhost:8000/api/v1/" where you need to authenticate yourself with the created token
in the Header via for example chrome plugin [simple-modify-headers](https://chrome.google.com/webstore/detail/simple-modify-headers/gjgiipmpldkpbdfjkgofildhapegmmic) or you can use any other API software for example: [Postman](https://www.postman.com/)




## List all events
Endpoint: `/api/v1/event/list`

### Request
Method: `GET`



## Create an event
Endpoint: `/api/v1/event`

### Request
Method: `POST`

Body:

```
{
  "name": "This is my event",
  "dates": [
    "2023-01-01",
    "2023-05-06",
    "2023-05-14"
  ]
}
```
## Update an event
Endpoint: `/api/v1/event/{id}/`

This endpoint updates the name or add dates to an event

### Request
Method: `PUT`

Body:

```
{
  "name": "This is updated event",
  "dates": [
    "2023-04-01",
    "2023-04-06",
    "2023-04-14"
  ]
}
```

## Delete an event
Endpoint: `/api/v1/event/{id}/`

### Request
Method: `DELETE`


## Show an event
Endpoint: `/api/v1/event/{id}/`

### Request
Method: `GET`

Parameters: `id`, `long`



## Add votes to an event
Endpoint: `/api/v1/event/{id}/vote`

### Request
Method: `POST`

Parameters: `id`, `long`

Body:

```
{
  "name": "Peter",
  "votes": [
    "2023-01-01",
    "2023-05-14"
  ]
}
```


## Show the results of an event
Endpoint: `/api/v1/event/{id}/results`
Responds with dates that are **suitable for all participants**.

### Request
Method: `GET`

Parameters: `id`, `long`

### Example Response

```
{
  "id": 1,
  "name": "This is my event",
  "suitabledates": [
    {
      "date": "2014-01-01",
      "people": [
        "Peter",
        "Ben",
        "Hagrid",
      ]
    }
  ]
}
```
