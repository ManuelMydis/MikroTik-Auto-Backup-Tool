/**
 * MikroTik Auto Backup Tool - Frontend JavaScript
 * Handles all UI interactions and API communications
 */

// API Configuration
const API_BASE = '/api';
const REFRESH_INTERVAL = 30000; // 30 seconds

// State Management
let state = {
  routers: [],
  backups: [],
  schedules: [],
  settings: {},
  darkMode: localStorage.getItem('darkMode') === 'true',
  refreshTimer: null,
  stats: {
    total_routers: 0,
    online_routers: 0,
    offline_routers: 0,
    total_size_mb: 0
  }
};

// DOM Elements
const elements = {
  // Theme
  themeToggle: document.getElementById('theme-toggle'),

  // Stats
  totalRouters: document.getElementById('total-routers'),
  onlineRouters: document.getElementById('online-routers'),
  offlineRouters: document.getElementById('offline-routers'),
  totalSize: document.getElementById('total-size'),

  // Buttons
  addRouterBtn: document.getElementById('add-router-btn'),
  addRouterSectionBtn: document.getElementById('add-router-section-btn'),
  refreshBtn: document.getElementById('refresh-btn'),
  createScheduleBtn: document.getElementById('create-schedule-btn'),
  testConnectionBtn: document.getElementById('test-connection'),
  updateRouterStatusBtn: document.getElementById('update-router-status'),

  // Containers
  routersContainer: document.getElementById('routers-container'),
  backupsContainer: document.getElementById('backups-container'),
  schedulesContainer: document.getElementById('schedules-container'),
  schedulerStatus: document.getElementById('scheduler-status'),

  // Modals
  addRouterModal: document.getElementById('add-router-modal'),
  createScheduleModal: document.getElementById('create-schedule-modal'),
  editRouterModal: document.getElementById('edit-router-modal'),

  // Forms
  addRouterForm: document.getElementById('add-router-form'),
  createScheduleForm: document.getElementById('create-schedule-form'),
  editRouterForm: document.getElementById('edit-router-form'),

  // Notifications
  notification: document.getElementById('notification'),
  loadingOverlay: document.getElementById('loading-overlay')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  init();
});

// Main Initialization
async function init() {
  try {
    // Initialize theme
    initTheme();

    // Setup event listeners
    setupEventListeners();

    // Load initial data
    await Promise.all([
      loadStats(),
      loadRouters(),
      loadBackups(),
      loadSchedules(),
      loadSettings()
    ]);

    // Start auto-refresh
    startAutoRefresh();

    console.log('MikroTik Backup Manager initialized successfully');
  } catch (error) {
    console.error('Initialization failed:', error);
    showNotification('Failed to initialize application', 'error');
  }
}

// Theme Management
function initTheme() {
  if (state.darkMode) {
    document.body.classList.add('theme-dark');
  }

  // Set correct icon based on current theme
  const icon = elements.themeToggle.querySelector('i');
  icon.className = state.darkMode ? 'fas fa-sun' : 'fas fa-moon';

  elements.themeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
  state.darkMode = !state.darkMode;
  localStorage.setItem('darkMode', state.darkMode);

  document.body.classList.toggle('theme-dark');
  const icon = elements.themeToggle.querySelector('i');
  icon.className = state.darkMode ? 'fas fa-sun' : 'fas fa-moon';
}

