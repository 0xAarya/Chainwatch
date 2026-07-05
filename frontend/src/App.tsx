import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  Blocks,
  CircleCheckBig,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Monitor,
  MoonStar,
  Play,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  SunMedium,
  Zap,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

type Transaction = {
  transaction_id: string;
  sender: string;
  receiver: string;
  amount: number;
  timestamp: string;
  status: string;
};

type Incident = {
  incident_id: string;
  incident_type: string;
  transaction_id: string;
  description: string;
  severity: string;
  timestamp: string;
  resolution_status: string;
};

type BlockData = {
  block_id: string;
  index: number;
  timestamp: string;
  transaction_count: number;
  previous_hash: string;
  current_hash: string;
};

type Health = {
  component: string;
  status: string;
  response_latency_ms: number;
  error_rate: number;
  uptime_percent: number;
};

type Analytics = {
  total_transactions: number;
  success_rate: number;
  failure_rate: number;
  total_incidents: number;
  critical_incidents: number;
  severity_breakdown: Record<string, number>;
};

type LogEntry = {
  id: number;
  level: string;
  component: string;
  message: string;
  timestamp: string;
};

type NavSection = 'Overview' | 'Live Monitor' | 'Transactions' | 'Blocks' | 'Incidents' | 'System Health' | 'Logs';

const API_BASE = 'http://127.0.0.1:8000';

const fetchJson = async <T,>(url: string): Promise<T> => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json() as Promise<T>;
};

const postJson = async (url: string) => {
  const response = await fetch(url, { method: 'POST' });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
};

