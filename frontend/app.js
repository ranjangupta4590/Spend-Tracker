// SpendTrack API Client & Dashboard Controller

let currentIdempotencyKey = generateUUID();
let currentPage = 1;
const pageSize = 10;
let currentExpenses = [];
let debounceTimer = null;

// Icons and styling mapping for categories
const CATEGORY_STYLES = {
  "Software & Tools": { icon: "dns", color: "text-primary", barColor: "bg-primary", badgeBg: "bg-secondary-container/60", badgeText: "text-on-secondary-container" },
  "Office & Facilities": { icon: "apartment", color: "text-secondary", barColor: "bg-secondary", badgeBg: "bg-surface-container-high", badgeText: "text-on-surface" },
  "Travel & Transport": { icon: "flight_takeoff", color: "text-tertiary", barColor: "bg-tertiary-container", badgeBg: "bg-surface-container-high", badgeText: "text-on-surface" },
  "Marketing & Ads": { icon: "campaign", color: "text-on-surface-variant", barColor: "bg-outline", badgeBg: "bg-surface-container-high", badgeText: "text-on-surface" },
  "Meals & Dining": { icon: "restaurant", color: "text-primary", barColor: "bg-primary-fixed-dim", badgeBg: "bg-secondary-container/40", badgeText: "text-on-secondary-container" },
  "Other": { icon: "receipt", color: "text-on-surface-variant", barColor: "bg-surface-container-highest", badgeBg: "bg-surface-container-high", badgeText: "text-on-surface" }
};

function getCategoryStyle(cat) {
  for (const key in CATEGORY_STYLES) {
    if (cat.toLowerCase().includes(key.toLowerCase()) || key.toLowerCase().includes(cat.toLowerCase())) {
      return CATEGORY_STYLES[key];
    }
  }
  return CATEGORY_STYLES["Other"];
}

function generateUUID() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function formatCurrency(amount) {
  const num = Number(amount) || 0;
  return '$' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function showToast(title, subtitle = "", isError = false) {
  const toast = document.getElementById('toastNotification');
  const msgElem = document.getElementById('toastMessage');
  const subElem = document.getElementById('toastSubMessage');
  const iconElem = document.getElementById('toastIcon');

  if (!toast || !msgElem) return;

  msgElem.textContent = title;
  if (subElem) subElem.textContent = subtitle;

  if (isError) {
    iconElem.className = "w-6 h-6 rounded-full bg-error-container text-error flex items-center justify-center";
    iconElem.innerHTML = '<span class="material-symbols-outlined text-[16px]">error</span>';
  } else {
    iconElem.className = "w-6 h-6 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center";
    iconElem.innerHTML = '<span class="material-symbols-outlined text-[16px]">check_circle</span>';
  }

  toast.classList.remove('-translate-y-24', 'opacity-0', 'pointer-events-none');
  toast.classList.add('translate-y-0', 'opacity-100');

  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('-translate-y-24', 'opacity-0', 'pointer-events-none');
  }, 3500);
}

function redirectToLogin() {
  localStorage.removeItem("spendtrack_token");
  localStorage.removeItem("spendtrack_user");
  window.location.href = "/login";
}

function logout() {
  redirectToLogin();
}

function getApiHeaders(extraHeaders = {}) {
  const token = localStorage.getItem("spendtrack_token");
  const headers = { ...extraHeaders };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function loadUserProfile() {
  try {
    const res = await fetch('/auth/me', { headers: getApiHeaders() });
    if (res.status === 401 || res.status === 403) {
      redirectToLogin();
      return;
    }
    if (res.ok) {
      const user = await res.json();
      const badge = document.getElementById('userEmailBadge');
      if (badge) badge.textContent = user.email;
      const mobileBadge = document.getElementById('mobileUserEmailBadge');
      if (mobileBadge) mobileBadge.textContent = user.email;
      localStorage.setItem("spendtrack_user", JSON.stringify(user));
    }
  } catch (err) {
    console.error("Failed to load user profile:", err);
  }
}

// Month & Period Selection State
const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];
const MONTH_SHORT = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
];

