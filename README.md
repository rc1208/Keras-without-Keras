## Softwares required to be installed: ##

1. Python 3 or >
2. Flask 
3. Docker
4. Tensorflow
5. Tensorflow Serving


curl -X POST   http://localhost:8501/v1/models/feeds:predict   -H 'cache-control: no-cache'   -H 'postman-token: f7fb6e3f-26ba-a742-4ab3-03c953cefaf5'   -d '{
 "inputs":[
  [23,27.125,419,686,0.00471494214590473]
  ]
}'
