<script lang="ts">
	const stats = [
		{ label: 'Monthly Revenue', value: '₦2.4M', change: '+12.5%', up: true },
		{ label: 'Active Subscriptions', value: '1,247', change: '+8.2%', up: true },
		{ label: 'Churn Rate', value: '3.1%', change: '-0.4%', up: false },
		{ label: 'MRR', value: '₦200K', change: '+15.3%', up: true },
	];

	const recentInvoices = [
		{ id: 'INV-001', customer: 'ade@techcorp.ng', amount: '₦25,000', status: 'PAID', date: '2 hours ago' },
		{ id: 'INV-002', customer: 'chidi@dataflow.io', amount: '₦50,000', status: 'PENDING', date: '4 hours ago' },
		{ id: 'INV-003', customer: 'fatima@nexapay.com', amount: '₦12,500', status: 'PAID', date: '6 hours ago' },
		{ id: 'INV-004', customer: 'emeka@cloudsync.ng', amount: '₦75,000', status: 'FAILED', date: '1 day ago' },
		{ id: 'INV-005', customer: 'sara@vertexlabs.io', amount: '₦30,000', status: 'PAID', date: '1 day ago' },
	];
</script>

<svelte:head>
	<title>Overview — PayPulse</title>
</svelte:head>

<!-- Stats -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
	{#each stats as stat}
		<div class="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
			<p class="text-sm text-gray-500">{stat.label}</p>
			<p class="mt-2 text-2xl font-bold text-gray-900">{stat.value}</p>
			<p class="mt-1 text-xs font-medium {stat.up ? 'text-emerald-600' : 'text-red-500'}">
				{stat.change} from last month
			</p>
		</div>
	{/each}
</div>

<!-- Recent Invoices -->
<div class="bg-white rounded-xl border border-gray-100">
	<div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
		<h2 class="text-base font-semibold text-gray-900">Recent Invoices</h2>
		<a href="/dashboard/invoices" class="text-sm font-medium text-primary hover:text-primary-dark transition-colors">View All →</a>
	</div>
	<div class="overflow-x-auto">
		<table class="w-full text-sm">
			<thead>
				<tr class="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
					<th class="px-5 py-3">Invoice</th>
					<th class="px-5 py-3">Customer</th>
					<th class="px-5 py-3">Amount</th>
					<th class="px-5 py-3">Status</th>
					<th class="px-5 py-3">Time</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-gray-50">
				{#each recentInvoices as inv}
					<tr class="hover:bg-gray-50/50 transition-colors">
						<td class="px-5 py-3.5 font-medium text-gray-900">{inv.id}</td>
						<td class="px-5 py-3.5 text-gray-600">{inv.customer}</td>
						<td class="px-5 py-3.5 font-semibold text-gray-900">{inv.amount}</td>
						<td class="px-5 py-3.5">
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
								{inv.status === 'PAID' ? 'bg-emerald-50 text-emerald-700' :
								  inv.status === 'PENDING' ? 'bg-amber-50 text-amber-700' :
								  'bg-red-50 text-red-600'}">
								{inv.status}
							</span>
						</td>
						<td class="px-5 py-3.5 text-gray-400">{inv.date}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
