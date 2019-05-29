# BlogService

## Setup 
```
$ docker build -t blogservice .
$ docker run -it -d --rm -p 5000:5000 blogservice
$ curl http://127.0.0.1:5000/blog/posts/ # show all posts
```

## Functionality
### `GET /blog/posts/`
```
$ curl http://localhost:5000/blog/posts/
```

### `POST /blog/posts/`
```
$ curl -X POST -H "Content-Type: application/json" -d '{"body": "test"}' http://localhost:5000/blog/posts/
```

### `GET /blog/posts/<id>`
```
$ curl http://localhost:5000/blog/posts/<id>
```

### `DELETE /blog/posts/<id>`
```
$ curl -X DELETE http://localhost:5000/blog/posts/<id>
```

### `PUT /blog/posts/<id>`
```
$ curl -X PUT -H "Content-Type: application/json" -d '{"body": "<new content>", "checksum": "<checksum of previous content"}' http://localhost:5000/blog/posts/<id>
```

## Example
```
$ curl http://localhost:5000/blog/posts/ 
{"error":0,"posts":[]}
$ curl http://localhost:5000/blog/posts/1
{"error":1,"message":"post not found"}
$ curl -X POST -H "Content-Type: application/json" -d '{"body": "This is test"}' http://localhost:5000/blog/posts/
{"error":0,"id":1}
$ curl -X POST -H "Content-Type: application/json" -d '{"body": "NPFuzz"}' http://localhost:5000/blog/posts/
{"error":0,"id":2}
$ curl http://localhost:5000/blog/posts/ 
{"error":0,"posts":[{"body":"NPFuzz"},{"body":"This is test"}]}
```
```
$ curl http://localhost:5000/blog/posts/1
{"error":0,"post":{"body":"This is test","checksum":"32558aace66e5b46c3c1"}}
$ curl -X PUT -H "Content-Type: application/json" -d '{"body": "Automatic Testing", "checksum": "32558aace66e5b46c3c1"}' http://localhost:5000/blog/posts/1
{"error":0}
$ curl http://localhost:5000/blog/posts/1
{"error":0,"post":{"body":"Automatic Testing","checksum":"1e11354ffa2906666bf8"}}
```
```
$ curl http://localhost:5000/blog/posts/ 
{"error":0,"posts":[{"body":"NPFuzz"},{"body":"Automatic Testing"}]}
$ curl -X DELETE http://localhost:5000/blog/posts/1
{"error":0}
$ curl http://localhost:5000/blog/posts/
{"error":0,"posts":[{"body":"NPFuzz"}]}

```

