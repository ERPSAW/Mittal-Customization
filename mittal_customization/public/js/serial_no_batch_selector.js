/* global erpnext */

class CustomSerialNoBatchBundleUpdate extends erpnext.SerialBatchPackageSelector {
	make() {
		let label = this.item?.has_serial_no ? __("Serial Nos") : __("Batch Nos");
		let primary_label = this.bundle ? __("Update") : __("Add");

		if (this.item?.has_serial_no && this.item?.has_batch_no) {
			label = __("Serial Nos / Batch Nos");
		}

		primary_label += " " + label;

		this.dialog = new frappe.ui.Dialog({
			title: this.item?.title || primary_label,
			size: "large",
			fields: this.get_dialog_fields(),
			primary_action_label: primary_label,
			primary_action: () => this.update_bundle_entries(),
			secondary_action_label: __("Edit Full Form"),
			secondary_action: () => this.edit_full_form(),
		});

		this.dialog.show();
		this.$scan_btn = this.dialog.$wrapper.find(".link-btn");
		this.$scan_btn.css("display", "inline");

		let qty = this.item.stock_qty || this.item.transfer_qty || this.item.qty;

		if (this.item?.is_rejected) {
			qty = this.item.rejected_qty;
		}

		qty = Math.abs(qty);
		if (qty == 1) {
			qty = 0;
		}
		if (qty > 0) {
			this.dialog.set_value("qty", qty).then(() => {
				if (this.item.serial_no && !this.item.serial_and_batch_bundle) {
					let serial_nos = this.item.serial_no.split("\n");
					if (serial_nos.length > 1) {
						serial_nos.forEach((serial_no) => {
							this.dialog.fields_dict.entries.df.data.push({
								serial_no: serial_no,
								batch_no: this.item.batch_no,
							});
						});
					} else {
						this.dialog.set_value("scan_serial_no", this.item.serial_no);
					}
					frappe.model.set_value(this.item.doctype, this.item.name, "serial_no", "");
				} else if (this.item.batch_no && !this.item.serial_and_batch_bundle) {
					this.dialog.set_value("scan_batch_no", this.item.batch_no);
					frappe.model.set_value(this.item.doctype, this.item.name, "batch_no", "");
				}

				this.dialog.fields_dict.entries.grid.refresh();
			});
		}
	}

	get_filter_fields() {
		this.item.qty = 0;
		return [
			{
				fieldtype: "Section Break",
				label: __("Auto Fetch"),
				hidden: 1,
			},
			{
				fieldtype: "Float",
				fieldname: "qty",
				label: __("Qty to Fetch"),
				default: 0,
				read_only: 1,
				onchange: () => this.get_auto_data(),
			},
			{
				fieldtype: "Column Break",
			},
			{
				fieldtype: "Select",
				options: ["FIFO", "LIFO", "Expiry"],
				default: "FIFO",
				fieldname: "based_on",
				label: __("Fetch Based On"),
				hidden: 1,
				onchange: () => this.get_auto_data(),
			},
			{
				fieldtype: "Section Break",
			},
		];
	}

	get_dialog_fields() {
		let fields = [];

		fields.push({
			fieldtype: "Link",
			fieldname: "warehouse",
			label: __("Warehouse"),
			options: "Warehouse",
			default: this.get_warehouse(),
			onchange: () => {
				if (this.item?.is_rejected) {
					this.item.rejected_warehouse = this.dialog.get_value("warehouse");
				} else {
					this.item.warehouse = this.dialog.get_value("warehouse");
				}

				this.get_auto_data();
			},
			get_query: () => {
				return {
					filters: {
						is_group: 0,
						company: this.frm.doc.company,
					},
				};
			},
		});

		if (this.frm.doc.doctype === "Stock Entry" && this.frm.doc.purpose === "Manufacture") {
			fields.push({
				fieldtype: "Column Break",
			});

			fields.push({
				fieldtype: "Link",
				fieldname: "work_order",
				label: __("For Work Order"),
				options: "Work Order",
				read_only: 1,
				default: this.frm.doc.work_order,
			});

			fields.push({
				fieldtype: "Section Break",
			});
		}

		fields.push({
			fieldtype: "Column Break",
		});

		if (this.item.has_serial_no) {
			fields.push({
				fieldtype: "Data",
				options: "Barcode",
				fieldname: "scan_serial_no",
				label: __("Scan Serial No"),
				get_query: () => {
					return {
						filters: this.get_serial_no_filters(),
					};
				},
				onchange: () => this.scan_barcode_data(),
			});
		}

		if (this.item.has_batch_no && !this.item.has_serial_no) {
			fields.push({
				fieldtype: "Data",
				options: "Barcode",
				fieldname: "scan_batch_no",
				label: __("Scan Batch No"),
				onchange: () => this.scan_barcode_data(),
			});
		}

		if (this.item?.type_of_transaction === "Outward") {
			fields = [...this.get_filter_fields(), ...fields];
		} else {
			fields = [...fields, ...this.get_attach_field()];
		}

		fields.push({
			fieldtype: "Section Break",
			depends_on: "eval:doc.enter_manually !== 1 || doc.entries?.length > 0",
		});

		fields.push({
			fieldname: "entries",
			fieldtype: "Table",
			cannot_add_rows: true, // Customization Code Add Line
			allow_bulk_edit: true,
			depends_on: "eval:doc.enter_manually !== 1 || doc.entries?.length > 0",
			data: [],
			fields: this.get_dialog_table_fields(),
		});

		return fields;
	}