let selectedYear = null;
let selectedMonth = null;
let pickerYear = new Date().getFullYear();

function renderMonthGrid() {
  const container = document.getElementById('monthGridContainer');
  const yearDisplay = document.getElementById('pickerYearDisplay');
  if (!container || !yearDisplay) return;

  yearDisplay.textContent = pickerYear.toString();
  container.innerHTML = '';

  const today = new Date();
  const currentCalYear = today.getFullYear();
  const currentCalMonth = today.getMonth() + 1;

  for (let m = 1; m <= 12; m++) {
    const btn = document.createElement('button');
    btn.type = 'button';
    const isSelected = (pickerYear === selectedYear && m === selectedMonth);
    const isCurrent = (pickerYear === currentCalYear && m === currentCalMonth);

    let classes = "py-2 px-2 rounded-xl text-xs font-medium transition-all text-center focus:outline-none cursor-pointer ";
    if (isSelected) {
      classes += "bg-primary text-on-primary font-semibold shadow-xs";
    } else if (isCurrent) {
      classes += "border border-primary/50 text-primary hover:bg-primary/10 font-medium";
    } else {
      classes += "hover:bg-surface-container-highest text-on-surface";
    }

    btn.className = classes;
    btn.textContent = MONTH_SHORT[m - 1];
    btn.onclick = (e) => {
      e.stopPropagation();
      selectMonth(m);
    };
    container.appendChild(btn);
  }
}

function toggleMonthPickerDropdown(e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById('monthPickerDropdown');
  const chevron = document.getElementById('headerMonthChevron');
  if (!dropdown) return;

  const isHidden = dropdown.classList.contains('hidden');
  if (isHidden) {
    pickerYear = selectedYear || new Date().getFullYear();
    renderMonthGrid();
    dropdown.classList.remove('hidden');
    if (chevron) chevron.classList.add('rotate-180');
  } else {
    closeMonthPickerDropdown();
  }
}

function closeMonthPickerDropdown() {
  const dropdown = document.getElementById('monthPickerDropdown');
  const chevron = document.getElementById('headerMonthChevron');
  if (dropdown) dropdown.classList.add('hidden');
  if (chevron) chevron.classList.remove('rotate-180');
}

function pickerChangeYear(delta, e) {
  if (e) e.stopPropagation();
  const newYear = pickerYear + delta;
  if (newYear >= 2000 && newYear <= 2100) {
    pickerYear = newYear;
    renderMonthGrid();
  }
}

function syncTableDateFiltersToMonth(year, month) {
  const y = year || new Date().getFullYear();
  const m = month || (new Date().getMonth() + 1);
  const padMonth = String(m).padStart(2, '0');
  const lastDay = new Date(y, m, 0).getDate();
  const startInput = document.getElementById('tableStartDateFilter');
  const endInput = document.getElementById('tableEndDateFilter');
  if (startInput) startInput.value = `${y}-${padMonth}-01`;
  if (endInput) endInput.value = `${y}-${padMonth}-${String(lastDay).padStart(2, '0')}`;
}

function selectMonth(m) {
  selectedYear = pickerYear;
  selectedMonth = m;
  closeMonthPickerDropdown();
  syncTableDateFiltersToMonth(selectedYear, selectedMonth);
  loadSummary(selectedYear, selectedMonth);
  loadExpenses(1);
}

function changeMonth(delta) {
  if (selectedYear === null || selectedMonth === null) {
    const d = new Date();
    selectedYear = d.getFullYear();
    selectedMonth = d.getMonth() + 1;
  }
  let m = selectedMonth + delta;
  let y = selectedYear;
  if (m < 1) {
    m = 12;
    y--;
  } else if (m > 12) {
    m = 1;
    y++;
  }
  if (y < 2000 || y > 2100) return;
  selectedMonth = m;
  selectedYear = y;
  pickerYear = y;
  syncTableDateFiltersToMonth(selectedYear, selectedMonth);
  loadSummary(selectedYear, selectedMonth);
  loadExpenses(1);
}

