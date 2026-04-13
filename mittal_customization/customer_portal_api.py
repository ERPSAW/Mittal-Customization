import frappe
from frappe.utils import flt


def get_customer_for_user(user):
    """Find the Customer linked to this user's email via Dynamic Link in Contact"""
    customer = frappe.db.sql("""
        SELECT dl.link_name
        FROM `tabContact` c
        INNER JOIN `tabDynamic Link` dl ON dl.parent = c.name AND dl.parenttype = 'Contact'
        WHERE dl.link_doctype = 'Customer'
        AND c.email_id = %s
        LIMIT 1
    """, user, as_dict=True)

    if customer:
        return customer[0].link_name

    # Fallback: check Contact Email table
    customer = frappe.db.sql("""
        SELECT dl.link_name
        FROM `tabContact Email` ce
        INNER JOIN `tabContact` c ON c.name = ce.parent
        INNER JOIN `tabDynamic Link` dl ON dl.parent = c.name AND dl.parenttype = 'Contact'
        WHERE dl.link_doctype = 'Customer'
        AND ce.email_id = %s
        LIMIT 1
    """, user, as_dict=True)

    if customer:
        return customer[0].link_name

    return None


def validate_customer_access():
    """Ensure logged-in user has a linked customer"""
    if frappe.session.user == "Guest":
        frappe.throw("Please login first", frappe.AuthenticationError)

    customer = get_customer_for_user(frappe.session.user)
    if not customer:
        frappe.throw("No customer account linked to your email", frappe.PermissionError)

    return customer


@frappe.whitelist()
def get_ledger(from_date, to_date):
    """Get customer ledger with running balance"""
    customer = validate_customer_access()

    # Get opening balance
    opening = frappe.db.sql("""
        SELECT COALESCE(SUM(debit) - SUM(credit), 0) as balance
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
        AND party = %s
        AND posting_date < %s
        AND is_cancelled = 0
    """, (customer, from_date), as_dict=True)

    opening_balance = flt(opening[0].balance) if opening else 0

    # Get GL entries for the period
    entries = frappe.db.sql("""
        SELECT
            gl.posting_date,
            CASE
                WHEN gl.debit > 0 THEN CONCAT('To ', gl.against)
                ELSE CONCAT('By ', gl.against)
            END as particulars,
            gl.voucher_type,
            gl.voucher_no,
            gl.debit,
            gl.credit
        FROM `tabGL Entry` gl
        WHERE gl.party_type = 'Customer'
        AND gl.party = %s
        AND gl.posting_date >= %s
        AND gl.posting_date <= %s
        AND gl.is_cancelled = 0
        ORDER BY gl.posting_date, gl.creation
    """, (customer, from_date, to_date), as_dict=True)

    # Calculate running balance
    running_balance = opening_balance
    for entry in entries:
        running_balance += flt(entry.debit) - flt(entry.credit)
        entry.balance = running_balance
        entry.posting_date = entry.posting_date.strftime("%d-%m-%Y")

    # Calculate totals
    total_debit = sum(flt(e.debit) for e in entries)
    total_credit = sum(flt(e.credit) for e in entries)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "opening_balance": opening_balance,
        "entries": entries,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": opening_balance + total_debit - total_credit
    }


@frappe.whitelist()
def get_outstanding():
    """Get outstanding invoices for the customer"""
    customer = validate_customer_access()

    invoices = frappe.db.sql("""
        SELECT
            si.name as invoice_no,
            si.posting_date,
            si.due_date,
            si.grand_total,
            si.outstanding_amount,
            DATEDIFF(CURDATE(), si.due_date) as overdue_days
        FROM `tabSales Invoice` si
        WHERE si.customer = %s
        AND si.docstatus = 1
        AND si.outstanding_amount > 0
        ORDER BY si.posting_date DESC
    """, customer, as_dict=True)

    for inv in invoices:
        inv.posting_date = inv.posting_date.strftime("%d-%m-%Y")
        inv.due_date = inv.due_date.strftime("%d-%m-%Y")
        inv.overdue_days = max(0, inv.overdue_days or 0)

    total_outstanding = sum(flt(i.outstanding_amount) for i in invoices)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "invoices": invoices,
        "total_outstanding": total_outstanding
    }


