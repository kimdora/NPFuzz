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
$ curl -X PUT -H "Content-Type: application/json" -d '{"body": "<new content>", "hash": "<previous content hash>"}' http://localhost:5000/blog/posts/<id>
```