function resetToCurrentMonth(e) {
  if (e) e.stopPropagation();
  const d = new Date();
  selectedYear = d.getFullYear();
  selectedMonth = d.getMonth() + 1;
  pickerYear = selectedYear;
  closeMonthPickerDropdown();
  syncTableDateFiltersToMonth(selectedYear, selectedMonth);
  loadSummary(selectedYear, selectedMonth);
  loadExpenses(1);
}

function toggleMobileMenu(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById('mobileNavMenu');
  const icon = document.getElementById('mobileMenuIcon');
  if (!menu) return;

  const isHidden = menu.classList.contains('hidden');
  if (isHidden) {
    menu.classList.remove('hidden');
    if (icon) icon.textContent = 'close';
    closeMonthPickerDropdown();
  } else {
    closeMobileMenu();
  }
}

function closeMobileMenu() {
  const menu = document.getElementById('mobileNavMenu');
  const icon = document.getElementById('mobileMenuIcon');
  if (menu) menu.classList.add('hidden');
  if (icon) icon.textContent = 'menu';
}

// Global outside click listener to close dropdowns
document.addEventListener('click', (e) => {
  const container = document.getElementById('monthSelectorContainer');
  if (container && !container.contains(e.target)) {
    closeMonthPickerDropdown();
  }

  const mobileMenu = document.getElementById('mobileNavMenu');
  const mobileToggle = document.getElementById('mobileMenuToggleBtn');
  if (mobileMenu && !mobileMenu.contains(e.target) && mobileToggle && !mobileToggle.contains(e.target)) {
    closeMobileMenu();
  }
});

// Load Summary Dashboard Metrics
async function loadSummary(year = null, month = null) {
  try {
    if (year !== null) selectedYear = year;
    if (month !== null) selectedMonth = month;

    let url = '/summary';
    if (selectedYear !== null && selectedMonth !== null) {
      url += `?year=${selectedYear}&month=${selectedMonth}`;
    }

    const res = await fetch(url, { headers: getApiHeaders() });
    if (res.status === 401 || res.status === 403) {
      redirectToLogin();
      return;
    }
    if (!res.ok) {
      throw new Error(`Summary request failed (${res.status})`);
    }
    const data = await res.json();

    // Parse period from server if selectedYear/selectedMonth were unset
    if (data.period && (selectedYear === null || selectedMonth === null)) {
      const parts = data.period.split(' ');
      if (parts.length === 2) {
        const mIdx = MONTH_NAMES.indexOf(parts[0]) + 1;
        const yNum = parseInt(parts[1], 10);
        if (mIdx > 0 && !isNaN(yNum)) {
          selectedYear = yNum;
          selectedMonth = mIdx;
          pickerYear = yNum;
        }
      }
    }

    // Update Header Badges
    const periodBadge = document.getElementById('headerMonthBadge');
    if (periodBadge) periodBadge.textContent = data.period;

    const periodBadgeShort = document.getElementById('headerMonthBadgeShort');
    if (periodBadgeShort && data.period) {
      const parts = data.period.split(' ');
      if (parts.length === 2) {
        const mIdx = MONTH_NAMES.indexOf(parts[0]);
        const shortName = mIdx >= 0 ? MONTH_SHORT[mIdx] : parts[0];
        periodBadgeShort.textContent = `${shortName} '${parts[1].slice(-2)}`;
      }
    }

    const periodSub = document.getElementById('headerPeriodSubtitle');
    if (periodSub) periodSub.textContent = `Overview for ${data.period}`;

    // Card 1: Total Spend & Transaction Count
    const totalSpendElem = document.getElementById('metricTotalSpend');
    if (totalSpendElem) totalSpendElem.textContent = formatCurrency(data.total_spend);

    const txCountElem = document.getElementById('metricTxCount');
    if (txCountElem) txCountElem.textContent = data.transaction_count;

    // Card 2: Month-over-Month
    const momPercentElem = document.getElementById('metricMoMPercent');
    const momBadgeElem = document.getElementById('metricMoMDiffBadge');
    const momDiffAmountElem = document.getElementById('metricMoMDiffAmount');
    const momDiffIconElem = document.getElementById('metricMoMDiffIcon');
    const prevTotalElem = document.getElementById('metricPrevTotal');

    const mom = data.month_over_month;
    if (prevTotalElem) prevTotalElem.textContent = formatCurrency(mom.previous_month);

    const diff = mom.current_month - mom.previous_month;

    if (mom.change_percent === null) {
      if (momPercentElem) momPercentElem.textContent = "N/A";
      if (momDiffAmountElem) momDiffAmountElem.textContent = formatCurrency(diff);
      if (momBadgeElem) {
        momBadgeElem.className = "inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface font-label-sm text-[11px] font-semibold";
      }
    } else {
      const isPositive = diff >= 0;
      if (momPercentElem) {
        momPercentElem.textContent = (isPositive ? "+" : "") + mom.change_percent.toFixed(1) + "%";
      }
      if (momDiffAmountElem) {
        momDiffAmountElem.textContent = (isPositive ? "+$" : "-$") + Math.abs(diff).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      }
      if (momDiffIconElem) {
        momDiffIconElem.textContent = isPositive ? "arrow_upward" : "arrow_downward";
      }
      if (momBadgeElem) {
        momBadgeElem.className = isPositive
          ? "inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-[11px] font-semibold"
          : "inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-error-container text-error font-label-sm text-[11px] font-semibold";
      }
    }

    // Card 3: Top Category
    let topCategory = "None";
    let topAmount = 0;
    let topPercent = 0;

    for (const [cat, amt] of Object.entries(data.spend_by_category)) {
      if (amt > topAmount) {
        topAmount = amt;
        topCategory = cat;
        topPercent = data.category_percentages[cat] || 0;
      }
    }

    const topCatNameElem = document.getElementById('metricTopCatName');
    const topCatAmtElem = document.getElementById('metricTopCatAmount');
    const topCatBarElem = document.getElementById('metricTopCatBar');
    const topCatPctElem = document.getElementById('metricTopCatPercentText');

    if (topCatNameElem) topCatNameElem.textContent = topCategory;
    if (topCatAmtElem) topCatAmtElem.textContent = formatCurrency(topAmount);
    if (topCatBarElem) topCatBarElem.style.width = `${Math.min(100, topPercent)}%`;
    if (topCatPctElem) topCatPctElem.textContent = `Represents ${topPercent.toFixed(1)}% of total outflow`;

    // Category Breakdown Section
    const catTotalTracked = document.getElementById('categoryTotalTracked');
    if (catTotalTracked) catTotalTracked.textContent = formatCurrency(data.total_spend);

    renderCategoryCards(data.spend_by_category, data.category_percentages);

    // Budget Health Gauge (Benchmark: $10,000)
    const benchmark = 10000.00;
    const utilization = benchmark > 0 ? (data.total_spend / benchmark) * 100 : 0;
    const remaining = Math.max(0, benchmark - data.total_spend);

    const gaugeCircle = document.getElementById('gaugeProgressCircle');
    const gaugePercentText = document.getElementById('gaugePercentText');
    const gaugeRemainingText = document.getElementById('gaugeRemainingText');
    const gaugeStatusBadge = document.getElementById('gaugeStatusBadge');

    if (gaugePercentText) gaugePercentText.textContent = `${utilization.toFixed(1)}%`;
    if (gaugeRemainingText) gaugeRemainingText.textContent = formatCurrency(remaining);

    // Circumference = 2 * PI * 40 = ~251.2
    if (gaugeCircle) {
      const circumference = 251.2;
      const offset = circumference - (Math.min(100, utilization) / 100) * circumference;
      gaugeCircle.style.strokeDashoffset = offset.toString();
      if (utilization > 100) {
        gaugeCircle.classList.remove('text-primary');
        gaugeCircle.classList.add('text-error');
      } else {
        gaugeCircle.classList.remove('text-error');
        gaugeCircle.classList.add('text-primary');
      }
    }

    if (gaugeStatusBadge) {
      if (utilization > 100) {
        gaugeStatusBadge.textContent = "Over Budget";
        gaugeStatusBadge.className = "px-2 py-0.5 rounded-full bg-error-container text-error font-label-sm text-label-sm font-semibold";
      } else {
        gaugeStatusBadge.textContent = "Under Budget";
        gaugeStatusBadge.className = "px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-label-sm font-semibold";
      }
    }

    // Render Spending Insights (Bonus Feature 2)
    renderInsights(data.category_insights || []);

  } catch (err) {
    console.error("Failed to load summary:", err);
  }
}

