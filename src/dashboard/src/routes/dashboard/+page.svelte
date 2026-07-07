<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, formatCurrency, timeAgo } from '$lib/format';

	let stats = $state([
		{ label: 'MRR', value: '₦0', change: '' },
		{ label: 'Active subscriptions', value: '0', change: '' },
		{ label: 'Failed invoices', value: '0', change: '' },
		{ label: 'Cancelled this period', value: '0', change: '' },
	]);
	let failedInvoices = $state<any[]>([]);
	let recentInvoices = $state<any[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const [subs, invoices] = await Promise.all([
				api.listSubscriptions(),
				api.listInvoices(),
			]);

			const active = subs.filter((s: any) => s.status === 'ACTIVE');
			const mrr = active.reduce((sum: number, s: any) => sum + (s.amount || 0), 0);
			const cancelled = subs.filter((s: any) => s.status === 'CANCELLED' || s.status === 'EXPIRED');
			const failed = invoices.filter((i: any) => i.status === 'FAILED');

			stats = [
				{ label: 'MRR', value: formatCurrency(mrr), change: `${active.length} active` },
				{ label: 'Active subscriptions', value: String(active.length), change: `${subs.length} total` },
				{ label: 'Failed invoices', value: String(failed.length), change: failed.length > 0 ? 'Needs attention' : 'All clear' },
				{ label: 'Cancelled this period', value: String(cancelled.length), change: `${subs.length ? Math.round(cancelled.length / subs.length * 100) : 0}% churn` },
			];

			failedInvoices = failed.slice(0, 5);
			recentInvoices = invoices.slice(0, 8);
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head><title>Overview — PayPulse</title></svelte:head>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
	{#each stats as stat}
		<div class="bg-white rounded-xl border border-hair p-5">
			<p class="text-[13px] text-slate">{stat.label}</p>
			<p class="mt-1.5 text-[28px] font-bold text-ink font-[family-name:var(--font-display)] tracking-tight">{stat.value}</p>
			<p class="mt-1 text-[12px] text-slate font-[family-name:var(--font-mono)]">{stat.change}</p>
		</div>
	{/each}
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
	<div class="lg:col-span-1 bg-white rounded-xl border border-hair">
		<div class="px-5 py-4 border-b border-hair">
			<h2 class="text-[14px] font-semibold text-ink">Needs attention</h2>
		</div>
		{#if failedInvoices.length === 0}
			<div class="p-8 text-center">
				<p class="text-[13px] text-slate">No failed invoices. All clear.</p>
			</div>
		{:else}
			<div class="divide-y divide-hair">
			{#each failedInvoices as inv}
				{@const s = formatStatus('FAILED')}
				<div class="px-5 py-3.5 flex items-center justify-between">
					<div>
						<p class="text-[13px] font-medium text-ink font-[family-name:var(--font-mono)]">{inv.customer_email}</p>
						<p class="text-[12px] text-slate">{formatCurrency(inv.amount)} · {timeAgo(inv.created_at)}</p>
					</div>
					<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
				</div>
			{/each}
			</div>
		{/if}
	</div>

	<div class="lg:col-span-2 bg-white rounded-xl border border-hair">
		<div class="px-5 py-4 border-b border-hair flex items-center justify-between">
			<h2 class="text-[14px] font-semibold text-ink">Recent invoices</h2>
			<a href="/dashboard/invoices" class="text-[13px] font-medium text-cobalt hover:text-cobalt-dim transition-colors">View all →</a>
		</div>
		{#if recentInvoices.length === 0}
			<div class="p-8 text-center">
				<p class="text-[13px] text-slate">No invoices yet.</p>
			</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-[13px]">
					<thead>
						<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
							<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Invoice</th>
							<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Customer</th>
							<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Amount</th>
							<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
							<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Time</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-hair/50">
						{#each recentInvoices as inv}
							{@const s = formatStatus(inv.status)}
							<tr class="hover:bg-paper transition-colors">
								<td class="px-5 py-3 font-medium text-ink font-[family-name:var(--font-mono)] text-[12px]">{inv.id.slice(0, 8)}…</td>
								<td class="px-5 py-3 text-slate">{inv.customer_email}</td>
								<td class="px-5 py-3 font-semibold text-ink font-[family-name:var(--font-mono)]">{formatCurrency(inv.amount)}</td>
								<td class="px-5 py-3">
									<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
								</td>
								<td class="px-5 py-3 text-slate text-[12px]">{timeAgo(inv.created_at)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
