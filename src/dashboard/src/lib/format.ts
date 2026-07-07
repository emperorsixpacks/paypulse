type BadgeKind = 'ok' | 'wait' | 'fail' | 'neutral';

const badgeClasses: Record<BadgeKind, { bg: string; text: string }> = {
	ok:     { bg: 'bg-badge-ok-bg',     text: 'text-badge-ok-text' },
	wait:   { bg: 'bg-badge-wait-bg',   text: 'text-badge-wait-text' },
	fail:   { bg: 'bg-badge-fail-bg',   text: 'text-badge-fail-text' },
	neutral:{ bg: 'bg-badge-neutral-bg', text: 'text-badge-neutral-text' },
};

const statusMap: Record<string, { label: string; badge: BadgeKind }> = {
	ACTIVE:       { label: 'Active',       badge: 'ok' },
	PAID:         { label: 'Paid',         badge: 'ok' },
	COMPLETED:    { label: 'Completed',    badge: 'ok' },
	PROCESSED:    { label: 'Processed',    badge: 'ok' },
	DELIVERED:    { label: 'Delivered',    badge: 'ok' },

	TRIALING:     { label: 'Trialing',     badge: 'wait' },
	PAUSED:       { label: 'Paused',       badge: 'wait' },
	PENDING:      { label: 'Pending',      badge: 'wait' },

	PAST_DUE:     { label: 'Past due',     badge: 'fail' },
	FAILED:       { label: 'Failed',       badge: 'fail' },

	CANCELLED:    { label: 'Cancelled',    badge: 'neutral' },
	EXPIRED:      { label: 'Expired',      badge: 'neutral' },
	VOID:         { label: 'Void',         badge: 'neutral' },
	NONE:         { label: 'None',         badge: 'neutral' },
};

export function formatStatus(status: string): { label: string; badge: BadgeKind; bgClass: string; textClass: string } {
	const entry = statusMap[status] ?? { label: status.charAt(0) + status.slice(1).toLowerCase(), badge: 'neutral' as BadgeKind };
	const classes = badgeClasses[entry.badge];
	return { ...entry, bgClass: classes.bg, textClass: classes.text };
}

export function formatInterval(interval: string, count: number): string {
	if (count === 1) return interval.charAt(0) + interval.slice(1).toLowerCase();
	const unit = interval.toLowerCase() + 's';
	return `Every ${count} ${unit}`;
}

export function formatCurrency(amount: number, currency: string = 'NGN'): string {
	return new Intl.NumberFormat('en-NG', { style: 'currency', currency, minimumFractionDigits: 0 }).format(amount);
}

export function timeAgo(date: string): string {
	const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
	if (seconds < 60) return 'just now';
	const minutes = Math.floor(seconds / 60);
	if (minutes < 60) return `${minutes}m ago`;
	const hours = Math.floor(minutes / 60);
	if (hours < 24) return `${hours}h ago`;
	const days = Math.floor(hours / 24);
	return `${days}d ago`;
}
