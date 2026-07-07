<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatCurrency } from '$lib/format';

	let policies = $state<any[]>([]);
	let loading = $state(true);
	let showForm = $state(false);
	let editing = $state<any>(null);
	let form = $state({ name: '', refund_type: 'none', refund_percentage: 0, refund_window_days: 0, prorate_refund: false, cancellation_fee: 0, apply_to_existing: true, is_default: false });
	let saving = $state(false);
	let error = $state('');

	async function load() {
		loading = true;
		policies = await api.listPolicies();
		loading = false;
	}

	function startCreate() {
		editing = null;
		form = { name: '', refund_type: 'none', refund_percentage: 0, refund_window_days: 0, prorate_refund: false, cancellation_fee: 0, apply_to_existing: true, is_default: false };
		showForm = true;
	}

	function startEdit(p: any) {
		editing = p;
		form = { name: p.name, refund_type: p.refund_type, refund_percentage: p.refund_percentage || 0, refund_window_days: p.refund_window_days, prorate_refund: p.prorate_refund, cancellation_fee: p.cancellation_fee, apply_to_existing: p.apply_to_existing, is_default: p.is_default };
		showForm = true;
	}

	async function save() {
		saving = true;
		error = '';
		try {
			if (editing) {
				await api.updatePolicy(editing.id, form);
			} else {
				await api.createPolicy(form);
			}
			showForm = false;
			await load();
		} catch (e: any) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	async function remove(id: string) {
		if (!confirm('Delete this policy?')) return;
		await api.deletePolicy(id);
		await load();
	}

	const refundTypes = [
		{ value: 'none', label: 'No refund' },
		{ value: 'full', label: 'Full refund' },
		{ value: 'percentage', label: 'Percentage' },
		{ value: 'prorate', label: 'Prorate' },
	];

	onMount(load);
</script>

<svelte:head><title>Cancellation Policies — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Cancellation policies</h2>
	<button onclick={startCreate} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
		+ New policy
	</button>
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading policies...</p>
{:else if policies.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No policies yet</p>
		<p class="text-[13px] text-slate mb-6">Create a cancellation policy to define refund rules.</p>
		<button onclick={startCreate} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
			Create policy
		</button>
	</div>
{:else}
	<div class="grid gap-4">
		{#each policies as p}
			<div class="bg-white rounded-xl border border-hair p-5">
				<div class="flex items-start justify-between">
					<div class="flex-1">
						<div class="flex items-center gap-2 mb-1">
							<h3 class="text-[15px] font-semibold text-ink">{p.name}</h3>
							{#if p.is_default}
								<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold bg-badge-ok-bg text-badge-ok-text">Default</span>
							{/if}
						</div>
						<div class="flex items-center gap-4 mt-2 text-[13px] text-slate">
							<span>Refund: <span class="font-medium text-ink capitalize">{p.refund_type}</span></span>
							{#if p.refund_percentage > 0}
								<span>({p.refund_percentage}%)</span>
							{/if}
							{#if p.cancellation_fee > 0}
								<span>Fee: <span class="font-medium text-ink">{formatCurrency(p.cancellation_fee)}</span></span>
							{/if}
							{#if p.refund_window_days > 0}
								<span>Window: <span class="font-medium text-ink">{p.refund_window_days}d</span></span>
							{/if}
							{#if p.prorate_refund}
								<span>Prorate refund</span>
							{/if}
						</div>
					</div>
					<div class="flex items-center gap-2 shrink-0 ml-4">
						<button onclick={() => startEdit(p)} class="text-cobalt hover:text-cobalt-dim text-[12px] font-medium">Edit</button>
						<button onclick={() => remove(p.id)} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium">Delete</button>
					</div>
				</div>
			</div>
		{/each}
	</div>
{/if}

{#if showForm}
	<div class="fixed inset-0 bg-ink/40 flex items-center justify-center z-50" role="dialog" onclick={() => showForm = false}>
		<div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 animate-fade-in max-h-[90vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
			<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-5">
				{editing ? 'Edit policy' : 'Create policy'}
			</h3>

			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}

			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Name</label>
					<input bind:value={form.name} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" placeholder="e.g. Standard policy" />
				</div>

				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Refund type</label>
					<div class="grid grid-cols-2 gap-2">
						{#each refundTypes as rt}
							<button
								type="button"
								onclick={() => form.refund_type = rt.value}
								class="h-10 px-3 rounded-lg border text-[13px] font-medium transition-colors
									{form.refund_type === rt.value ? 'border-cobalt bg-cobalt/5 text-cobalt' : 'border-hair bg-paper text-slate hover:border-cobalt/40'}"
							>
								{rt.label}
							</button>
						{/each}
					</div>
				</div>

				{#if form.refund_type === 'percentage'}
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Refund percentage</label>
						<input type="number" bind:value={form.refund_percentage} min="0" max="100" class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
				{/if}

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Refund window (days)</label>
						<input type="number" bind:value={form.refund_window_days} min="0" class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
					<div>
						<label class="block text-[12px] font-medium text-slate mb-1.5">Cancellation fee (NGN)</label>
						<input type="number" bind:value={form.cancellation_fee} min="0" class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
					</div>
				</div>

				<div class="flex items-center gap-6">
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="checkbox" bind:checked={form.prorate_refund} class="accent-cobalt" />
						<span class="text-[13px] text-ink">Prorate refund</span>
					</label>
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="checkbox" bind:checked={form.apply_to_existing} class="accent-cobalt" />
						<span class="text-[13px] text-ink">Apply to existing</span>
					</label>
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="checkbox" bind:checked={form.is_default} class="accent-cobalt" />
						<span class="text-[13px] text-ink">Default</span>
					</label>
				</div>
			</div>

			<div class="flex items-center justify-end gap-3 mt-6">
				<button onclick={() => showForm = false} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Cancel</button>
				<button onclick={save} disabled={saving || !form.name} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors disabled:opacity-50">
					{saving ? 'Saving...' : editing ? 'Update' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}
