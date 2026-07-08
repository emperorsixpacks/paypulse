<script lang="ts">
	import { api, setToken, setApiKey } from '$lib/api';
	import { goto } from '$app/navigation';

	let email = $state('');
	let businessName = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');

	async function register() {
		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}
		loading = true;
		error = '';
		try {
			const result = await api.register({ email, business_name: businessName, password });
			setToken(result.access_token);
			if (result.api_keys.length > 0) {
				setApiKey(result.api_keys[0].key);
			}
			goto('/dashboard');
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Create account — PayPulse</title></svelte:head>

<div class="min-h-screen bg-paper flex items-center justify-center px-4">
	<div class="w-full max-w-sm">
		<div class="text-center mb-8">
			<img src="/logo.svg" alt="PayPulse" class="h-10 mx-auto mb-4" />
			<h1 class="text-[22px] font-bold text-ink font-[family-name:var(--font-display)]">Create your account</h1>
			<p class="text-[13px] text-slate mt-1">Start billing in minutes.</p>
		</div>

		<div class="bg-white rounded-2xl border border-hair p-6">
			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}

			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Business name</label>
					<input
						type="text"
						bind:value={businessName}
						class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all"
						placeholder="Acme Inc"
					/>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Email</label>
					<input
						type="email"
						bind:value={email}
						class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all"
						placeholder="you@example.com"
					/>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Password</label>
					<input
						type="password"
						bind:value={password}
						class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all"
						placeholder="Min 8 characters"
					/>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Confirm password</label>
					<input
						type="password"
						bind:value={confirmPassword}
						class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all"
						placeholder="Repeat password"
						onkeydown={(e) => { if (e.key === 'Enter') register(); }}
					/>
				</div>
			</div>

			<button
				onclick={register}
				disabled={loading || !email || !password || !businessName || !confirmPassword}
				class="w-full h-11 mt-6 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[14px] font-semibold transition-colors disabled:opacity-50"
			>
				{loading ? 'Creating account...' : 'Create account'}
			</button>

			<p class="text-[13px] text-slate text-center mt-4">
				Already have an account?
				<a href="/login" class="text-cobalt hover:text-cobalt-dim font-medium">Sign in</a>
			</p>
		</div>
	</div>
</div>
