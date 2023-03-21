This is an event scheduling API that can be used as a backend for event organizing or get toghter application.


## Installation

Download repository


In project folder:

### Create virtualenv

```
mkvirtualenv --python=`which python3` nameofEnviroment
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
