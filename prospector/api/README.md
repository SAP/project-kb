# API for Prospector Backend

## Authentication

`GET /users/`

 * Return: all users data

`GET /users/<USER_ID>`

 * Return: data for user <USER_ID>

`GET /users/me`

 * Return: data for the currently authenticated user

`POST /token`

 * Input: user/pass
 * Return: auth. token

## Searching for fix-commits

`POST /search`

 * Input: advisory record
 * Output: a reference to the job, to retrieve the results later

`GET /search/<JOB_ID>`

 * Input: the job id
 * Output: status of the job and results (if completed)

## Model management

....

## Data management

`POST /preprocessed-data`


`GET /data/commits`
