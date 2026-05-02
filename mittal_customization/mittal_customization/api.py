import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import flt, formatdate


@frappe.whitelist()
def get_statement_pdf(customer, from_date, to_date):
    """Generate Customer Statement PDF for date range. Called by MittalBuddy."""

    if not customer:
        frappe.throw("Customer is required")

    if not frappe.db.exists("Customer", customer):
        frappe.throw("Customer " + str(customer) + " not found")

    company = frappe.defaults.get_user_default("Company") or \
              frappe.db.get_single_value("Global Defaults", "default_company")

    from erpnext.accounts.report.general_ledger.general_ledger import execute as gl_execute

    filters = frappe._dict({
        "company": company,
        "from_date": from_date,
        "to_date": to_date,
        "party_type": "Customer",
        "party": [customer],
        "group_by": "Group by Voucher (Consolidated)",
        "show_opening_entries": 1,
    })

    result = gl_execute(filters)
    columns = result[0] if len(result) > 0 else []
    data = result[1] if len(result) > 1 else []

    opening_balance = 0
    total_debit = 0
    total_credit = 0

    for row in data:
        if isinstance(row, dict):
            if "Opening" in str(row.get("account", "")) or row.get("voucher_type") == "Opening Balance":
                opening_balance = flt(row.get("balance", 0))
            total_debit += flt(row.get("debit", 0))
            total_credit += flt(row.get("credit", 0))

    closing_balance = opening_balance + total_debit - total_credit

    customer_doc = frappe.get_doc("Customer", customer)

    context = {
        "customer": customer,
        "customer_doc": customer_doc,
        "company": company,
        "from_date": formatdate(from_date, "dd-MM-yyyy"),
        "to_date": formatdate(to_date, "dd-MM-yyyy"),
        "data": data,
        "opening_balance": opening_balance,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": closing_balance,
        "now": formatdate(frappe.utils.nowdate(), "dd-MM-yyyy"),
    }

    html = frappe.render_template(
        "templates/customer_statement_mb.html",
        context
    )

    pdf = get_pdf(html, {"orientation": "Portrait", "page-size": "A4"})

    filename = "Statement-" + str(customer) + "-" + str(from_date) + "-to-" + str(to_date) + ".pdf"
    frappe.local.response.filename = filename
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"
