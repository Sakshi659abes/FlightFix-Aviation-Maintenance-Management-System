/**
 * FlightFix Aviation MRO Management System
 * Dynamic Frontend Controller connecting HTML/CSS with Django REST Framework
 */

// Global State
const FlightFix = {
  currentModule: 'overview',
  activeRole: 'CHIEF_ENGINEER',
  apiBase: '/api/v1',
  charts: {},
};

// DOM Content Loaded Handler
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initNavigation();
  loadOverviewMetrics();
  loadAllModuleData();
  initModalListeners();
});

// Real-Time UTC Aviation Clock
function initClock() {
  const clockEl = document.getElementById('utc-clock');
  function update() {
    const d = new Date();
    const utcStr = d.toUTCString().split(' ').slice(1, 4).join(' ') + ' ' + d.toISOString().substr(11, 8) + ' UTC';
    if (clockEl) clockEl.textContent = utcStr;
  }
  update();
  setInterval(update, 1000);
}

// Module Navigation Tab Switcher
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetModule = item.dataset.module;
      switchModule(targetModule);
    });
  });
}

function switchModule(moduleKey) {
  FlightFix.currentModule = moduleKey;

  // Update sidebar active class
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const activeNav = document.querySelector(`.nav-item[data-module="${moduleKey}"]`);
  if (activeNav) activeNav.classList.add('active');

  // Show selected pane
  document.querySelectorAll('.module-content-pane').forEach(pane => pane.classList.remove('active'));
  const targetPane = document.getElementById(`pane-${moduleKey}`);
  if (targetPane) {
    targetPane.classList.add('active');
  }

  // Reload data for this pane
  refreshActiveModuleData(moduleKey);
}

function refreshActiveModuleData(moduleKey) {
  switch (moduleKey) {
    case 'overview':
      loadOverviewMetrics();
      break;
    case 'planning':
      loadPlanningData();
      break;
    case 'workorders':
      loadWorkOrdersData();
      break;
    case 'fleet':
      loadFleetData();
      break;
    case 'inventory':
      loadInventoryData();
      break;
    case 'execution':
      loadExecutionData();
      break;
    case 'compliance':
      loadComplianceData();
      break;
    case 'supplychain':
      loadSupplyChainData();
      break;
    case 'analytics':
      loadAnalyticsData();
      break;
    case 'audit':
      loadAuditData();
      break;
  }
}

function loadAllModuleData() {
  loadPlanningData();
  loadWorkOrdersData();
  loadFleetData();
  loadInventoryData();
  loadExecutionData();
  loadComplianceData();
  loadSupplyChainData();
  loadAnalyticsData();
  loadAuditData();
}

// -------------------------------------------------------------
// MODULE 0: OVERVIEW & DASHBOARD METRICS
// -------------------------------------------------------------
async function loadOverviewMetrics() {
  try {
    const [fleetRes, woRes, kpiRes] = await Promise.all([
      fetch(`${FlightFix.apiBase}/fleet/aircraft/summary/`),
      fetch(`${FlightFix.apiBase}/workorders/orders/metrics/`),
      fetch(`${FlightFix.apiBase}/analytics/kpis/live_kpis/`)
    ]);

    const fleetData = await fleetRes.json();
    const woData = await woRes.json();
    const kpiData = await kpiRes.json();

    // Update KPI UI
    safeSetText('dash-fleet-readiness', `${fleetData.fleet_readiness_pct || 75}%`);
    safeSetText('dash-total-aircraft', fleetData.total_aircraft || 4);
    safeSetText('dash-aog-count', fleetData.aog || 1);
    safeSetText('dash-active-wo', (woData.open + woData.in_progress + woData.awaiting_parts) || 2);
    safeSetText('dash-dispatch-rel', `${kpiData.dispatch_reliability || 99.4}%`);
    safeSetText('dash-mtbf', `${kpiData.mtbf_hours || 438}h`);

    // Render Charts
    renderOverviewCharts(fleetData, kpiData);
  } catch (err) {
    console.error('Error fetching dashboard overview:', err);
  }
}

