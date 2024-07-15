# Enfoque live
A RTMP video streaming platform. Give to users privates unsharable-links to watch content.

- Supports local rtmp streaming
- CDN usage for delivery hls chunks
- Real time refresh and viewer counter
- Many configurations
- Mercado pago payment method.

1. Run the flask application (port 80 by default)
2. Start the nginx server and start to streaming throught RTMP

	`rtmp://127.0.0.1/hls ` using the key `stream`

3. Login as admin into the app

`http://127.0.0.1/login `

Others:

- `http://127.0.0.1/admin/panel ` to administrate links and parameters.
- `http://127.0.0.1/admin/monitoring ` to monitoring the stream


Build js modules for taildwindcss:

`cd jstoolchain`
`npm install`
`npm run taildwindcss-build`
