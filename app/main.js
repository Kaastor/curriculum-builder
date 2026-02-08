const RUNS_INDEX_URL = "../runs/";
const RUN_CURRICULUM_SUFFIX = "/outputs/curriculum/curriculum.json";
const RUN_ID_PATTERN = /^\d{8}-\d{6}(?:-[a-z0-9-]+)?\/?$/;

const REQUIRED_TOP_LEVEL = ["topic", "nodes"];

const state = {
  curriculum: null,
  derived: null,
  selectedNodeId: null,
  searchText: "",
  selectedLayers: new Set(),
  cy: null,
};

const els = {
  fileInput: document.getElementById("fileInput"),
  searchInput: document.getElementById("searchInput"),
  statusBanner: document.getElementById("statusBanner"),
  metricCards: document.getElementById("metricCards"),
  layerExplorer: document.getElementById("layerExplorer"),
  nodeTable: document.getElementById("nodeTable"),
  openQuestions: document.getElementById("openQuestions"),
  learningPath: document.getElementById("learningPath"),
  milestones: document.getElementById("milestones"),
  nodeDetails: document.getElementById("nodeDetails"),
  layerFilters: document.getElementById("layerFilters"),
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

async function fetchCurriculum(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function listRunDirectories() {
  const response = await fetch(RUNS_INDEX_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const html = await response.text();
  const doc = new window.DOMParser().parseFromString(html, "text/html");
  const runIds = Array.from(doc.querySelectorAll("a"))
    .map((link) => link.getAttribute("href") || "")
    .filter((href) => RUN_ID_PATTERN.test(href))
    .map((href) => href.replace(/\/$/, ""))
    .sort();
  return runIds;
}

async function loadLatestRunCurriculum() {
  const runIds = await listRunDirectories();
  if (runIds.length === 0) {
    throw new Error("No run directories found under runs/.");
  }

  for (const runId of [...runIds].reverse()) {
    const url = `${RUNS_INDEX_URL}${runId}${RUN_CURRICULUM_SUFFIX}`;
    try {
      const data = await fetchCurriculum(url);
      setCurriculum(data);
      showStatus(`Loaded latest run curriculum from ${runId}`);
      return;
    } catch {
      // Keep scanning older runs until a curriculum artifact is found.
    }
  }

  throw new Error("No run contains outputs/curriculum/curriculum.json.");
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
  state.derived = buildDerivedGraph(data.nodes);

  if (!data.nodes.find((node) => node.id === state.selectedNodeId)) {
    state.selectedNodeId = data.nodes[0]?.id ?? null;
  }

  initFilterState();
  clearStatus();
  render();
}

function initFilterState() {
  const layers = new Set(
    Object.values(state.derived?.nodeLayers || {}).map((layer) => String(layer))
  );
  state.selectedLayers = layers;
}

function filterNodes() {
  if (!state.curriculum) {
    return [];
  }

  const query = state.searchText.trim().toLowerCase();

  return state.curriculum.nodes.filter((node) => {
    const layer = String(state.derived?.nodeLayers?.[node.id] ?? 0);
    const matchesLayer = state.selectedLayers.has(layer);

    const searchableText = [
      node.id,
      node.title,
      node.capability,
      ...(node.core_ideas || []),
      ...(node.pitfalls || []),
    ]
      .join(" ")
      .toLowerCase();

    const matchesSearch = !query || searchableText.includes(query);

    return matchesLayer && matchesSearch;
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

function layerColor(layer) {
  const palette = [
    "#0f766e",
    "#1d4ed8",
    "#b45309",
    "#7c3aed",
    "#be123c",
    "#334155",
  ];
  return palette[layer % palette.length];
}

function sumEstimatedHours(nodes) {
  const totalMinutes = nodes.reduce((acc, node) => {
    const value = Number(node.estimate_minutes);
    return Number.isFinite(value) ? acc + value : acc;
  }, 0);
  return Math.round((totalMinutes / 60) * 100) / 100;
}

function buildDerivedGraph(nodes) {
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const dependentsById = Object.fromEntries(nodes.map((node) => [node.id, []]));
  const edges = [];
  const indegree = Object.fromEntries(nodes.map((node) => [node.id, 0]));

  nodes.forEach((node) => {
    (node.prerequisites || []).forEach((prereqId) => {
      if (!nodeMap.has(prereqId)) {
        return;
      }
      edges.push({ from: prereqId, to: node.id });
      dependentsById[prereqId].push(node.id);
      indegree[node.id] += 1;
    });
  });

  Object.values(dependentsById).forEach((ids) => ids.sort());

  const queue = Object.keys(indegree)
    .filter((nodeId) => indegree[nodeId] === 0)
    .sort();
  const topologicalOrder = [];

  while (queue.length) {
    const current = queue.shift();
    topologicalOrder.push(current);
    (dependentsById[current] || []).forEach((next) => {
      indegree[next] -= 1;
      if (indegree[next] === 0) {
        queue.push(next);
        queue.sort();
      }
    });
  }

  if (topologicalOrder.length !== nodes.length) {
    const fallback = [...nodes].sort((a, b) => a.id.localeCompare(b.id)).map((node) => node.id);
    topologicalOrder.splice(0, topologicalOrder.length, ...fallback);
  }

  const nodeLayers = {};
  topologicalOrder.forEach((nodeId) => {
    const node = nodeMap.get(nodeId);
    const prereqs = node?.prerequisites || [];
    if (prereqs.length === 0) {
      nodeLayers[nodeId] = 0;
      return;
    }

    let layer = 0;
    prereqs.forEach((prereqId) => {
      const parentLayer = nodeLayers[prereqId] ?? 0;
      layer = Math.max(layer, parentLayer + 1);
    });
    nodeLayers[nodeId] = layer;
  });

  const durationById = Object.fromEntries(
    nodes.map((node) => [node.id, Number(node.estimate_minutes) || 0])
  );
  const distanceById = {};
  const previousById = {};

  topologicalOrder.forEach((nodeId) => {
    const node = nodeMap.get(nodeId);
    if (!node) {
      return;
    }

    const prereqs = (node.prerequisites || []).filter((prereqId) =>
      Object.prototype.hasOwnProperty.call(durationById, prereqId)
    );
    if (prereqs.length === 0) {
      distanceById[nodeId] = durationById[nodeId];
      previousById[nodeId] = null;
      return;
    }

    let bestPrereq = prereqs[0];
    let bestDistance = distanceById[bestPrereq] ?? durationById[bestPrereq];

    prereqs.slice(1).forEach((candidate) => {
      const candidateDistance = distanceById[candidate] ?? durationById[candidate];
      if (candidateDistance > bestDistance) {
        bestDistance = candidateDistance;
        bestPrereq = candidate;
      }
    });

    distanceById[nodeId] = bestDistance + durationById[nodeId];
    previousById[nodeId] = bestPrereq;
  });

  const terminalId = topologicalOrder.reduce((bestId, nodeId) => {
    if (!bestId) {
      return nodeId;
    }
    return (distanceById[nodeId] || 0) > (distanceById[bestId] || 0) ? nodeId : bestId;
  }, null);

  const criticalPath = [];
  let cursor = terminalId;
  while (cursor) {
    criticalPath.unshift(cursor);
    cursor = previousById[cursor];
  }

  const maxLayer = Math.max(...Object.values(nodeLayers), 0);
  const milestones = Array.from({ length: maxLayer + 1 }, (_, layer) => {
    const layerNodes = nodes
      .filter((node) => Number(nodeLayers[node.id]) === layer)
      .map((node) => node.id)
      .sort();

    return {
      id: `M${layer + 1}`,
      name: `Layer ${layer}`,
      nodes: layerNodes,
      after_this: `Complete layer ${layer} mastery checks`,
    };
  });

  return {
    nodeLayers,
    edges,
    dependentsById,
    topologicalOrder,
    criticalPath,
    milestones,
    maxLayer,
    estimatedTotalHours: sumEstimatedHours(nodes),
  };
}

function buildGraphElements() {
  const nodeLayers = state.derived?.nodeLayers || {};
  const layers = Array.from(new Set(Object.values(nodeLayers))).sort((a, b) => a - b);
  const nodesByLayer = new Map(layers.map((layer) => [layer, []]));

  state.curriculum.nodes.forEach((node) => {
    const layer = Number(nodeLayers[node.id] ?? 0);
    if (!nodesByLayer.has(layer)) {
      nodesByLayer.set(layer, []);
    }
    nodesByLayer.get(layer).push(node);
  });

  const nodeElements = [];
  const xStep = 220;
  const yStep = 100;
  const xStart = 90;
  const yStart = 70;

  [...nodesByLayer.keys()]
    .sort((a, b) => a - b)
    .forEach((layer) => {
      (nodesByLayer.get(layer) || [])
        .sort((a, b) => a.id.localeCompare(b.id))
        .forEach((node, index) => {
          nodeElements.push({
            group: "nodes",
            data: {
              id: node.id,
              label: node.id,
              title: node.title,
              layer: String(layer),
              color: layerColor(layer),
            },
            position: {
              x: xStart + layer * xStep,
              y: yStart + index * yStep,
            },
          });
        });
    });

  const edgeElements = (state.derived?.edges || []).map((edge) => ({
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
      const shouldHide = !visibleIds.has(edge.source().id()) || !visibleIds.has(edge.target().id());
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
  renderLearningPath();
  renderMilestones();
  renderOpenQuestions();
  renderNodeDetails();
}

function renderFilters() {
  const layers = Array.from(new Set(Object.values(state.derived?.nodeLayers || {}))).sort(
    (a, b) => a - b
  );

  renderChipFilter(
    els.layerFilters,
    layers.map(String),
    state.selectedLayers,
    (value) => {
      toggleSetValue(state.selectedLayers, value);
      render();
    },
    "L"
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
  const nodes = state.curriculum.nodes;
  const derived = state.derived || {
    edges: [],
    milestones: [],
    estimatedTotalHours: 0,
    maxLayer: 0,
  };

  const openQuestionCount = Array.isArray(state.curriculum.open_questions)
    ? state.curriculum.open_questions.length
    : 0;

  const cards = [
    ["Nodes", nodes.length],
    ["Edges", derived.edges.length],
    ["Max depth", derived.maxLayer],
    ["Milestones", derived.milestones.length],
    ["Est. hours", derived.estimatedTotalHours],
    ["Open questions", openQuestionCount],
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
  const maxLayer = state.derived?.maxLayer || 0;
  const byLayer = new Map(Array.from({ length: maxLayer + 1 }, (_, layer) => [layer, []]));

  filteredNodes.forEach((node) => {
    const layer = Number(state.derived?.nodeLayers?.[node.id] ?? 0);
    if (Number.isInteger(layer) && byLayer.has(layer)) {
      byLayer.get(layer).push(node);
    }
  });

  els.layerExplorer.innerHTML = "";

  Array.from(byLayer.keys())
    .sort((a, b) => a - b)
    .forEach((layer) => {
      const nodesInLayer = byLayer.get(layer) ?? [];
      const column = document.createElement("div");
      column.className = "layer-column";

      const heading = document.createElement("div");
      heading.className = "layer-title";
      heading.textContent = `Layer ${layer}`;
      column.append(heading);

      nodesInLayer
        .sort((a, b) => a.id.localeCompare(b.id))
        .forEach((node) => column.append(makeNodeCard(node, layer)));

      if (nodesInLayer.length === 0) {
        const empty = document.createElement("p");
        empty.className = "muted";
        empty.textContent = "No nodes";
        column.append(empty);
      }

      els.layerExplorer.append(column);
    });
}

function makeNodeCard(node, layer) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = `node-card ${state.selectedNodeId === node.id ? "selected" : ""}`;
  const safeId = escapeHtml(node.id);

  card.innerHTML = `
    <div class="title mono">${safeId} - ${escapeHtml(node.title)}</div>
    <div class="meta">Layer ${layer} | ${node.estimate_minutes}m</div>
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
      const layer = state.derived?.nodeLayers?.[node.id] ?? 0;
      const resourceCount = Array.isArray(node.resources) ? node.resources.length : 0;
      const safeId = escapeHtml(node.id);
      return `
        <tr class="clickable ${selectedClass}" data-node-id="${safeId}">
          <td class="mono">${safeId}</td>
          <td>${escapeHtml(node.title)}</td>
          <td>${layer}</td>
          <td>${node.estimate_minutes}m</td>
          <td>${resourceCount}</td>
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
            <th>Time</th>
            <th>Resources</th>
          </tr>
        </thead>
        <tbody>${rows || `<tr><td colspan="5">No nodes match filters.</td></tr>`}</tbody>
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

function renderLearningPath() {
  const topological = state.derived?.topologicalOrder || [];
  const criticalPath = new Set(state.derived?.criticalPath || []);

  els.learningPath.innerHTML = topological
    .map((nodeId, index) => {
      const marker = criticalPath.has(nodeId) ? "critical" : "path";
      const safeId = escapeHtml(nodeId);
      return `
        <div class="path-item">
          <span class="mono">${index + 1}. ${safeId}</span>
          <span class="chip-link" data-node-link="${safeId}">${marker}</span>
        </div>
      `;
    })
    .join("");

  bindNodeLinks(els.learningPath);
}

function renderMilestones() {
  els.milestones.innerHTML = (state.derived?.milestones || [])
    .map((milestone) => {
      const chips = (milestone.nodes || [])
        .map((nodeId) => {
          const safeId = escapeHtml(nodeId);
          return `<button class="chip-link mono" data-node-link="${safeId}">${safeId}</button>`;
        })
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

function renderOpenQuestions() {
  const openQuestions = Array.isArray(state.curriculum.open_questions)
    ? state.curriculum.open_questions
    : [];

  if (openQuestions.length === 0) {
    els.openQuestions.innerHTML = `<p class="muted">No open questions in this curriculum.</p>`;
    return;
  }

  els.openQuestions.innerHTML = openQuestions
    .map((item) => {
      const related = (item.related_nodes || [])
        .map((nodeId) => {
          const safeId = escapeHtml(nodeId);
          return `<button class="chip-link mono" data-node-link="${safeId}">${safeId}</button>`;
        })
        .join(" ");
      return `
        <article class="coverage-item">
          <div class="coverage-key">${escapeHtml(item.status || "open")}</div>
          <p>${escapeHtml(item.question || "")}</p>
          <div>${related}</div>
        </article>
      `;
    })
    .join("");

  bindNodeLinks(els.openQuestions);
}

function renderNodeDetails() {
  const node = state.curriculum.nodes.find((item) => item.id === state.selectedNodeId);
  if (!node) {
    els.nodeDetails.innerHTML = `<p class="details-placeholder">Select a node to inspect details.</p>`;
    return;
  }

  const layer = state.derived?.nodeLayers?.[node.id] ?? 0;
  const prereqLinks = formatNodeLinks(node.prerequisites || []);
  const dependentLinks = formatNodeLinks(state.derived?.dependentsById?.[node.id] || []);

  const resources = (node.resources || [])
    .map((resource) => {
      const citation = resource.citation ? ` | citation: ${escapeHtml(resource.citation)}` : "";
      return `<li><a href="${escapeHtml(resource.url)}" target="_blank" rel="noreferrer">${escapeHtml(
        resource.title
      )}</a> (${escapeHtml(resource.kind)}${resource.role ? `, ${escapeHtml(resource.role)}` : ""}${citation})</li>`;
    })
    .join("");

  els.nodeDetails.innerHTML = `
    <div class="kv">
      <div class="kv-key">Identity</div>
      <div class="kv-value mono">${escapeHtml(node.id)} - ${escapeHtml(node.title)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Meta</div>
      <div class="kv-value">Layer ${layer} | ${node.estimate_minutes}m</div>
    </div>
    <div class="kv">
      <div class="kv-key">Capability</div>
      <div class="kv-value">${escapeHtml(node.capability)}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Core ideas</div>
      <div class="kv-value">${escapeHtml((node.core_ideas || []).join(", "))}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Pitfalls</div>
      <div class="kv-value">${escapeHtml((node.pitfalls || []).join(", "))}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Mastery task</div>
      <div class="kv-value">${escapeHtml(node.mastery_check?.task || "")}</div>
    </div>
    <div class="kv">
      <div class="kv-key">Pass criteria</div>
      <div class="kv-value">${escapeHtml(node.mastery_check?.pass_criteria || "")}</div>
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
      <div class="kv-key">Resources</div>
      <div class="kv-value"><ul>${resources}</ul></div>
    </div>
  `;

  bindNodeLinks(els.nodeDetails);
}

function formatNodeLinks(nodeIds) {
  return nodeIds
    .map((nodeId) => {
      const safeId = escapeHtml(nodeId);
      return `<button class="chip-link mono" data-node-link="${safeId}">${safeId}</button>`;
    })
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
loadLatestRunCurriculum().catch((error) => {
  showStatus(`Failed to load latest run curriculum: ${error.message}`, "error");
});
