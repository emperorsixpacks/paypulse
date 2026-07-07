<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, formatCurrency, formatInterval } from '$lib/format';

	let subs = $state<any[]>([]);
	let loading = $state(true);
	let filter = $state('');
	let canceling = $state<any>(null);
	let cancelAtPeriodEnd = $state(true);
	let cancelingResult = $state<any>(null);
	let showCancelResult = $state(false);

	async function load() {
		loading = true;
		subs = await api.listSubscriptions(filter || undefined);
		loading = false;
	}

	function openCancel(sub: any) {
		canceling = sub;
		cancelAtPeriodEnd = true;
		cancelingResult = null;
		showCancelResult = false;
	}

	async function doCancel() {
		if (!canceling) return;
		try {
			cancelingResult = await api.cancelSubscription(canceling.id, cancelAtPeriodEnd);
			showCancelResult = true;
			await load();
		} catch (e: any) {
			cancelingResult = { error: e.message };
			showCancelResult = true;
		}
	}

	function closeCancel() {
		canceling = null;
		cancelingResult = null;
		showCancelResult = false;
	}

	function applyFilter(f: string) {
		filter = f;
		load();
	}

	onMount(load);
</script>

<svelte:head><title>Subscriptions — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Subscriptions</h2>
</div>

<div class="flex items-center gap-2 mb-4">
	{#each ['ALL', 'ACTIVE', 'PAST_DUE', 'CANCELLED'] as f}
		<button
			onclick={() => applyFilter(f === 'ALL' ? '' : f)}
			class="h-7 px-3 rounded-full text-[12px] font-semibold transition-colors
				{(f === 'ALL' && !filter) || filter === f ? 'bg-cobalt text-white' : 'bg-white border border-hair text-slate hover:border-cobalt hover:text-cobalt'}"
		>
			{f.replace('_', ' ')}
		</button>
	{/each}
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading subscriptions...</p>
{:else if subs.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No subscriptions</p>
		<p class="text-[13px] text-slate">Subscriptions appear here when customers check out.</p>
	</div>
{:else}
	<div class="bg-white rounded-xl border border-hair overflow-hidden">
		<table class="w-full text-[13px]">
			<thead>
				<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Customer</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Plan</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Amount</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Interval</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Period ends</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]"></th>
				</tr>
			</thead>
			<tbody class="divide-y divide-hair/50">
				{#each subs as sub}
					{@const s = formatStatus(sub.status)}
					<tr class="hover:bg-paper transition-colors">
						<td class="px-5 py-3 text-ink">{sub.customer_email}</td>
						<td class="px-5 py-3 font-semibold text-ink">{sub.plan_name}</td>
						<td class="px-5 py-3 font-[family-name:var(--font-mono)]">{formatCurrency(sub.amount)}</td>
						<td class="px-5 py-3 text-slate">{formatInterval(sub.interval, 1)}</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
						</td>
						<td class="px-5 py-3 text-slate text-[12px]">{new Date(sub.current_period_end).toLocaleDateString()}</td>
						<td class="px-5 py-3 text-right">
							{#if sub.status === 'ACTIVE' || sub.status === 'PAST_DUE'}
								<button onclick={() => openCancel(sub)} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium">Cancel</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if canceling}
	<div class="fixed inset-0 bg-ink/40 flex items-center justify-center z-50" role="dialog" onclick={closeCancel}>
		<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-fade-in" onclick={(e) => e.stopPropagation()}>
			{#if showCancelResult && cancelingResult}
				<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-3">
					{cancelingResult.error ? 'Cancellation failed' : 'Subscription cancelled'}
				</h3>
				{#if cancelingResult.error}
					<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5">{cancelingResult.error}</p>
				{:else}
					<div class="space-y-2 text-[13px] text-slate mb-4">
						<p>Status: <span class="font-semibold text-ink">{cancelingResult.status}</span></p>
						{#if cancelingResult.refund}
							<p>Refund: <span class="font-semibold text-ink">{formatCurrency(cancelingResult.refund.refund_amount)}</span></p>
							<p>Reason: {cancelingResult.refund.reason}</p>
						{/if}
					</div>
				{/if}
				<button onclick={closeCancel} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors mt-4">Done</button>
			{:else}
				<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-3">Cancel subscription</h3>
				<p class="text-[13px] text-slate mb-4">
					Cancel subscription for <span class="font-semibold text-ink">{canceling.customer_email}</span>?
				</p>
				<label class="flex items-center gap-2 mb-4 cursor-pointer">
					<input type="checkbox" bind:checked={cancelAtPeriodEnd} class="accent-cobalt" />
					<span class="text-[13px] text-ink">Cancel at period end</span>
				</label>
				<div class="flex items-center justify-end gap-3">
					<button onclick={closeCancel} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Keep</button>
					<button onclick={doCancel} class="h-9 px-4 bg-badge-fail-text hover:opacity-90 text-white rounded-lg text-[13px] font-semibold transition-colors">Cancel subscription</button>
				</div>
			{/if}
		</div>
	</div>
{/if}
