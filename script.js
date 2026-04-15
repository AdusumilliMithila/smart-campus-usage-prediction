let fullData = [];
let trendChart = null;
let breakdownChart = null;

const monthNames = {
  "01": "January",
  "02": "February",
  "03": "March",
  "04": "April",
  "05": "May",
  "06": "June",
  "07": "July",
  "08": "August",
  "09": "September",
  "10": "October",
  "11": "November",
  "12": "December"
};

Papa.parse("predictions.csv", {
  download: true,
  header: true,
  skipEmptyLines: true,
  complete: function(results) {
    fullData = results.data
      .filter(r => r.Date)
      .map(r => ({
        Date: String(r.Date).trim(),
        Attendance: Number(r.Attendance),
        Lab: Number(r.Lab),
        Library: Number(r.Library),
        Internet: Number(r.Internet),
        Event: String(r.Event || "Normal").trim()
      }));

    populateMonthDropdown();
    document.getElementById("predictBtn").addEventListener("click", updateDashboard);
    updateDashboard();
  }
});

function populateMonthDropdown() {
  const monthSelect = document.getElementById("monthSelect");
  monthSelect.innerHTML = `<option value="all">All Months</option>`;

  const months = [...new Set(fullData.map(d => d.Date.split("-")[1]))];
  months.forEach(m => {
    const option = document.createElement("option");
    option.value = m;
    option.textContent = monthNames[m] || m;
    monthSelect.appendChild(option);
  });
}

function avg(arr) {
  if (!arr.length) return 0;
  return Math.round(arr.reduce((a, b) => a + b, 0) / arr.length);
}

function pctDiff(current, previous) {
  if (!previous || previous === 0) return 0;
  return (((current - previous) / previous) * 100).toFixed(1);
}

function getWeekNumberFromDay(day) {
  return Math.ceil(day / 7);
}

function filterData(monthValue, weekValue) {
  return fullData.filter(d => {
    const [, month, day] = d.Date.split("-");
    const week = getWeekNumberFromDay(parseInt(day, 10));

    const monthMatch = monthValue === "all" || month === monthValue;
    const weekMatch = weekValue === "all" || String(week) === weekValue;

    return monthMatch && weekMatch;
  });
}

function getComparisonData(monthValue, weekValue) {
  if (monthValue === "all" && weekValue === "all") return null;

  if (weekValue !== "all" && monthValue !== "all") {
    const prevWeek = String(Number(weekValue) - 1);
    if (prevWeek === "0") return null;
    return filterData(monthValue, prevWeek);
  }

  if (monthValue !== "all" && weekValue === "all") {
    const prevMonthNum = String(Number(monthValue) - 1).padStart(2, "0");
    if (prevMonthNum === "00") return null;
    return filterData(prevMonthNum, "all");
  }

  return null;
}

function updateCards(selected, previous) {
  const att = avg(selected.map(d => d.Attendance));
  const lab = avg(selected.map(d => d.Lab));
  const lib = avg(selected.map(d => d.Library));
  const net = avg(selected.map(d => d.Internet));

  document.getElementById("attendanceValue").textContent = `${att}%`;
  document.getElementById("labValue").textContent = `${lab}%`;
  document.getElementById("libraryValue").textContent = `${lib}%`;
  document.getElementById("internetValue").textContent = `${net}%`;

  if (previous && previous.length) {
    const prevAtt = avg(previous.map(d => d.Attendance));
    const prevLab = avg(previous.map(d => d.Lab));
    const prevLib = avg(previous.map(d => d.Library));
    const prevNet = avg(previous.map(d => d.Internet));

    setChange("attendanceChange", att, prevAtt);
    setChange("labChange", lab, prevLab);
    setChange("libraryChange", lib, prevLib);
    setChange("internetChange", net, prevNet);
  } else {
    document.getElementById("attendanceChange").textContent = "No previous comparison";
    document.getElementById("labChange").textContent = "No previous comparison";
    document.getElementById("libraryChange").textContent = "No previous comparison";
    document.getElementById("internetChange").textContent = "No previous comparison";
  }
}

function setChange(id, current, previous) {
  const diff = pctDiff(current, previous);
  const el = document.getElementById(id);

  if (Number(diff) > 0) {
    el.textContent = `▲ ${diff}% vs previous period`;
    el.style.color = "#16a34a";
  } else if (Number(diff) < 0) {
    el.textContent = `▼ ${Math.abs(diff)}% vs previous period`;
    el.style.color = "#dc2626";
  } else {
    el.textContent = `0.0% vs previous period`;
    el.style.color = "#64748b";
  }
}

