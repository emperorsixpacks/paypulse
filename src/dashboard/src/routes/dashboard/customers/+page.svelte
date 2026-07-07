<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, formatCurrency, formatInterval } from '$lib/format';

	let customers = $state<any[]>([]);
	let loading = $state(true);
	let selected = $state<any>(null);
	let detail = $state<any>(null);
	let detailTab = $state<'subscriptions' | 'invoices'>('subscriptions');

	async function load() {
		loading = true;
		customers = await api.listCustomers();
		loading = false;
	}

	async function selectCustomer(c: any) {
		selected = c;
		detail = null;
		detail = await api.getCustomer(c.id);
	}

	function goBack() {
		selected = null;
		detail = null;
	}

	onMount(load);
</script>

<svelte:head><title>Customers — PayPulse</title></svelte:head>

{#if !selected}
	<div class="flex items-center justify-between mb-6">
		<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Customers</h2>
	</div>

	{#if loading}
		<p class="text-[13px] text-slate py-12 text-center">Loading customers...</p>
	{:else if customers.length === 0}
		<div class="bg-white rounded-xl border border-hair p-12 text-center">
			<p class="text-[15px] font-medium text-ink mb-2">No customers yet</p>
			<p class="text-[13px] text-slate">Customers appear here once they complete a checkout.</p>
		</div>
	{:else}
		<div class="bg-white rounded-xl border border-hair overflow-hidden">
			<table class="w-full text-[13px]">
				<thead>
					<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
						<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Customer</th>
						<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Email</th>
						<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Nomba ID</th>
						<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Created</th>
						<th class="px-5 py-3 font-[family-name:var(--font-mono)]"></th>
					</tr>
				</thead>
				<tbody class="divide-y divide-hair/50">
					{#each customers as c}
						<tr class="hover:bg-paper transition-colors cursor-pointer" onclick={() => selectCustomer(c)}>
							<td class="px-5 py-3 font-semibold text-ink">{c.name || '—'}</td>
							<td class="px-5 py-3 text-slate">{c.email}</td>
							<td class="px-5 py-3 text-slate font-[family-name:var(--font-mono)] text-[12px]">{c.nomba_customer_id || '—'}</td>
							<td class="px-5 py-3 text-slate text-[12px]">{new Date(c.created_at).toLocaleDateString()}</td>
							<td class="px-5 py-3 text-right">
								<span class="text-cobalt text-[12px] font-medium">View →</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
{:else}
	<div class="flex items-center gap-3 mb-6">
		<button onclick={goBack} class="h-8 w-8 flex items-center justify-center rounded-lg bg-white border border-hair hover:bg-mist transition-colors">
			<svg class="h-4 w-4 text-ink" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" /></svg>
		</button>
		<div>
			<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">{detail?.customer?.name || detail?.customer?.email}</h2>
			<p class="text-[13px] text-slate">{detail?.customer?.email}</p>
		</div>
	</div>

	{#if !detail}
		<p class="text-[13px] text-slate py-8 text-center">Loading details...</p>
	{:else}
		<div class="flex gap-1 mb-6 border-b border-hair">
			<button
				onclick={() => detailTab = 'subscriptions'}
				class="px-4 py-2.5 text-[13px] font-medium transition-colors border-b-2 -mb-px
					{detailTab === 'subscriptions' ? 'text-cobalt border-cobalt' : 'text-slate border-transparent hover:text-ink'}"
			>
				Subscriptions ({detail.subscriptions.length})
			</button>
			<button
				onclick={() => detailTab = 'invoices'}
				class="px-4 py-2.5 text-[13px] font-medium transition-colors border-b-2 -mb-px
					{detailTab === 'invoices' ? 'text-cobalt border-cobalt' : 'text-slate border-transparent hover:text-ink'}"
			>
				Invoices ({detail.invoices.length})
			</button>
		</div>

		{#if detailTab === 'subscriptions'}
			{#if detail.subscriptions.length === 0}
				<p class="text-[13px] text-slate py-8 text-center">No subscriptions.</p>
			{:else}
				<div class="bg-white rounded-xl border border-hair overflow-hidden">
					<table class="w-full text-[13px]">
						<thead>
							<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Plan</th>
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Amount</th>
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Interval</th>
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-hair/50">
							{#each detail.subscriptions as sub}
								{@const s = formatStatus(sub.status)}
								<tr class="hover:bg-paper transition-colors">
									<td class="px-5 py-3 font-semibold text-ink">{sub.plan_name}</td>
									<td class="px-5 py-3 font-[family-name:var(--font-mono)]">{formatCurrency(sub.amount)}</td>
									<td class="px-5 py-3 text-slate">{formatInterval(sub.interval, 1)}</td>
									<td class="px-5 py-3">
										<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		{:else}
			{#if detail.invoices.length === 0}
				<p class="text-[13px] text-slate py-8 text-center">No invoices.</p>
			{:else}
				<div class="bg-white rounded-xl border border-hair overflow-hidden">
					<table class="w-full text-[13px]">
						<thead>
							<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Amount</th>
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
								<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Due</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-hair/50">
							{#each detail.invoices as inv}
								{@const s = formatStatus(inv.status)}
								<tr class="hover:bg-paper transition-colors">
									<td class="px-5 py-3 font-semibold text-ink font-[family-name:var(--font-mono)]">{formatCurrency(inv.amount)}</td>
									<td class="px-5 py-3">
										<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
									</td>
									<td class="px-5 py-3 text-slate">{new Date(inv.due_date).toLocaleDateString()}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		{/if}
	{/if}
{/if}
