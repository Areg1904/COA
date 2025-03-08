docker run -p 8080:8080 -e SWAGGER_JSON=/swagger.yaml -v $(pwd)/swagger.yaml:/swagger.yaml swaggerapi/swagger-ui
# http://localhost:8080