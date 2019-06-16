curls for testing:
USER API:
curl -X POST -H "Content-Type: application/json" -d "{\"firstName\": \"Brian\", \"lastName\": \"Raison\"}" http://127.0.0.1:5000/users
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:5000/users/2
curl -X DELETE -H "Content-Type: application/json" http://127.0.0.1:5000/users/2
curl -X PUT -H "Content-Type: application/json" -d "{\"firstName\": \"Becky\", \"lastName\": \"Smith\"}" http://127.0.0.1:5000/users/2

points API:
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8080/users/0/points
curl -X POST -H "Content-Type: application/json" -d "{\"notes\": \"Test metric record in percentage.\", \"tags\": [\"Heart Rate Cap.\"], \"time\": 1557453458, \"units\": \"percentage\", \"value\": \"50%\"}" http://127.0.0.1:8080/users/3/points
curl -X GET -H "Content-Type: application/json" http://127.0.0.1:8080/users/3/points/8


curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiAiSFMyNTYifQ%3D%3D.eyJJRCI6IDEsICJyb2xlIjogInVzZXIifQ%3D%3D.aSheyqrdpcWzSU9WShYxSjoBZqaL779hadgXxLQ%2Fgrc%3D" "http://127.0.0.1:8080/users/1/points?tags=c"


filter by tag:
curl -X GET -H "Content-Type: application/json;" -H "Authorization: Bearer eyJhbGciOiAiSFMyNTYifQ==.eyJJRCI6IDEsICJyb2xlIjogInVzZXIifQ==.aSheyqrdpcWzSU9WShYxSjoBZqaL779hadgXxLQ/grc=" http://127.0.0.1:8080/users/1/points?tags=Heart%20Rate%20Cap.



FOR GROUP DEFINITIONS: