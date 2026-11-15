import { useEffect, useState } from "react";

const API = "https://job-tracker-kcwu.onrender.com";
const JOBS_PATH = "/api/jobs";
const JOB_PATH = (id) => `/api/jobs/${id}`;
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];

const css = `
:root{--bg:#f3f5f2;--card:#fff;--ink:#1d2a26;--mute:#6b7a74;--line:#d9dfdb;--accent:#1f5c4a}
@media (prefers-color-scheme:dark){:root{--bg:#121917;--card:#1a2421;--ink:#e6ece9;--mute:#8fa09a;--line:#2b3834;--accent:#5fc4a4}}
*{box-sizing:border-box}
body{margin:0;display:block;background:var(--bg);color:var(--ink);font-family:system-ui,sans-serif}
.wrap{max-width:640px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:1.6rem;margin:0 0 4px}
.sub{color:var(--mute);margin:0 0 20px}
form{display:grid;gap:8px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:20px}
input,select,button{font:inherit;padding:10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}
button{background:var(--accent);color:#fff;border:0;font-weight:600;cursor:pointer}
button:disabled{opacity:.6}
.job{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}
.job b{display:block}
.job span{color:var(--mute);font-size:.9rem}
.job select{padding:6px}
.msg{padding:10px;border-radius:8px;background:var(--card);border:1px solid var(--line);margin-bottom:12px}
`;

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ title: "", company: "", status: "saved" });

  async function load() {
    try {
      setError("");
      const res = await fetch(API + JOBS_PATH);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data = await res.json();
      setJobs(Array.isArray(data) ? data : data.jobs || []);
    } catch (e) {
      setError(`Could not load jobs: ${e.message}. Free Render servers take about a minute to wake up, so try again shortly.`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function addJob(e) {
    e.preventDefault();
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      const res = await fetch(API + JOBS_PATH, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setForm({ title: "", company: "", status: "saved" });
      await load();
    } catch (e) {
      setError(`Could not add job: ${e.message}`);
    } finally {
      setSaving(false);
    }
  }

  async function setStatus(id, status) {
    try {
      const res = await fetch(API + JOB_PATH(id), {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setJobs((js) => js.map((j) => (j.id === id ? { ...j, status } : j)));
    } catch (e) {
      setError(`Could not update status: ${e.message}`);
    }
  }

  return (
    <>
      <style>{css}</style>
      <div className="wrap">
        <h1>Job Tracker</h1>
        <p className="sub">{jobs.length} saved</p>
        {error && <div className="msg">{error}</div>}
        <form onSubmit={addJob}>
          <input placeholder="Job title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <input placeholder="Company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
          <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            {STATUSES.map((s) => (<option key={s}>{s}</option>))}
          </select>
          <button disabled={saving}>{saving ? "Adding..." : "Add job"}</button>
        </form>
        {loading && <p className="sub">Loading jobs...</p>}
        {!loading && jobs.length === 0 && !error && (<p className="sub">No jobs yet. Add your first one above.</p>)}
        {jobs.map((j) => (
          <div className="job" key={j.id}>
            <div><b>{j.title}</b><span>{j.company}</span></div>
            <select value={j.status} onChange={(e) => setStatus(j.id, e.target.value)}>
              {STATUSES.map((s) => (<option key={s}>{s}</option>))}
            </select>
          </div>
        ))}
      </div>
    </>
  );
}