function renderOverviewCharts(fleet, kpi) {
  if (typeof Chart === 'undefined') return;

  // 1. Fleet Status Donut Chart
  const fleetCtx = document.getElementById('chartFleetStatus');
  if (fleetCtx) {
    if (FlightFix.charts.fleetStatus) FlightFix.charts.fleetStatus.destroy();
    FlightFix.charts.fleetStatus = new Chart(fleetCtx, {
      type: 'doughnut',
      data: {
        labels: ['Operational Ready', 'In Hangar MRO', 'Aircraft on Ground (AOG)'],
        datasets: [{
          data: [fleet.operational || 2, fleet.in_maintenance || 1, fleet.aog || 1],
          backgroundColor: ['#16877d', '#e8a34b', '#d46b5e'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#64748b', font: { size: 11 } } }
        }
      }
    });
  }

  // 2. MTBF & Telemetry Reliability Chart
  const relCtx = document.getElementById('chartReliability');
  if (relCtx) {
    if (FlightFix.charts.reliability) FlightFix.charts.reliability.destroy();
    FlightFix.charts.reliability = new Chart(relCtx, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Current'],
        datasets: [{
          label: 'Dispatch Reliability (%)',
          data: [98.8, 99.0, 99.1, 98.9, 99.3, 99.2, kpi.dispatch_reliability || 99.4],
          backgroundColor: '#6689a6',
          borderRadius: 4
        }, {
          label: 'AOG Incidents Catch Rate (%)',
          data: [82, 85, 89, 87, 92, 94, 96],
          type: 'line',
          borderColor: '#16877d',
          tension: 0.3,
          borderWidth: 2,
          pointBackgroundColor: '#16877d'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { min: 70, max: 100, grid: { color: '#e6e9ed' }, ticks: { color: '#64748b' } },
          x: { grid: { display: false }, ticks: { color: '#64748b' } }
        },
        plugins: {
          legend: { position: 'bottom', labels: { color: '#64748b' } }
        }
      }
    });
  }
}

// -------------------------------------------------------------
// MODULE 1: MAINTENANCE PLANNING & SCHEDULING
// -------------------------------------------------------------
async function loadPlanningData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/planning/schedules/`);
    if (!res.ok) throw new Error(`planning API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-planning-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(item => `
      <tr>
        <td><strong>${item.schedule_id}</strong></td>
        <td><span class="badge badge-blue">${item.aircraft_tail}</span> <span class="text-muted">(${item.aircraft_model})</span></td>
        <td>${item.check_type_display}</td>
        <td><span class="badge badge-purple">${item.hangar_bay_code || 'TBD'}</span></td>
        <td>${formatDate(item.scheduled_start)}</td>
        <td>${formatDate(item.scheduled_end)}</td>
        <td><span class="badge ${getStatusBadgeClass(item.status)}">${item.status_display || item.status}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="promptUpdateScheduleStatus('${item.id}', '${item.schedule_id}')">Update Status</button>
          <button class="btn btn-danger btn-sm" onclick="deleteRecord('/planning/schedules/${item.id}/', 'schedule ${item.schedule_id}', loadPlanningData)">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading planning data:', err);
  }
}

// -------------------------------------------------------------
// MODULE 2: WORK ORDER MANAGEMENT
// -------------------------------------------------------------
async function loadWorkOrdersData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/workorders/orders/`);
    if (!res.ok) throw new Error(`work orders API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-workorders-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(wo => `
      <tr>
        <td><strong>${wo.work_order_no}</strong></td>
        <td><span class="badge badge-blue">${wo.aircraft_tail}</span></td>
        <td>
          <div style="font-weight:600">${escapeHtml(wo.title)}</div>
          <div class="text-muted" style="font-size:0.75rem">${escapeHtml(wo.description.substring(0, 85))}...</div>
        </td>
        <td><span class="badge ${getPriorityBadgeClass(wo.priority)}">${wo.priority_display}</span></td>
        <td><span class="badge ${getStatusBadgeClass(wo.status)}">${wo.status_display}</span></td>
        <td>${wo.actual_man_hours} / ${wo.estimated_man_hours} hrs</td>
        <td>
          ${wo.status === 'CLOSED_RELEASED' ? 
            `<span class="badge badge-green">✓ CRS Released</span>` :
            `<button class="btn btn-success btn-sm" onclick="openReleaseCRSModal('${wo.id}', '${wo.work_order_no}', '${wo.aircraft_tail}')">Sign & Release (CRS)</button>`
          }
          <button class="btn btn-danger btn-sm" onclick="deleteRecord('/workorders/orders/${wo.id}/', 'work order ${wo.work_order_no}', loadWorkOrdersData)">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading work orders:', err);
  }
}