// Render dynamic category cards
function renderCategoryCards(categories, percentages) {
  const container = document.getElementById('categoryCardsGrid');
  if (!container) return;

  container.innerHTML = '';
  const entries = Object.entries(categories);

  if (entries.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-4 text-center text-on-surface-variant font-body-sm">
        No category data available for this month.
      </div>
    `;
    return;
  }

  entries.forEach(([cat, amt]) => {
    const pct = percentages[cat] || 0;
    const style = getCategoryStyle(cat);

    const card = document.createElement('div');
    card.className = "bg-surface-container-low rounded-lg p-space-sm flex flex-col justify-between hover:bg-surface-container transition-colors";

    const topRow = document.createElement('div');
    topRow.className = "flex items-start justify-between";

    const iconBox = document.createElement('div');
    iconBox.className = `w-8 h-8 rounded-lg bg-surface-container-lowest ${style.color} flex items-center justify-center shadow-sm`;
    const iconSpan = document.createElement('span');
    iconSpan.className = "material-symbols-outlined text-[18px]";
    iconSpan.textContent = style.icon;
    iconBox.appendChild(iconSpan);

    const pctBadge = document.createElement('span');
    pctBadge.className = `px-2 py-0.5 rounded-full ${style.badgeBg} ${style.badgeText} font-tabular-numeric text-[11px] font-semibold`;
    pctBadge.textContent = `${pct.toFixed(1)}%`;

    topRow.appendChild(iconBox);
    topRow.appendChild(pctBadge);

    const bottomRow = document.createElement('div');
    bottomRow.className = "mt-space-sm";

    const titleElem = document.createElement('p');
    titleElem.className = "font-label-md text-label-md text-on-surface-variant truncate";
    titleElem.textContent = cat;

    const amtElem = document.createElement('p');
    amtElem.className = "font-tabular-numeric text-headline-sm font-bold text-on-surface mt-0.5";
    amtElem.textContent = formatCurrency(amt);

    const barBg = document.createElement('div');
    barBg.className = "w-full bg-surface-container-highest rounded-full h-1 mt-2";

    const barFill = document.createElement('div');
    barFill.className = `${style.barColor} h-1 rounded-full transition-all duration-500`;
    barFill.style.width = `${Math.min(100, pct)}%`;
    barBg.appendChild(barFill);

    bottomRow.appendChild(titleElem);
    bottomRow.appendChild(amtElem);
    bottomRow.appendChild(barBg);

    card.appendChild(topRow);
    card.appendChild(bottomRow);
    container.appendChild(card);
  });
}

// Render Category Spending Insights (Bonus Feature 2)
function renderInsights(categoryInsights) {
  const container = document.getElementById('insightsContainer');
  if (!container) return;

  container.classList.remove('hidden');
  container.innerHTML = '';

  const card = document.createElement('div');
  card.className = "bg-surface-container-lowest rounded-xl p-space-md shadow-sm border border-outline-variant/20";

  const header = document.createElement('div');
  header.className = "flex items-center gap-space-xs pb-space-xs";

  const icon = document.createElement('span');
  icon.className = "material-symbols-outlined text-secondary text-[20px]";
  icon.textContent = "insights";

  const title = document.createElement('h3');
  title.className = "font-headline-sm text-headline-sm font-semibold text-on-surface";
  title.textContent = "Spending Insights";

  header.appendChild(icon);
  header.appendChild(title);
  card.appendChild(header);

  const flagged = (categoryInsights || []).filter(item => item.flagged);
  const list = document.createElement('div');
  list.className = "mt-space-xs flex flex-col gap-2";

  if (flagged.length > 0) {
    flagged.forEach(item => {
      const alertDiv = document.createElement('div');
      alertDiv.className = "flex items-center gap-space-sm bg-error-container/40 text-on-surface px-space-md py-space-xs rounded-lg border border-error-container/50";

      const warnIcon = document.createElement('span');
      warnIcon.className = "material-symbols-outlined text-error text-[18px]";
      warnIcon.textContent = "warning";

      const text = document.createElement('p');
      text.className = "font-body-sm text-sm";
      text.textContent = `${item.category} spending increased ${item.change_percent}% compared with last month.`;

      alertDiv.appendChild(warnIcon);
      alertDiv.appendChild(text);
      list.appendChild(alertDiv);
    });
  } else {
    const infoDiv = document.createElement('div');
    infoDiv.className = "flex items-center gap-space-sm bg-surface-container-low text-on-surface-variant px-space-md py-space-xs rounded-lg";

    const infoIcon = document.createElement('span');
    infoIcon.className = "material-symbols-outlined text-secondary text-[18px]";
    infoIcon.textContent = "check_circle";

    const text = document.createElement('p');
    text.className = "font-body-sm text-sm";
    text.textContent = "No categories increased by more than 20% compared with last month.";

    infoDiv.appendChild(infoIcon);
    infoDiv.appendChild(text);
    list.appendChild(infoDiv);
  }

  card.appendChild(list);
  container.appendChild(card);
}

// Load Expenses with Filtering and Pagination
async function loadExpenses(page = 1) {
  currentPage = page;
  const tbody = document.getElementById('expensesTableBody');
  const stateContainer = document.getElementById('tableStateContainer');
  const countTag = document.getElementById('displayCountTag');
  const paginationSummary = document.getElementById('paginationSummary');
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');
  const pageBadge = document.getElementById('currentPageBadge');

  const catFilter = document.getElementById('tableCategoryFilter')?.value || '';
  const startDate = document.getElementById('tableStartDateFilter')?.value || '';
  const endDate = document.getElementById('tableEndDateFilter')?.value || '';

  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (catFilter) params.append('category', catFilter);
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  try {
    const res = await fetch(`/expenses?${params.toString()}`, { headers: getApiHeaders() });
    if (res.status === 401 || res.status === 403) {
      redirectToLogin();
      return;
    }
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${res.status})`);
    }

    const data = await res.json();
    currentExpenses = data.items;

    if (countTag) countTag.textContent = `Showing ${data.items.length} of ${data.total} entries`;
    if (paginationSummary) {
      const startIdx = data.total > 0 ? (page - 1) * pageSize + 1 : 0;
      const endIdx = Math.min(page * pageSize, data.total);
      paginationSummary.textContent = `Displaying ${startIdx} to ${endIdx} of ${data.total} expenses`;
    }

    if (pageBadge) pageBadge.textContent = page.toString();
    if (prevBtn) prevBtn.disabled = page <= 1;
    if (nextBtn) nextBtn.disabled = page >= data.total_pages;

    renderTableRows(data.items);

  } catch (err) {
    console.error("Failed to load expenses:", err);
    if (tbody) tbody.innerHTML = '';
    if (stateContainer) {
      stateContainer.classList.remove('hidden');
      document.getElementById('stateIcon').textContent = 'error_outline';
      document.getElementById('stateTitle').textContent = 'Error Loading Expenses';
      document.getElementById('stateSubtitle').textContent = err.message || 'Could not connect to the API.';
    }
  }
}

