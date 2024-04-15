import logging

handler = logging.FileHandler('logs/flask_app.log')
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))