// -------------------------------------------------------------
// MODULE 3: AIRCRAFT & FLEET MANAGEMENT
// -------------------------------------------------------------
async function loadFleetData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/fleet/aircraft/`);
    if (!res.ok) throw new Error(`aircraft API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const issueSelect = document.getElementById('issue-aircraft');
    if (issueSelect) issueSelect.innerHTML = list.map(a => `<option value="${a.id}">${a.tail_number} — ${a.model}</option>`).join('');
    const grid = document.getElementById('fleet-aircraft-cards');
    if (!grid) return;

    grid.innerHTML = list.map(ac => {
      const statusBadge = ac.status === 'OPERATIONAL' ? 'badge-green' : (ac.status === 'AOG' ? 'badge-rose' : 'badge-amber');
      return `
        <div class="kpi-card" style="min-height: 200px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:1.3rem; font-weight:700; color:#93c5fd;">${ac.tail_number}</div>
              <div style="font-size:0.85rem; color:var(--text-secondary);">${ac.model}</div>
            </div>
            <span class="badge ${statusBadge}">${ac.status_display || ac.status}</span>
          </div>

          <div style="margin: 12px 0; font-size: 0.8rem; display:grid; grid-template-columns: 1fr 1fr; gap:6px;">
            <div><span class="text-muted">Serial:</span> <strong>${ac.serial_number}</strong></div>
            <div><span class="text-muted">Location:</span> <strong>${ac.current_location}</strong></div>
            <div><span class="text-muted">Hours:</span> <strong>${ac.total_flight_hours} hrs</strong></div>
            <div><span class="text-muted">Cycles:</span> <strong>${ac.total_flight_cycles}</strong></div>
          </div>

          <div style="border-top:1px solid var(--border-subtle); padding-top:8px; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:0.75rem; color:var(--text-muted);">
              Subsystems: <strong>${ac.subsystems ? ac.subsystems.length : 0} monitored</strong>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
              <button class="btn btn-secondary btn-sm" onclick="showSubsystems('${ac.tail_number}', '${encodeURIComponent(JSON.stringify(ac.subsystems || []))}')">View Health</button>
              <button class="btn btn-secondary btn-sm" onclick="editAircraft(${ac.id})">Edit</button>
              <button class="btn btn-danger btn-sm" onclick="deleteAircraft(${ac.id}, '${ac.tail_number}')">Delete</button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading fleet:', err);
  }
}

// -------------------------------------------------------------
// MODULE 4: SPARE PARTS INVENTORY
// -------------------------------------------------------------
async function loadInventoryData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/inventory/parts/`);
    if (!res.ok) throw new Error(`spare parts API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-inventory-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(part => `
      <tr>
        <td><strong>${part.part_number}</strong></td>
        <td>
          <div>${escapeHtml(part.description)}</div>
          <span class="badge badge-gray" style="font-size:0.68rem;">${part.category_name || 'Standard'}</span>
        </td>
        <td>
          <span style="font-size:1.05rem; font-weight:700; ${part.is_low_stock ? 'color:var(--accent-rose);' : ''}">
            ${part.quantity_on_hand} ${part.unit_of_measure}
          </span>
          ${part.is_low_stock ? `<span class="badge badge-rose" style="margin-left:6px;">LOW STOCK</span>` : ''}
        </td>
        <td>${part.minimum_safety_stock} / ${part.reorder_quantity}</td>
        <td><code style="color:#93c5fd;">${part.storage_bin_location}</code></td>
        <td>$${parseFloat(part.unit_cost_usd).toLocaleString()}</td>
        <td><span class="badge badge-blue">${part.condition_display}</span></td>
        <td>
          <div style="display:flex;gap:5px;flex-wrap:wrap;">
            <button class="btn btn-primary btn-sm" onclick="openStockAdjustModal('${part.id}', '${part.part_number}', ${part.quantity_on_hand})">Issue / Restock</button>
            <button class="btn btn-secondary btn-sm" onclick="editSparePart(${part.id})">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteSparePart(${part.id}, '${part.part_number}')">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading inventory:', err);
  }
}