function updateAlerts(selected, previous) {
  const container = document.getElementById("alertList");
  container.innerHTML = "";

  const eventCounts = {};
  selected.forEach(d => {
    eventCounts[d.Event] = (eventCounts[d.Event] || 0) + 1;
  });

  const avgAtt = avg(selected.map(d => d.Attendance));
  const avgLab = avg(selected.map(d => d.Lab));
  const avgLib = avg(selected.map(d => d.Library));

  const examDays = eventCounts["Exam"] || 0;
  const prepDays = eventCounts["PrepHoliday"] || 0;
  const labDays = eventCounts["LabExam"] || 0;
  const holidayDays = eventCounts["Holiday"] || 0;

  let statusTitle = "Normal Activity";
  let statusDesc = "This selected period shows regular academic activity with balanced campus usage.";
  let statusClass = "green";

  // Priority order
  if (holidayDays >= Math.ceil(selected.length * 0.5)) {
    statusTitle = "Holiday Period";
    statusDesc = "Most days in this selected period are holidays, so attendance and resource usage remain low.";
    statusClass = "orange";
  } else if (labDays >= 1) {
    statusTitle = "Lab Activity";
    statusDesc = "This selected period includes lab exam days, so lab usage is expected to be especially high.";
    statusClass = "blue";
  } else if (examDays >= 1) {
    statusTitle = "Exam + Preparation Phase";
    statusDesc = "This selected period includes exam days, with very high attendance and strong library usage.";
    statusClass = "red";
  } else if (prepDays >= 1) {
    statusTitle = "Preparation Phase";
    statusDesc = "This selected period includes preparation holidays, with high library and internet usage expected.";
    statusClass = "orange";
  } else {
    // Fallback only if no event found
    if (avgAtt <= 25) {
      statusTitle = "Holiday Period";
      statusDesc = "Attendance is very low, indicating reduced campus activity.";
      statusClass = "orange";
    } else if (avgLab >= 80) {
      statusTitle = "Lab Activity";
      statusDesc = "Lab usage is dominant in this period, indicating practical or lab-intensive activity.";
      statusClass = "blue";
    } else if (avgLib >= 80) {
      statusTitle = "Preparation Phase";
      statusDesc = "Library usage is very high, showing preparation-focused academic activity.";
      statusClass = "orange";
    } else if (avgAtt >= 80) {
      statusTitle = "Exam + Preparation Phase";
      statusDesc = "Attendance is very high, indicating an exam-heavy academic period.";
      statusClass = "red";
    }
  }

  container.appendChild(createAlertCard(statusClass, statusTitle, statusDesc));

  if (previous && previous.length) {
    const curAtt = avg(selected.map(d => d.Attendance));
    const prevAtt = avg(previous.map(d => d.Attendance));
    const diffAtt = pctDiff(curAtt, prevAtt);

    const curLib = avg(selected.map(d => d.Library));
    const prevLib = avg(previous.map(d => d.Library));
    const diffLib = pctDiff(curLib, prevLib);

    const curLab = avg(selected.map(d => d.Lab));
    const prevLab = avg(previous.map(d => d.Lab));
    const diffLab = pctDiff(curLab, prevLab);

    const insightText = `
      Attendance changed by ${diffAtt}% from the previous selected period.
      Library changed by ${diffLib}% and Lab changed by ${diffLab}%.
    `.replace(/\s+/g, " ").trim();

    container.appendChild(
      createAlertCard("green", "Comparison Insight", insightText)
    );
  }
}

function createAlertCard(colorClass, title, desc) {
  const wrapper = document.createElement("div");
  wrapper.className = `alert-item ${colorClass}`;

  const content = document.createElement("div");

  const titleEl = document.createElement("div");
  titleEl.className = "alert-title";
  titleEl.textContent = title;

  const descEl = document.createElement("div");
  descEl.className = "alert-desc";
  descEl.textContent = desc;

  content.appendChild(titleEl);
  content.appendChild(descEl);
  wrapper.appendChild(content);

  return wrapper;
}

