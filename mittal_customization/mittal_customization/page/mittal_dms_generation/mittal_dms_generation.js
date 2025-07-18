frappe.pages['mittal-dms-generation'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Mittal DMS Generation',
		single_column: true
	});

	let filters = {
		from_date: null,
		to_date: null,
		type: null
	};

	this.page = page;

	this.form = new frappe.ui.FieldGroup({
		fields: [
			{
                fieldtype: 'Date',
                label: 'From Date',
                fieldname: 'from_date',
                onchange: function() {
                    filters.from_date = this.value;
                }
            },
			{
                fieldtype: 'Column Break',
            },
			{
				fieldtype: 'Date',
				label: 'To Date',
				fieldname: 'to_date',
				onchange: function() {
					filters.to_date = this.value;
				}
			},
			{
                fieldtype: 'Column Break',
            },
			{
				fieldtype: 'Select',
				label: 'Type',
				fieldname: 'type',
				options: ['ISL', 'OSL'],
				onchange: function() {
					filters.type = this.value;
				}
			}
		],
		body: this.page.body,
	});

	this.form.make();

	// ➕ Add button to download filters as .txt file
	page.add_download_button = function () {
		page.add_button('Download Text File', () => {
			if (!filters.from_date || !filters.to_date || !filters.type) {
				frappe.msgprint('Please select all filters.');
				return;
			}

			frappe.call({
				method: 'mittal_customization.mittal_customization.page.mittal_dms_generation.mittal_dms_generation.download_text_file',
				args: {
					filters: filters
				},
				callback: function (r) {
					if (r.message) {
						const content = r.message.content;
						const file_name = r.message.file_name;

						// Create a .txt file and trigger download
						const blob = new Blob([content], { type: 'text/plain' });
						const url = URL.createObjectURL(blob);
						const a = document.createElement('a');
						a.href = url;
						a.download = `${file_name}.txt`;
						document.body.appendChild(a);
						a.click();
						document.body.removeChild(a);
						URL.revokeObjectURL(url);
					}
				}
			});
		});
	};


	page.add_download_button();
};