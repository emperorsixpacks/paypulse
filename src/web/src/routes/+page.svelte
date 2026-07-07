<script lang="ts">
	let scrolled = $state(false);

	function handleScroll() {
		scrolled = window.scrollY > 20;
	}

	const features = [
		{
			icon: '⚡',
			title: 'Automated Billing',
			description: 'Recurring invoices, proration, and dunning handled automatically. Never miss a payment again.'
		},
		{
			icon: '📊',
			title: 'Usage-Based Pricing',
			description: 'Metered billing with real-time usage tracking. Charge per API call, per seat, or per unit.'
		},
		{
			icon: '🔒',
			title: 'Secure Payments',
			description: 'PCI-compliant checkout with Nomba integration. Tokenized cards and encrypted transactions.'
		},
		{
			icon: '🔄',
			title: 'Smart Dunning',
			description: 'Automated retry schedules that recover failed payments. Exponential backoff with merchant controls.'
		},
		{
			icon: '🔔',
			title: 'Webhook Events',
			description: 'Real-time event delivery with HMAC signatures. Track every subscription lifecycle event.'
		},
		{
			icon: '💰',
			title: 'Revenue Recovery',
			description: 'Cancellation policies with smart refunds. Reduce churn with configurable retention tools.'
		}
	];

	const logos = [
		'TechCorp', 'DataFlow', 'CloudSync', 'NexaPay', 'QuantumAI', 'VertexLabs'
	];
</script>

<svelte:window onscroll={handleScroll} />