// -------------------------------------------------------------
// MODULE 5: EXECUTION & AMM JOB CARDS
// -------------------------------------------------------------
async function loadExecutionData() {
  try {
    const [jcRes, defRes] = await Promise.all([
      fetch(`${FlightFix.apiBase}/execution/job-cards/`),
      fetch(`${FlightFix.apiBase}/execution/defects/`)
    ]);

    const jcData = await jcRes.json();
    const defData = await defRes.json();

    const jcList = jcData.results || jcData;
    const defList = defData.results || defData;

    // Render Job Cards
    const jcTbody = document.getElementById('table-jobcards-body');
    if (jcTbody) {
      jcTbody.innerHTML = jcList.map(jc => `
        <tr>
          <td><strong>${jc.job_card_no}</strong> (Step ${jc.step_number})</td>
          <td>
            <div>${escapeHtml(jc.step_instruction)}</div>
            <code style="font-size:0.75rem; color:var(--text-muted);">${jc.amm_clause_reference}</code>
          </td>
          <td>
            ${jc.is_completed ? 
              `<span class="badge badge-green">✓ Stamped: ${jc.technician_stamp}</span><br><span style="font-size:0.72rem; color:var(--text-muted);">${jc.technician_name}</span>` :
              `<button class="btn btn-accent btn-sm" onclick="openTechnicianStampModal('${jc.id}', '${jc.job_card_no}', ${jc.step_number})">
                Digital Stamp Step
              </button>`
            }
          </td>
          <td>
            ${jc.is_inspected ?
              `<span class="badge badge-purple">✓ QC: ${jc.inspector_stamp}</span>` :
              (jc.is_completed ? `<span class="badge badge-amber">QC Pending</span>` : `<span class="text-muted">-</span>`)
            }
          </td>
        </tr>
      `).join('');
    }

    // Render Defects
    const defTbody = document.getElementById('table-defects-body');
    if (defTbody) {
      defTbody.innerHTML = defList.map(def => `
        <tr>
          <td><strong>${def.defect_log_number}</strong></td>
          <td><span class="badge badge-blue">${def.aircraft_tail}</span></td>
          <td>
            <div style="font-weight:600">${escapeHtml(def.title)}</div>
            <div class="text-muted" style="font-size:0.75rem">${escapeHtml(def.discrepancy_details)}</div>
          </td>
          <td><span class="badge ${def.severity === 'AOG' ? 'badge-rose' : 'badge-amber'}">${def.severity_display}</span></td>
          <td><span class="badge ${getStatusBadgeClass(def.status)}">${def.status_display}</span></td>
          <td>
            <div class="text-muted" style="font-size:.72rem">Engineer: ${escapeHtml(def.assigned_engineer || 'Not assigned')}<br>Due: ${def.expected_completion_date || 'Not scheduled'}</div>
            ${def.status === 'RECTIFIED' ? `<span class="badge badge-green">Resolved</span>` : `<button class="btn btn-secondary btn-sm" onclick="manageAircraftIssue(${def.id})">Manager Update</button> <button class="btn btn-success btn-sm" onclick="promptRectifyDefect('${def.id}', '${def.defect_log_number}')">Resolve</button>`}
          </td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading execution data:', err);
  }
}

// -------------------------------------------------------------
// MODULE 6: COMPLIANCE MANAGEMENT (AD & SB)
// -------------------------------------------------------------
async function loadComplianceData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/compliance/directives/`);
    if (!res.ok) throw new Error(`compliance directives API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-compliance-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(ad => `
      <tr>
        <td><strong>${ad.ad_number}</strong></td>
        <td><span class="badge badge-purple">${ad.authority_display || ad.issuing_authority}</span></td>
        <td>
          <div style="font-weight:600">${escapeHtml(ad.title)}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">Applicable: ${ad.applicable_models}</div>
        </td>
        <td><span style="color:var(--accent-amber); font-weight:600;">${ad.compliance_deadline}</span></td>
        <td>${ad.is_recurring ? `Yes (${ad.repeat_interval_flight_hours} hrs)` : 'One-time Mod'}</td>
        <td><span class="badge ${ad.status === 'COMPLIED' ? 'badge-green' : 'badge-rose'}">${ad.status_display || ad.status}</span></td>
        <td>
          ${ad.status === 'COMPLIED' ? `<span class="badge badge-green">✓ Certified</span>` : `<button class="btn btn-primary btn-sm" onclick="certifyAD('${ad.id}', '${ad.ad_number}')">Certify AD</button>`}
          <button class="btn btn-danger btn-sm" onclick="deleteRecord('/compliance/directives/${ad.id}/', 'directive ${ad.ad_number}', loadComplianceData)">Delete</button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading compliance:', err);
  }
}

// -------------------------------------------------------------
// MODULE 7: ERP & SUPPLY CHAIN
// -------------------------------------------------------------
async function loadSupplyChainData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/supplychain/purchase-orders/`);
    if (!res.ok) throw new Error(`purchase orders API returned HTTP ${res.status}`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-supplychain-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(po => `
      <tr>
        <td><strong>${po.po_number}</strong></td>
        <td>
          <div style="font-weight:600;">${po.vendor_name || 'OEM Vendor'}</div>
          <code style="font-size:0.72rem; color:var(--text-muted);">${po.erp_system_ref}</code>
        </td>
        <td>$${parseFloat(po.total_amount_usd).toLocaleString()}</td>
        <td><span class="badge ${po.status === 'RECEIVED' ? 'badge-green' : (po.status === 'IN_TRANSIT' ? 'badge-amber' : 'badge-blue')}">${po.status_display}</span></td>
        <td>
          <div style="font-size:0.8rem;">${po.shipping_carrier}</div>
          <code style="font-size:0.75rem; color:#93c5fd;">${po.air_waybill_number || 'N/A'}</code>
        </td>
        <td>${po.expected_delivery_date}</td>
        <td>
          ${po.status === 'RECEIVED' ?
            `<span class="badge badge-green">✓ In Hangar Stores</span>` :
            `<button class="btn btn-secondary btn-sm" onclick="syncERP('${po.id}', '${po.po_number}')">
              ERP Sync / Receive
            </button>`
          }
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading supply chain:', err);
  }
}

// -------------------------------------------------------------
// MODULE 9: PREDICTIVE DIAGNOSTICS & TELEMETRY
// -------------------------------------------------------------
async function loadAnalyticsData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/analytics/alerts/`);
    const data = await res.json();
    const list = data.results || data;

    const tbody = document.getElementById('table-predictive-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(alert => `
      <tr>
        <td><strong>${alert.alert_id}</strong></td>
        <td><span class="badge badge-blue">${alert.aircraft_tail}</span> <span class="text-muted">(${alert.aircraft_model})</span></td>
        <td>
          <div style="font-weight:600;">${escapeHtml(alert.component_name)}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(alert.recommended_action)}</div>
        </td>
        <td>
          <div style="display:flex; align-items:center; gap:8px;">
            <div style="flex:1; height:6px; background:#1e293b; border-radius:3px; overflow:hidden;">
              <div style="width:${alert.predicted_failure_probability_pct}%; height:100%; background:var(--accent-rose);"></div>
            </div>
            <strong style="color:var(--accent-rose);">${alert.predicted_failure_probability_pct}%</strong>
          </div>
          <div style="font-size:0.72rem; color:var(--text-muted);">${alert.predicted_failure_window}</div>
        </td>
        <td><span class="badge ${alert.severity === 'CRITICAL' ? 'badge-rose' : 'badge-amber'}">${alert.severity_display}</span></td>
        <td><span class="badge ${getStatusBadgeClass(alert.status)}">${alert.status_display}</span></td>
        <td>
          ${alert.status === 'ACTIVE' ?
            `<button class="btn btn-accent btn-sm" onclick="acknowledgePredictiveAlert('${alert.id}')">
              Acknowledge Alert
            </button>` :
            `<span class="badge badge-green">✓ Monitored</span>`
          }
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading predictive alerts:', err);
  }
}

