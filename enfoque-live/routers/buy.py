from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for

from utils import configuration, tokens
import mercadopago

from models import tokens as tokens_db

mp_checkout = Blueprint('mp_checkout', __name__)

SDK = mercadopago.SDK(configuration.get("mercadopago_private_key"))

@mp_checkout.route('/comprar')
def buy():
    user_limit = configuration.get("users_limit")
    if tokens_db.count_all_sold_tokens() >= int(user_limit):
        current_app.logger.warning(f"Limite de usuarios alcanzado! { user_limit }")
        return render_template("generic_advertence.html", title="¡Limite de usuarios alcanzado!", message="Lo sentimos, se superó el limite de usuarios y ya no hay más cupos.")
    current_app.logger.info(f"Buy attempt from '{request.remote_addr}' started.")
    return render_template("purchase/buy.html", public_key=configuration.get('mercadopago_public_key'))

@mp_checkout.route('/purchased')
def purchased():
    if token:=request.args.get("token"):
        full_link = url_for("stream.play", stream_token=token, _external=True)
        return render_template("purchase/sold.html", url=full_link)
    return "Not found!", 404

@mp_checkout.route('/paid_error')
def paid_error():
    return render_template("purchase/paid_error.html")


@mp_checkout.route('/approve/sold/<stream_token>')
def approve(stream_token: str):
    token = tokens_db.get(stream_token)
    if token and not token.sold:
        current_app.logger.info(f"Token {token} approved and sold to '{request.remote_addr}'!")
        token.sold = True
        token.status = "Vendido"
        tokens_db.save()
        return redirect(url_for("mp_checkout.purchased", token=token.token))
    current_app.logger.info(f"A tried of approve but the '{stream_token}' doesn't exist.")
    return redirect("/comprar")

@mp_checkout.route('/get_preference', methods=['GET'])
def get_preference():
    token_value = tokens.generate_token()
    tokens_db.create_token(name=tokens.generate_alias(), token_value=token_value, sold=False)

    target_url = url_for("mp_checkout.approve", stream_token=token_value , _external=True)

    current_app.logger.info(f"get_preference called and target url '{target_url}' generated for an intent from {request.remote_addr} to buy the token {token_value}")
    
    # set returns url
    if configuration.get("in_production") == False:
        ok_url = "https://test-403.vercel.app/"
        bad_url = "https://test-alert.vercel.app/"
    else:
        ok_url = target_url
        bad_url = f"{request.host_url}paid_error"

    preference_data = {
        "items": [
            {
                "title": "Link EnfoqueLive",
                "quantity": 1,
                "unit_price": float(configuration.get("link_price"))
            }
        ],
        "back_urls": {
            "success": ok_url,
            "failure": bad_url,
            "pending": ok_url
        },
        "auto_return": "approved"
    }

    preference_response = SDK.preference().create(preference_data)
    preference = preference_response["response"]
    current_app.logger.info("Preference content:" + str(preference))

    return jsonify({"id": preference_response["response"]["id"]})
