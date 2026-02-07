const DEFAULT_URL = "../data/curriculum.json";
const MOCK_URL = "../data/reliability/curriculum.mock.json";

const REQUIRED_TOP_LEVEL = [
  "domain",
  "domain_ref",
  "scenario",
  "metadata",
  "nodes",
  "edges",
  "learning_path",
  "milestones",
  "coverage_map",
];

const CATEGORY_COLORS = {
  foundation: "#007f6d",
  selection: "#2c6fce",
  ordering: "#b46a18",
  arguments: "#8b5cf6",
  output: "#0077b6",
  hallucination: "#d1495b",
  avoidance: "#6a994e",
  debug: "#3d405b",
  capstone: "#111827",
};

const state = {
  curriculum: null,
  selectedNodeId: null,
  searchText: "",
  selectedLayers: new Set(),
  selectedCategories: new Set(),
  selectedTypes: new Set(),
  cy: null,
};

const els = {
  loadDefaultBtn: document.getElementById("loadDefaultBtn"),
  loadMockBtn: document.getElementById("loadMockBtn"),
  fileInput: document.getElementById("fileInput"),
  searchInput: document.getElementById("searchInput"),
  statusBanner: document.getElementById("statusBanner"),
  metricCards: document.getElementById("metricCards"),
  layerExplorer: document.getElementById("layerExplorer"),
  nodeTable: document.getElementById("nodeTable"),
  coverageMap: document.getElementById("coverageMap"),
  learningPath: document.getElementById("learningPath"),
  milestones: document.getElementById("milestones"),
  nodeDetails: document.getElementById("nodeDetails"),
  layerFilters: document.getElementById("layerFilters"),
  categoryFilters: document.getElementById("categoryFilters"),
  typeFilters: document.getElementById("typeFilters"),
  visibleCount: document.getElementById("visibleCount"),
  graphView: document.getElementById("graphView"),
  graphFitBtn: document.getElementById("graphFitBtn"),
};

function showStatus(message, type = "ok") {
  els.statusBanner.textContent = message;
  els.statusBanner.className = `status-banner ${type}`;
}

function clearStatus() {
  els.statusBanner.textContent = "";
  els.statusBanner.className = "status-banner";
}

function validateCurriculumShape(data) {
  if (!data || typeof data !== "object") {
    return "JSON root must be an object.";
  }

  for (const key of REQUIRED_TOP_LEVEL) {
    if (!(key in data)) {
      return `Missing top-level key: ${key}`;
    }
  }

  if (!Array.isArray(data.nodes)) {
    return "nodes must be an array.";
  }

  if (data.nodes.length === 0) {
    return "nodes array cannot be empty.";
  }

  return null;
}

async function loadFromUrl(url, label) {
  try {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    setCurriculum(data);
    showStatus(`Loaded ${label} from ${url}`);
  } catch (error) {
    showStatus(`Failed to load ${label}: ${error.message}`, "error");
  }
}

async function loadFromFile(file) {
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    setCurriculum(data);
    showStatus(`Loaded ${file.name}`);
  } catch (error) {
    showStatus(`Failed to parse file: ${error.message}`, "error");
  }
}

function setCurriculum(data) {
  const shapeError = validateCurriculumShape(data);
  if (shapeError) {
    showStatus(`Invalid curriculum JSON: ${shapeError}`, "error");
    return;
  }

  destroyGraph();
  state.curriculum = data;
  if (!data.nodes.find((node) => node.id === state.selectedNodeId)) {
    state.selectedNodeId = data.nodes[0]?.id ?? null;
  }

  initFilterState();
  clearStatus();
  render();
}

function initFilterState() {
  const layers = new Set(state.curriculum.nodes.map((node) => String(node.layer)));
  const categories = new Set(state.curriculum.nodes.map((node) => node.category));
  const types = new Set(state.curriculum.nodes.map((node) => node.exercise_type));

  state.selectedLayers = layers;
  state.selectedCategories = categories;
  state.selectedTypes = types;
}