// XSS-Safe Table Rendering
function renderTableRows(items) {
  const tbody = document.getElementById('expensesTableBody');
  const stateContainer = document.getElementById('tableStateContainer');
  if (!tbody) return;

  tbody.innerHTML = '';

  // Apply client search query if present
  const searchQuery = (document.getElementById('tableSearchInput')?.value || '').trim().toLowerCase();
  const filteredItems = searchQuery
    ? items.filter(it => (it.note || '').toLowerCase().includes(searchQuery) || it.category.toLowerCase().includes(searchQuery))
    : items;

  if (filteredItems.length === 0) {
    if (stateContainer) {
      stateContainer.classList.remove('hidden');
      document.getElementById('stateIcon').textContent = 'inbox';
      document.getElementById('stateTitle').textContent = 'No expenses found';
      document.getElementById('stateSubtitle').textContent = 'Try adjusting your search or date filters.';
    }
    return;
  }

  if (stateContainer) stateContainer.classList.add('hidden');

  filteredItems.forEach(item => {
    const tr = document.createElement('tr');
    tr.className = "h-12 hover:bg-surface-container-low transition-colors group cursor-default";

    // Date
    const tdDate = document.createElement('td');
    tdDate.className = "px-space-md font-tabular-numeric text-body-sm text-on-surface-variant";
    const dateObj = new Date(item.date + 'T00:00:00');
    tdDate.textContent = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

    // Category
    const tdCat = document.createElement('td');
    tdCat.className = "px-space-md";
    const catBadge = document.createElement('span');
    const style = getCategoryStyle(item.category);
    catBadge.className = `inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full ${style.badgeBg} ${style.badgeText} font-label-sm text-[11px] font-medium`;
    const dot = document.createElement('span');
    dot.className = `w-1.5 h-1.5 rounded-full ${style.barColor}`;
    catBadge.appendChild(dot);
    catBadge.appendChild(document.createTextNode(item.category));
    tdCat.appendChild(catBadge);

    // Note / Vendor (Safe textContent)
    const tdNote = document.createElement('td');
    tdNote.className = "px-space-md font-body-md text-body-md text-on-surface font-medium";
    tdNote.textContent = item.note || "—";

    // Amount
    const tdAmount = document.createElement('td');
    tdAmount.className = "px-space-md text-right font-tabular-numeric text-body-md font-bold text-error";
    tdAmount.textContent = formatCurrency(item.amount);

    tr.appendChild(tdDate);
    tr.appendChild(tdCat);
    tr.appendChild(tdNote);
    tr.appendChild(tdAmount);

    tbody.appendChild(tr);
  });
}

