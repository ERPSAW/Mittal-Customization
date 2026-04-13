{% extends "templates/web.html" %}

{% block page_content %}
<style>
    .portal-container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 15px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .portal-header {
        border-bottom: 3px solid #C8902F;
        padding-bottom: 15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .portal-header img {
        width: 70px;
        object-fit: contain;
    }
    .portal-header-text h2 {
        margin: 0;
        font-size: 20px;
        font-weight: 700;
        color: #333;
    }
    .portal-header-text p {
        margin: 2px 0 0 0;
        font-size: 11px;
        color: #666;
        line-height: 1.5;
    }
    .customer-info {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .customer-info h3 {
        margin: 0;
        font-size: 16px;
        color: #333;
    }
    .customer-info .logout-btn {
        background: #dc3545;
        color: white;
        border: none;
        padding: 6px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 13px;
    }
    .portal-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 20px;
        border-bottom: 2px solid #e0e0e0;
    }
    .portal-tab {
        padding: 10px 24px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        color: #888;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s;
    }
    .portal-tab:hover {
        color: #555;
    }
    .portal-tab.active {
        color: #C8902F;
        border-bottom-color: #C8902F;
    }
    .tab-content {
        display: none;
    }
    .tab-content.active {
        display: block;
    }
    .filter-row {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }
    .filter-row label {
        font-size: 13px;
        font-weight: 600;
        color: #555;
    }
    .filter-row input[type="date"] {
        padding: 6px 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 13px;
    }
    .filter-row button {
        background: #C8902F;
        color: white;
        border: none;
        padding: 7px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 600;
    }
    .filter-row button:hover {
        background: #b07d28;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin-top: 10px;
    }
    .data-table thead th {
        background: #2c3e50;
        color: white;
        padding: 10px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }
    .data-table thead th.text-right {
        text-align: right;
    }
    .data-table tbody td {
        padding: 8px 12px;
        border-bottom: 1px solid #eee;
    }
    .data-table tbody tr:nth-child(even) {
        background: #f8f9fa;
    }
    .data-table tbody tr:hover {
        background: #e9ecef;
    }
    .text-right {
        text-align: right;
    }
    .text-center {
        text-align: center;
    }
    .total-row td {
        font-weight: 700;
        border-top: 2px solid #333;
        background: #f0f0f0 !important;
        padding: 10px 12px;
    }
    .opening-row td {
        font-weight: 600;
        background: #fff3cd !important;
        font-style: italic;
    }
    .closing-row td {
        font-weight: 700;
        background: #d4edda !important;
        border-top: 2px solid #333;
    }
    .summary-cards {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .summary-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px 20px;
        flex: 1;
        min-width: 200px;
    }
    .summary-card .label {
        font-size: 12px;
        color: #888;
        text-transform: uppercase;
        font-weight: 600;
    }
    .summary-card .value {
        font-size: 22px;
        font-weight: 700;
        color: #333;
        margin-top: 4px;
    }
    .summary-card.danger .value {
        color: #dc3545;
    }
    .summary-card.success .value {
        color: #28a745;
    }
    .overdue {
        color: #dc3545;
        font-weight: 600;
    }
    .loading {
        text-align: center;
        padding: 40px;
        color: #888;
        font-size: 14px;
    }
    .no-data {
        text-align: center;
        padding: 40px;
        color: #aaa;
        font-size: 14px;
    }
    .print-btn {
        background: #6c757d;
        color: white;
        border: none;
        padding: 7px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 12px;
        margin-left: 8px;
    }
    @media print {
        .portal-tabs, .filter-row, .logout-btn, .print-btn, .customer-info { display: none !important; }
        .tab-content { display: block !important; }
        .data-table { font-size: 11px; }
        @page { size: A4 portrait; margin: 10mm; }
    }
    @media (max-width: 768px) {
        .portal-header { flex-direction: column; text-align: center; }
        .filter-row { flex-direction: column; align-items: stretch; }
        .summary-cards { flex-direction: column; }
        .portal-tab { padding: 8px 14px; font-size: 12px; }
    }
</style>

<div class="portal-container">
    <!-- Header -->
    <div class="portal-header">
        <img src="/files/Mittal%20Logo.jpg" alt="Mittal">
        <div class="portal-header-text">
            <h2>Mittal Infocom Private Limited</h2>
            <p>
                Office No- 11 &amp; 12, 4th Floor, Suyog Platinum Tower,
                OFF. Mangaldas Road, Next to BMW BIKES, Bund Garden, Sangamvadi, Pune, 411001<br>
                Tel: (+91) 8888884335 &nbsp;|&nbsp; E-mail: accounts@mittalone.com &nbsp;|&nbsp; GSTIN: 27AAICM8474F1Z2
            </p>
        </div>
    </div>

    <!-- Customer Info -->
    <div class="customer-info">
        <h3>Welcome, {{ customer_name }}</h3>
        <button class="logout-btn" onclick="window.location.href='/api/method/logout'">Logout</button>
    </div>

    <!-- Tabs -->
    <div class="portal-tabs">
        <div class="portal-tab active" data-tab="ledger">Customer Ledger</div>
        <div class="portal-tab" data-tab="outstanding">Outstanding Invoices</div>
        <div class="portal-tab" data-tab="payments">Payment History</div>
    </div>

    <!-- Tab 1: Ledger -->
    <div class="tab-content active" id="tab-ledger">
        <div class="filter-row">
            <label>From:</label>
            <input type="date" id="ledger-from" value="">
            <label>To:</label>
            <input type="date" id="ledger-to" value="">
            <button onclick="loadLedger()">Load</button>
            <button class="print-btn" onclick="window.print()">Print</button>
        </div>
        <div id="ledger-summary"></div>
        <div id="ledger-data"><div class="no-data">Select date range and click Load</div></div>
    </div>

    <!-- Tab 2: Outstanding -->
    <div class="tab-content" id="tab-outstanding">
        <div class="filter-row">
            <button onclick="loadOutstanding()">Refresh</button>
            <button class="print-btn" onclick="window.print()">Print</button>
        </div>
        <div id="outstanding-summary"></div>
        <div id="outstanding-data"><div class="loading">Loading...</div></div>
    </div>

    <!-- Tab 3: Payments -->
    <div class="tab-content" id="tab-payments">
        <div class="filter-row">
            <label>From:</label>
            <input type="date" id="pay-from" value="">
            <label>To:</label>
            <input type="date" id="pay-to" value="">
            <button onclick="loadPayments()">Load</button>
            <button class="print-btn" onclick="window.print()">Print</button>
        </div>
        <div id="payments-summary"></div>
        <div id="payments-data"><div class="no-data">Select date range and click Load</div></div>
    </div>
</div>

<script>
    // Set default dates (current financial year)
    const today = new Date();
    const fyStart = today.getMonth() >= 3
        ? new Date(today.getFullYear(), 3, 1)
        : new Date(today.getFullYear() - 1, 3, 1);

    document.getElementById('ledger-from').value = formatDate(fyStart);
    document.getElementById('ledger-to').value = formatDate(today);
    document.getElementById('pay-from').value = formatDate(fyStart);
    document.getElementById('pay-to').value = formatDate(today);

    function formatDate(d) {
        return d.toISOString().split('T')[0];
    }

    function formatCurrency(val) {
        val = parseFloat(val) || 0;
        return '₹ ' + val.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    // Tab switching
    document.querySelectorAll('.portal-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.portal-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('tab-' + this.dataset.tab).classList.add('active');

            // Auto-load outstanding on first click
            if (this.dataset.tab === 'outstanding' && !this._loaded) {
                loadOutstanding();
                this._loaded = true;
            }
        });
    });

    // Load Ledger
    function loadLedger() {
        const from = document.getElementById('ledger-from').value;
        const to = document.getElementById('ledger-to').value;
        if (!from || !to) { alert('Please select both dates'); return; }

        document.getElementById('ledger-data').innerHTML = '<div class="loading">Loading ledger...</div>';

        frappe.call({
            method: 'mittal_customization.customer_portal_api.get_ledger',
            args: { from_date: from, to_date: to },
            callback: function (r) {
                if (r.message) renderLedger(r.message);
            },
            error: function () {
                document.getElementById('ledger-data').innerHTML = '<div class="no-data">Error loading data</div>';
            }
        });
    }

    function renderLedger(data) {
        // Summary cards
        document.getElementById('ledger-summary').innerHTML = `
            <div class="summary-cards">
                <div class="summary-card">
                    <div class="label">Opening Balance</div>
                    <div class="value">${formatCurrency(data.opening_balance)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Total Debit</div>
                    <div class="value">${formatCurrency(data.total_debit)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Total Credit</div>
                    <div class="value">${formatCurrency(data.total_credit)}</div>
                </div>
                <div class="summary-card ${data.closing_balance > 0 ? 'danger' : 'success'}">
                    <div class="label">Closing Balance</div>
                    <div class="value">${formatCurrency(Math.abs(data.closing_balance))} ${data.closing_balance > 0 ? 'Dr' : 'Cr'}</div>
                </div>
            </div>`;

        if (!data.entries.length) {
            document.getElementById('ledger-data').innerHTML = '<div class="no-data">No transactions found</div>';
            return;
        }

        let html = `<table class="data-table">
            <thead><tr>
                <th>#</th><th>Date</th><th>Particulars</th><th>Vch Type</th><th>Vch No.</th>
                <th class="text-right">Debit (₹)</th><th class="text-right">Credit (₹)</th><th class="text-right">Balance (₹)</th>
            </tr></thead><tbody>`;

        // Opening balance row
        html += `<tr class="opening-row">
            <td></td><td></td><td colspan="3">Opening Balance</td>
            <td class="text-right"></td><td class="text-right"></td>
            <td class="text-right">${formatCurrency(Math.abs(data.opening_balance))} ${data.opening_balance >= 0 ? 'Dr' : 'Cr'}</td>
        </tr>`;

        data.entries.forEach((e, i) => {
            html += `<tr>
                <td>${i + 1}</td>
                <td>${e.posting_date}</td>
                <td>${e.particulars}</td>
                <td>${e.voucher_type}</td>
                <td>${e.voucher_no}</td>
                <td class="text-right">${e.debit ? formatCurrency(e.debit) : ''}</td>
                <td class="text-right">${e.credit ? formatCurrency(e.credit) : ''}</td>
                <td class="text-right">${formatCurrency(Math.abs(e.balance))} ${e.balance >= 0 ? 'Dr' : 'Cr'}</td>
            </tr>`;
        });

        // Total row
        html += `<tr class="total-row">
            <td></td><td></td><td colspan="3">Total</td>
            <td class="text-right">${formatCurrency(data.total_debit)}</td>
            <td class="text-right">${formatCurrency(data.total_credit)}</td>
            <td class="text-right"></td>
        </tr>`;

        // Closing balance row
        html += `<tr class="closing-row">
            <td></td><td></td><td colspan="5">Closing Balance</td>
            <td class="text-right">${formatCurrency(Math.abs(data.closing_balance))} ${data.closing_balance >= 0 ? 'Dr' : 'Cr'}</td>
        </tr>`;

        html += '</tbody></table>';
        document.getElementById('ledger-data').innerHTML = html;
    }

    // Load Outstanding
    function loadOutstanding() {
        document.getElementById('outstanding-data').innerHTML = '<div class="loading">Loading outstanding invoices...</div>';

        frappe.call({
            method: 'mittal_customization.customer_portal_api.get_outstanding',
            callback: function (r) {
                if (r.message) renderOutstanding(r.message);
            },
            error: function () {
                document.getElementById('outstanding-data').innerHTML = '<div class="no-data">Error loading data</div>';
            }
        });
    }

    function renderOutstanding(data) {
        document.getElementById('outstanding-summary').innerHTML = `
            <div class="summary-cards">
                <div class="summary-card danger">
                    <div class="label">Total Outstanding</div>
                    <div class="value">${formatCurrency(data.total_outstanding)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Pending Invoices</div>
                    <div class="value">${data.invoices.length}</div>
                </div>
            </div>`;

        if (!data.invoices.length) {
            document.getElementById('outstanding-data').innerHTML = '<div class="no-data">No outstanding invoices! All clear.</div>';
            return;
        }

        let html = `<table class="data-table">
            <thead><tr>
                <th>#</th><th>Invoice No.</th><th>Invoice Date</th><th>Due Date</th>
                <th class="text-right">Invoice Amount (₹)</th><th class="text-right">Outstanding (₹)</th><th class="text-center">Overdue Days</th>
            </tr></thead><tbody>`;

        data.invoices.forEach((inv, i) => {
            const overdueClass = inv.overdue_days > 0 ? 'overdue' : '';
            html += `<tr>
                <td>${i + 1}</td>
                <td>${inv.invoice_no}</td>
                <td>${inv.posting_date}</td>
                <td>${inv.due_date}</td>
                <td class="text-right">${formatCurrency(inv.grand_total)}</td>
                <td class="text-right">${formatCurrency(inv.outstanding_amount)}</td>
                <td class="text-center ${overdueClass}">${inv.overdue_days > 0 ? inv.overdue_days + ' days' : 'Not due'}</td>
            </tr>`;
        });

        html += `<tr class="total-row">
            <td></td><td colspan="4">Total</td>
            <td class="text-right">${formatCurrency(data.total_outstanding)}</td>
            <td></td>
        </tr>`;

        html += '</tbody></table>';
        document.getElementById('outstanding-data').innerHTML = html;
    }

    // Load Payments
    function loadPayments() {
        const from = document.getElementById('pay-from').value;
        const to = document.getElementById('pay-to').value;
        if (!from || !to) { alert('Please select both dates'); return; }

        document.getElementById('payments-data').innerHTML = '<div class="loading">Loading payments...</div>';

        frappe.call({
            method: 'mittal_customization.customer_portal_api.get_payments',
            args: { from_date: from, to_date: to },
            callback: function (r) {
                if (r.message) renderPayments(r.message);
            },
            error: function () {
                document.getElementById('payments-data').innerHTML = '<div class="no-data">Error loading data</div>';
            }
        });
    }

    function renderPayments(data) {
        document.getElementById('payments-summary').innerHTML = `
            <div class="summary-cards">
                <div class="summary-card success">
                    <div class="label">Total Payments</div>
                    <div class="value">${formatCurrency(data.total_paid)}</div>
                </div>
                <div class="summary-card">
                    <div class="label">Number of Payments</div>
                    <div class="value">${data.payments.length}</div>
                </div>
            </div>`;

        if (!data.payments.length) {
            document.getElementById('payments-data').innerHTML = '<div class="no-data">No payments found in this period</div>';
            return;
        }

        let html = `<table class="data-table">
            <thead><tr>
                <th>#</th><th>Payment No.</th><th>Date</th><th>Mode</th>
                <th>Reference No.</th><th>Reference Date</th><th class="text-right">Amount (₹)</th>
            </tr></thead><tbody>`;

        data.payments.forEach((p, i) => {
            html += `<tr>
                <td>${i + 1}</td>
                <td>${p.payment_no}</td>
                <td>${p.posting_date}</td>
                <td>${p.mode_of_payment || '-'}</td>
                <td>${p.reference_no || '-'}</td>
                <td>${p.reference_date || '-'}</td>
                <td class="text-right">${formatCurrency(p.paid_amount)}</td>
            </tr>`;
        });

        html += `<tr class="total-row">
            <td></td><td colspan="5">Total</td>
            <td class="text-right">${formatCurrency(data.total_paid)}</td>
        </tr>`;

        html += '</tbody></table>';
        document.getElementById('payments-data').innerHTML = html;
    }
</script>
{% endblock %}
