<script lang="ts">
	import { onMount } from 'svelte';

	let reduced = $state(false);
	let liveNum = $state(128412);

	const feed = [
		{ s:'ok',   amt:'$24.00',  who:'Acme Ltd',        state:'charged' },
		{ s:'wait', amt:'$18.50',  who:'Nova Systems',    state:'retrying' },
		{ s:'ok',   amt:'$340.00', who:'Quantum Labs',    state:'charged' },
		{ s:'ok',   amt:'$9.00',   who:'Fenwick Studio',  state:'charged' },
		{ s:'fail', amt:'$65.00',  who:'Drift Analytics', state:'failed' },
		{ s:'ok',   amt:'$65.00',  who:'Drift Analytics', state:'recovered' },
		{ s:'ok',   amt:'$212.00', who:'Baseline Co',     state:'charged' },
	];

	const iconFor: Record<string, string> = { ok:'✓', wait:'↻', fail:'!' };

	onMount(() => {
		reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

		// Scroll reveal
		const revealEls = document.querySelectorAll('.reveal');
		if ('IntersectionObserver' in window && !reduced) {
			const io = new IntersectionObserver((entries) => {
				entries.forEach(e => {
					if ((e as IntersectionObserverEntry).isIntersecting) {
						(e.target as HTMLElement).classList.add('in');
						io.unobserve(e.target);
					}
				});
			}, { threshold: 0.15 });
			revealEls.forEach(el => io.observe(el));
		} else {
			revealEls.forEach(el => el.classList.add('in'));
		}

		// Count-up stats
		const statEls = document.querySelectorAll('.stat .num');
		if ('IntersectionObserver' in window && !reduced) {
			const statIo = new IntersectionObserver((entries) => {
				entries.forEach(e => {
					if ((e as IntersectionObserverEntry).isIntersecting) {
						animateCount(e.target as HTMLElement);
						statIo.unobserve(e.target);
					}
				});
			}, { threshold: 0.4 });
			statEls.forEach(el => statIo.observe(el));
		} else {
			statEls.forEach(el => animateCount(el as HTMLElement));
		}

		// Live counter
		if (!reduced) {
			const iv = setInterval(() => {
				liveNum += Math.floor(Math.random() * 47) + 3;
			}, 3400);
			return () => clearInterval(iv);
		}
	});

	function animateCount(el: HTMLElement) {
		const target = parseFloat(el.dataset.count || '0');
		const suffix = el.dataset.suffix || '';
		const prefix = el.dataset.prefix || '';
		if (reduced || isNaN(target)) {
			el.textContent = prefix + (el.dataset.count || '0') + suffix;
			return;
		}
		const duration = 1100;
		const start = performance.now();
		const decimals = ((el.dataset.count || '').split('.')[1] || '').length;
		function tick(now: number) {
			const p = Math.min(1, (now - start) / duration);
			const eased = 1 - Math.pow(1 - p, 3);
			const val = (target * eased).toFixed(decimals);
			el.textContent = prefix + val + suffix;
			if (p < 1) requestAnimationFrame(tick);
		}
		requestAnimationFrame(tick);
	}

	function renderLine(item: typeof feed[0]) {
		const cls = item.s === 'ok' ? 'tk-ok' : item.s === 'wait' ? 'tk-wait' : 'tk-fail';
		return { cls, icon: iconFor[item.s], ...item };
	}

	let tickerLines = $derived(feed.slice(0, 4).map(renderLine));
</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
</svelte:head>

<!-- NAV -->
<nav class="nav">
	<div class="wrap">
		<a class="brand" href="#top" aria-label="PayPulse home">
			<img src="/logo.svg" alt="PayPulse" height="40" width="160" />
		</a>
		<div class="navlinks">
			<a href="#features">Features</a>
			<a href="#pricing">Pricing</a>
			<a href="#docs">Docs</a>
			<a href="#contact">Contact</a>
		</div>
		<div class="navcta">
			<a class="login" href="/login">Log in</a>
			<a class="btn btn-cobalt btn-sm" href="/register">Start free trial</a>
		</div>
	</div>
</nav>

