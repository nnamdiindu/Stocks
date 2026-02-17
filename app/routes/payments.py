from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone
import uuid
from app.models import Notification
from app.utils.nowpayments import NOWPaymentsService, PaymentStatus
from app.models.payment import (
    db, CryptoPayment, PaymentCallback,
    payment_to_dict, is_payment_completed, is_payment_pending, is_payment_failed
)
from app.utils.transactions import TransactionService

# Create blueprint
payment_bp = Blueprint("payments", __name__, url_prefix="/dashboard/payments")


def get_nowpayments_service():
    """Initialize NOWPayments service with app config"""
    return NOWPaymentsService(
        api_key=current_app.config["NOWPAYMENTS_API_KEY"],
        ipn_secret=current_app.config["NOWPAYMENTS_IPN_SECRET"],
        sandbox=current_app.config.get("NOWPAYMENTS_SANDBOX", False)
    )


# ============= Payment Creation Routes =============

@payment_bp.route("/deposit", methods=["POST"])
@login_required
def create_deposit():
    """
    Handle deposit request from frontend modal

    Expected JSON from modal:
    {
        "amount": 100.00,
        "currency": "USD",
        "payment_method": "crypto" or "card"
    }
    """
    try:
        data = request.get_json()

        # Log received data for debugging
        current_app.logger.info(f"Deposit request from user {current_user.id}: {data}")
        amount = float(data.get("amount", 0))

        # Check minimum amount
        MIN_DEPOSIT = 20.00
        if amount < MIN_DEPOSIT:
            return jsonify({
                "success": False,
                "error": f"Minimum deposit is ${MIN_DEPOSIT:.2f} due to blockchain network fees."
            }), 400

        # Validate required fields
        if not data or "amount" not in data:
            return jsonify({
                "success": False,
                "error": "Missing required field: amount"
            }), 400

        # Extract and validate amount
        amount = data.get("amount")
        if not amount or float(amount) <= 0:
            return jsonify({
                "success": False,
                "error": "Invalid amount. Please enter a valid deposit amount."
            }), 400

        # Get currency (default to USD)
        currency = data.get("currency", "USD")

        # Get payment method
        payment_method = data.get("payment_method", "crypto")

        # Handle different payment methods
        if payment_method == "card":
            # Bank Transfer payments not implemented yet
            return jsonify({
                "success": False,
                "error": "Bank transfer payments are not available yet. Please use cryptocurrency."
            }), 501

        # Handle cryptocurrency payments
        if payment_method != "crypto":
            return jsonify({
                "success": False,
                "error": "Invalid payment method. Please select cryptocurrency."
            }), 400

        # Generate order ID
        order_id = f"DEPOSIT-{uuid.uuid4().hex[:8].upper()}"

        # Generate description
        description = data.get("description", f"Account Deposit - {current_user.username}")

        # Initialize NOWPayments service
        np_service = get_nowpayments_service()

        # Get callback URLs
        ipn_callback_url = current_app.config.get("NOWPAYMENTS_IPN_CALLBACK_URL")
        if ipn_callback_url and not ipn_callback_url.startswith("http"):
            ipn_callback_url = request.url_root.rstrip('/') + ipn_callback_url

        success_url = request.url_root.rstrip("/") + url_for("payments.payment_success")
        cancel_url = request.url_root.rstrip("/") + url_for("payments.payment_cancel")

        # Check if specific cryptocurrency was requested
        pay_currency = data.get("pay_currency")

        if pay_currency:
            # Create direct payment with specific currency
            payment_response = np_service.create_payment(
                price_amount=float(amount),
                price_currency=currency.upper(),
                pay_currency=pay_currency.lower(),
                order_id=order_id,
                order_description=description,
                ipn_callback_url=ipn_callback_url,
                success_url=success_url,
                cancel_url=cancel_url,
                fixed_rate=current_app.config.get("NOWPAYMENTS_FIXED_RATE", True),
                is_fee_paid_by_user=current_app.config.get("NOWPAYMENTS_FEE_PAID_BY_USER", True)
            )

            # Save to database
            payment = CryptoPayment(
                payment_id=str(payment_response.get("payment_id")),
                order_id=order_id,
                user_id=current_user.id,
                price_amount=float(amount),
                price_currency=currency.upper(),
                pay_amount=payment_response.get("pay_amount"),
                pay_currency=payment_response.get("pay_currency"),
                payment_status=payment_response.get("payment_status", "waiting"),
                payment_type="payment",
                pay_address=payment_response.get("pay_address"),
                payin_extra_id=payment_response.get("payin_extra_id"),
                order_description=description,
                success_url=success_url,
                cancel_url=cancel_url,
                expiration_estimate_date=datetime.fromisoformat(
                    payment_response["expiration_estimate_date"].replace("Z", "+00:00")
                ) if payment_response.get("expiration_estimate_date") else None
            )

        else:
            # Create invoice (user chooses cryptocurrency on NOWPayments page)
            invoice_response = np_service.create_invoice(
                price_amount=float(amount),
                price_currency=currency.upper(),
                order_id=order_id,
                order_description=description,
                ipn_callback_url=ipn_callback_url,
                success_url=success_url,
                cancel_url=cancel_url,
                is_fee_paid_by_user=current_app.config.get("NOWPAYMENTS_FEE_PAID_BY_USER", True),
                is_fixed_rate=current_app.config.get("NOWPAYMENTS_FIXED_RATE", True)
            )

            # Save to database
            payment = CryptoPayment(
                invoice_id=str(invoice_response.get("id")),
                order_id=order_id,
                user_id=current_user.id,
                price_amount=float(amount),
                price_currency=currency.upper(),
                payment_status="waiting",
                payment_type="invoice",
                invoice_url=invoice_response.get("invoice_url"),
                order_description=description,
                success_url=success_url,
                cancel_url=cancel_url
            )

        db.session.add(payment)
        db.session.commit()

        current_app.logger.info(f"Payment created successfully: {order_id}")
        # Create transaction record for history table
        TransactionService.create_deposit(payment)


        # Return response with invoice URL for redirect
        # return jsonify({
        #     "success": True,
        #     "payment_id": payment.id,
        #     "order_id": order_id,
        #     "invoice_url": payment.invoice_url if payment.payment_type == "invoice" else None,
        #     "pay_address": payment.pay_address if payment.payment_type == "payment" else None,
        #     "pay_amount": payment.pay_amount if payment.payment_type == "payment" else None,
        #     "pay_currency": payment.pay_currency if payment.payment_type == "payment" else None,
        #     "payment_status": payment.payment_status,
        #     "amount": float(amount),
        #     "currency": currency.upper()
        # }), 201

        # except Exception as e:
        # current_app.logger.error(f"Deposit creation error: {str(e)}", exc_info=True)
        # return jsonify({
        #     "success": False,
        #     "error": f"Failed to create deposit: {str(e)}"
        # }), 500

        # FIXED: Return response with correct invoice_id
        response_data = {
            "success": True,
            "payment_id": payment.id,  # Database ID
            "order_id": order_id,
            "payment_status": payment.payment_status,
            "amount": float(amount),
            "currency": currency.upper()
        }

        # Add invoice-specific data
        if payment.payment_type == "invoice":
            response_data["invoice_id"] = payment.invoice_id  # NOWPayments invoice ID
            response_data["invoice_url"] = payment.invoice_url

        # Add payment-specific data
        if payment.payment_type == "payment":
            response_data["pay_address"] = payment.pay_address
            response_data["pay_amount"] = payment.pay_amount
            response_data["pay_currency"] = payment.pay_currency

        return jsonify(response_data), 201

    except Exception as e:
        current_app.logger.error(f"Deposit creation error: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to create deposit: {str(e)}"
        }), 500




