# Enfoque live
A RTMP video streaming platform. Give to users privates unsharable-links to watch content.

1. Run the flask application (port 80 by default)
2. Start the nginx server and start to streaming throught RTMP

	`rtmp://127.0.0.1/hls ` using the key `stream`

3. Login to app

`http://127.0.0.1/login `

Others:

- `http://127.0.0.1/panel ` to administrate links and parameters.
- `http://127.0.0.1/monitoring ` to monitoring the stream