function filterNodes() {
  if (!state.curriculum) {
    return [];
  }

  const query = state.searchText.trim().toLowerCase();

  return state.curriculum.nodes.filter((node) => {
    const matchesLayer = state.selectedLayers.has(String(node.layer));
    const matchesCategory = state.selectedCategories.has(node.category);
    const matchesType = state.selectedTypes.has(node.exercise_type);

    const searchableText = [
      node.id,
      node.title,
      node.failure_mode,
      node.teaches,
      node.exercise,
      node.category,
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch = !query || searchableText.includes(query);

    return matchesLayer && matchesCategory && matchesType && matchesSearch;
  });
}

function destroyGraph() {
  if (state.cy) {
    state.cy.destroy();
    state.cy = null;
  }
  if (els.graphView) {
    els.graphView.innerHTML = "";
  }
}

function categoryColor(category) {
  return CATEGORY_COLORS[category] ?? "#51606f";
}

function buildGraphElements() {
  const nodesByLayer = new Map();
  for (let i = 0; i <= 4; i += 1) {
    nodesByLayer.set(i, []);
  }

  state.curriculum.nodes.forEach((node) => {
    if (!nodesByLayer.has(node.layer)) {
      nodesByLayer.set(node.layer, []);
    }
    nodesByLayer.get(node.layer).push(node);
  });

  const nodeElements = [];
  const xStep = 220;
  const yStep = 96;
  const xStart = 90;
  const yStart = 70;

  nodesByLayer.forEach((nodes, layer) => {
    nodes
      .sort((a, b) => a.id.localeCompare(b.id))
      .forEach((node, index) => {
        nodeElements.push({
          group: "nodes",
          data: {
            id: node.id,
            label: node.id,
            title: node.title,
            layer: String(layer),
            category: node.category,
            color: categoryColor(node.category),
          },
          position: {
            x: xStart + layer * xStep,
            y: yStart + index * yStep,
          },
        });
      });
  });

  const edgeElements = (state.curriculum.edges || []).map((edge) => ({
    group: "edges",
    data: {
      id: `${edge.from}->${edge.to}`,
      source: edge.from,
      target: edge.to,
    },
  }));

  return [...nodeElements, ...edgeElements];
}

function ensureGraph() {
  if (state.cy || !state.curriculum) {
    return;
  }

  if (typeof window.cytoscape !== "function") {
    els.graphView.innerHTML =
      '<p class="muted" style="padding: 0.75rem;">Cytoscape is unavailable. Check network access and reload.</p>';
    return;
  }

  state.cy = window.cytoscape({
    container: els.graphView,
    elements: buildGraphElements(),
    layout: {
      name: "preset",
      fit: true,
      padding: 48,
    },
    minZoom: 0.35,
    maxZoom: 2.6,
    wheelSensitivity: 0.18,
    style: [
      {
        selector: "node",
        style: {
          "background-color": "data(color)",
          label: "data(label)",
          color: "#f8fafc",
          "font-size": "11px",
          "font-weight": 700,
          "text-outline-width": 2,
          "text-outline-color": "data(color)",
          "text-valign": "center",
          "text-halign": "center",
          width: 42,
          height: 42,
          "border-width": 2,
          "border-color": "#ffffff",
        },
      },
      {
        selector: "edge",
        style: {
          width: 1.8,
          "line-color": "#8aa1b5",
          "target-arrow-color": "#8aa1b5",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "arrow-scale": 0.9,
        },
      },
      {
        selector: ".is-context",
        style: {
          "border-color": "#ffd166",
          "border-width": 3,
        },
      },
      {
        selector: ".is-selected",
        style: {
          "overlay-color": "#1f7a8c",
          "overlay-opacity": 0.18,
          "overlay-padding": 6,
          "border-color": "#072f3a",
          "border-width": 4,
        },
      },
      {
        selector: ".is-hidden",
        style: {
          display: "none",
        },
      },
    ],
  });

  state.cy.on("tap", "node", (event) => {
    const nodeId = event.target.id();
    if (!nodeId || nodeId === state.selectedNodeId) {
      return;
    }
    state.selectedNodeId = nodeId;
    render();
  });
}

function fitVisibleGraph() {
  if (!state.cy) {
    return;
  }
  const visible = state.cy.elements().not(".is-hidden");
  if (visible.length === 0) {
    return;
  }
  state.cy.fit(visible, 48);
}

function renderGraph(filteredNodes) {
  ensureGraph();
  if (!state.cy) {
    return;
  }

  const visibleIds = new Set(filteredNodes.map((node) => node.id));

  state.cy.batch(() => {
    state.cy.nodes().forEach((node) => {
      const shouldHide = !visibleIds.has(node.id());
      node.toggleClass("is-hidden", shouldHide);
      node.removeClass("is-selected");
      node.removeClass("is-context");
    });

    state.cy.edges().forEach((edge) => {
      const shouldHide =
        !visibleIds.has(edge.source().id()) || !visibleIds.has(edge.target().id());
      edge.toggleClass("is-hidden", shouldHide);
    });

    const selected = state.selectedNodeId ? state.cy.getElementById(state.selectedNodeId) : null;
    if (selected && selected.nonempty() && !selected.hasClass("is-hidden")) {
      selected.addClass("is-selected");
      selected.incomers("node").forEach((node) => {
        if (!node.hasClass("is-hidden")) {
          node.addClass("is-context");
        }
      });
      selected.outgoers("node").forEach((node) => {
        if (!node.hasClass("is-hidden")) {
          node.addClass("is-context");
        }
      });
    }
  });
}

function render() {
  if (!state.curriculum) {
    return;
  }

  renderFilters();
  renderMetrics();

  const filteredNodes = filterNodes();
  els.visibleCount.textContent = `${filteredNodes.length}/${state.curriculum.nodes.length} nodes visible`;

  renderGraph(filteredNodes);
  renderLayerExplorer(filteredNodes);
  renderNodeTable(filteredNodes);
  renderCoverageMap();
  renderLearningPath();
  renderMilestones();
  renderNodeDetails();
}

function renderFilters() {
  renderChipFilter(
    els.layerFilters,
    [...new Set(state.curriculum.nodes.map((n) => String(n.layer)))].sort(),
    state.selectedLayers,
    (value) => {
      toggleSetValue(state.selectedLayers, value);
      render();
    },
    "L"
  );

  renderChipFilter(
    els.categoryFilters,
    [...new Set(state.curriculum.nodes.map((n) => n.category))].sort(),
    state.selectedCategories,
    (value) => {
      toggleSetValue(state.selectedCategories, value);
      render();
    }
  );

  renderChipFilter(
    els.typeFilters,
    [...new Set(state.curriculum.nodes.map((n) => n.exercise_type))].sort(),
    state.selectedTypes,
    (value) => {
      toggleSetValue(state.selectedTypes, value);
      render();
    }
  );
}

function renderChipFilter(container, values, selectedSet, onClick, prefix = "") {
  container.innerHTML = "";
  values.forEach((value) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = `chip ${selectedSet.has(value) ? "active" : ""}`;
    chip.textContent = prefix ? `${prefix}${value}` : value;
    chip.addEventListener("click", () => onClick(value));
    container.append(chip);
  });
}