function debounceFilter() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    renderTableRows(currentExpenses);
  }, 200);
}

function applyFilters() {
  loadExpenses(1);
}

function resetFilters() {
  const search = document.getElementById('tableSearchInput');
  const cat = document.getElementById('tableCategoryFilter');
  const start = document.getElementById('tableStartDateFilter');
  const end = document.getElementById('tableEndDateFilter');

  if (search) search.value = '';
  if (cat) cat.value = '';
  if (start) start.value = '';
  if (end) end.value = '';

  loadExpenses(1);
}

function filterTableToSelectedMonth() {
  const y = selectedYear || new Date().getFullYear();
  const m = selectedMonth || (new Date().getMonth() + 1);
  const padMonth = String(m).padStart(2, '0');
  const lastDay = new Date(y, m, 0).getDate();
  const start = document.getElementById('tableStartDateFilter');
  const end = document.getElementById('tableEndDateFilter');
  if (start) start.value = `${y}-${padMonth}-01`;
  if (end) end.value = `${y}-${padMonth}-${String(lastDay).padStart(2, '0')}`;
  loadExpenses(1);
}

function changePage(delta) {
  const newPage = currentPage + delta;
  if (newPage >= 1) {
    loadExpenses(newPage);
  }
}

// Handle Add Expense Form Submission with Idempotency
async function handleExpenseSubmit(e) {
  e.preventDefault();

  const amountInput = document.getElementById('amountInput');
  const categoryInput = document.getElementById('categoryInput');
  const dateInput = document.getElementById('dateInput');
  const noteInput = document.getElementById('noteInput');
  const submitBtn = document.getElementById('submitBtn');
  const submitBtnText = document.getElementById('submitBtnText');

  const amount = parseFloat(amountInput.value);
  const category = categoryInput.value.trim();
  const date = dateInput.value;
  const note = noteInput.value.trim();

  if (!amount || amount <= 0 || !category || !date) {
    showToast("Invalid Form Input", "Please fill in all required fields correctly.", true);
    return;
  }

  // Set loading state
  if (submitBtn) submitBtn.disabled = true;
  if (submitBtnText) submitBtnText.textContent = "Adding...";

  try {
    const payload = {
      amount: amount,
      category: category,
      date: date,
      note: note || null,
    };

    const res = await fetch('/expenses', {
      method: 'POST',
      headers: getApiHeaders({
        'Content-Type': 'application/json',
        'Idempotency-Key': currentIdempotencyKey,
      }),
      body: JSON.stringify(payload),
    });

    if (res.status === 201) {
      showToast("Expense Recorded", `Successfully added ${formatCurrency(amount)} for "${note || category}"`);

      // Clear form inputs
      amountInput.value = '';
      noteInput.value = '';

      // Generate a brand new idempotency key for the subsequent transaction
      currentIdempotencyKey = generateUUID();

      // If the expense was recorded on a different month, switch to that month
      if (payload.date) {
        const [pY, pM] = payload.date.split('-').map(Number);
        if (pY && pM && (pY !== selectedYear || pM !== selectedMonth)) {
          selectedYear = pY;
          selectedMonth = pM;
          pickerYear = pY;
          syncTableDateFiltersToMonth(selectedYear, selectedMonth);
        }
      }

      // Refresh data
      await loadSummary(selectedYear, selectedMonth);
      await loadExpenses(1);

    } else if (res.status === 401 || res.status === 403) {
      redirectToLogin();
      return;
    } else if (res.status === 409) {
      showToast("Idempotency Conflict", "This transaction key was reused with a different request payload.", true);
    } else {
      const errData = await res.json().catch(() => ({}));
      let msg = "Could not record expense.";
      if (errData.detail) {
        if (Array.isArray(errData.detail)) {
          msg = errData.detail.map(d => d.msg).join(", ");
        } else {
          msg = errData.detail;
        }
      }
      showToast("Validation Error", msg, true);
    }

  } catch (err) {
    console.error("Submission failed:", err);
    showToast("Network Error", "Unable to communicate with the server.", true);
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (submitBtnText) submitBtnText.textContent = "Add Expense";
  }
}