// Event Listeners Setup
function setupEventListeners() {
  // Modal close buttons
  document.querySelectorAll('.modal-close').forEach(button => {
    button.addEventListener('click', closeAllModals);
  });

  // Close modal when clicking outside
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeAllModals();
      }
    });
  });

  // Refresh button
  elements.refreshBtn.addEventListener('click', refreshAll);

  // Add router buttons
  elements.addRouterBtn.addEventListener('click', () => showModal('add-router-modal'));
  if (elements.addRouterSectionBtn) {
    elements.addRouterSectionBtn.addEventListener('click', () => showModal('add-router-modal'));
  }

  // Create schedule button
  elements.createScheduleBtn.addEventListener('click', () => showModal('create-schedule-modal'));

  // Form submissions
  elements.addRouterForm.addEventListener('submit', handleAddRouter);
  elements.createScheduleForm.addEventListener('submit', handleCreateSchedule);
  elements.editRouterForm.addEventListener('submit', handleEditRouter);

  // Test connection button
  document.getElementById('test-connection').addEventListener('click', handleTestConnection);

  // Update router status button
  document.getElementById('update-router-status').addEventListener('click', handleUpdateRouterStatus);

  // Schedule form preview updates
  document.getElementById('schedule-name').addEventListener('input', updateSchedulePreview);
  document.getElementById('schedule-cron').addEventListener('input', updateSchedulePreview);
  document.getElementById('schedule-router').addEventListener('change', updateSchedulePreview);
  document.getElementById('schedule-type').addEventListener('change', updateSchedulePreview);
  document.getElementById('schedule-frequency').addEventListener('change', updateSchedulePreview);
  document.getElementById('schedule-time').addEventListener('change', generateCronExpression);
  document.getElementById('schedule-day').addEventListener('change', generateCronExpression);
  document.getElementById('schedule-month-day').addEventListener('change', generateCronExpression);
}