	get_attach_field() {
		let me = this;
		let label = this.item?.has_serial_no ? __("Serial Nos") : __("Batch Nos");
		let primary_label = this.bundle ? __("Update") : __("Add");

		if (this.item?.has_serial_no && this.item?.has_batch_no) {
			label = __("Serial Nos / Batch Nos");
		}

		let fields = [];
		if (this.item.has_serial_no) {
			fields.push({
				fieldtype: "Check",
				label: __("Enter Manually"),
				fieldname: "enter_manually",
				default: 0, // Customization Code Line Change
				depends_on: "eval:doc.import_using_csv_file !== 1",
				change() {
					if (me.dialog.get_value("enter_manually")) {
						me.dialog.set_value("import_using_csv_file", 0);
					}
				},
			});
		}

		fields = [
			...fields,
			{
				fieldtype: "Check",
				label: __("Import Using CSV file"),
				fieldname: "import_using_csv_file",
				depends_on: "eval:doc.enter_manually !== 1",
				default: !this.item.has_serial_no ? 1 : 0,
				change() {
					if (me.dialog.get_value("import_using_csv_file")) {
						me.dialog.set_value("enter_manually", 0);
					}
				},
			},
			{
				fieldtype: "Section Break",
				depends_on: "eval:doc.import_using_csv_file === 1",
				label: __("{0} {1} via CSV File", [primary_label, label]),
			},
			{
				fieldtype: "Button",
				fieldname: "download_csv",
				label: __("Download CSV Template"),
				click: () => this.download_csv_file(),
			},
			{
				fieldtype: "Column Break",
			},
			{
				fieldtype: "Attach",
				fieldname: "attach_serial_batch_csv",
				label: __("Attach CSV File"),
				onchange: () => this.upload_csv_file(),
			},
		];

		if (this.item?.has_serial_no) {
			fields = [
				...fields,
				{
					fieldtype: "Section Break",
					label: __("{0} {1} Manually", [primary_label, label]),
					depends_on: "eval:doc.enter_manually === 1",
				},
				{
					fieldtype: "Data",
					label: __("Serial No Range"),
					fieldname: "serial_no_range",
					depends_on: "eval:doc.enter_manually === 1 && !doc.serial_no_series",
					description: __('"SN-01::10" for "SN-01" to "SN-10"'),
					onchange: () => {
						this.set_serial_nos_from_range();
					},
				},
			];
		}

		if (this.item?.has_serial_no) {
			fields = [
				...fields,
				{
					fieldtype: "Column Break",
					depends_on: "eval:doc.enter_manually === 1",
				},
				{
					fieldtype: "Small Text",
					label: __("Enter Serial Nos"),
					fieldname: "upload_serial_nos",
					depends_on: "eval:doc.enter_manually === 1",
					description: __("Enter each serial no in a new line"),
				},
			];
		}

		return fields;
	}

	get_dialog_table_fields() {
		let fields = [];
		let me = this;

		if (this.item.has_serial_no) {
			fields.push({
				fieldtype: "Link",
				options: "Serial No",
				fieldname: "serial_no",
				label: __("Serial No"),
				hidden: 1, // Customization Code Add Line
				in_list_view: 1,
				get_query: () => {
					return {
						filters: this.get_serial_no_filters(),
					};
				},
			});

			// Customization Code Add Two Field Custom Adding
			fields.push({
				fieldtype: "Data",
				fieldname: "custom_serial_no_id",
				label: __("Serial No"),
				in_list_view: 1,
			});
			fields.push({
				fieldtype: "Data",
				fieldname: "custom_imei_no_1",
				label: __("IMEI No 1"),
				in_list_view: 1,
			});
		}

		let batch_fields = [];
		if (this.item.has_batch_no) {
			batch_fields = [
				{
					fieldtype: "Link",
					options: "Batch",
					fieldname: "batch_no",
					label: __("Batch No"),
					in_list_view: 1,
					get_route_options_for_new_doc: () => {
						return {
							item: this.item.item_code,
						};
					},
					change() {
						let doc = this.doc;
						if (!doc.qty && me.item.type_of_transaction === "Outward") {
							me.get_batch_qty(doc.batch_no, (qty) => {
								doc.qty = qty;
								this.grid.set_value("qty", qty, doc);
							});
						}
					},
					get_query: () => {
						let is_inward = false;
						if (
							(["Purchase Receipt", "Purchase Invoice"].includes(
								this.frm.doc.doctype,
							) &&
								!this.frm.doc.is_return) ||
							(this.frm.doc.doctype === "Stock Entry" &&
								this.frm.doc.purpose === "Material Receipt")
						) {
							is_inward = true;
						}

						let include_expired_batches = me.include_expired_batches();

						return {
							query: "erpnext.controllers.queries.get_batch_no",
							filters: {
								item_code: this.item.item_code,
								warehouse:
									this.item.s_warehouse ||
									this.item.t_warehouse ||
									this.item.warehouse,
								is_inward: is_inward,
								include_expired_batches: include_expired_batches,
							},
						};
					},
				},
			];

			if (!this.item.has_serial_no) {
				batch_fields.push({
					fieldtype: "Float",
					fieldname: "qty",
					label: __("Quantity"),
					in_list_view: 1,
				});
			}
		}

		fields = [...fields, ...batch_fields];

		fields.push({
			fieldtype: "Data",
			fieldname: "name",
			label: __("Name"),
			hidden: 1,
		});

		return fields;
	}

