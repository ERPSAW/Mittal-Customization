import json
from datetime import datetime

import frappe
from frappe import _
from frappe.utils import getdate, now


class MitallDmsGeneration:
	def __init__(self):
		self.dms_settings = frappe.get_doc("DMS Settings", "DMS Settings")
		self.now_datetime = datetime.strptime(now(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y%m%d%H%M%S")
		self.now_date = datetime.strptime(now(), "%Y-%m-%d %H:%M:%S.%f").strftime("%Y%m%d")
		self.small_now_date = datetime.strptime(now(), "%Y-%m-%d %H:%M:%S.%f").strftime("%y%m%d")
		self.dms_settings.unique_identifier = self.increment_serial_code(self.dms_settings.unique_identifier)

	def execute(self, filters):
		if filters.type == "ISL":
			return self.generate_isl_file(filters)
		elif filters.type == "OSL":
			return self.generate_osl_file(filters)

	def generate_isl_file(self, filters):
		query = f"""
            SELECT
                "DTL" AS record_type,
                sbb.item_code,
                IFNULL(sbe.custom_imei_no_1, '') AS custom_imei_no_1,
                IFNULL(sbe.custom_imei_no_2, '') AS custom_imei_no_2,
                IFNULL(sbe.custom_serial_no_id, '') AS custom_serial_no_id,
                '{self.dms_settings.point_of_entry}' AS point_of_entry,
                IFNULL(pi.bill_date, '') AS inward_order_date,
                IFNULL(pi.bill_date, '') AS inward_receipt_date,
                IFNULL(pi.bill_no, '') AS invoice_invoice_no,
                IFNULL(pi.bill_date, '') AS inward_invoice_date
            FROM
                `tabSerial and Batch Entry` AS sbe
            LEFT JOIN
                `tabSerial and Batch Bundle` AS sbb ON sbb.name = sbe.parent
            LEFT JOIN
                `tabPurchase Invoice` AS pi ON sbb.voucher_type = 'Purchase Invoice' AND sbb.voucher_no = pi.name
            LEFT JOIN
                `tabItem` AS it ON sbb.item_code = it.name
            WHERE
                sbb.docstatus = 1
                AND it.custom_include_in_dms = 1
                AND sbb.type_of_transaction = 'Inward'
                AND sbb.voucher_type = 'Purchase Invoice'
                AND pi.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
            ORDER BY
                (pi.bill_date or pi.posting_date) ASC
        """

		result = frappe.db.sql(query, as_dict=1)

		if not result:
			frappe.throw(_("No data found"))

		if result:
			txt_details = self.generate_header(filters)

			for res in result:
				txt_details += "\n"

				txt_details += "\t".join(
					[
						res.record_type,
						res.item_code,
						res.custom_imei_no_1,
						res.custom_imei_no_2,
						res.custom_serial_no_id[len(self.dms_settings.serial_no_starts) :]
						if res.custom_serial_no_id.startswith(self.dms_settings.serial_no_starts)
						else res.custom_serial_no_id,
						res.point_of_entry,
						getdate(res.inward_order_date).strftime("%Y%m%d"),
						getdate(res.inward_receipt_date).strftime("%Y%m%d"),
						res.invoice_invoice_no,
						getdate(res.inward_invoice_date).strftime("%Y%m%d"),
					]
				)

			frappe.db.set_single_value(
				"DMS Settings", "unique_identifier", self.dms_settings.unique_identifier
			)
			return {
				"content": txt_details,
				"file_name": f"{self.dms_settings.senders_id}_{self.dms_settings.region}_{filters.type}_{self.small_now_date}{self.dms_settings.unique_identifier[-2:]}",
			}

	def generate_osl_file(self, filters):
		query = f"""
            SELECT
                "DTL" AS record_type,
                sbb.item_code,
                IFNULL(sbe.custom_imei_no_1, '') AS custom_imei_no_1,
                IFNULL(sbe.custom_imei_no_2, '') AS custom_imei_no_2,
                IFNULL(sbe.custom_serial_no_id, '') AS custom_serial_no_id,
                si.posting_date AS outward_order_date,
                si.posting_date AS outward_shipping_date,
                '' as partner_hq_id,
                si.name AS outward_invoice_no,
                si.posting_date AS outward_invoice_date,
                '' as pos_apple_id,
                IFNULL(c.custom_apple_id, '9') as sold_to_pos_apple_id,
                si.name as po_no,
                '' as tin_number
            FROM
                `tabSerial and Batch Entry` AS sbe
            LEFT JOIN
                `tabSerial and Batch Bundle` AS sbb ON sbb.name = sbe.parent
            LEFT JOIN
                `tabSales Invoice` AS si ON sbb.voucher_type = 'Sales Invoice' AND sbb.voucher_no = si.name
            LEFT JOIN
                `tabItem` AS it ON sbb.item_code = it.name
            LEFT JOIN
                `tabCustomer` AS c ON si.customer = c.name
            WHERE
                sbb.docstatus = 1
                AND it.custom_include_in_dms = 1
                AND sbb.type_of_transaction = 'Outward'
                AND sbb.voucher_type = 'Sales Invoice'
                AND si.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
            ORDER BY
                si.posting_date ASC, sbe.creation ASC
        """

		result = frappe.db.sql(query, as_dict=1)

		if not result:
			frappe.throw(_("No data found"))

		if result:
			txt_details = self.generate_header(filters)

			for res in result:
				txt_details += "\n"

				txt_details += "\t".join(
					[
						res.record_type,
						res.item_code,
						res.custom_imei_no_1,
						res.custom_imei_no_2,
						res.custom_serial_no_id[len(self.dms_settings.serial_no_starts) :]
						if res.custom_serial_no_id.startswith(self.dms_settings.serial_no_starts)
						else res.custom_serial_no_id,
						getdate(res.outward_order_date).strftime("%Y%m%d"),
						getdate(res.outward_shipping_date).strftime("%Y%m%d"),
						res.partner_hq_id,
						res.outward_invoice_no,
						getdate(res.outward_invoice_date).strftime("%Y%m%d"),
						res.pos_apple_id,
						res.sold_to_pos_apple_id,
						res.po_no,
						res.tin_number,
					]
				)

			frappe.db.set_single_value(
				"DMS Settings", "unique_identifier", self.dms_settings.unique_identifier
			)
			return {
				"content": txt_details,
				"file_name": f"{self.dms_settings.senders_id}_{self.dms_settings.region}_{filters.type}_{self.small_now_date}{self.dms_settings.unique_identifier[-2:]}",
			}

	def generate_header(self, filters):
		txt_details = "\t".join(
			[
				"CTRL",
				self.dms_settings.senders_id,
				self.dms_settings.receiver_id,
				filters.type,
				self.dms_settings.unique_identifier,
				self.now_datetime,
				self.dms_settings.sender_name,
				self.dms_settings.country_code,
				self.dms_settings.source_encoding_type,
			]
		)

		txt_details += "\n"
		txt_details += "\t".join(
			["HDR", self.now_date, self.dms_settings.senders_id, self.dms_settings.partner_type]
		)

		return txt_details

	def increment_serial_code(self, code: str) -> str:
		date_part = code[:8]
		serial_part = code[8:]

		if date_part != self.now_date:
			return f"{self.now_date}00000001"

		serial_number = int(serial_part) + 1
		updated_serial = f"{serial_number:0{len(serial_part)}d}"
		return f"{date_part}{updated_serial}"


@frappe.whitelist()
def download_text_file(filters):
	filters = frappe._dict(json.loads(filters))
	return MitallDmsGeneration().execute(filters)