function updateSummary(selected, previous, monthValue, weekValue) {
  const box = document.getElementById("summaryBox");

  const att = avg(selected.map(d => d.Attendance));
  const lab = avg(selected.map(d => d.Lab));
  const lib = avg(selected.map(d => d.Library));
  const net = avg(selected.map(d => d.Internet));

  let title = "Selected period summary";
  if (monthValue !== "all" && weekValue !== "all") {
    title = `${monthNames[monthValue]} - Week ${weekValue}`;
  } else if (monthValue !== "all") {
    title = `${monthNames[monthValue]} - Full Month`;
  } else if (weekValue !== "all") {
    title = `All Months - Week ${weekValue}`;
  }

  let comparison = "No previous comparison available.";
  if (previous && previous.length) {
    const prevAtt = avg(previous.map(d => d.Attendance));
    comparison = `Attendance changed by ${pctDiff(att, prevAtt)}% from previous period.`;
  }

  box.innerHTML = `
    <strong>${title}</strong><br><br>
    Attendance average: <strong>${att}%</strong><br>
    Lab average: <strong>${lab}%</strong><br>
    Library average: <strong>${lib}%</strong><br>
    Internet average: <strong>${net}%</strong><br><br>
    ${comparison}
  `;
}

function drawTrendChart(selected) {
  const labels = selected.map(d => {
    const parts = d.Date.split("-");
    return `${parts[2]}/${parts[1]}`;
  });

  const attendance = selected.map(d => d.Attendance);
  const lab = selected.map(d => d.Lab);
  const library = selected.map(d => d.Library);
  const internet = selected.map(d => d.Internet);

  if (trendChart) trendChart.destroy();

  trendChart = new Chart(document.getElementById("trendChart"), {
    data: {
      labels,
      datasets: [
        {
          type: "line",
          label: "Attendance %",
          data: attendance,
          borderColor: "#1e5eff",
          backgroundColor: "rgba(30,94,255,0.10)",
          tension: 0.35,
          pointRadius: 3,
          yAxisID: "y"
        },
        {
          type: "bar",
          label: "Lab %",
          data: lab,
          backgroundColor: "rgba(0,191,165,0.75)",
          yAxisID: "y"
        },
        {
          type: "bar",
          label: "Library %",
          data: library,
          backgroundColor: "rgba(245,158,11,0.75)",
          yAxisID: "y"
        },
        {
          type: "bar",
          label: "Internet %",
          data: internet,
          backgroundColor: "rgba(124,58,237,0.70)",
          yAxisID: "y"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: {
          labels: {
            color: "#5a6a8a",
            font: { family: "Outfit", size: 11 }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "rgba(30,80,180,0.07)" },
          ticks: { color: "#6b85a7" }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: "rgba(30,80,180,0.07)" },
          ticks: {
            color: "#6b85a7",
            callback: value => `${value}%`
          }
        }
      }
    }
  });
}

function drawBreakdownChart(selected) {
  const avgAtt = avg(selected.map(d => d.Attendance));
  const avgLab = avg(selected.map(d => d.Lab));
  const avgLib = avg(selected.map(d => d.Library));
  const avgNet = avg(selected.map(d => d.Internet));

  if (breakdownChart) breakdownChart.destroy();

  breakdownChart = new Chart(document.getElementById("breakdownChart"), {
    type: "bar",
    data: {
      labels: ["Attendance", "Lab", "Library", "Internet"],
      datasets: [{
        label: "Average %",
        data: [avgAtt, avgLab, avgLib, avgNet],
        backgroundColor: [
          "rgba(30,94,255,0.8)",
          "rgba(0,191,165,0.8)",
          "rgba(245,158,11,0.8)",
          "rgba(124,58,237,0.8)"
        ],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#6b85a7" }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: "rgba(30,80,180,0.07)" },
          ticks: {
            color: "#6b85a7",
            callback: value => `${value}%`
          }
        }
      }
    }
  });
}

function updateDashboard() {
  const monthValue = document.getElementById("monthSelect").value || "all";
  const weekValue = document.getElementById("weekSelect").value || "all";

  const selected = filterData(monthValue, weekValue);
  const previous = getComparisonData(monthValue, weekValue);

  if (!selected.length) return;

  updateCards(selected, previous);
  updateAlerts(selected, previous);
  updateSummary(selected, previous, monthValue, weekValue);
  drawTrendChart(selected);
  drawBreakdownChart(selected);
}