@frappe.whitelist()
def get_payments(from_date, to_date):
    """Get payment history for the customer"""
    customer = validate_customer_access()

    payments = frappe.db.sql("""
        SELECT
            pe.name as payment_no,
            pe.posting_date,
            pe.paid_amount,
            pe.reference_no,
            pe.reference_date,
            pe.mode_of_payment
        FROM `tabPayment Entry` pe
        WHERE pe.party_type = 'Customer'
        AND pe.party = %s
        AND pe.docstatus = 1
        AND pe.posting_date >= %s
        AND pe.posting_date <= %s
        ORDER BY pe.posting_date DESC
    """, (customer, from_date, to_date), as_dict=True)

    for pay in payments:
        pay.posting_date = pay.posting_date.strftime("%d-%m-%Y")
        if pay.reference_date:
            pay.reference_date = pay.reference_date.strftime("%d-%m-%Y")

    total_paid = sum(flt(p.paid_amount) for p in payments)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "payments": payments,
        "total_paid": total_paid
    }
    # Get opening balance
    opening = frappe.db.sql("""
        SELECT COALESCE(SUM(debit) - SUM(credit), 0) as balance
        FROM `tabGL Entry`
        WHERE party_type = 'Customer'
        AND party = %s
        AND posting_date < %s
        AND is_cancelled = 0
    """, (customer, from_date), as_dict=True)

    opening_balance = flt(opening[0].balance) if opening else 0

    # Get GL entries for the period
    entries = frappe.db.sql("""
        SELECT
            gl.posting_date,
            CASE
                WHEN gl.debit > 0 THEN CONCAT('To ', gl.against)
                ELSE CONCAT('By ', gl.against)
            END as particulars,
            gl.voucher_type,
            gl.voucher_no,
            gl.debit,
            gl.credit
        FROM `tabGL Entry` gl
        WHERE gl.party_type = 'Customer'
        AND gl.party = %s
        AND gl.posting_date >= %s
        AND gl.posting_date <= %s
        AND gl.is_cancelled = 0
        ORDER BY gl.posting_date, gl.creation
    """, (customer, from_date, to_date), as_dict=True)

    # Calculate running balance
    running_balance = opening_balance
    for entry in entries:
        running_balance += flt(entry.debit) - flt(entry.credit)
        entry.balance = running_balance
        entry.posting_date = entry.posting_date.strftime("%d-%m-%Y")

    # Calculate totals
    total_debit = sum(flt(e.debit) for e in entries)
    total_credit = sum(flt(e.credit) for e in entries)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "opening_balance": opening_balance,
        "entries": entries,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "closing_balance": opening_balance + total_debit - total_credit
    }


@frappe.whitelist()
def get_outstanding():
    """Get outstanding invoices for the customer"""
    customer = validate_customer_access()

    invoices = frappe.db.sql("""
        SELECT
            si.name as invoice_no,
            si.posting_date,
            si.due_date,
            si.grand_total,
            si.outstanding_amount,
            DATEDIFF(CURDATE(), si.due_date) as overdue_days
        FROM `tabSales Invoice` si
        WHERE si.customer = %s
        AND si.docstatus = 1
        AND si.outstanding_amount > 0
        ORDER BY si.posting_date DESC
    """, customer, as_dict=True)

    for inv in invoices:
        inv.posting_date = inv.posting_date.strftime("%d-%m-%Y")
        inv.due_date = inv.due_date.strftime("%d-%m-%Y")
        inv.overdue_days = max(0, inv.overdue_days or 0)

    total_outstanding = sum(flt(i.outstanding_amount) for i in invoices)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "invoices": invoices,
        "total_outstanding": total_outstanding
    }


@frappe.whitelist()
def get_payments(from_date, to_date):
    """Get payment history for the customer"""
    customer = validate_customer_access()

    payments = frappe.db.sql("""
        SELECT
            pe.name as payment_no,
            pe.posting_date,
            pe.paid_amount,
            pe.reference_no,
            pe.reference_date,
            pe.mode_of_payment
        FROM `tabPayment Entry` pe
        WHERE pe.party_type = 'Customer'
        AND pe.party = %s
        AND pe.docstatus = 1
        AND pe.posting_date >= %s
        AND pe.posting_date <= %s
        ORDER BY pe.posting_date DESC
    """, (customer, from_date, to_date), as_dict=True)

    for pay in payments:
        pay.posting_date = pay.posting_date.strftime("%d-%m-%Y")
        if pay.reference_date:
            pay.reference_date = pay.reference_date.strftime("%d-%m-%Y")

    total_paid = sum(flt(p.paid_amount) for p in payments)

    return {
        "customer": customer,
        "customer_name": frappe.db.get_value("Customer", customer, "customer_name"),
        "payments": payments,
        "total_paid": total_paid
    }


@frappe.whitelist()
def get_invoice_pdf(invoice_no):
    """Generate and return PDF for a sales invoice"""
    customer = validate_customer_access()

    # Verify this invoice belongs to the customer
    invoice_customer = frappe.db.get_value("Sales Invoice", invoice_no, "customer")
    if invoice_customer != customer:
        frappe.throw("You don't have access to this invoice", frappe.PermissionError)

    # Generate PDF
    from frappe.utils.pdf import get_pdf
    html = frappe.get_print("Sales Invoice", invoice_no)
    pdf = get_pdf(html)

    frappe.local.response.filename = "{}.pdf".format(invoice_no)
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "pdf"