// Client-Side CSV Export of Currently Loaded Data
function exportLedgerCSV() {
  if (!currentExpenses || currentExpenses.length === 0) {
    showToast("Export Failed", "No expense records available to export.", true);
    return;
  }

  const headers = ["Date", "Category", "Description", "Amount"];
  const rows = currentExpenses.map(item => [
    item.date,
    `"${(item.category || '').replace(/"/g, '""')}"`,
    `"${(item.note || '').replace(/"/g, '""')}"`,
    `-${Number(item.amount).toFixed(2)}`
  ]);

  const csvContent = [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `spendtrack_ledger_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  showToast("CSV Downloaded", `Exported ${currentExpenses.length} records successfully.`);
}

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem("spendtrack_token");
  if (!token) {
    redirectToLogin();
    return;
  }

  // Set default transaction date to today's local date
  const dateInput = document.getElementById('dateInput');
  if (dateInput) {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateInput.value = `${yyyy}-${mm}-${dd}`;
  }

  // Set default active month to current month and sync table filters
  const now = new Date();
  selectedYear = now.getFullYear();
  selectedMonth = now.getMonth() + 1;
  pickerYear = selectedYear;
  syncTableDateFiltersToMonth(selectedYear, selectedMonth);

  // Load user profile and initial datasets
  loadUserProfile();
  loadSummary(selectedYear, selectedMonth);
  loadExpenses(1);
});
