from app import app

if __name__ == '__main__':
    #app.run(ssl_context=("cert.pem", "key.pem"), host="0.0.0.0", port=443)
    #app.run(ssl_context="adhoc", host="0.0.0.0", port=443)
    app.run(host="0.0.0.0", port=80)

