/* =========================================================
   Student Early Support Platform — Global Vanilla JS
   ========================================================= */

(function () {
    'use strict';

    /* ------------------------------------------------------
       Flash / Alert Dismiss
       ------------------------------------------------------ */
    document.querySelectorAll(".alert-dismiss").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            var alert = e.target.closest(".alert");
            if (alert) {
                alert.remove();
            }
        });
    });

    /* ------------------------------------------------------
       Color helpers — read CSS variables from :root
       ------------------------------------------------------ */
    function cssVar(name) {
        var v = getComputedStyle(document.documentElement)
            .getPropertyValue(name)
            .trim();
        return v || '';
    }

    function hexToRgba(hex, alpha) {
        if (!hex) return 'rgba(0,0,0,' + alpha + ')';
        var m = hex.replace('#', '');
        if (m.length === 3) {
            m = m.split('').map(function (c) { return c + c; }).join('');
        }
        var r = parseInt(m.substring(0, 2), 16) || 0;
        var g = parseInt(m.substring(2, 4), 16) || 0;
        var b = parseInt(m.substring(4, 6), 16) || 0;
        return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
    }

    function getColors() {
        return {
            primary: cssVar('--primary') || '#1e40af',
            primaryLight: cssVar('--primary-light') || '#3b82f6',
            secondary: cssVar('--secondary') || '#0f766e',
            success: cssVar('--success') || '#16a34a',
            danger: cssVar('--danger') || '#dc2626',
            warning: cssVar('--warning') || '#d97706',
            info: cssVar('--info') || '#0ea5e9',
            muted: cssVar('--muted') || '#64748b',
            text: cssVar('--text') || '#0f172a',
            border: cssVar('--border') || '#e2e8f0',
            bg: cssVar('--bg') || '#f8fafc'
        };
    }

    function baseOptions(colors) {
        return {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: colors.text,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    backgroundColor: colors.text,
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    cornerRadius: 6,
                    padding: 10
                }
            },
            scales: {
                x: {
                    ticks: { color: colors.muted },
                    grid: { color: colors.border }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: colors.muted, precision: 0 },
                    grid: { color: colors.border }
                }
            }
        };
    }

    /* ------------------------------------------------------
       Line Chart
       ------------------------------------------------------ */
    window.drawLineChart = function (id, labels, values, label) {
        var ctx = document.getElementById(id);
        if (!ctx) return null;

        var colors = getColors();
        var color = colors.primary;

        var data = {
            labels: labels || [],
            datasets: [{
                label: label || 'Value',
                data: values || [],
                borderColor: color,
                backgroundColor: hexToRgba(color, 0.15),
                fill: true,
                tension: 0.3,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: color,
                pointRadius: 4,
                pointHoverRadius: 5,
                borderWidth: 2
            }]
        };

        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: baseOptions(colors)
        });
    };

    /* ------------------------------------------------------
       Bar Chart
       ------------------------------------------------------ */
    window.drawBarChart = function (id, labels, values, label) {
        var ctx = document.getElementById(id);
        if (!ctx) return null;

        var colors = getColors();
        var color = colors.primary;

        var data = {
            labels: labels || [],
            datasets: [{
                label: label || 'Value',
                data: values || [],
                backgroundColor: hexToRgba(color, 0.85),
                borderColor: color,
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: color
            }]
        };

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: baseOptions(colors)
        });
    };

    /* ------------------------------------------------------
       Stacked Bar Chart (At Risk vs Total)
       ------------------------------------------------------ */
    window.drawStackedBar = function (id, labels, atRisk, total) {
        var ctx = document.getElementById(id);
        if (!ctx) return null;

        var colors = getColors();
        atRisk = atRisk || [];
        total = total || [];

        // Non-risk column = total - atRisk (per label)
        var safe = total.map(function (t, i) {
            var r = atRisk[i] || 0;
            return Math.max(0, (t || 0) - r);
        });

        var data = {
            labels: labels || [],
            datasets: [
                {
                    label: 'At Risk',
                    data: atRisk,
                    backgroundColor: hexToRgba(colors.danger, 0.85),
                    borderColor: colors.danger,
                    borderWidth: 1,
                    borderRadius: 4,
                    hoverBackgroundColor: colors.danger
                },
                {
                    label: 'On Track',
                    data: safe,
                    backgroundColor: hexToRgba(colors.success, 0.7),
                    borderColor: colors.success,
                    borderWidth: 1,
                    borderRadius: 4,
                    hoverBackgroundColor: colors.success
                }
            ]
        };

        var opts = baseOptions(colors);
        opts.scales.x.stacked = true;
        opts.scales.y.stacked = true;

        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: opts
        });
    };

})();
