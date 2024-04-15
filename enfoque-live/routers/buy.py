from flask import Blueprint, jsonify, render_template, request, current_app, redirect, url_for

from utils import configuration, tokens
import database
import mercadopago

mp_checkout = Blueprint('mp_checkout', __name__)

SDK = mercadopago.SDK(configuration.get("MERCADOPAGO_PRIVATE_KEY"))

@mp_checkout.route('/comprar')
def comprar():
    if database.count_tokens_with_condition("sold") >= int(configuration.get("USERS_LIMIT")):
        current_app.logger.warning(
            f"Limite de usuarios alcanzado! { configuration.get('USERS_LIMIT') }")
        return render_template(
            "generic_advertence.html", 
            title="¡Limite de usuarios alcanzado!",
            message="Lo sentimos, se superó el limite de usuarios y ya no hay más cupos.")
    current_app.logger.info(
        f"Intento de compra por parte de {request.remote_addr}.")
    return render_template("purchase/buy.html", public_key=configuration.get('MERCADOPAGO_PUBLIC_KEY'))


@mp_checkout.route('/purchased')
def purchased():
    if token := request.args.get("token"):
        full_link = url_for("stream.play", token=token, _external=True)
        return render_template("purchase/sold.html", url=full_link)
    else:
        return "Not found!", 404


@mp_checkout.route('/paid_error')
def paid_error():
    return render_template("purchase/paid_error.html")


@mp_checkout.route('/approve/sold/<token>')
def approve(token):
    if (database.token_exists(token)):
        status = database.dump_token(token)['status']
        if status == "to_approve":
            current_app.logger.info(
                f"Token {token} aprobado y vendido a {request.remote_addr}!.")
            database.set_token_status(token, "sold")
            return redirect(url_for("mp_checkout.purchased", token=token))

    return redirect("/comprar")


@mp_checkout.route('/get_preference', methods=['GET'])
def get_preference():
    token = tokens.generate_token(status="to_approve")
    target_url = url_for("mp_checkout.approve", token=token, _external=True)
    current_app.logger.info(
        f"get_preference called and target url '{target_url}' generated for an intent from {request.remote_addr} to buy the token {token}")
    if configuration.get("IN_PRODUCTION") == "no":
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
                "unit_price": float(configuration.get("LINK_PRICE"))
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
    current_app.logger.info(str(preference))
    return jsonify({"id": preference_response["response"]["id"]})
