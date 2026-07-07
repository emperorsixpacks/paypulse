const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
}

export function getApiKey(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('api_key');
}

export function setApiKey(key: string) {
  localStorage.setItem('api_key', key);
}

export function clearApiKey() {
  localStorage.removeItem('api_key');
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = getToken();
  const apiKey = getApiKey();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(opts.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (apiKey) headers['X-Api-Key'] = apiKey;

  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (res.status === 204) return null as T;
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  // Auth
  register: (data: { email: string; business_name: string; password: string }) =>
    request<any>('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string }>('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => request<any>('/api/v1/auth/me'),

  // Projects
  listProjects: () => request<any[]>('/api/v1/merchants/projects'),
  createProject: (name: string) =>
    request<any>('/api/v1/merchants/projects', { method: 'POST', body: JSON.stringify({ name }) }),

  // API Keys
  listApiKeys: () => request<any[]>('/api/v1/merchants/api-keys'),
  createApiKey: (name: string, is_live: boolean) =>
    request<any>('/api/v1/merchants/api-keys', { method: 'POST', body: JSON.stringify({ name, is_live }) }),
  revokeApiKey: (id: string) =>
    request<null>(`/api/v1/merchants/api-keys/${id}`, { method: 'DELETE' }),

  // Plans
  listPlans: () => request<any[]>('/api/v1/plans'),
  createPlan: (data: any) => request<any>('/api/v1/plans', { method: 'POST', body: JSON.stringify(data) }),
  getPlan: (id: string) => request<any>(`/api/v1/plans/${id}`),
  updatePlan: (id: string, data: any) => request<any>(`/api/v1/plans/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deletePlan: (id: string) => request<null>(`/api/v1/plans/${id}`, { method: 'DELETE' }),

  // Customers
  listCustomers: () => request<any[]>('/api/v1/customers'),
  getCustomer: (id: string) => request<any>(`/api/v1/customers/${id}`),

  // Subscriptions
  listSubscriptions: (status?: string) =>
    request<any[]>(`/api/v1/subscriptions${status ? `?status_filter=${status}` : ''}`),
  getSubscription: (id: string) => request<any>(`/api/v1/subscriptions/${id}`),
  cancelSubscription: (id: string, cancelAtPeriodEnd: boolean) =>
    request<any>(`/api/v1/subscriptions/${id}/cancel`, { method: 'POST', body: JSON.stringify({ cancel_at_period_end: cancelAtPeriodEnd }) }),
  reportUsage: (subId: string, data: any) =>
    request<any>(`/api/v1/subscriptions/${subId}/usage`, { method: 'POST', body: JSON.stringify(data) }),
  getUsage: (subId: string) => request<any>(`/api/v1/subscriptions/${subId}/usage`),
  getUsageHistory: (subId: string, from?: string, to?: string) => {
    const params = new URLSearchParams();
    if (from) params.set('from_dt', from);
    if (to) params.set('to_dt', to);
    const qs = params.toString();
    return request<any[]>(`/api/v1/subscriptions/${subId}/usage/history${qs ? `?${qs}` : ''}`);
  },

  // Invoices
  listInvoices: () => request<any[]>('/api/v1/invoices'),
  getInvoice: (id: string) => request<any>(`/api/v1/invoices/${id}`),

  // Checkout
  listCheckoutSessions: () => request<any[]>('/api/v1/checkout/sessions'),
  createCheckoutSession: (data: any) =>
    request<any>('/api/v1/checkout/sessions', { method: 'POST', body: JSON.stringify(data) }),
  getCheckoutSession: (code: string) => request<any>(`/api/v1/checkout/sessions/${code}`),
  cancelCheckoutSession: (code: string) =>
    request<null>(`/api/v1/checkout/sessions/${code}`, { method: 'DELETE' }),

  // Webhooks
  listWebhooks: () => request<any[]>('/api/v1/webhooks'),
  createWebhook: (data: { url: string; events: string[] }) =>
    request<any>('/api/v1/webhooks', { method: 'POST', body: JSON.stringify(data) }),
  deleteWebhook: (id: string) => request<null>(`/api/v1/webhooks/${id}`, { method: 'DELETE' }),

  // Cancellation Policies
  listPolicies: () => request<any[]>('/api/v1/cancellation-policies'),
  createPolicy: (data: any) =>
    request<any>('/api/v1/cancellation-policies', { method: 'POST', body: JSON.stringify(data) }),
  getPolicy: (id: string) => request<any>(`/api/v1/cancellation-policies/${id}`),
  updatePolicy: (id: string, data: any) =>
    request<any>(`/api/v1/cancellation-policies/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deletePolicy: (id: string) => request<null>(`/api/v1/cancellation-policies/${id}`, { method: 'DELETE' }),
};
