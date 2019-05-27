# BlogService

## Usage
```
$ docker build -t blogservice .
$ docker run -it -p 80:3000 --name blog blogservice
$ curl http://127.0.0.1/blog/posts/
```
