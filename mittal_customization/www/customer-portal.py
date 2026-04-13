import frappe

no_cache = 1

def get_context(context):
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access Customer Portal", frappe.AuthenticationError)

    # Get customer linked to this user
    customer = get_customer_for_user(frappe.session.user)
    if not customer:
        frappe.throw("No customer account linked to your email. Please contact Mittal Infocom.", frappe.PermissionError)

    context.customer = customer
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
    context.show_sidebar = False
    context.no_breadcrumbs = True
    context.title = "Customer Portal - Mittal Infocom"

    return context


def get_customer_for_user(user):
    """Find the Customer linked to this user's email via Dynamic Link in Contact"""
    # Method 1: Check Contact → Dynamic Link
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

    # Method 2: Check if user email matches a Customer's name or primary contact
    customer = frappe.db.sql("""
        SELECT name FROM `tabCustomer`
        WHERE name = %s OR customer_name = %s
        LIMIT 1
    """, (user, user), as_dict=True)

    if customer:
        return customer[0].name

    return None