function App() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [blocks, setBlocks] = useState<BlockData[]>([]);
  const [health, setHealth] = useState<Health[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeSection, setActiveSection] = useState<NavSection>('Overview');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [demoRunning, setDemoRunning] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [toast, setToast] = useState<string | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  const loadData = async () => {
    try {
      const [txData, incidentData, blockData, healthData, analyticsData, logsData] = await Promise.all([
        fetchJson<Transaction[]>(`${API_BASE}/transactions`),
        fetchJson<Incident[]>(`${API_BASE}/incidents`),
        fetchJson<BlockData[]>(`${API_BASE}/blocks`),
        fetchJson<Health[]>(`${API_BASE}/system-health`),
        fetchJson<Analytics>(`${API_BASE}/analytics`),
        fetchJson<LogEntry[]>(`${API_BASE}/logs`),
      ]);
      setTransactions(txData);
      setIncidents(incidentData);
      setBlocks(blockData);
      setHealth(healthData);
      setAnalytics(analyticsData);
      setLogs(logsData);
      if (!selectedIncident && incidentData.length > 0) setSelectedIncident(incidentData[0]);
    } catch (error) {
      console.error(error);
      setToast('Unable to connect to the monitoring backend.');
    }
  };

  useEffect(() => {
    void loadData();
    const interval = window.setInterval(() => {
      if (!demoRunning) return;
      void loadData();
    }, 7000);
    return () => window.clearInterval(interval);
  }, [demoRunning]);

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 2400);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('chainwatch-theme') as 'dark' | 'light' | null;
    if (storedTheme) setTheme(storedTheme);
  }, []);

  useEffect(() => {
    window.localStorage.setItem('chainwatch-theme', theme);
  }, [theme]);

  const isDark = theme === 'dark';

  const summaryCards = useMemo(() => {
    if (!analytics) return [];
    return [
      { label: 'Total Transactions', value: analytics.total_transactions, icon: Activity, accent: 'cyan' },
      { label: 'Success Rate', value: `${analytics.success_rate}%`, icon: ShieldCheck, accent: 'emerald' },
      { label: 'Failure Rate', value: `${analytics.failure_rate}%`, icon: AlertTriangle, accent: 'amber' },
      { label: 'Critical Incidents', value: analytics.critical_incidents, icon: Sparkles, accent: 'violet' },
    ];
  }, [analytics]);

  const chartData = useMemo(() => transactions.slice(0, 8).reverse().map((tx) => ({ name: tx.transaction_id.slice(-4), amount: tx.amount, status: tx.status })), [transactions]);
  const severityChart = useMemo(() => {
    if (!analytics) return [];
    return Object.entries(analytics.severity_breakdown).map(([name, value]) => ({ name, value }));
  }, [analytics]);

  const filteredTransactions = useMemo(() => transactions.filter((tx) => {
    const matchesSearch = `${tx.transaction_id} ${tx.sender} ${tx.receiver}`.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || tx.status === statusFilter;
    return matchesSearch && matchesStatus;
  }), [transactions, searchTerm, statusFilter]);

  const filteredIncidents = useMemo(() => incidents.filter((incident) => `${incident.incident_type} ${incident.description} ${incident.transaction_id}`.toLowerCase().includes(searchTerm.toLowerCase())), [incidents, searchTerm]);

  const handleStart = async () => {
    try {
      await postJson(`${API_BASE}/simulation/start`);
      setDemoRunning(true);
      setToast('Simulation started on TRON Chain.');
      await loadData();
    } catch {
      setToast('Could not start the simulation.');
    }
  };

  const handlePause = () => {
    setDemoRunning((value) => !value);
    setToast(demoRunning ? 'Simulation paused.' : 'Simulation resumed.');
  };

  const handleReset = async () => {
    try {
      await postJson(`${API_BASE}/simulation/reset`);
      setToast('Demo data reset.');
      await loadData();
    } catch {
      setToast('Reset failed.');
    }
  };

  const handleTriggerIncident = async () => {
    try {
      await postJson(`${API_BASE}/simulation/incident`);
      setToast('Random incident injected.');
      await loadData();
    } catch {
      setToast('Incident injection failed.');
    }
  };

  const handleResolve = async (incidentId: string) => {
    try {
      await fetch(`${API_BASE}/incidents/${incidentId}/resolve`, { method: 'POST' });
      setToast('Incident marked resolved.');
      await loadData();
    } catch {
      setToast('Unable to resolve incident.');
    }
  };

  const shell = isDark
    ? 'bg-[#040404] text-slate-100'
    : 'bg-[#fff7f7] text-slate-900';
  const card = isDark
    ? 'border-red-900/40 bg-[#140606]/90 shadow-red-950/40'
    : 'border-red-200/80 bg-white/95 shadow-red-100/70';
  const subdued = isDark ? 'text-slate-400' : 'text-slate-500';
  const mutedBorder = isDark ? 'border-red-900/40' : 'border-red-100';
  const soft = isDark ? 'bg-[#1f0f0f]' : 'bg-red-50';
  const accent = isDark ? 'text-red-400' : 'text-red-600';
  const badge = isDark ? 'border-red-500/30 bg-red-500/10 text-red-300' : 'border-red-600/20 bg-red-100 text-red-700';

  const renderOverview = () => (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((cardItem, index) => (
          <motion.div key={cardItem.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }} whileHover={{ y: -4, scale: 1.02 }} className={`rounded-2xl border p-4 ${card}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm ${subdued}`}>{cardItem.label}</p>
                <p className="mt-2 text-2xl font-semibold">{cardItem.value}</p>
              </div>
              <div className={`rounded-xl border p-2 ${badge}`}>
                <cardItem.icon size={18} />
              </div>
            </div>
          </motion.div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.85fr]">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl border p-4 ${card}`}>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className={`text-sm ${subdued}`}>TRON transaction activity</p>
              <h2 className="text-xl font-semibold">Block traffic and volume</h2>
            </div>
            <div className={`rounded-full border px-3 py-1 text-sm ${badge}`}>Live feed</div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid stroke={isDark ? '#1f2937' : '#e2e8f0'} vertical={false} />
                <XAxis dataKey="name" stroke={isDark ? '#64748b' : '#64748b'} />
                <YAxis stroke={isDark ? '#64748b' : '#64748b'} />
                <Tooltip />
                <Line type="monotone" dataKey="amount" stroke="#ef4444" strokeWidth={2.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl border p-4 ${card}`}>
          <div className="mb-4">
            <p className={`text-sm ${subdued}`}>Incident severity</p>
            <h2 className="text-xl font-semibold">Current distribution</h2>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityChart}>
                <CartesianGrid stroke={isDark ? '#1f2937' : '#e2e8f0'} vertical={false} />
                <XAxis dataKey="name" stroke={isDark ? '#64748b' : '#64748b'} />
                <YAxis stroke={isDark ? '#64748b' : '#64748b'} />
                <Tooltip />
                <Bar dataKey="value" fill={isDark ? '#ef4444' : '#dc2626'} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl border p-4 ${card}`}>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className={`text-sm ${subdued}`}>Recent incidents</p>
              <h2 className="text-xl font-semibold">Active investigation queue</h2>
            </div>
            <button onClick={() => setActiveSection('Incidents')} className={`text-sm ${accent}`}>Open queue</button>
          </div>
          <div className="space-y-3">
            {incidents.slice(0, 5).map((incident) => (
              <div key={incident.incident_id} className={`rounded-xl border p-3 ${mutedBorder}`}>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-medium">{incident.incident_type}</p>
                    <p className={`text-sm ${subdued}`}>{incident.transaction_id}</p>
                  </div>
                  <span className={`rounded-full border px-2 py-1 text-xs ${badge}`}>{incident.severity}</span>
                </div>
                <p className={`mt-2 text-sm ${subdued}`}>{incident.description}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`rounded-2xl border p-4 ${card}`}>
          <div className="mb-4">
            <p className={`text-sm ${subdued}`}>System health</p>
            <h2 className="text-xl font-semibold">Component status</h2>
          </div>
          <div className="space-y-3">
            {health.map((item) => (
              <div key={item.component} className={`rounded-xl border p-3 ${mutedBorder}`}>
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.component}</span>
                  <span className={`text-sm ${accent}`}>{item.status}</span>
                </div>
                <div className={`mt-2 text-sm ${subdued}`}>Latency {item.response_latency_ms}ms • Error {item.error_rate}%</div>
              </div>
            ))}
          </div>
        </motion.div>
      </section>
    </div>
  );

  const renderLiveMonitor = () => (
    <div className="space-y-6">
      <div className={`rounded-2xl border p-4 ${card}`}>
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className={`text-sm ${subdued}`}>Live monitoring</p>
            <h2 className="text-xl font-semibold">TRON chain signals</h2>
          </div>
          <div className="flex gap-2">
            <button onClick={handleStart} className={`rounded-xl border px-3 py-2 text-sm ${badge}`}><Play size={14} className="mr-1 inline" />Start</button>
            <button onClick={handlePause} className={`rounded-xl border px-3 py-2 text-sm ${badge}`}><Zap size={14} className="mr-1 inline" />{demoRunning ? 'Pause' : 'Resume'}</button>
            <button onClick={handleTriggerIncident} className={`rounded-xl border px-3 py-2 text-sm ${badge}`}><AlertTriangle size={14} className="mr-1 inline" />Inject</button>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {transactions.slice(0, 6).map((tx) => (
            <div key={tx.transaction_id} className={`rounded-xl border p-3 ${mutedBorder}`}>
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold">{tx.transaction_id}</p>
                <span className={`rounded-full border px-2 py-1 text-xs ${badge}`}>{tx.status}</span>
              </div>
              <p className={`mt-2 text-sm ${subdued}`}>{tx.sender} → {tx.receiver}</p>
              <p className="mt-1 text-sm font-medium">{tx.amount} TRX</p>
            </div>
          ))}
        </div>
      </div>
      <div className={`rounded-2xl border p-4 ${card}`}>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Latest operational notes</h3>
          <span className={`text-sm ${accent}`}>Auto-refreshing</span>
        </div>
        <div className="space-y-2">
          {logs.slice(0, 8).map((entry) => (
            <div key={entry.id} className={`rounded-xl border p-3 ${mutedBorder}`}>
              <div className="flex items-center justify-between">
                <span className="font-medium">{entry.component}</span>
                <span className={`text-xs ${subdued}`}>{entry.timestamp}</span>
              </div>
              <p className={`mt-1 text-sm ${subdued}`}>{entry.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTransactions = () => (
    <div className={`rounded-2xl border p-4 ${card}`}>
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className={`text-sm ${subdued}`}>Transactions explorer</p>
          <h2 className="text-xl font-semibold">TRON transaction ledger</h2>
        </div>
        <div className="flex gap-2">
          <input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search transactions" className={`rounded-xl border px-3 py-2 text-sm ${soft}`} />
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className={`rounded-xl border px-3 py-2 text-sm ${soft}`}>
            <option value="ALL">All</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILED">Failed</option>
            <option value="PENDING">Pending</option>
          </select>
        </div>
      </div>
      <div className="space-y-2">
        {filteredTransactions.map((tx) => (
          <div key={tx.transaction_id} className={`rounded-xl border p-3 ${mutedBorder}`}>
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-semibold">{tx.transaction_id}</p>
                <p className={`text-sm ${subdued}`}>{tx.sender} → {tx.receiver}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`rounded-full border px-2 py-1 text-xs ${badge}`}>{tx.status}</span>
                <span className="font-medium">{tx.amount} TRX</span>
                <span className={`text-sm ${subdued}`}>{tx.timestamp}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderBlocks = () => (
    <div className="grid gap-4 md:grid-cols-2">
      {blocks.map((block) => (
        <div key={block.block_id} className={`rounded-2xl border p-4 ${card}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm ${subdued}`}>Block #{block.index}</p>
              <h3 className="text-lg font-semibold">{block.block_id}</h3>
            </div>
            <div className={`rounded-full border px-2 py-1 text-xs ${badge}`}>{block.transaction_count} tx</div>
          </div>
          <div className={`mt-4 space-y-2 text-sm ${subdued}`}>
            <p>Timestamp: {block.timestamp}</p>
            <p>Previous hash: {block.previous_hash}</p>
            <p>Current hash: {block.current_hash}</p>
          </div>
        </div>
      ))}
    </div>
  );

  const renderIncidents = () => (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_0.95fr]">
      <div className={`rounded-2xl border p-4 ${card}`}>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className={`text-sm ${subdued}`}>Incident management</p>
            <h2 className="text-xl font-semibold">Operational review board</h2>
          </div>
          <input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search incidents" className={`rounded-xl border px-3 py-2 text-sm ${soft}`} />
        </div>
        <div className="space-y-3">
          {filteredIncidents.map((incident) => (
            <button key={incident.incident_id} onClick={() => setSelectedIncident(incident)} className={`w-full rounded-xl border p-3 text-left ${mutedBorder}`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{incident.incident_type}</p>
                  <p className={`text-sm ${subdued}`}>{incident.transaction_id}</p>
                </div>
                <span className={`rounded-full border px-2 py-1 text-xs ${badge}`}>{incident.severity}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
      <div className={`rounded-2xl border p-4 ${card}`}>
        {selectedIncident ? (
          <>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className={`text-sm ${subdued}`}>Incident details</p>
                <h3 className="text-lg font-semibold">{selectedIncident.incident_type}</h3>
              </div>
              <button onClick={() => handleResolve(selectedIncident.incident_id)} className={`rounded-xl border px-3 py-2 text-sm ${badge}`}><CircleCheckBig size={14} className="mr-1 inline" />Resolve</button>
            </div>
            <div className="space-y-3 text-sm">
              <p><span className="font-medium">Transaction:</span> {selectedIncident.transaction_id}</p>
              <p><span className="font-medium">Status:</span> {selectedIncident.resolution_status}</p>
              <p><span className="font-medium">Description:</span> {selectedIncident.description}</p>
              <p><span className="font-medium">Detected:</span> {selectedIncident.timestamp}</p>
            </div>
          </>
        ) : (
          <p className={subdued}>Select an incident to inspect it.</p>
        )}
      </div>
    </div>
  );

  const renderHealth = () => (
    <div className="space-y-4">
      {health.map((item) => (
        <div key={item.component} className={`rounded-2xl border p-4 ${card}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold">{item.component}</p>
              <p className={`text-sm ${subdued}`}>Latency {item.response_latency_ms}ms • Error {item.error_rate}%</p>
            </div>
            <div className={`rounded-full border px-3 py-2 text-sm ${badge}`}>{item.status}</div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderLogs = () => (
    <div className={`rounded-2xl border p-4 ${card}`}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className={`text-sm ${subdued}`}>Debug console</p>
          <h2 className="text-xl font-semibold">Application and incident logs</h2>
        </div>
        <div className={`rounded-full border px-3 py-2 text-sm ${badge}`}>Structured logging</div>
      </div>
      <div className="space-y-2">
        {logs.map((entry) => (
          <div key={entry.id} className={`rounded-xl border p-3 ${mutedBorder}`}>
            <div className="flex items-center justify-between">
              <span className="font-medium">{entry.component}</span>
              <span className={`text-xs ${subdued}`}>{entry.level}</span>
            </div>
            <p className={`mt-1 text-sm ${subdued}`}>{entry.message}</p>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className={`min-h-screen transition-colors ${shell}`}>
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 lg:flex-row lg:px-6">
        <motion.aside initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.35 }} className={`relative z-10 w-full rounded-3xl border p-4 shadow-2xl backdrop-blur lg:w-72 ${card}`}>
          <div className="mb-6 flex items-center gap-3">
            <div className={`rounded-xl border p-2 ${badge}`}>
              <Blocks size={20} />
            </div>
            <div>
              <p className={`text-sm font-semibold tracking-[0.25em] ${subdued}`}>CHAINWATCH</p>
              <p className="text-lg font-semibold">TRON Operations Hub</p>
            </div>
          </div>

          <nav className="space-y-2">
            {(['Overview', 'Live Monitor', 'Transactions', 'Blocks', 'Incidents', 'System Health', 'Logs'] as NavSection[]).map((section) => (
              <button key={section} onClick={() => setActiveSection(section)} className={`flex w-full items-center gap-3 rounded-xl border px-3 py-3 text-left text-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-lg ${activeSection === section ? badge : `${mutedBorder} hover:${soft}`}`}>
                {section === 'Overview' && <LayoutDashboard size={16} />}
                {section === 'Live Monitor' && <Monitor size={16} />}
                {section === 'Transactions' && <Activity size={16} />}
                {section === 'Blocks' && <Blocks size={16} />}
                {section === 'Incidents' && <AlertTriangle size={16} />}
                {section === 'System Health' && <ShieldCheck size={16} />}
                {section === 'Logs' && <ListChecks size={16} />}
                {section}
              </button>
            ))}
          </nav>

          <div className={`mt-8 rounded-2xl border p-4 ${badge}`}>
            <p className="text-sm font-medium">Live Tronscan Feed</p>
            <p className={`mt-1 text-sm ${subdued}`}>Recent TRON transfers are streamed into the dashboard in real time.</p>
          </div>
        </motion.aside>

        <main className="relative z-10 flex-1 space-y-6">
          <motion.header initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className={`relative overflow-hidden rounded-3xl border p-5 shadow-2xl backdrop-blur ${card}`}>
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(239,68,68,0.2),transparent_45%)]" />
            <div className="relative flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className={`mb-3 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.3em] ${badge}`}>
                  <Sparkles size={12} /> Genz-ready live ops
                </div>
                <p className={`text-sm uppercase tracking-[0.3em] ${accent}`}>Application Support Engineering</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight">ChainWatch • TRON Redline Pulse</h1>
                <p className={`mt-2 max-w-2xl text-sm ${subdued}`}>The slick chaos radar for every TRON signal, incident spike, and transaction burst.</p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <button onClick={() => setTheme(isDark ? 'light' : 'dark')} className={`rounded-full border px-3 py-2 text-sm transition hover:-translate-y-0.5 hover:shadow-lg ${badge}`}>
                  {isDark ? <SunMedium size={16} className="mr-1 inline" /> : <MoonStar size={16} className="mr-1 inline" />}
                  {isDark ? 'Light mode' : 'Dark mode'}
                </button>
                <div className={`flex items-center gap-2 rounded-full border px-3 py-2 text-sm ${badge}`}>
                  <span className={`h-2.5 w-2.5 rounded-full ${demoRunning ? 'bg-emerald-400' : 'bg-amber-400'}`} /> {demoRunning ? 'Monitoring live' : 'Paused'}
                </div>
                <div className={`flex items-center gap-2 rounded-full border px-3 py-2 text-sm ${soft}`}>
                  <Search size={16} /> Search events
                </div>
                <button onClick={handleReset} className={`rounded-full border p-2 transition hover:-translate-y-0.5 hover:shadow-lg ${soft}`}>
                  <RefreshCw size={16} />
                </button>
                <button onClick={handleReset} className={`rounded-full border p-2 transition hover:-translate-y-0.5 hover:shadow-lg ${soft}`}>
                  <LogOut size={16} />
                </button>
              </div>
            </div>
          </motion.header>

          {activeSection === 'Overview' && renderOverview()}
          {activeSection === 'Live Monitor' && renderLiveMonitor()}
          {activeSection === 'Transactions' && renderTransactions()}
          {activeSection === 'Blocks' && renderBlocks()}
          {activeSection === 'Incidents' && renderIncidents()}
          {activeSection === 'System Health' && renderHealth()}
          {activeSection === 'Logs' && renderLogs()}
        </main>
      </div>

      {toast && (
        <div className={`fixed bottom-4 right-4 rounded-2xl border px-4 py-3 text-sm shadow-xl ${badge}`}>
          {toast}
        </div>
      )}
    </div>
  );
}

export default App;
