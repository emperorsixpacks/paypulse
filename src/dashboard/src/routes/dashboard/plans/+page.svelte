<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, formatInterval, formatCurrency } from '$lib/format';

	let plans = $state<any[]>([]);
	let loading = $state(true);
	let showCreate = $state(false);
	let editingPlan = $state<any>(null);
	let form = $state({ name: '', amount: 0, currency: 'NGN', interval: 'MONTHLY', interval_count: 1, trial_period_days: 0 });
	let saving = $state(false);
	let error = $state('');

	async function load() {
		loading = true;
		plans = await api.listPlans();
		loading = false;
	}

	function startCreate() {
		editingPlan = null;
		form = { name: '', amount: 0, currency: 'NGN', interval: 'MONTHLY', interval_count: 1, trial_period_days: 0 };
		showCreate = true;
	}

	function startEdit(p: any) {
		editingPlan = p;
		form = { name: p.name, amount: p.amount, currency: p.currency, interval: p.interval, interval_count: p.interval_count, trial_period_days: p.trial_period_days || 0 };
		showCreate = true;
	}

	async function save() {
		saving = true;
		error = '';
		try {
			if (editingPlan) {
				await api.updatePlan(editingPlan.id, form);
			} else {
				await api.createPlan(form);
			}
			showCreate = false;
			await load();
		} catch (e: any) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	async function remove(id: string) {
		if (!confirm('Delete this plan?')) return;
		await api.deletePlan(id);
		await load();
	}

	onMount(load);
</script>

<svelte:head><title>Plans — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Plans</h2>
	<button onclick={startCreate} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
		+ New plan
	</button>
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading plans...</p>
{:else if plans.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No plans yet</p>
		<p class="text-[13px] text-slate mb-6">Create your first plan to start accepting subscriptions.</p>
		<button onclick={startCreate} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
			Create plan
		</button>
	</div>
{:else}
	<div class="bg-white rounded-xl border border-hair overflow-hidden">
		<table class="w-full text-[13px]">
			<thead>
				<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Name</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Price</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Interval</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Trial</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Actions</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-hair/50">
				{#each plans as plan}
					{@const s = formatStatus(plan.is_active ? 'ACTIVE' : 'CANCELLED')}
					<tr class="hover:bg-paper transition-colors">
						<td class="px-5 py-3 font-semibold text-ink">{plan.name}</td>
						<td class="px-5 py-3 font-semibold text-ink font-[family-name:var(--font-mono)]">
							{formatCurrency(plan.amount)} <span class="text-slate text-[11px]">/ {plan.currency}</span>
						</td>
						<td class="px-5 py-3 text-slate">{formatInterval(plan.interval, plan.interval_count)}</td>
						<td class="px-5 py-3 text-slate">{plan.trial_period_days || '—'}d</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
						</td>
						<td class="px-5 py-3">
							<div class="flex items-center gap-2">
								<button onclick={() => startEdit(plan)} class="text-cobalt hover:text-cobalt-dim text-[12px] font-medium">Edit</button>
								<button onclick={() => remove(plan.id)} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium">Delete</button>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if showCreate}
	<div class="fixed inset-0 bg-ink/40 flex items-center justify-center z-50" role="dialog" onclick={() => showCreate = false}>
		<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-fade-in" onclick={(e) => e.stopPropagation()}>
			<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-5">
				{editingPlan ? 'Edit plan' : 'Create plan'}
			</h3>
			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}
			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Name</label>
					<input bind:value={form.name} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" placeholder="e.g. Pro Plan" />
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Amount (NGN)</label>
						<input type="number" bind:value={form.amount} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Interval</label>
						<select bind:value={form.interval} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all">
							<option value="DAILY">Daily</option>
							<option value="WEEKLY">Weekly</option>
							<option value="MONTHLY">Monthly</option>
							<option value="QUARTERLY">Quarterly</option>
							<option value="ANNUALLY">Annually</option>
						</select>
					</div>
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Interval count</label>
						<input type="number" bind:value={form.interval_count} min="1" class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Trial days</label>
						<input type="number" bind:value={form.trial_period_days} min="0" class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
				</div>
			</div>
			<div class="flex items-center justify-end gap-3 mt-6">
				<button onclick={() => showCreate = false} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Cancel</button>
				<button onclick={save} disabled={saving} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors disabled:opacity-50">
					{saving ? 'Saving...' : editingPlan ? 'Update' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}
