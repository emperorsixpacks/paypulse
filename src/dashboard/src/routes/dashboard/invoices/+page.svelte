<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, formatCurrency, timeAgo } from '$lib/format';

	let invoices = $state<any[]>([]);
	let loading = $state(true);

	onMount(async () => {
		loading = true;
		invoices = await api.listInvoices();
		loading = false;
	});
</script>

<svelte:head><title>Invoices — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Invoices</h2>
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading invoices...</p>
{:else if invoices.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No invoices yet</p>
		<p class="text-[13px] text-slate">Invoices are generated when subscriptions are billed.</p>
	</div>
{:else}
	<div class="bg-white rounded-xl border border-hair overflow-hidden">
		<table class="w-full text-[13px]">
			<thead>
				<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Invoice</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Customer</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Amount</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Refund</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Due</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Time</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-hair/50">
				{#each invoices as inv}
					{@const s = formatStatus(inv.status)}
					{@const rs = inv.refund_status ? formatStatus(inv.refund_status) : null}
					<tr class="hover:bg-paper transition-colors">
						<td class="px-5 py-3 font-medium text-ink font-[family-name:var(--font-mono)] text-[12px]">{inv.id.slice(0, 8)}…</td>
						<td class="px-5 py-3 text-slate">{inv.customer_email}</td>
						<td class="px-5 py-3 font-semibold text-ink font-[family-name:var(--font-mono)]">{formatCurrency(inv.amount)}</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
						</td>
						<td class="px-5 py-3">
							{#if inv.refund_amount > 0}
								<div class="flex items-center gap-1">
									<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold bg-badge-wait-bg text-badge-wait-text">
										{formatCurrency(inv.refund_amount)}
									</span>
									{#if rs}
										<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {rs.bgClass} {rs.textClass}">{rs.label}</span>
									{/if}
								</div>
							{:else}
								<span class="text-[12px] text-slate">—</span>
							{/if}
						</td>
						<td class="px-5 py-3 text-slate text-[12px]">{new Date(inv.due_date).toLocaleDateString()}</td>
						<td class="px-5 py-3 text-slate text-[12px]">{timeAgo(inv.created_at)}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}