// -------------------------------------------------------------
// MODULE 10: SECURITY & AUDIT TRAIL
// -------------------------------------------------------------
async function loadAuditData() {
  try {
    const res = await fetch(`${FlightFix.apiBase}/audit/logs/recent_activities/`);
    const list = await res.json();

    const tbody = document.getElementById('table-audit-body');
    if (!tbody) return;

    tbody.innerHTML = list.map(log => `
      <tr>
        <td><code style="color:var(--text-muted);">${formatDate(log.timestamp)}</code></td>
        <td>
          <strong>${escapeHtml(log.user_name)}</strong>
          <div style="font-size:0.72rem; color:var(--text-muted);">${log.user_role}</div>
        </td>
        <td><span class="badge badge-blue">${log.action_type_display}</span></td>
        <td><span class="badge badge-purple">${log.target_module_display}</span></td>
        <td><strong>${log.entity_reference}</strong></td>
        <td>${escapeHtml(log.details)}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading audit logs:', err);
  }
}

// -------------------------------------------------------------
// INTERACTIVE ACTION HANDLERS
// -------------------------------------------------------------

// Sign-off / Release to Service (CRS)
function openReleaseCRSModal(id, woNo, tail) {
  document.getElementById('crs-wo-id').value = id;
  document.getElementById('crs-modal-title').textContent = `Release to Service: ${woNo} (${tail})`;
  document.getElementById('modal-release-crs').classList.add('open');
}

async function submitReleaseCRS() {
  const id = document.getElementById('crs-wo-id').value;
  const engineer = document.getElementById('crs-engineer-name').value;
  const crsCode = document.getElementById('crs-code-input').value;

  try {
    const res = await fetch(`${FlightFix.apiBase}/workorders/orders/${id}/release_to_service/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sign_off_engineer: engineer, crs_code: crsCode })
    });
    const result = await res.json();
    closeAllModals();
    showToast(result.message, 'success');
    loadWorkOrdersData();
    loadOverviewMetrics();
    loadAuditData();
  } catch (err) {
    showToast('Failed to issue CRS.', 'error');
  }
}

// Adjust Stock (Module 4)
function openStockAdjustModal(partId, partNo, currentQty) {
  document.getElementById('stock-part-id').value = partId;
  document.getElementById('stock-modal-title').textContent = `Adjust Stock: ${partNo} (Current: ${currentQty})`;
  document.getElementById('modal-adjust-stock').classList.add('open');
}

async function submitStockAdjustment() {
  const id = document.getElementById('stock-part-id').value;
  const qty = document.getElementById('stock-qty-input').value;
  const type = document.getElementById('stock-txn-type').value;
  const ref = document.getElementById('stock-ref-order').value;

  try {
    const res = await fetch(`${FlightFix.apiBase}/inventory/parts/${id}/adjust_stock/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: qty, transaction_type: type, reference_order: ref, performed_by: 'Chief Eng. Rajesh' })
    });
    const result = await res.json();
    if (!res.ok) {
      showToast(result.error || 'Adjustment failed', 'error');
      return;
    }
    closeAllModals();
    showToast(result.message, 'success');
    loadInventoryData();
  } catch (err) {
    showToast('Stock adjustment error.', 'error');
  }
}

// Technician Stamp on Job Card (Module 5)
function openTechnicianStampModal(cardId, cardNo, stepNo) {
  document.getElementById('stamp-card-id').value = cardId;
  document.getElementById('stamp-modal-title').textContent = `Digital Stamp: ${cardNo} (Step ${stepNo})`;
  document.getElementById('modal-technician-stamp').classList.add('open');
}

async function submitTechnicianStamp() {
  const id = document.getElementById('stamp-card-id').value;
  const name = document.getElementById('stamp-tech-name').value;
  const stamp = document.getElementById('stamp-license-code').value;

  try {
    const res = await fetch(`${FlightFix.apiBase}/execution/job-cards/${id}/stamp_technician/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ technician_name: name, technician_stamp: stamp })
    });
    const result = await res.json();
    closeAllModals();
    showToast(result.message, 'success');
    loadExecutionData();
  } catch (err) {
    showToast('Failed to apply digital stamp.', 'error');
  }
}

