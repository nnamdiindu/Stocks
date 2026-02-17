from flask import render_template, Blueprint
from flask_login import current_user, login_required
from app.utils.stocks_api import api
from app.utils.transactions import TransactionService

# Create blueprint
dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # all_stocks = api.get_all_major_stocks(
    #     limit=50,
    #     use_cache=True,
    #     cache_max_age_hours=24
    # )
    # categories = api.categorize_stocks(all_stocks)
    # gainers_and_losers = categories["gainers"][:3] + categories["losers"][:2]
    transactions = TransactionService.get_user_transactions(current_user.id)
    return render_template("dashboard/dashboard.html", transactions=transactions,
                           # all_stocks=all_stocks,
                           # trending_stocks=categories["trending"],
                           # gainers_losers_stocks=gainers_and_losers,
                           current_user=current_user)

@dashboard_bp.route("/dashboard/portfolio")
@login_required
def portfolio():
    transactions = TransactionService.get_user_transactions(current_user.id)
    return render_template("dashboard/portfolio.html", current_user=current_user, transactions=transactions)

@dashboard_bp.route("/dashboard/invest")
@login_required
def invest():
    return render_template("dashboard/invest.html")

@dashboard_bp.route("/dashboard/settings")
@login_required
def settings():
    return render_template("dashboard/settings.html")

@dashboard_bp.route("/dashboard/wallet")
@login_required
def wallet():
    transactions = TransactionService.get_user_transactions(current_user.id)
    return render_template("dashboard/wallet.html", transactions=transactions)

@dashboard_bp.route("/dashboard/insights")
@login_required
def insights():
    return render_template("dashboard/insights.html")

@dashboard_bp.route("/dashboard/support")
@login_required
def support():
    return render_template("dashboard/support.html")

@dashboard_bp.route("/dashboard/referrals")
@login_required
def referrals():
    return render_template("dashboard/referrals.html")