@payment_bp.route("/invoice/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    """View invoice payment page"""
    payment = CryptoPayment.query.filter_by(
        invoice_id=str(invoice_id),
        user_id=current_user.id
    ).first_or_404()

    return render_template("dashboard/payments/invoice.html",
                           payment=payment,
                           is_completed=is_payment_completed(payment),
                           is_pending=is_payment_pending(payment))


# ============= Payment Status Routes =============

@payment_bp.route("/status/<order_id>")
@login_required
def payment_status(order_id):
    """Check payment status"""
    payment = CryptoPayment.query.filter_by(
        order_id=order_id,
        user_id=current_user.id
    ).first_or_404()

    # Fetch latest status from NOWPayments
    try:
        np_service = get_nowpayments_service()

        if payment.payment_id:
            status_response = np_service.get_payment_status(int(payment.payment_id))

            # Update payment record
            payment.payment_status = status_response.get("payment_status")
            payment.actually_paid = status_response.get("actually_paid")
            payment.updated_at = lambda: datetime.now(timezone.utc)
            db.session.commit()

        return jsonify({
            "success": True,
            "payment": payment_to_dict(payment)
        })

    except Exception as e:
        current_app.logger.error(f"Status check error: {str(e)}")
        return jsonify({
            "success": False,
            "payment": payment_to_dict(payment),
            "error": str(e)
        })


@payment_bp.route("/list")
@login_required
def list_payments():
    """List user's payments"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    payments = CryptoPayment.query.filter_by(user_id=current_user.id) \
        .order_by(CryptoPayment.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template("payments/list.html", payments=payments)


# ============= Webhook/IPN Routes =============

@payment_bp.route("/webhook/ipn", methods=["POST"])
def ipn_callback():
    """
    Handle IPN (Instant Payment Notification) callbacks from NOWPayments
    This endpoint should be publicly accessible (no @login_required)
    """
    try:
        # Get raw request data and signature
        request_data = request.get_data()
        signature = request.headers.get("x-nowpayments-sig")

        if not signature:
            current_app.logger.error("Missing IPN signature")
            return jsonify({"error": "Missing signature"}), 400

        # Verify and process callback
        np_service = get_nowpayments_service()
        callback_data = np_service.process_ipn_callback(request_data, signature)

        # Find payment by payment_id
        payment = CryptoPayment.query.filter_by(
            payment_id=str(callback_data.get("payment_id"))
        ).first()

        if not payment:
            current_app.logger.warning(f"Payment not found: {callback_data.get('payment_id')}")
            return jsonify({"error": "Payment not found"}), 404

        # Log callback
        callback_log = PaymentCallback(
            payment_db_id=payment.id,
            payment_id=str(callback_data.get("payment_id")),
            payment_status=callback_data.get("payment_status"),
            pay_amount=callback_data.get("pay_amount"),
            actually_paid=callback_data.get("actually_paid"),
            callback_data=callback_data,
            signature=signature,
            signature_valid=True
        )
        db.session.add(callback_log)

        # Update payment status
        old_status = payment.payment_status
        payment.payment_status = callback_data.get("payment_status")
        payment.actually_paid = callback_data.get("actually_paid")
        payment.pay_amount = callback_data.get("pay_amount")
        payment.outcome_amount = callback_data.get("outcome_amount")
        payment.outcome_currency = callback_data.get("outcome_currency")
        payment.updated_at = lambda: datetime.now(timezone.utc)

        # Handle status changes
        if old_status != payment.payment_status:
            current_app.logger.info(
                f"Payment {payment.order_id} status changed: {old_status} -> {payment.payment_status}"
            )

            # Call status-specific handlers
            if is_payment_completed(payment):
                handle_payment_completed(payment)
            elif is_payment_failed(payment):
                handle_payment_failed(payment)
            elif payment.payment_status == PaymentStatus.EXPIRED:
                handle_payment_expired(payment)

        db.session.commit()

        return jsonify({"success": True}), 200

    except Exception as e:
        current_app.logger.error(f"IPN callback error: {str(e)}")

        # Log failed callback attempt
        if request.get_data():
            try:
                callback_log = PaymentCallback(
                    payment_db_id=None,
                    payment_id="unknown",
                    payment_status="error",
                    callback_data={"error": str(e), "raw_data": request.get_data().decode("utf-8")},
                    signature=request.headers.get("x-nowpayments-sig"),
                    signature_valid=False
                )
                db.session.add(callback_log)
                db.session.commit()
            except:
                pass

        return jsonify({"error": str(e)}), 500


# ============= Success/Cancel Routes =============

@payment_bp.route("/success")
def payment_success():
    """Payment success page"""
    order_id = request.args.get("order_id")

    if order_id and current_user.is_authenticated:
        payment = CryptoPayment.query.filter_by(
            order_id=order_id,
            user_id=current_user.id
        ).first()

        if payment:
            flash("Payment completed successfully!", "success")
            return render_template("payments/success.html", payment=payment)

    return render_template("payments/success.html")


@payment_bp.route("/cancel")
def payment_cancel():
    """Payment cancellation page"""
    order_id = request.args.get("order_id")

    if order_id and current_user.is_authenticated:
        payment = CryptoPayment.query.filter_by(
            order_id=order_id,
            user_id=current_user.id
        ).first()

        if payment:
            flash("Payment was cancelled.", "warning")
            return render_template("payments/cancel.html", payment=payment)

    return render_template("payments/cancel.html")


# ============= Admin Routes =============

@payment_bp.route("/admin/payments")
@login_required
def admin_payments():
    """Admin view of all payments (add role check)"""
    # Add admin check here: if not current_user.is_admin: abort(403)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)

    payments = CryptoPayment.query \
        .order_by(CryptoPayment.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return render_template("payments/admin.html", payments=payments)


# ============= Utility Functions =============

def handle_payment_completed(payment):
    """Handle completed payment logic"""
    current_app.logger.info(f"Payment completed: {payment.order_id}")
    TransactionService.update_status(payment.order_id, "finished")

    # Add your business logic here:
    # - Update order status
    # Send notification to user dashboard
    Notification.create_wallet_notification(
        session=db.session,
        user_id=current_user.id,
        wallet_data={
            "amount": 50000,
            "method": "bank transfer",
            "transaction_id": 456
        },
        notification_type="deposit"
    )
    # - Send confirmation email
    from app.utils.email import send_payment_confirmation_email

    send_payment_confirmation_email(
        user_email=current_user.email,
        user_name=current_user.first_name,
        amount=payment.amount,
    )
    # - Grant access to service
    # - Update user credits/subscription
    # etc.


def handle_payment_failed(payment):
    """Handle failed payment logic"""
    current_app.logger.warning(f"Payment failed: {payment.order_id}")
    # Add your business logic here:
    # - Send notification
    # - Log for review
    # etc.
    TransactionService.update_status(payment.order_id, "failed")


def handle_payment_expired(payment):
    """Handle expired payment logic"""
    current_app.logger.info(f"Payment expired: {payment.order_id}")
    # Add your business logic here:
    # - Clean up pending orders
    # - Send notification
    # etc.
    TransactionService.update_status(payment.order_id, "expired")


# ============= API Routes (for AJAX) =============

@payment_bp.route("/api/currencies", methods=["GET"])
def get_currencies():
    """Get available cryptocurrencies"""
    try:
        np_service = get_nowpayments_service()
        currencies = np_service.get_available_currencies()

        return jsonify({
            "success": True,
            "currencies": currencies
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/api/estimate", methods=["POST"])
def get_estimate():
    """Get payment estimate"""
    try:
        data = request.get_json()

        np_service = get_nowpayments_service()
        estimate = np_service.get_estimate(
            amount=float(data["amount"]),
            currency_from=data["currency_from"],
            currency_to=data["currency_to"]
        )

        return jsonify({
            "success": True,
            "estimate": estimate
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500