// API Communication
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API call failed: ${endpoint}`, error);
    throw error;
  }
}

// Notification System
function showNotification(message, type = 'success') {
  const notification = elements.notification;
  notification.textContent = message;
  notification.className = `notification ${type} show`;

  setTimeout(() => {
    notification.className = 'notification hidden';
  }, 4000);
}

// Loading Management
function showLoading(message = 'Loading...') {
  elements.loadingOverlay.querySelector('p').textContent = message;
  elements.loadingOverlay.classList.add('show');
}

function hideLoading() {
  elements.loadingOverlay.classList.remove('show');
}

// Modal Management
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.add('show'), 10);
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.classList.remove('show');
    setTimeout(() => modal.classList.add('hidden'), 300);
  });
}

// Data Loading Functions
async function loadStats() {
  try {
    const response = await apiCall('/stats');
    if (response.success) {
      updateStatsDisplay(response.stats);
      state.stats = response.stats;
    }
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
}

function updateStatsDisplay(stats) {
  animateNumber(elements.totalRouters, stats.total_routers);
  animateNumber(elements.onlineRouters, stats.online_routers);
  animateNumber(elements.offlineRouters, stats.offline_routers);
  elements.totalSize.textContent = `${stats.total_size_mb} MB`;
}

async function loadRouters() {
  try {
    const response = await apiCall('/routers');
    if (response.success) {
      state.routers = response.routers;
      renderRouters();
    }
  } catch (error) {
    console.error('Failed to load routers:', error);
    showNotification('Failed to load routers', 'error');
  }
}

async function loadBackups() {
  try {
    const response = await apiCall('/backups');
    if (response.success) {
      state.backups = response.backups;
      renderBackups();
    }
  } catch (error) {
    console.error('Failed to load backups:', error);
  }
}

async function loadSchedules() {
  try {
    const response = await apiCall('/schedules');
    if (response.success) {
      state.schedules = response.schedules;
      renderSchedules();
      updateScheduleFormRouters();
    }
  } catch (error) {
    console.error('Failed to load schedules:', error);
  }
}

async function loadSettings() {
  try {
    const response = await apiCall('/settings');
    if (response.success) {
      state.settings = response.settings;
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
  }
}

// Rendering Functions
function renderRouters() {
  if (state.routers.length === 0) {
    elements.routersContainer.innerHTML = `
      <div class="empty-state fade-in">
        <div class="empty-header">
          <div class="empty-icon">
            <i class="fas fa-router"></i>
          </div>
          <h3>No Routers Configured</h3>
        </div>
        <p>Get started by adding your first MikroTik router to the system.</p>
        <button id="add-first-router" class="btn-primary" onclick="showModal('add-router-modal')">
          <i class="fas fa-plus"></i>
          Add Your First Router
        </button>
      </div>
    `;
    return;
  }

  elements.routersContainer.innerHTML = state.routers.map(router => `
    <div class="router-card professional-router-card fade-in" data-id="${router.id}">
      <div class="router-card-header">
        <div class="router-main-info">
          <div class="router-identity">
            <h3 class="router-name">${escapeHtml(router.name)}</h3>
            <div class="router-host">${escapeHtml(router.host)}</div>
          </div>
          <div class="router-status-badge status-${router.status}">
            <span class="status-indicator ${router.status}"></span>
            <span class="status-text">${router.status.charAt(0).toUpperCase() + router.status.slice(1)}</span>
          </div>
        </div>

        <div class="router-details">
          <div class="router-meta">
            <div class="meta-item">
              <i class="fas fa-calendar"></i>
              <span>Last backup: ${router.last_backup ? new Date(router.last_backup).toLocaleString() : 'Never'}</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-user"></i>
              <span>User: ${escapeHtml(router.username)}</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-plug"></i>
              <span>Port: ${router.port}</span>
            </div>
            ${router.use_ssl ? '<div class="meta-item ssl-indicator"><i class="fas fa-shield-alt"></i><span>SSL Enabled</span></div>' : ''}
          </div>

          ${router.notes ? `
            <div class="router-notes">
              <i class="fas fa-sticky-note"></i>
              <span>${escapeHtml(router.notes)}</span>
            </div>
          ` : ''}
        </div>
      </div>

      <div class="router-card-actions">
        <button class="action-btn backup-btn" onclick="backupRouter(${router.id})" title="Create backup">
          <i class="fas fa-download"></i>
          <span>Backup Now</span>
        </button>
        <button class="action-btn edit-btn" onclick="editRouter(${router.id})" title="Edit router">
          <i class="fas fa-edit"></i>
          <span>Edit</span>
        </button>
        <button class="action-btn delete-btn" onclick="deleteRouter(${router.id})" title="Delete router">
          <i class="fas fa-trash"></i>
          <span>Delete</span>
        </button>
      </div>
    </div>
  `).join('');
}

function renderBackups() {
  if (state.backups.length === 0) {
    elements.backupsContainer.innerHTML = `
      <div class="backups-empty-state fade-in">
        <div class="empty-icon">
          <i class="fas fa-file-archive"></i>
        </div>
        <h3>No Backups Yet</h3>
        <p>Create your first backup to see the history here.</p>
        <button class="btn-primary" onclick="document.getElementById('add-router-btn').click()">
          <i class="fas fa-plus"></i>
          Add Router & Create Backup
        </button>
      </div>
    `;
    return;
  }

  elements.backupsContainer.innerHTML = state.backups.slice(0, 10).map(backup => `
    <div class="backup-item professional-backup-item fade-in">
      <div class="backup-item-header">
        <div class="backup-main-info">
          <div class="backup-filename">
            <h4>${escapeHtml(backup.filename)}</h4>
            <div class="backup-router">${escapeHtml(backup.router_name)}</div>
          </div>
          <div class="backup-status">
            <span class="backup-size">${formatFileSize(backup.file_size)}</span>
          </div>
        </div>

        <div class="backup-details">
          <div class="backup-meta-info">
            <div class="meta-info-item">
              <i class="fas fa-calendar-alt"></i>
              <span>${new Date(backup.created_at).toLocaleString()}</span>
            </div>
            <div class="meta-info-item">
              <i class="fas fa-router"></i>
              <span>Router: ${escapeHtml(backup.router_name)}</span>
            </div>
            <div class="meta-info-item">
              <i class="fas fa-weight"></i>
              <span>Size: ${formatFileSize(backup.file_size)}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="backup-item-actions">
        <a href="/api/download/${encodeURIComponent(backup.filename)}"
           class="backup-download-btn" download title="Download backup">
          <i class="fas fa-download"></i>
          <span>Download</span>
        </a>
      </div>
    </div>
  `).join('');
}

function renderSchedules() {
  if (state.schedules.length === 0) {
    elements.schedulesContainer.innerHTML = `
      <div class="empty-state fade-in">
        <p>No schedules created yet. Create your first schedule to automate backups.</p>
      </div>
    `;
    return;
  }

  elements.schedulesContainer.innerHTML = state.schedules.map(schedule => `
    <div class="schedule-item fade-in">
      <div class="schedule-info">
        <h4>${escapeHtml(schedule.name)}</h4>
        <div class="schedule-meta">
          Router: ${escapeHtml(schedule.router_name)} •
          Cron: ${escapeHtml(schedule.cron_expression)} •
          Type: ${schedule.backup_type}
        </div>
      </div>
      <div class="schedule-actions">
        <button class="btn-danger" onclick="deleteSchedule(${schedule.id})" title="Delete schedule">
          <i class="fas fa-trash"></i>
          Delete
        </button>
      </div>
    </div>
  `).join('');
}

// Router Management
async function handleAddRouter(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const routerData = {
    name: formData.get('router-name').trim(),
    host: formData.get('router-host').trim(),
    username: formData.get('router-username').trim(),
    password: formData.get('router-password'),
    port: parseInt(formData.get('router-port')) || 8728,
    use_ssl: formData.has('router-use-ssl'),
    notes: formData.get('router-notes').trim()
  };

  // Validation
  if (!routerData.name || !routerData.host || !routerData.username || !routerData.password) {
    showNotification('Please fill in all required fields', 'error');
    return;
  }

  try {
    showLoading('Adding router...');
    const response = await apiCall('/routers', {
      method: 'POST',
      body: JSON.stringify(routerData)
    });

    if (response.success) {
      showNotification('Router added successfully!', 'success');
      closeAllModals();
      e.target.reset();
      await refreshAll();
    } else {
      showNotification(response.error || 'Failed to add router', 'error');
    }
  } catch (error) {
    showNotification('Failed to add router', 'error');
  } finally {
    hideLoading();
  }
}

async function editRouter(routerId) {
  const router = state.routers.find(r => r.id === routerId);
  if (!router) return;

  // Populate edit form
  document.getElementById('edit-router-id').value = router.id;
  document.getElementById('edit-router-name').value = router.name;
  document.getElementById('edit-router-host').value = router.host;
  document.getElementById('edit-router-username').value = router.username;
  document.getElementById('edit-router-password').value = router.password;
  document.getElementById('edit-router-port').value = router.port;
  document.getElementById('edit-router-use-ssl').checked = router.use_ssl;
  document.getElementById('edit-router-notes').value = router.notes || '';

  showModal('edit-router-modal');
}

async function handleEditRouter(e) {
  e.preventDefault();

  const routerId = parseInt(document.getElementById('edit-router-id').value);
  const formData = new FormData(e.target);
  const routerData = {
    name: formData.get('edit-router-name').trim(),
    host: formData.get('edit-router-host').trim(),
    username: formData.get('edit-router-username').trim(),
    password: formData.get('edit-router-password'),
    port: parseInt(formData.get('edit-router-port')) || 8728,
    use_ssl: formData.has('edit-router-use-ssl'),
    notes: formData.get('edit-router-notes').trim()
  };

  // Validation
  if (!routerData.name || !routerData.host || !routerData.username || !routerData.password) {
    showNotification('Please fill in all required fields', 'error');
    return;
  }

  try {
    showLoading('Updating router...');
    const response = await apiCall(`/routers/${routerId}`, {
      method: 'PUT',
      body: JSON.stringify(routerData)
    });

    if (response.success) {
      showNotification('Router updated successfully!', 'success');
      closeAllModals();
      await refreshAll();
    } else {
      showNotification(response.error || 'Failed to update router', 'error');
    }
  } catch (error) {
    showNotification('Failed to update router', 'error');
  } finally {
    hideLoading();
  }
}

async function deleteRouter(routerId) {
  if (!confirm('Are you sure you want to delete this router? This will also delete all associated backups and schedules.')) {
    return;
  }

  try {
    showLoading('Deleting router...');
    const response = await apiCall(`/routers/${routerId}`, {
      method: 'DELETE'
    });

    if (response.success) {
      showNotification('Router deleted successfully!', 'success');
      await refreshAll();
    } else {
      showNotification(response.error || 'Failed to delete router', 'error');
    }
  } catch (error) {
    showNotification('Failed to delete router', 'error');
  } finally {
    hideLoading();
  }
}

async function handleTestConnection() {
  const host = document.getElementById('router-host').value.trim();
  const username = document.getElementById('router-username').value.trim();
  const password = document.getElementById('router-password').value;
  const port = parseInt(document.getElementById('router-port').value) || 8728;
  const use_ssl = document.getElementById('router-use-ssl').checked;

  if (!host || !username || !password) {
    showNotification('Please fill in host, username, and password', 'error');
    return;
  }

  try {
    showLoading('Testing connection...');
    const response = await apiCall('/test-connection', {
      method: 'POST',
      body: JSON.stringify({ host, username, password, port, use_ssl })
    });

    if (response.success && response.connected) {
      showNotification('✅ Connection successful!', 'success');
    } else {
      showNotification('❌ Connection failed', 'error');
    }
  } catch (error) {
    showNotification('Connection test failed', 'error');
  } finally {
    hideLoading();
  }
}

async function handleUpdateRouterStatus() {
  const routerId = parseInt(document.getElementById('edit-router-id').value);
  const router = state.routers.find(r => r.id === routerId);

  if (!router) {
    showNotification('Router not found', 'error');
    return;
  }

  try {
    showLoading('Testing connection...');
    const response = await apiCall('/test-connection', {
      method: 'POST',
      body: JSON.stringify({
        host: router.host,
        username: router.username,
        password: router.password,
        port: router.port,
        use_ssl: router.use_ssl
      })
    });

    if (response.success && response.connected) {
      showNotification('✅ Router is online!', 'success');
    } else {
      showNotification('❌ Router is offline', 'error');
    }
  } catch (error) {
    showNotification('Connection test failed', 'error');
  } finally {
    hideLoading();
  }
}

// Backup Operations
async function backupRouter(routerId) {
  try {
    showLoading('Creating backup...');
    const response = await apiCall(`/backup/${routerId}`, {
      method: 'POST'
    });

    if (response.success) {
      showNotification(`✅ Backup successful! File: ${response.filename}`, 'success');

      // Trigger file download
      const link = document.createElement('a');
      link.href = `/api/download/${encodeURIComponent(response.filename)}`;
      link.download = response.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      await refreshAll();
    } else {
      showNotification(response.error || 'Backup failed', 'error');
    }
  } catch (error) {
    showNotification('Backup failed', 'error');
  } finally {
    hideLoading();
  }
}

// Schedule Management
async function handleCreateSchedule(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const scheduleData = {
    router_id: parseInt(formData.get('schedule-router')),
    name: formData.get('schedule-name').trim(),
    cron_expression: formData.get('schedule-cron').trim(),
    backup_type: formData.get('schedule-type')
  };

  // Validation
  if (!scheduleData.router_id || !scheduleData.name || !scheduleData.cron_expression) {
    showNotification('Please fill in all required fields', 'error');
    return;
  }

  // Basic cron validation
  if (!isValidCronExpression(scheduleData.cron_expression)) {
    showNotification('Invalid cron expression format', 'error');
    return;
  }

  try {
    showLoading('Creating schedule...');
    const response = await apiCall('/schedules', {
      method: 'POST',
      body: JSON.stringify(scheduleData)
    });

    if (response.success) {
      showNotification('Schedule created successfully!', 'success');
      closeAllModals();
      e.target.reset();
      await refreshAll();
    } else {
      showNotification(response.error || 'Failed to create schedule', 'error');
    }
  } catch (error) {
    showNotification('Failed to create schedule', 'error');
  } finally {
    hideLoading();
  }
}

async function deleteSchedule(scheduleId) {
  if (!confirm('Are you sure you want to delete this schedule?')) {
    return;
  }

  try {
    showLoading('Deleting schedule...');
    const response = await apiCall(`/schedules/${scheduleId}`, {
      method: 'DELETE'
    });

    if (response.success) {
      showNotification('Schedule deleted successfully!', 'success');
      await refreshAll();
    } else {
      showNotification(response.error || 'Failed to delete schedule', 'error');
    }
  } catch (error) {
    showNotification('Failed to delete schedule', 'error');
  } finally {
    hideLoading();
  }
}

// Utility Functions
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function animateNumber(element, target) {
  const start = parseInt(element.textContent) || 0;
  const difference = target - start;
  const increment = difference > 0 ? 1 : -1;
  const duration = 500;
  const steps = Math.abs(difference) || 1;
  const stepTime = duration / steps;

  let current = start;
  const timer = setInterval(() => {
    current += increment;
    element.textContent = Math.max(0, current); // Prevent negative numbers

    if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
      element.textContent = target; // Ensure final value is exact
      clearInterval(timer);
    }
  }, stepTime);
}

function isValidCronExpression(expr) {
  // Basic validation for cron expressions
  const parts = expr.trim().split(/\s+/);
  return parts.length >= 2 && parts.length <= 5;
}

function updateScheduleFormRouters() {
  const routerSelect = document.getElementById('schedule-router');
  if (!routerSelect) return;

  // Clear existing options except the first one
  while (routerSelect.children.length > 1) {
    routerSelect.removeChild(routerSelect.lastChild);
  }

  // Add router options
  state.routers.forEach(router => {
    const option = document.createElement('option');
    option.value = router.id;
    option.textContent = `${router.name} (${router.host})`;
    routerSelect.appendChild(option);
  });
}

function startAutoRefresh() {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
  }

  state.refreshTimer = setInterval(async () => {
    try {
      await Promise.all([
        loadStats(),
        loadRouters(),
        loadBackups()
      ]);
    } catch (error) {
      console.error('Auto-refresh failed:', error);
    }
  }, REFRESH_INTERVAL);
}

async function refreshAll() {
  try {
    await Promise.all([
      loadStats(),
      loadRouters(),
      loadBackups(),
      loadSchedules()
    ]);
  } catch (error) {
    console.error('Manual refresh failed:', error);
    showNotification('Refresh failed', 'error');
  }
}

// Enhanced Form Functions
function togglePasswordVisibility(passwordFieldId) {
  const passwordField = document.getElementById(passwordFieldId);
  const toggleButton = passwordField.parentElement.querySelector('.password-toggle i');

  if (passwordField.type === 'password') {
    passwordField.type = 'text';
    toggleButton.className = 'fas fa-eye-slash';
  } else {
    passwordField.type = 'password';
    toggleButton.className = 'fas fa-eye';
  }
}

function updateCronFromFrequency() {
  const frequencySelect = document.getElementById('schedule-frequency');
  const timeInput = document.getElementById('schedule-time');
  const daySelect = document.getElementById('schedule-day');
  const monthDaySelect = document.getElementById('schedule-month-day');
  const customCronDiv = document.getElementById('custom-cron');
  const timeSelectionDiv = document.getElementById('time-selection');
  const daySelectionDiv = document.getElementById('day-selection');
  const monthDaySelectionDiv = document.getElementById('month-day-selection');

  const frequency = frequencySelect.value;

  // Hide all conditional sections first
  timeSelectionDiv.style.display = 'none';
  daySelectionDiv.style.display = 'none';
  monthDaySelectionDiv.style.display = 'none';
  customCronDiv.style.display = 'none';

  switch(frequency) {
    case 'daily':
      timeSelectionDiv.style.display = 'block';
      generateCronExpression();
      break;
    case 'weekly':
      timeSelectionDiv.style.display = 'block';
      daySelectionDiv.style.display = 'block';
      generateCronExpression();
      break;
    case 'monthly':
      timeSelectionDiv.style.display = 'block';
      monthDaySelectionDiv.style.display = 'block';
      generateCronExpression();
      break;
    case 'hourly':
      generateCronExpression();
      break;
    case 'custom':
      customCronDiv.style.display = 'block';
      document.getElementById('schedule-cron').value = '0 2 * * *';
      generateCronExpression();
      break;
  }

  updateSchedulePreview();
}

function generateCronExpression() {
  const frequency = document.getElementById('schedule-frequency').value;
  const timeInput = document.getElementById('schedule-time');
  const daySelect = document.getElementById('schedule-day');
  const monthDaySelect = document.getElementById('schedule-month-day');
  const cronInput = document.getElementById('schedule-cron');

  let cronExpression = '';

  switch(frequency) {
    case 'daily':
      if (timeInput.value) {
        const [hours, minutes] = timeInput.value.split(':');
        cronExpression = `${minutes} ${hours} * * *`;
      }
      break;
    case 'weekly':
      if (timeInput.value && daySelect.value !== undefined) {
        const [hours, minutes] = timeInput.value.split(':');
        cronExpression = `${minutes} ${hours} * * ${daySelect.value}`;
      }
      break;
    case 'monthly':
      if (timeInput.value && monthDaySelect.value) {
        const [hours, minutes] = timeInput.value.split(':');
        if (monthDaySelect.value === 'last') {
          cronExpression = `${minutes} ${hours} L * *`;
        } else {
          cronExpression = `${minutes} ${hours} ${monthDaySelect.value} * *`;
        }
      }
      break;
    case 'hourly':
      cronExpression = '0 */6 * * *';
      break;
    case 'custom':
      cronExpression = cronInput.value || '0 2 * * *';
      break;
  }

  if (cronInput) {
    cronInput.value = cronExpression;
  }
}

function setCronExpression(expression) {
  const cronInput = document.getElementById('schedule-cron');
  cronInput.value = expression;
  cronInput.focus();
  updateSchedulePreview();
}

function updateSchedulePreview() {
  const previewContent = document.getElementById('schedule-preview-content');
  const routerSelect = document.getElementById('schedule-router');
  const nameInput = document.getElementById('schedule-name');
  const frequencySelect = document.getElementById('schedule-frequency');
  const timeInput = document.getElementById('schedule-time');
  const daySelect = document.getElementById('schedule-day');
  const monthDaySelect = document.getElementById('schedule-month-day');
  const cronInput = document.getElementById('schedule-cron');
  const typeSelect = document.getElementById('schedule-type');

  if (!nameInput.value || !frequencySelect.value || !routerSelect.value) {
    previewContent.innerHTML = `
      <p><i class="fas fa-info-circle"></i> Fill in the details above to see a preview of your schedule</p>
    `;
    return;
  }

  const selectedRouter = state.routers.find(r => r.id == routerSelect.value);
  const frequencyDescription = getFrequencyDescription();

  previewContent.innerHTML = `
    <div class="preview-item">
      <strong><i class="fas fa-calendar-check"></i> Schedule:</strong> ${escapeHtml(nameInput.value)}<br>
      <strong><i class="fas fa-router"></i> Router:</strong> ${escapeHtml(selectedRouter?.name || 'Unknown')}<br>
      <strong><i class="fas fa-clock"></i> Frequency:</strong> ${frequencyDescription}<br>
      <strong><i class="fas fa-database"></i> Type:</strong> ${typeSelect.value === 'full' ? 'Full Backup' : 'Incremental Backup'}
    </div>
  `;
}

function getFrequencyDescription() {
  const frequency = document.getElementById('schedule-frequency').value;
  const timeInput = document.getElementById('schedule-time');
  const daySelect = document.getElementById('schedule-day');
  const monthDaySelect = document.getElementById('schedule-month-day');

  switch(frequency) {
    case 'daily':
      return timeInput.value ? `Daily at ${timeInput.value}` : 'Daily';
    case 'weekly':
      const dayName = daySelect.options[daySelect.selectedIndex].text;
      return timeInput.value ? `Weekly on ${dayName} at ${timeInput.value}` : `Weekly on ${dayName}`;
    case 'monthly':
      const monthDayText = monthDaySelect.options[monthDaySelect.selectedIndex].text;
      return timeInput.value ? `Monthly on ${monthDayText} at ${timeInput.value}` : `Monthly on ${monthDayText}`;
    case 'hourly':
      return 'Every 6 hours';
    case 'custom':
      const cronExpression = document.getElementById('schedule-cron').value;
      return `Custom: ${cronExpression}`;
    default:
      return 'Not specified';
  }
}

// Global Functions (called from HTML onclick)
window.backupRouter = backupRouter;
window.editRouter = editRouter;
window.deleteRouter = deleteRouter;
window.deleteSchedule = deleteSchedule;
window.togglePasswordVisibility = togglePasswordVisibility;
window.setCronExpression = setCronExpression;

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + R for refresh
  if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
    e.preventDefault();
    refreshAll();
  }

  // Escape to close modals
  if (e.key === 'Escape') {
    closeAllModals();
  }

  // Ctrl/Cmd + D for theme toggle
  if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
    e.preventDefault();
    toggleTheme();
  }
});

// Error Handling
window.addEventListener('error', (e) => {
  console.error('Global error:', e.error);
  showNotification('An unexpected error occurred', 'error');
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled promise rejection:', e.reason);
  showNotification('An unexpected error occurred', 'error');
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