<!-- HERO -->
<header class="hero" id="top">
	<div class="blob blob-a" aria-hidden="true"></div>
	<div class="blob blob-b" aria-hidden="true"></div>
	<div class="wrap hero-grid">
		<div>
			<p class="eyebrow"><span class="dot" aria-hidden="true"></span>Now in early access</p>
			<h1 class="headline">Billing that keeps<br>up with <span class="accent">you.</span></h1>
			<p class="sub">Automated invoicing, smart dunning, usage-based pricing and secure payouts — the full revenue stack behind subscriptions that just work.</p>
			<div class="cta-row">
				<a class="btn btn-primary" href="/register">Start free trial</a>
				<a class="btn btn-ghost" href="#docs">Read the docs →</a>
			</div>
			<p class="fine">No card required · Free for your first 50 customers</p>
			<div class="live-stat">
				<span class="pulse-dot" aria-hidden="true"></span>
				<span>Processed today: <span class="num">${liveNum.toLocaleString('en-US')}</span></span>
			</div>
		</div>

		<div class="card-stage">
			<div class="invoice-card behind" aria-hidden="true">
				<div class="invoice-top"><span>INVOICE · #0093</span><span class="badge-paid">PAID</span></div>
				<p class="invoice-amt">$89.00</p>
				<p class="invoice-who">Fenwick Studio</p>
			</div>
			<div class="invoice-card">
				<div class="invoice-top">
					<span>INVOICE · #0094</span>
					<span class="badge-paid">PAID</span>
				</div>
				<p class="invoice-amt">$340.00</p>
				<p class="invoice-who">Quantum Labs</p>
				<div class="invoice-meta">
					<div><span>Plan</span><b>Growth · Monthly</b></div>
					<div><span>Method</span><b>•••• 4471</b></div>
					<div><span>Next charge</span><b>Aug 7, 2026</b></div>
				</div>
			</div>
		</div>
	</div>
</header>

<!-- BUILT FOR -->
<section class="builtfor">
	<div class="wrap">
		<span class="builtfor-label">Built for</span>
		<div class="category-list">
			<span>SaaS platforms</span>
			<span>Marketplaces</span>
			<span>API-first products</span>
			<span>Creator tools</span>
			<span>Fintech apps</span>
		</div>
	</div>
</section>

<!-- FEATURES -->
<section class="features" id="features">
	<div class="wrap">
		<div class="section-head reveal">
			<h2 class="section-title">Everything you need to scale revenue.</h2>
			<p class="section-desc">From the first invoice to the last cancellation — every tool you need to manage the full customer lifecycle.</p>
		</div>

		<div class="feature-grid reveal">
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h7l-1 8 11-14h-7l1-6z"/></svg></div>
				<h3>Automated billing</h3>
				<p>Recurring invoices, proration and dunning handled without a script.</p>
				<p class="feature-spec">&lt; 50ms per charge</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M12 20V4M20 20v-7"/></svg></div>
				<h3>Usage-based pricing</h3>
				<p>Meter API calls, seats or units, and bill exactly what's used.</p>
				<p class="feature-spec">Billed per-unit</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg></div>
				<h3>Secure payments</h3>
				<p>PCI-compliant checkout with Nomba. Cards tokenized end to end.</p>
				<p class="feature-spec">PCI DSS</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M21 3v5h-5M3 21v-5h5"/></svg></div>
				<h3>Smart dunning</h3>
				<p>Failed payments retry on an exponential schedule you control.</p>
				<p class="feature-spec">Auto-retry</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z"/><path d="M10 20a2 2 0 0 0 4 0"/></svg></div>
				<h3>Webhook events</h3>
				<p>Every lifecycle event delivered in real time, signed with HMAC.</p>
				<p class="feature-spec">HMAC signed</p>
			</div>
			<div class="feature-card">
				<div class="feature-icon"><svg viewBox="0 0 24 24" fill="none" stroke="#0E1116" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 15s1 1.5 2.5 1.5 2.5-1 2.5-2-1-1.5-2.5-2-2.5-1-2.5-2 1-2 2.5-2 2.5 1.5 2.5 1.5"/></svg></div>
				<h3>Revenue recovery</h3>
				<p>Cancellation flows with configurable win-back offers.</p>
				<p class="feature-spec">Configurable</p>
			</div>
		</div>
	</div>
