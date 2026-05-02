import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import flt, formatdate, getdate


@frappe.whitelist()
def get_statement_pdf(customer, from_date, to_date):
    """Generate Customer Statement PDF for date range. Called by MittalBuddy."""

    if not customer:
        frappe.throw("Customer is required")

    if not frappe.db.exists("Customer", customer):
        frappe.throw("Customer " + str(customer) + " not found")

    company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")

    # Compute opening balance: sum of all GL entries for this customer BEFORE from_date
    opening_query = """
        SELECT COALESCE(SUM(debit - credit), 0) as opening
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
          AND party = %(customer)s
          AND posting_date < %(from_date)s
          AND is_cancelled = 0
          AND company = %(company)s
    """
    opening_result = frappe.db.sql(opening_query, {
        "customer": customer,
        "from_date": from_date,
        "company": company,
    }, as_dict=True)
    opening_balance = flt(opening_result[0].opening) if opening_result else 0

    # Get all transactions in date range
    transactions_query = """
        SELECT
            posting_date,
            voucher_type,
            voucher_no,
            against_voucher,
            against,
            debit,
            credit,
            remarks
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
          AND party = %(customer)s
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND is_cancelled = 0
          AND company = %(company)s
        ORDER BY posting_date, creation
    """
    transactions = frappe.db.sql(transactions_query, {
        "customer": customer,
        "from_date": from_date,
        "to_date": to_date,
        "company": company,
    }, as_dict=True)

    # Compute running balance and totals
    running_balance = opening_balance
    total_debit = 0
    total_credit = 0

    for t in transactions:
        t["debit"] = flt(t.get("debit", 0))
        t["credit"] = flt(t.get("credit", 0))
        running_balance += t["debit"] - t["credit"]
        t["balance"] = running_balance
        total_debit += t["debit"]
        total_credit += t["credit"]

    closing_balance = opening_balance + total_debit - total_credit

    customer_doc = frappe.get_doc("Customer", customer)

    context = {
        "customer": customer,
        "customer_doc": customer_doc,
        "company": company,
        "from_date": formatdate(from_date, "dd-MM-yyyy"),
        "to_date": formatdate(to_date, "dd-MM-yyyy"),
        "transactions": transactions,
        "opening_balance": opening_balance,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": closing_balance,
        "now": formatdate(frappe.utils.nowdate(), "dd-MM-yyyy"),
    }

    html = frappe.render_template("templates/customer_statement_mb.html", context)
    pdf = get_pdf(html, {"orientation": "Portrait", "page-size": "A4"})

    filename = "Statement-" + str(customer) + "-" + str(from_date) + "-to-" + str(to_date) + ".pdf"
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"
