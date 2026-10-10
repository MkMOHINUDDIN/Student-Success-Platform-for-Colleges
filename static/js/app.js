function read(id) {
  const el = document.getElementById(id);
  if (!el) return null;
  try { return JSON.parse(el.dataset.points || "[]"); } catch { return []; }
}
window.addEventListener("DOMContentLoaded", () => {
  const trend = read("trendChart");
  if (trend && window.Chart) {
    new Chart(document.getElementById("trendChart"), {
      type: "line",
      data: { labels: trend.map(t => t.term), datasets: [{ label: "Mean score", data: trend.map(t => t.mean), borderColor: "#1f6f8b" }] },
      options: { plugins: { legend: { display: false } } }
    });
  }
  const cls = read("classChart");
  if (cls && window.Chart) {
    new Chart(document.getElementById("classChart"), {
      type: "bar",
      data: { labels: cls.map(c => c.class), datasets: [{ label: "At risk", data: cls.map(c => c.risk), backgroundColor: "#b42318" }] },
      options: { plugins: { legend: { display: false } } }
    });
  }
  const prof = read("profileChart");
  if (prof && window.Chart) {
    new Chart(document.getElementById("profileChart"), {
      type: "bar",
      data: {
        labels: prof.map(p => p.term),
        datasets: [
          { label: "Attendance %", data: prof.map(p => Math.round(p.attendance_rate * 100)), backgroundColor: "#1f6f8b" },
          { label: "Mean score", data: prof.map(p => p.mean_score), backgroundColor: "#0f3d4c" }
        ]
      }
    });
  }
});
