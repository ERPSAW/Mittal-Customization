import frappe

no_cache = 1

def get_context(context):
    context.show_sidebar = False
    context.no_breadcrumbs = True
    context.title = "Retailer Portal - Mittal Infocom"

    if frappe.session.user == "Guest":
        context.is_guest = True
        context.customer = None
        context.customer_name = None
        return context

    customer = get_customer_for_user(frappe.session.user)

    if not customer:
        context.is_guest = False
        context.no_customer = True
        context.customer = None
        context.customer_name = None
        return context

    context.is_guest = False
    context.no_customer = False
    context.customer = customer
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")

    return context


def get_customer_for_user(user):
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