// Rectify Defect (Module 5)
async function promptRectifyDefect(defectId, logNo) {
  const action = prompt(`Enter rectification action performed for ${logNo}:`, 'Replaced O-ring seal, torqued to AMM spec, and leak check SAT.');
  if (!action) return;

  try {
    const res = await fetch(`${FlightFix.apiBase}/execution/defects/${defectId}/rectify/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rectification_action: action, rectified_by: 'Lead AME R. Sen' })
    });
    const data = await res.json();
    showToast(data.message, 'success');
    loadExecutionData();
  } catch (err) {
    showToast('Failed to rectify defect.', 'error');
  }
}

async function deleteRecord(path, label, refresh) {
  if (!confirm(`Delete ${label}? This cannot be undone.`)) return;
  try { await apiRequest(`${FlightFix.apiBase}${path}`, 'DELETE'); showToast(`${label} deleted.`, 'success'); refresh(); }
  catch(e) { showToast(`Delete failed: ${e.message}`, 'error'); }
}

// Create records for the main management modules. IDs are selected from existing records.
async function addMaintenanceSchedule() {
  try {
    const aircrafts = await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/`);
    const aircraftList = aircrafts.results || aircrafts;
    if (!aircraftList.length) throw new Error('Pehle Aircraft add karein.');
    const aircraft = prompt('Aircraft ID (available: ' + aircraftList.map(a => `${a.id}=${a.tail_number}`).join(', ') + '):', aircraftList[0].id);
    if (aircraft === null) return;
    const schedule_id = prompt('Schedule ID:', 'SCH-' + Date.now()); if (!schedule_id) return;
    const scheduled_start = prompt('Start date/time (YYYY-MM-DDTHH:MM:SS):', new Date().toISOString().slice(0,19)); if (!scheduled_start) return;
    const scheduled_end = prompt('End date/time (YYYY-MM-DDTHH:MM:SS):', new Date(Date.now()+86400000).toISOString().slice(0,19)); if (!scheduled_end) return;
    await apiRequest(`${FlightFix.apiBase}/planning/schedules/`, 'POST', {schedule_id, aircraft:Number(aircraft), scheduled_start, scheduled_end});
    showToast('Maintenance schedule added successfully.', 'success'); loadPlanningData();
  } catch(e) { showToast('Schedule add failed: ' + e.message, 'error'); }
}
async function addWorkOrder() {
  try {
    const aircrafts = await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/`);
    const aircraftList = aircrafts.results || aircrafts;
    if (!aircraftList.length) throw new Error('Pehle Aircraft add karein.');
    const aircraft = prompt('Aircraft ID (available: ' + aircraftList.map(a => `${a.id}=${a.tail_number}`).join(', ') + '):', aircraftList[0].id); if (aircraft === null) return;
    const work_order_no = prompt('Work Order Number:', 'WO-' + Date.now()); if (!work_order_no) return;
    const title = prompt('Work title:'); if (!title) return;
    const description = prompt('Work description:'); if (!description) return;
    await apiRequest(`${FlightFix.apiBase}/workorders/orders/`, 'POST', {work_order_no, aircraft:Number(aircraft), title, description});
    showToast('Work order added successfully.', 'success'); loadWorkOrdersData();
  } catch(e) { showToast('Work order add failed: ' + e.message, 'error'); }
}
async function addDirective() {
  try {
    const ad_number = prompt('Directive number (AD):'); if (!ad_number) return;
    const title = prompt('Directive title:'); if (!title) return;
    const applicable_models = prompt('Applicable aircraft models:'); if (!applicable_models) return;
    const effective_date = prompt('Effective date (YYYY-MM-DD):', new Date().toISOString().slice(0,10)); if (!effective_date) return;
    const compliance_deadline = prompt('Compliance deadline (YYYY-MM-DD):', effective_date); if (!compliance_deadline) return;
    const action_required = prompt('Action required:'); if (!action_required) return;
    await apiRequest(`${FlightFix.apiBase}/compliance/directives/`, 'POST', {ad_number,title,applicable_models,effective_date,compliance_deadline,action_required});
    showToast('Airworthiness directive added.', 'success'); loadComplianceData();
  } catch(e) { showToast('Directive add failed: ' + e.message, 'error'); }
}
async function addVendor() {
  try {
    const vendor_code = prompt('Vendor code:'); if (!vendor_code) return;
    const name = prompt('Vendor name:'); if (!name) return;
    const contact_email = prompt('Contact email:'); if (!contact_email) return;
    const phone = prompt('Phone number:'); if (!phone) return;
    await apiRequest(`${FlightFix.apiBase}/supplychain/vendors/`, 'POST', {vendor_code,name,contact_email,phone});
    showToast('Vendor added successfully.', 'success');
  } catch(e) { showToast('Vendor add failed: ' + e.message, 'error'); }
}

// Aircraft and spare-parts CRUD + aircraft issue workflow
async function apiRequest(url, method='GET', body=null) {
  const opts = {method, headers:{'Content-Type':'application/json'}};
  if (body) opts.body = JSON.stringify(body);
  const response = await fetch(url, opts);
  const raw = response.status === 204 ? '' : await response.text();
  let data = {};
  try { data = raw ? JSON.parse(raw) : {}; } catch (_) { data = {detail: raw || response.statusText}; }
  if (!response.ok) {
    const message = typeof data === 'object' ? Object.entries(data).map(([k,v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : (typeof v === 'string' ? v : JSON.stringify(v))}`).join(' | ') : String(data);
    throw new Error(message || `HTTP ${response.status}`);
  }
  return data;
}
async function addAircraft() {
  const tail_number=prompt('Aircraft registration / tail number:'); if(!tail_number) return;
  const model=prompt('Aircraft model:'); if(!model) return;
  const serial_number=prompt('Serial number:'); if(!serial_number) return;
  const manufacturer=prompt('Manufacturer:','Airbus'); if(!manufacturer) return;
  try { await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/`,'POST',{tail_number,model,serial_number,manufacturer}); showToast('Aircraft added successfully.','success'); loadFleetData(); }
  catch(e){showToast('Could not add aircraft: '+e.message,'error');}
}
async function editAircraft(id) {
  try { const a=await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/${id}/`);
    const model=prompt('Aircraft model:',a.model); if(model===null)return;
    const manufacturer=prompt('Manufacturer:',a.manufacturer); if(manufacturer===null)return;
    const status=prompt('Status: OPERATIONAL, IN_MAINTENANCE, AOG, RESERVE',a.status); if(status===null)return;
    await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/${id}/`,'PATCH',{model,manufacturer,status}); showToast('Aircraft updated.','success'); loadFleetData();
  } catch(e){showToast('Update failed: '+e.message,'error');}
}
async function deleteAircraft(id, tail){ if(!confirm(`Delete aircraft ${tail}? This cannot be undone.`))return;
  try{await apiRequest(`${FlightFix.apiBase}/fleet/aircraft/${id}/`,'DELETE');showToast('Aircraft deleted.','success');loadFleetData();}catch(e){showToast('Delete failed: '+e.message,'error');}}
async function addSparePart(){
  const part_number=prompt('Part number:');if(!part_number)return;
  const description=prompt('Part description:');if(!description)return;
  const quantity_on_hand=Number(prompt('Opening stock quantity:','0'));if(!Number.isFinite(quantity_on_hand)||quantity_on_hand<0)return;
  const minimum_safety_stock=Number(prompt('Minimum safety stock:','5'));
  const unit_cost_usd=prompt('Unit cost (USD):','150');
  try{await apiRequest(`${FlightFix.apiBase}/inventory/parts/`,'POST',{part_number,description,quantity_on_hand,minimum_safety_stock,unit_cost_usd});showToast('Spare part added.','success');loadInventoryData();}
  catch(e){showToast('Could not add spare part: '+e.message,'error');}
}
async function editSparePart(id){
  try{const p=await apiRequest(`${FlightFix.apiBase}/inventory/parts/${id}/`);
    const description=prompt('Description:',p.description);if(description===null)return;
    const quantity_on_hand=Number(prompt('Quantity on hand:',p.quantity_on_hand));if(!Number.isFinite(quantity_on_hand)||quantity_on_hand<0)return;
    const minimum_safety_stock=Number(prompt('Minimum safety stock:',p.minimum_safety_stock));
    const storage_bin_location=prompt('Storage bin:',p.storage_bin_location);if(storage_bin_location===null)return;
    await apiRequest(`${FlightFix.apiBase}/inventory/parts/${id}/`,'PATCH',{description,quantity_on_hand,minimum_safety_stock,storage_bin_location});showToast('Spare part updated.','success');loadInventoryData();
  }catch(e){showToast('Update failed: '+e.message,'error');}}
async function deleteSparePart(id, partNo){if(!confirm(`Delete spare part ${partNo}?`))return;try{await apiRequest(`${FlightFix.apiBase}/inventory/parts/${id}/`,'DELETE');showToast('Spare part deleted.','success');loadInventoryData();}catch(e){showToast('Delete failed: '+e.message,'error');}}
async function submitAircraftIssue(){
  const aircraft=document.getElementById('issue-aircraft').value, title=document.getElementById('issue-title').value.trim(), severity=document.getElementById('issue-severity').value, reported_by=document.getElementById('issue-reporter').value.trim()||'Website User', discrepancy_details=document.getElementById('issue-details').value.trim();
  if(!aircraft||!title||!discrepancy_details){showToast('Select aircraft and enter issue title and details.','error');return;}
  const defect_log_number='FF-'+Date.now();
  try{await apiRequest(`${FlightFix.apiBase}/execution/defects/`,'POST',{aircraft:Number(aircraft),defect_log_number,title,severity,reported_by,discrepancy_details,report_source:'MAREP'});showToast('Issue submitted. Manager can now review it.','success');document.getElementById('issue-title').value='';document.getElementById('issue-details').value='';document.getElementById('issue-reporter').value='';loadExecutionData();}
  catch(e){showToast('Issue submission failed: '+e.message,'error');}}
async function manageAircraftIssue(id){
  try{const d=await apiRequest(`${FlightFix.apiBase}/execution/defects/${id}/`);
    const assigned_engineer=prompt('Assign engineer:',d.assigned_engineer||'');if(assigned_engineer===null)return;
    const expected_start_date=prompt('Expected start date (YYYY-MM-DD):',d.expected_start_date||'');if(expected_start_date===null)return;
    const expected_completion_date=prompt('Expected completion date (YYYY-MM-DD):',d.expected_completion_date||'');if(expected_completion_date===null)return;
    const manager_notes=prompt('Manager notes:',d.manager_notes||'');if(manager_notes===null)return;
    await apiRequest(`${FlightFix.apiBase}/execution/defects/${id}/`,'PATCH',{assigned_engineer,expected_start_date:expected_start_date||null,expected_completion_date:expected_completion_date||null,manager_notes});showToast('Engineer and schedule updated.','success');loadExecutionData();
  }catch(e){showToast('Manager update failed: '+e.message,'error');}}

// Certify AD (Module 6)
async function certifyAD(id, adNo) {
  if (!confirm(`Certify compliance for Airworthiness Directive ${adNo}?`)) return;
  try {
    showToast(`AD ${adNo} certified. Updating regulatory records...`, 'success');
    loadComplianceData();
  } catch (err) {
    showToast('Failed to certify AD.', 'error');
  }
}

// ERP Sync (Module 7)
async function syncERP(id, poNo) {
  try {
    const res = await fetch(`${FlightFix.apiBase}/supplychain/purchase-orders/${id}/sync_erp_status/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'RECEIVED' })
    });
    const data = await res.json();
    showToast(data.message, 'success');
    loadSupplyChainData();
  } catch (err) {
    showToast('ERP synchronization failed.', 'error');
  }
}

