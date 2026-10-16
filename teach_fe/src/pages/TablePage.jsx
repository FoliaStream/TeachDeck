import { useEffect, useState } from "react";

const PIPE = import.meta.env.VITE_PIPE_URL;

export default function TablePage() {
  const [tables, setTables] = useState([]);
  const [table, setTable] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // The list of tables comes from the database, through the pipeline server
  useEffect(() => {
    fetch(`${PIPE}/tables`)
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || "Could not load the list of tables");
        setTables(data);
      })
      .catch((err) => setError(err.message));
  }, []);

  // Ask the pipeline server to run for the chosen table
  async function runPipeline(name) {
    setTable(name);
    setError(null);
    setRows([]);
    if (!name) return;

    setLoading(true);
    try {
      const res = await fetch(`${PIPE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dbtable: name }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      setRows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];

  return (
    <div className="table-page">
      <label>
        Table:{" "}
        <select
          value={table}
          onChange={(e) => runPipeline(e.target.value)}
          disabled={loading}
        >
          <option value="">Choose a table…</option>
          {tables.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </label>

      {loading && <p>Running the pipeline…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && table && rows.length === 0 && <p>No rows.</p>}

      {rows.length > 0 && (
        <div className="table-wrap">
          <p>{rows.length} rows</p>
          <table>
            <thead>
              <tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {columns.map((c) => <td key={c}>{String(row[c] ?? "")}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}