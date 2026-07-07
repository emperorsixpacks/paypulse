<script lang="ts">
	import { goto } from '$app/navigation';

	let email = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state('');

	async function handleLogin(e: Event) {
		e.preventDefault();
		loading = true;
		error = '';

		try {
			const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password }),
			});

			if (!res.ok) {
				const data = await res.json();
				error = data.detail || 'Invalid credentials';
				return;
			}

			const data = await res.json();
			localStorage.setItem('token', data.access_token);
			goto('/dashboard');
		} catch {
			error = 'Connection failed. Is the API running?';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login — PayPulse</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-surface px-4">
	<div class="w-full max-w-sm">
		<!-- Logo -->
		<div class="flex items-center justify-center gap-2 mb-8">
			<div class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary">
				<svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
					<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
				</svg>
			</div>
			<span class="text-2xl font-bold text-gray-900">PayPulse</span>
		</div>

		<div class="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm">
			<h1 class="text-xl font-bold text-gray-900 mb-1">Welcome back</h1>
			<p class="text-sm text-gray-500 mb-6">Sign in to your merchant dashboard</p>

			{#if error}
				<div class="mb-4 p-3 rounded-lg bg-red-50 text-sm text-red-600">{error}</div>
			{/if}

			<form onsubmit={handleLogin} class="space-y-4">
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						required
						class="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
						placeholder="you@company.com"
					/>
				</div>

				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						required
						class="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
						placeholder="••••••••"
					/>
				</div>

				<button
					type="submit"
					disabled={loading}
					class="w-full py-2.5 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{loading ? 'Signing in...' : 'Sign In'}
				</button>
			</form>
		</div>

		<p class="mt-6 text-center text-sm text-gray-500">
			Don't have an account? <a href="/register" class="font-medium text-primary hover:text-primary-dark">Create one</a>
		</p>
	</div>
</div>