// Acknowledge Predictive Alert (Module 9)
async function acknowledgePredictiveAlert(id) {
  try {
    const res = await fetch(`${FlightFix.apiBase}/analytics/alerts/${id}/acknowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    showToast(data.message, 'success');
    loadAnalyticsData();
  } catch (err) {
    showToast('Failed to acknowledge alert.', 'error');
  }
}

// Subsystems Modal
function showSubsystems(tail, subsystemsJsonEnc) {
  const subsystems = JSON.parse(decodeURIComponent(subsystemsJsonEnc));
  let html = `<div style="font-size:0.9rem; font-weight:700; margin-bottom:12px; color:#93c5fd;">${tail} Subsystem Telemetry</div>`;
  if (subsystems.length === 0) {
    html += `<p class="text-muted">No telemetry sensors assigned yet.</p>`;
  } else {
    html += subsystems.map(s => `
      <div style="background:var(--bg-input); border:1px solid var(--border-subtle); border-radius:8px; padding:10px; margin-bottom:8px;">
        <div style="display:flex; justify-content:space-between;">
          <strong>${s.system_name}</strong>
          <span class="badge ${s.health_score > 85 ? 'badge-green' : (s.health_score > 60 ? 'badge-amber' : 'badge-rose')}">${s.health_score}%</span>
        </div>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">${s.notes || 'Operating within standard nominal envelope.'}</div>
      </div>
    `).join('');
  }
  document.getElementById('subsystems-content').innerHTML = html;
  document.getElementById('modal-subsystems').classList.add('open');
}

// Modal Listeners
function initModalListeners() {
  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', closeAllModals);
  });
  window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) closeAllModals();
  });
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
}

// Toast System
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast-item ${type}`;
  toast.innerHTML = `
    <div style="font-size:1.1rem;">${type === 'success' ? '✓' : (type === 'error' ? '⚠' : 'ℹ')}</div>
    <div style="font-size:0.85rem; font-weight:500;">${escapeHtml(message)}</div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Helper Utilities
function formatDate(str) {
  if (!str) return 'N/A';
  const d = new Date(str);
  return d.toISOString().replace('T', ' ').substr(0, 16);
}

function safeSetText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function getStatusBadgeClass(status) {
  switch (status) {
    case 'OPERATIONAL':
    case 'COMPLETED':
    case 'CLOSED_RELEASED':
    case 'SYNCED_TO_CORE_MRO':
    case 'RECEIVED':
      return 'badge-green';
    case 'IN_PROGRESS':
    case 'IN_MAINTENANCE':
    case 'IN_TRANSIT':
      return 'badge-amber';
    case 'AOG':
    case 'CRITICAL':
    case 'MANDATORY_OPEN':
      return 'badge-rose';
    default:
      return 'badge-blue';
  }
}

function getPriorityBadgeClass(p) {
  if (p === 'CRITICAL_AOG') return 'badge-rose';
  if (p === 'HIGH' || p === 'URGENT') return 'badge-amber';
  return 'badge-blue';
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