<div class="min-h-screen bg-white">
	<!-- Navbar -->
	<header class="fixed top-0 left-0 right-0 z-50 transition-all duration-300 {scrolled ? 'nav-scrolled' : ''}">
		<nav class="mx-auto max-w-7xl px-6 lg:px-8">
			<div class="flex h-18 items-center justify-between">
				<div class="flex items-center gap-2">
					<div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
						<svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
						</svg>
					</div>
					<span class="text-xl font-bold text-gray-900">PayPulse</span>
				</div>

				<div class="hidden md:flex items-center gap-8">
					<a href="#features" class="text-sm font-medium text-gray-600 hover:text-primary transition-colors">Features</a>
					<a href="#pricing" class="text-sm font-medium text-gray-600 hover:text-primary transition-colors">Pricing</a>
					<a href="#docs" class="text-sm font-medium text-gray-600 hover:text-primary transition-colors">Docs</a>
					<a href="#contact" class="text-sm font-medium text-gray-600 hover:text-primary transition-colors">Contact</a>
				</div>

				<div class="flex items-center gap-3">
					<a href="/login" class="text-sm font-medium text-gray-700 hover:text-primary transition-colors px-4 py-2">Log In</a>
					<a href="/register" class="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-white hover:bg-primary-dark transition-all hover:shadow-lg hover:shadow-primary/20">Get Started</a>
				</div>
			</div>
		</nav>
	</header>

	<!-- Hero -->
	<section class="relative pt-32 pb-20 lg:pt-40 lg:pb-28 hero-gradient overflow-hidden">
		<!-- Decorative blobs -->
		<div class="absolute top-20 left-10 h-72 w-72 rounded-full bg-primary/5 blur-3xl animate-float"></div>
		<div class="absolute bottom-10 right-10 h-96 w-96 rounded-full bg-primary-light/5 blur-3xl animate-float-delay"></div>

		<div class="mx-auto max-w-7xl px-6 lg:px-8 relative">
			<div class="text-center max-w-4xl mx-auto">
				<!-- Badge -->
				<div class="animate-fade-up inline-flex items-center gap-2 rounded-full border border-primary/20 bg-surface-alt px-4 py-1.5 mb-8">
					<span class="h-2 w-2 rounded-full bg-primary animate-pulse-glow"></span>
					<span class="text-sm font-medium text-primary">Now in Early Access</span>
				</div>

				<!-- Headline -->
				<h1 class="animate-fade-up-delay-1 text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-gray-900 leading-[1.1]">
					All Your
					<span class="gradient-text"> Subscription Billing</span>
					<br />In One Platform
				</h1>

				<!-- Subtitle -->
				<p class="animate-fade-up-delay-2 mt-6 text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
					Streamline revenue operations with automated billing, smart dunning,
					usage tracking, and flexible cancellation policies — all in one powerful API.
				</p>

				<!-- CTAs -->
				<div class="animate-fade-up-delay-3 mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
					<a href="/register" class="rounded-full bg-primary px-8 py-3.5 text-base font-semibold text-white hover:bg-primary-dark transition-all hover:shadow-xl hover:shadow-primary/25 hover:-translate-y-0.5">
						Start Free Trial
					</a>
					<a href="#docs" class="rounded-full border border-gray-300 bg-white px-8 py-3.5 text-base font-semibold text-gray-700 hover:border-primary/30 hover:text-primary transition-all">
						Read the Docs →
					</a>
				</div>

				<!-- Social proof -->
				<p class="animate-fade-in mt-8 text-sm text-gray-400">No credit card required · Free for up to 50 customers</p>
			</div>
		</div>
	</section>

	<!-- Logos -->
	<section class="py-12 border-y border-gray-100">
		<div class="mx-auto max-w-7xl px-6 lg:px-8">
			<p class="text-center text-xs font-semibold uppercase tracking-widest text-gray-400 mb-8">Trusted by innovative companies</p>
			<div class="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
				{#each logos as name}
					<span class="text-lg font-bold text-gray-300 select-none">{name}</span>
				{/each}
			</div>
		</div>
	</section>

	<!-- Features -->
	<section id="features" class="py-20 lg:py-28">
		<div class="mx-auto max-w-7xl px-6 lg:px-8">
			<div class="text-center max-w-2xl mx-auto mb-16">
				<h2 class="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
					Everything You Need to
					<span class="gradient-text"> Scale Revenue</span>
				</h2>
				<p class="mt-4 text-lg text-gray-500">
					From subscription creation to cancellation — every tool you need to manage the full customer lifecycle.
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each features as feature, i}
					<div class="card-hover group rounded-2xl border border-gray-100 bg-white p-8 hover:border-primary/20">
						<div class="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-alt text-2xl mb-5 group-hover:scale-110 transition-transform">
							{feature.icon}
						</div>
						<h3 class="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
						<p class="text-sm text-gray-500 leading-relaxed">{feature.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- Stats Banner -->
	<section class="py-16 bg-surface-alt">
		<div class="mx-auto max-w-7xl px-6 lg:px-8">
			<div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
				<div>
					<div class="text-3xl sm:text-4xl font-extrabold text-primary">99.9%</div>
					<div class="mt-1 text-sm text-gray-500">Uptime SLA</div>
				</div>
				<div>
					<div class="text-3xl sm:text-4xl font-extrabold text-primary">50ms</div>
					<div class="mt-1 text-sm text-gray-500">Avg Response</div>
				</div>
				<div>
					<div class="text-3xl sm:text-4xl font-extrabold text-primary">25+</div>
					<div class="mt-1 text-sm text-gray-500">API Endpoints</div>
				</div>
				<div>
					<div class="text-3xl sm:text-4xl font-extrabold text-primary">$0</div>
					<div class="mt-1 text-sm text-gray-500">Setup Fees</div>
				</div>
			</div>
		</div>
	</section>

	<!-- CTA -->
	<section class="py-20 lg:py-28">
		<div class="mx-auto max-w-7xl px-6 lg:px-8">
			<div class="relative rounded-3xl bg-primary overflow-hidden p-12 lg:p-16 text-center">
				<div class="absolute top-0 right-0 h-64 w-64 rounded-full bg-white/10 blur-3xl -translate-y-1/2 translate-x-1/2"></div>
				<div class="absolute bottom-0 left-0 h-48 w-48 rounded-full bg-white/5 blur-2xl translate-y-1/2 -translate-x-1/2"></div>

				<div class="relative">
					<h2 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
						Ready to Transform Your Billing?
					</h2>
					<p class="mt-4 text-lg text-white/80 max-w-xl mx-auto">
						Join hundreds of businesses automating their subscription revenue. Start free, scale as you grow.
					</p>
					<div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
						<a href="/register" class="rounded-full bg-white px-8 py-3.5 text-base font-semibold text-primary hover:bg-white/90 transition-all hover:shadow-xl hover:-translate-y-0.5">
							Create Free Account
						</a>
						<a href="#contact" class="rounded-full border border-white/30 px-8 py-3.5 text-base font-semibold text-white hover:bg-white/10 transition-all">
							Talk to Sales
						</a>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="border-t border-gray-100 py-12">
		<div class="mx-auto max-w-7xl px-6 lg:px-8">
			<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
				<div>
					<div class="flex items-center gap-2 mb-4">
						<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
							<svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
								<path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
						</div>
						<span class="text-lg font-bold text-gray-900">PayPulse</span>
					</div>
					<p class="text-sm text-gray-500 leading-relaxed">Subscription billing and revenue operations for modern businesses.</p>
				</div>

				<div>
					<h4 class="text-sm font-semibold text-gray-900 mb-4">Product</h4>
					<ul class="space-y-2.5">
						<li><a href="#features" class="text-sm text-gray-500 hover:text-primary transition-colors">Features</a></li>
						<li><a href="#pricing" class="text-sm text-gray-500 hover:text-primary transition-colors">Pricing</a></li>
						<li><a href="#docs" class="text-sm text-gray-500 hover:text-primary transition-colors">API Docs</a></li>
						<li><a href="/status" class="text-sm text-gray-500 hover:text-primary transition-colors">Status</a></li>
					</ul>
				</div>

				<div>
					<h4 class="text-sm font-semibold text-gray-900 mb-4">Company</h4>
					<ul class="space-y-2.5">
						<li><a href="#about" class="text-sm text-gray-500 hover:text-primary transition-colors">About</a></li>
						<li><a href="#contact" class="text-sm text-gray-500 hover:text-primary transition-colors">Contact</a></li>
						<li><a href="#careers" class="text-sm text-gray-500 hover:text-primary transition-colors">Careers</a></li>
						<li><a href="#blog" class="text-sm text-gray-500 hover:text-primary transition-colors">Blog</a></li>
					</ul>
				</div>

				<div>
					<h4 class="text-sm font-semibold text-gray-900 mb-4">Legal</h4>
					<ul class="space-y-2.5">
						<li><a href="#privacy" class="text-sm text-gray-500 hover:text-primary transition-colors">Privacy</a></li>
						<li><a href="#terms" class="text-sm text-gray-500 hover:text-primary transition-colors">Terms</a></li>
						<li><a href="#security" class="text-sm text-gray-500 hover:text-primary transition-colors">Security</a></li>
					</ul>
				</div>
			</div>

			<div class="mt-12 pt-8 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4">
				<p class="text-sm text-gray-400">&copy; {new Date().getFullYear()} PayPulse. All rights reserved.</p>
				<div class="flex items-center gap-5">
					<a href="https://twitter.com/paypulse" class="text-gray-400 hover:text-primary transition-colors" aria-label="Twitter">
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
					</a>
					<a href="https://github.com/paypulse" class="text-gray-400 hover:text-primary transition-colors" aria-label="GitHub">
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
					</a>
					<a href="https://linkedin.com/company/paypulse" class="text-gray-400 hover:text-primary transition-colors" aria-label="LinkedIn">
						<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
					</a>
				</div>
			</div>
		</div>
	</footer>
</div>