	scan_barcode_data() {
		const { scan_serial_no, scan_batch_no } = this.dialog.get_values();

		this.dialog.set_value("enter_manually", 0);

		let fieldname = "";
		let party_name = "";

		if (this.frm.doc.is_return) {
			if (["Delivery Note", "Sales Invoice"].includes(this.frm.doc.doctype)) {
				fieldname = "customer";
				party_name = this.frm.doc.customer;
			} else if (["Purchase Invoice", "Purchase Receipt"].includes(this.frm.doc.doctype)) {
				fieldname = "supplier";
				party_name = this.frm.doc.supplier;
			}
		}

		if (scan_serial_no || scan_batch_no) {
			frappe.call({
				method: "erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle.is_serial_batch_no_exists",
				args: {
					item_code: this.item.item_code,
					type_of_transaction: this.item.type_of_transaction,
					serial_no: scan_serial_no,
					batch_no: scan_batch_no,
					warehouse: this.dialog.get_value("warehouse"), // Customization Code Add Line
					doctype: this.frm.doc.doctype,
					fieldname: fieldname,
					party_name: party_name,
				},
				callback: (r) => {
					this.update_serial_batch_no();
				},
			});
		}
	}

	// Customization Code Function Change Scan Serial No and IMEI No
	async update_serial_batch_no() {
		let { scan_serial_no, scan_batch_no } = this.dialog.get_values();
		let serial_no_actual = scan_serial_no;
		let custom_imei_no_1 = "";
		let custom_serial_no_id = "";

		if (scan_serial_no) {
			let response = await frappe.call({
				method: "mittal_customization.overrides.serial_and_batch_bundle.get_serial_no_from_imei_no",
				args: {
					imei_no: scan_serial_no,
				},
			});

			scan_serial_no = response.message.serial_no;
			custom_imei_no_1 = response.message.custom_imei_no_1;
			custom_serial_no_id = response.message.custom_serial_no_id;

			let existing_row = this.dialog.fields_dict.entries.df.data.filter((d) => {
				if (d.serial_no === scan_serial_no) {
					return d;
				}
			});

			if (existing_row?.length) {
				frappe.throw(__("Serial No {0} already exists", [serial_no_actual]));
			}

			if (!this.item.has_batch_no) {
				this.dialog.fields_dict.entries.df.data.push({
					serial_no: scan_serial_no,
					custom_serial_no_id: custom_serial_no_id,
					custom_imei_no_1: custom_imei_no_1,
				});

				this.dialog.fields_dict.scan_serial_no.set_value("");
			} else {
				frappe.call({
					method: "erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle.get_batch_no_from_serial_no",
					args: {
						serial_no: scan_serial_no,
					},
					callback: (r) => {
						this.dialog.fields_dict.entries.df.data.push({
							serial_no: scan_serial_no,
							batch_no: r.message,
						});

						this.dialog.fields_dict.scan_serial_no.set_value("");
						this.dialog.fields_dict.entries.grid.refresh();
					},
				});
			}
		} else if (scan_batch_no) {
			let existing_row = this.dialog.fields_dict.entries.df.data.filter((d) => {
				if (d.batch_no === scan_batch_no) {
					return d;
				}
			});

			if (existing_row?.length) {
				existing_row[0].qty += 1;
			} else {
				this.dialog.fields_dict.entries.df.data.push({
					batch_no: scan_batch_no,
					qty: 1,
				});
			}

			this.dialog.fields_dict.scan_batch_no.set_value("");
		}

		this.dialog.fields_dict.entries.grid.refresh();
	}

	render_data() {
		if (this.bundle || this.frm.doc.is_return) {
			frappe
				.call({
					method: "mittal_customization.overrides.serial_and_batch_bundle.get_serial_batch_ledgers",
					args: {
						item_code: this.item.item_code,
						name: this.bundle,
						voucher_no: !this.frm.is_new() ? this.item.parent : "",
						child_row: this.frm.doc.is_return ? this.item : "",
					},
				})
				.then((r) => {
					if (r.message) {
						this.set_data(r.message);
					}
				});
		}
	}
}

erpnext.SerialBatchPackageSelector = CustomSerialNoBatchBundleUpdate;