function toggleSetValue(set, value) {
  if (set.has(value)) {
    if (set.size > 1) {
      set.delete(value);
    }
    return;
  }
  set.add(value);
}

function renderMetrics() {
  const { metadata, nodes, edges, milestones, learning_path: learningPath } =
    state.curriculum;

  const advancedCount = nodes.filter((node) => node.difficulty === "advanced").length;
  const debugReadCount = nodes.filter((node) =>
    ["debug", "read"].includes(node.exercise_type)
  ).length;

  const cards = [
    ["Nodes", metadata.node_count ?? nodes.length],
    ["Edges", metadata.edge_count ?? edges.length],
    ["Max depth", metadata.max_depth],
    ["Milestones", milestones.length],
    ["Debug/Read", debugReadCount],
    ["Advanced", advancedCount],
    ["Est. hours", learningPath.estimated_total_hours],
  ];

  els.metricCards.innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="metric-card">
          <div class="metric-value mono">${value}</div>
          <div class="metric-label">${label}</div>
        </article>
      `
    )
    .join("");
}

function renderLayerExplorer(filteredNodes) {
  const byLayer = new Map();
  for (let i = 0; i <= 4; i += 1) {
    byLayer.set(i, []);
  }

  filteredNodes.forEach((node) => {
    byLayer.get(node.layer)?.push(node);
  });

  els.layerExplorer.innerHTML = "";

  byLayer.forEach((nodesInLayer, layer) => {
    const column = document.createElement("div");
    column.className = "layer-column";

    const heading = document.createElement("div");
    heading.className = "layer-title";
    heading.textContent = `Layer ${layer}`;
    column.append(heading);

    nodesInLayer
      .sort((a, b) => a.id.localeCompare(b.id))
      .forEach((node) => column.append(makeNodeCard(node)));

    if (nodesInLayer.length === 0) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "No nodes";
      column.append(empty);
    }

    els.layerExplorer.append(column);
  });
}

function makeNodeCard(node) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = `node-card ${state.selectedNodeId === node.id ? "selected" : ""}`;

  card.innerHTML = `
    <div class="title mono">${node.id} - ${escapeHtml(node.title)}</div>
    <div class="meta">${node.category} | ${node.exercise_type} | ${node.difficulty}</div>
  `;

  card.addEventListener("click", () => {
    state.selectedNodeId = node.id;
    render();
  });

  return card;
}

function renderNodeTable(filteredNodes) {
  const rows = filteredNodes
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((node) => {
      const selectedClass = node.id === state.selectedNodeId ? "active" : "";
      return `
        <tr class="clickable ${selectedClass}" data-node-id="${node.id}">
          <td class="mono">${node.id}</td>
          <td>${escapeHtml(node.title)}</td>
          <td>${node.layer}</td>
          <td>${node.category}</td>
          <td>${node.exercise_type}</td>
          <td>${node.estimated_time_minutes}m</td>
        </tr>
      `;
    })
    .join("");

  els.nodeTable.innerHTML = `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Layer</th>
            <th>Category</th>
            <th>Type</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>${rows || `<tr><td colspan="6">No nodes match filters.</td></tr>`}</tbody>
      </table>
    </div>
  `;

  els.nodeTable.querySelectorAll("tr[data-node-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedNodeId = row.dataset.nodeId;
      render();
    });
  });
}

function renderCoverageMap() {
  const coverageEntries = Object.entries(state.curriculum.coverage_map || {});

  els.coverageMap.innerHTML = coverageEntries
    .map(([key, nodeIds]) => {
      const chips = nodeIds
        .map((nodeId) => `<button class="chip-link mono" data-node-link="${nodeId}">${nodeId}</button>`)
        .join("");

      return `
        <article class="coverage-item">
          <div class="coverage-key">${escapeHtml(key)}</div>
          <div>${chips}</div>
        </article>
      `;
    })
    .join("");

  bindNodeLinks(els.coverageMap);
}

function renderLearningPath() {
  const topological = state.curriculum.learning_path?.topological_order || [];
  const criticalPath = new Set(state.curriculum.learning_path?.critical_path || []);

  els.learningPath.innerHTML = topological
    .map((nodeId, index) => {
      const marker = criticalPath.has(nodeId) ? "critical" : "path";
      return `
        <div class="path-item">
          <span class="mono">${index + 1}. ${nodeId}</span>
          <span class="chip-link" data-node-link="${nodeId}">${marker}</span>
        </div>
      `;
    })
    .join("");

  bindNodeLinks(els.learningPath);
}

function renderMilestones() {
  els.milestones.innerHTML = (state.curriculum.milestones || [])
    .map((milestone) => {
      const chips = (milestone.nodes || [])
        .map((nodeId) => `<button class="chip-link mono" data-node-link="${nodeId}">${nodeId}</button>`)
        .join("");

      return `
        <article class="milestone-item">
          <div class="mono">${escapeHtml(milestone.id)} - ${escapeHtml(milestone.name)}</div>
          <p class="muted" style="margin: 0.35rem 0;">${escapeHtml(milestone.after_this)}</p>
          <div>${chips}</div>
        </article>
      `;
    })
    .join("");

  bindNodeLinks(els.milestones);
}

function renderNodeDetails() {
  const node = state.curriculum.nodes.find((item) => item.id === state.selectedNodeId);
  if (!node) {
    els.nodeDetails.innerHTML = `<p class="details-placeholder">Select a node to inspect details.</p>`;
    return;
  }

  const prereqLinks = formatNodeLinks(node.prerequisites || []);
  const dependentLinks = formatNodeLinks(node.dependents || []);

  els.nodeDetails.innerHTML = `
    <div class="kv">
      <div class="kv-key">Identity</div>
      <div class="kv-value mono">${node.id} - ${escapeHtml(node.title)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Meta</div>
      <div class="kv-value">Layer ${node.layer} | ${node.category} | ${node.exercise_type} | ${node.difficulty}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Failure mode</div>
      <div class="kv-value">${escapeHtml(node.failure_mode)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Exercise</div>
      <div class="kv-value">${escapeHtml(node.exercise)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Pass condition</div>
      <div class="kv-value">${escapeHtml(node.pass_condition)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Fail condition</div>
      <div class="kv-value">${escapeHtml(node.fail_condition)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Reference hint</div>
      <div class="kv-value">${escapeHtml(node.reference_hint)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Prerequisites</div>
      <div class="kv-value">${prereqLinks || `<span class="muted">None</span>`}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Dependents</div>
      <div class="kv-value">${dependentLinks || `<span class="muted">None</span>`}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Teaches</div>
      <div class="kv-value">${escapeHtml(node.teaches)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Connects to field map</div>
      <div class="kv-value">${escapeHtml((node.connects_to_field_map || []).join(", "))}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Tags</div>
      <div class="kv-value">${escapeHtml((node.tags || []).join(", "))}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Skeleton file</div>
      <div class="kv-value mono">${escapeHtml(node.skeleton_file)}</div>
    </div>
  `;

  bindNodeLinks(els.nodeDetails);
}

function formatNodeLinks(nodeIds) {
  return nodeIds
    .map((nodeId) => `<button class="chip-link mono" data-node-link="${nodeId}">${nodeId}</button>`)
    .join(" ");
}

function bindNodeLinks(container) {
  container.querySelectorAll("[data-node-link]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const nodeId = btn.getAttribute("data-node-link");
      if (!nodeId) {
        return;
      }
      state.selectedNodeId = nodeId;
      render();
    });
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setupEvents() {
  els.loadDefaultBtn.addEventListener("click", () => {
    loadFromUrl(DEFAULT_URL, "default curriculum");
  });

  els.loadMockBtn.addEventListener("click", () => {
    loadFromUrl(MOCK_URL, "mock curriculum");
  });

  els.fileInput.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) {
      loadFromFile(file);
    }
  });

  els.searchInput.addEventListener("input", (event) => {
    state.searchText = event.target.value || "";
    render();
  });

  els.graphFitBtn.addEventListener("click", () => {
    fitVisibleGraph();
  });
}

setupEvents();
loadFromUrl(DEFAULT_URL, "default curriculum");
