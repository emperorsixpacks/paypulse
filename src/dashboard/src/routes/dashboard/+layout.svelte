<script lang="ts">
	import { page } from '$app/state';

	let { children } = $props();
	let sidebarOpen = $state(true);

	const navItems = [
		{ href: '/dashboard', label: 'Overview', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4' },
		{ href: '/dashboard/plans', label: 'Plans', icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
		{ href: '/dashboard/customers', label: 'Customers', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
		{ href: '/dashboard/subscriptions', label: 'Subscriptions', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' },
		{ href: '/dashboard/invoices', label: 'Invoices', icon: 'M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z' },
		{ href: '/dashboard/webhooks', label: 'Webhooks', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
		{ href: '/dashboard/settings', label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
	];
</script>

<div class="flex h-screen bg-surface">
	<!-- Sidebar -->
	<aside class="flex flex-col w-64 bg-sidebar text-white transition-all duration-300 {sidebarOpen ? '' : 'w-16'}">
		<!-- Logo -->
		<div class="flex items-center h-16 px-4 border-b border-white/10">
			<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary shrink-0">
				<svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
					<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
				</svg>
			</div>
			{#if sidebarOpen}
				<span class="ml-3 text-lg font-bold">PayPulse</span>
			{/if}
		</div>

		<!-- Nav -->
		<nav class="flex-1 py-4 space-y-1 px-2">
			{#each navItems as item}
				{@const active = page.url.pathname === item.href || (item.href !== '/dashboard' && page.url.pathname.startsWith(item.href))}
				<a
					href={item.href}
					class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
						{active ? 'bg-primary text-white' : 'text-gray-400 hover:bg-sidebar-hover hover:text-white'}"
				>
					<svg class="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d={item.icon} />
					</svg>
					{#if sidebarOpen}
						{item.label}
					{/if}
				</a>
			{/each}
		</nav>

		<!-- Toggle -->
		<div class="p-2 border-t border-white/10">
			<button
				onclick={() => sidebarOpen = !sidebarOpen}
				class="flex items-center justify-center w-full h-10 rounded-lg text-gray-400 hover:bg-sidebar-hover hover:text-white transition-colors"
			>
				<svg class="h-5 w-5 transition-transform {sidebarOpen ? '' : 'rotate-180'}" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
					<path stroke-linecap="round" stroke-linejoin="round" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
				</svg>
			</button>
		</div>
	</aside>

	<!-- Main -->
	<div class="flex-1 flex flex-col overflow-hidden">
		<!-- Top bar -->
		<header class="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-100">
			<h1 class="text-lg font-semibold text-gray-900">
				{navItems.find(n => page.url.pathname === n.href || (n.href !== '/dashboard' && page.url.pathname.startsWith(n.href)))?.label ?? 'Dashboard'}
			</h1>
			<div class="flex items-center gap-4">
				<button class="text-gray-400 hover:text-gray-600 transition-colors">
					<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
						<path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
					</svg>
				</button>
				<div class="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold text-primary">M</div>
			</div>
		</header>

		<!-- Content -->
		<main class="flex-1 overflow-y-auto p-6">
			<div class="animate-fade-in">
				{@render children()}
			</div>
		</main>
	</div>
</div>
