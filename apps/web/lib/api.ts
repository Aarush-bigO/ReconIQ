const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  get: (path: string) => apiFetch<any>(path).then(data => ({ data })),
  post: (path: string, body?: any) => apiFetch<any>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }).then(data => ({ data })),
  
  health: () => apiFetch<any>("/health"),
  systemStatus: () => apiFetch<any>("/system/status"),

  // Reconciliation
  runReconciliation: (config?: any) =>
    apiFetch<any>("/reconcile", { method: "POST", body: JSON.stringify(config || {}) }),
  listRuns: () => apiFetch<any>("/reconcile/runs"),
  getRun: (runId: string) => apiFetch<any>(`/reconcile/runs/${runId}`),

  // Transactions
  listTransactions: (params?: { source?: string; status?: string; search?: string; page?: number }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiFetch<any>(`/transactions${qs ? "?" + qs : ""}`);
  },
  getTransaction: (id: string) => apiFetch<any>(`/transactions/${id}`),
  getTransaction360: (id: string) => apiFetch<any>(`/transactions/${id}/360`),

  // Exceptions
  listExceptions: (params?: { status?: string; severity?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return apiFetch<any>(`/exceptions${qs ? "?" + qs : ""}`);
  },
  getException: (id: string) => apiFetch<any>(`/exceptions/${id}`),
  reviewException: (id: string, body: any) =>
    apiFetch<any>(`/exceptions/${id}/review`, { method: "POST", body: JSON.stringify(body) }),
  explainException: (id: string) =>
    apiFetch<any>(`/exceptions/${id}/explain`, { method: "POST" }),

  // Settlements
  listSettlements: () => apiFetch<any>("/settlements"),
  getSettlement: (id: string) => apiFetch<any>(`/settlements/${id}`),

  // Audit
  getAuditTrail: () => apiFetch<any>("/audit"),
  verifyAuditChain: () => apiFetch<any>("/audit/verify"),

  // Reports
  getLatestReport: () => apiFetch<any>("/reports/latest"),

  // Evaluation
  runEvaluation: () => apiFetch<any>("/evaluation/run", { method: "POST" }),
  getEvaluationResults: () => apiFetch<any>("/evaluation/results"),
};

export function formatMinorAmount(minor: number, currency = "INR"): string {
  const major = minor / 100;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(major);
}

export function formatLakhAmount(minor: number): string {
  const major = minor / 100;
  if (major >= 100000) return `₹${(major / 100000).toFixed(2)}L`;
  if (major >= 1000) return `₹${(major / 1000).toFixed(1)}K`;
  return `₹${major.toFixed(0)}`;
}

export function confidenceColor(prob: number): string {
  if (prob >= 0.95) return "#10b981";
  if (prob >= 0.70) return "#f59e0b";
  return "#ef4444";
}

export function decisionBadge(decision: string): string {
  const map: Record<string, string> = {
    AUTO_MATCH: "badge-matched",
    MANUAL_REVIEW: "badge-review",
    UNRESOLVED: "badge-unresolved",
  };
  return map[decision] || "badge-medium";
}

export function severityBadge(severity: string): string {
  const map: Record<string, string> = {
    HIGH: "badge-high",
    MEDIUM: "badge-medium",
    LOW: "badge-low",
  };
  return map[severity] || "badge-medium";
}