</section>

<!-- STATS -->
<section class="stats" id="pricing">
	<div class="wrap">
		<div class="stats-row reveal">
			<div class="stat"><div class="num" data-count="99.9" data-suffix="%">0%</div><div class="label">Uptime</div></div>
			<div class="stat"><div class="num" data-count="50" data-suffix="ms">0ms</div><div class="label">Response time</div></div>
			<div class="stat"><div class="num" data-count="25" data-suffix="+">0+</div><div class="label">Integrations</div></div>
			<div class="stat"><div class="num" data-count="0" data-prefix="$">$0</div><div class="label">Cost to start</div></div>
		</div>
	</div>
</section>

<!-- CTA BAND -->
<section class="wrap">
	<div class="cta-band reveal">
		<div class="blob blob-a" aria-hidden="true"></div>
		<div class="blob blob-b" aria-hidden="true"></div>
		<div class="cta-inner">
			<p class="eyebrow"><span class="dot" aria-hidden="true"></span>Ready when you are</p>
			<h2>Get paid on time. Every time.</h2>
			<p>Start free, connect your first product in an afternoon, and scale into usage billing whenever you're ready.</p>
			<div class="cta-row">
				<a class="btn btn-on-cobalt" href="/register">Create free account</a>
				<a class="btn btn-ghost-on-cobalt" href="#contact">Talk to sales</a>
			</div>
		</div>
	</div>
</section>

<!-- FOOTER -->
<footer id="docs">
	<div class="wrap">
		<div class="foot-grid">
			<div class="foot-brand">
			<a class="brand" href="#top" aria-label="PayPulse home">
				<img src="/logo.svg" alt="PayPulse" height="40" width="160" />
			</a>
				<p>Subscription billing and revenue operations for teams that get paid on a schedule.</p>
			</div>
			<div class="foot-col">
				<h4>Product</h4>
				<a href="#features">Features</a>
				<a href="#pricing">Pricing</a>
				<a href="#docs">API docs</a>
				<a href="#">Status</a>
			</div>
			<div class="foot-col">
				<h4>Company</h4>
				<a href="#">About</a>
				<a href="#contact">Contact</a>
				<a href="#">Careers</a>
				<a href="#">Blog</a>
			</div>
			<div class="foot-col">
				<h4>Legal</h4>
				<a href="#">Privacy</a>
				<a href="#">Terms</a>
				<a href="#">Security</a>
			</div>
		</div>
		<div class="foot-bottom">
			<span>&copy; 2026 PayPulse Inc. All rights reserved.</span>
			<div class="socials">
				<a href="#" aria-label="X (Twitter)"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7.6 8.7L23.4 22H16.8l-5.2-6.8L5.6 22H2.5l8.1-9.3L1.6 2h6.8l4.7 6.2L18.9 2Zm-1.2 18h1.7L7.4 3.9H5.6l12.1 16.1Z"/></svg></a>
				<a href="#" aria-label="GitHub"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.3-3.4-1.3-.5-1.1-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-4.9 0-1.1.4-2 1-2.6-.1-.3-.4-1.3.1-2.6 0 0 .8-.3 2.7 1a9 9 0 0 1 4.9 0c1.9-1.3 2.7-1 2.7-1 .5 1.3.2 2.3.1 2.6.6.6 1 1.5 1 2.6 0 3.8-2.4 4.6-4.6 4.9.4.3.7.9.7 1.9v2.7c0 .3.2.6.7.5A10 10 0 0 0 12 2Z"/></svg></a>
				<a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.9 8.4H3.6V20H6.9V8.4ZM5.3 3.4a1.9 1.9 0 1 0 0 3.8 1.9 1.9 0 0 0 0-3.8ZM20.4 20h-3.3v-6.1c0-1.5-.5-2.5-1.8-2.5-1 0-1.6.7-1.9 1.3-.1.2-.1.6-.1.9V20H10c0-11.6 0-11.6 0-11.6h3.3v1.7c.4-.7 1.2-1.6 3-1.6 2.2 0 3.9 1.4 3.9 4.5V20Z"/></svg></a>
			</div>
		</div>
	</div>
</footer>
