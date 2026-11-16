// SPDX-License-Identifier: Apache-2.0
// Interactive expansion & box-type selector with client-side STORE-mode ZIP downloads.

const stlBufferCache = new Map();

// ---------------------------------------------------------------------------
// Minimal PKZIP (STORE method 0) archive builder with standard IEEE CRC-32
// ---------------------------------------------------------------------------

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) !== 0 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[i] = c >>> 0;
  }
  return table;
})();

function crc32(bytes) {
  let crc = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) {
    crc = CRC_TABLE[(crc ^ bytes[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function buildZipBlob(entries) {
  const encoder = new TextEncoder();
  const localParts = [];
  const centralParts = [];
  let offset = 0;
  const count = entries.length;

  const now = new Date();
  const dosTime =
    ((now.getHours() & 0x1f) << 11) |
    ((now.getMinutes() & 0x3f) << 5) |
    ((now.getSeconds() >> 1) & 0x1f);
  const dosDate =
    (((Math.max(now.getFullYear(), 1980) - 1980) & 0x7f) << 9) |
    (((now.getMonth() + 1) & 0x0f) << 5) |
    (now.getDate() & 0x1f);

  for (const entry of entries) {
    const nameBytes = encoder.encode(entry.filename);
    const data = entry.bytes;
    const crc = crc32(data);
    const size = data.byteLength;

    const lfh = new Uint8Array(30 + nameBytes.length);
    const lv = new DataView(lfh.buffer);
    lv.setUint32(0, 0x04034b50, true);
    lv.setUint16(4, 20, true); // version needed: 2.0
    lv.setUint16(6, 0x0800, true); // UTF-8 filename flag
    lv.setUint16(8, 0, true); // compression method: 0 (STORE)
    lv.setUint16(10, dosTime, true);
    lv.setUint16(12, dosDate, true);
    lv.setUint32(14, crc, true);
    lv.setUint32(18, size, true);
    lv.setUint32(22, size, true);
    lv.setUint16(26, nameBytes.length, true);
    lv.setUint16(28, 0, true);
    lfh.set(nameBytes, 30);

    localParts.push(lfh, data);

    const cdh = new Uint8Array(46 + nameBytes.length);
    const cv = new DataView(cdh.buffer);
    cv.setUint32(0, 0x02014b50, true);
    cv.setUint16(4, 20, true); // version made by
    cv.setUint16(6, 20, true); // version needed
    cv.setUint16(8, 0x0800, true); // UTF-8 filename
    cv.setUint16(10, 0, true); // STORE
    cv.setUint16(12, dosTime, true);
    cv.setUint16(14, dosDate, true);
    cv.setUint32(16, crc, true);
    cv.setUint32(20, size, true);
    cv.setUint32(24, size, true);
    cv.setUint16(28, nameBytes.length, true);
    cv.setUint16(30, 0, true);
    cv.setUint16(32, 0, true);
    cv.setUint16(34, 0, true);
    cv.setUint16(36, 0, true);
    cv.setUint32(38, 0, true);
    cv.setUint32(42, offset, true);
    cdh.set(nameBytes, 46);

    centralParts.push(cdh);
    offset += lfh.byteLength + size;
  }

  let cdSize = 0;
  for (const part of centralParts) cdSize += part.byteLength;

  const eocd = new Uint8Array(22);
  const ev = new DataView(eocd.buffer);
  ev.setUint32(0, 0x06054b50, true);
  ev.setUint16(4, 0, true);
  ev.setUint16(6, 0, true);
  ev.setUint16(8, count, true);
  ev.setUint16(10, count, true);
  ev.setUint32(12, cdSize, true);
  ev.setUint32(16, offset, true);
  ev.setUint16(20, 0, true);

  return new Blob([...localParts, ...centralParts, eocd], {
    type: "application/zip",
  });
}

async function fetchStlBytes(uri) {
  if (stlBufferCache.has(uri)) {
    return stlBufferCache.get(uri);
  }
  const resp = await fetch(uri);
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status} while fetching ${uri}`);
  }
  const bytes = new Uint8Array(await resp.arrayBuffer());
  stlBufferCache.set(uri, bytes);
  return bytes;
}

async function downloadFilesAsZip(fileSpecs, zipFilename, onProgress) {
  if (!fileSpecs.length) return;
  const seenNames = new Set();
  const uniqueSpecs = [];
  for (const spec of fileSpecs) {
    if (seenNames.has(spec.filename)) continue;
    seenNames.add(spec.filename);
    uniqueSpecs.push(spec);
  }

  const results = new Array(uniqueSpecs.length);
  let completed = 0;
  let nextIdx = 0;
  const concurrency = Math.min(6, uniqueSpecs.length);

  async function worker() {
    while (nextIdx < uniqueSpecs.length) {
      const idx = nextIdx++;
      const spec = uniqueSpecs[idx];
      const bytes = await fetchStlBytes(spec.uri);
      results[idx] = { filename: spec.filename, bytes };
      completed += 1;
      if (onProgress) onProgress(completed, uniqueSpecs.length);
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()));
  const blob = buildZipBlob(results);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = zipFilename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}

// ---------------------------------------------------------------------------
// DOM helper utilities
// ---------------------------------------------------------------------------

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function sanitizeFilename(raw) {
  return String(raw).replace(/[^a-zA-Z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
}

// ---------------------------------------------------------------------------
// Box & Expansion Selector Controller
// ---------------------------------------------------------------------------

function initBoxSelector(container) {
  const configScript = container.querySelector("script[data-box-selector-config]");
  if (!configScript) return;

  let config;
  try {
    config = JSON.parse(configScript.textContent || "{}");
  } catch (err) {
    container.textContent = "Failed to parse box selector configuration.";
    return;
  }

  const allAvailableSubgroups = new Set();
  const subgroupsByExpansion = new Map();
  const expByKey = new Map();
  for (const exp of config.expansions || []) {
    expByKey.set(exp.key, exp);
    subgroupsByExpansion.set(exp.key, exp.subgroups || []);
    if (exp.status === "available") {
      for (const sg of exp.subgroups || []) allAvailableSubgroups.add(sg);
    }
  }

  const subgroupByKey = new Map((config.subgroups || []).map((s) => [s.key, s]));
  const categoryList = config.categories || [];
  const boxes = config.boxes || [];
  const presets = config.presets || [];
  const spacerSets = config.spacerSets || {};

  // Default state: last preset (full current layout) or first preset
  const defaultPreset =
    presets.find((p) => p.key === config.defaultPreset) ||
    presets[presets.length - 1] ||
    null;

  const state = {
    activeSubgroups: new Set(
      defaultPreset ? defaultPreset.subgroups : Array.from(allAvailableSubgroups),
    ),
    excludedBoxes: new Set(),
    includeSpacers: true,
    busy: false,
  };

  // Layout shells inside container
  const mount = container.querySelector("[data-box-selector-mount]") || container;
  mount.innerHTML = "";

  const rootEl = el("div", "bs-root");

  // 1. Presets + top CTA
  const presetBar = el("div", "bs-section bs-presets");
  const presetHeader = el("div", "bs-section-header");
  presetHeader.appendChild(el("h3", "bs-title", "1. Choose Configuration Preset"));
  presetBar.appendChild(presetHeader);
  const presetButtonsRow = el("div", "bs-preset-buttons");
  const presetButtons = new Map();
  for (const preset of presets) {
    const btn = el("button", "bs-preset-btn");
    btn.type = "button";
    const strong = el("span", "bs-preset-name", preset.name);
    const desc = el("span", "bs-preset-desc", preset.description);
    btn.appendChild(strong);
    btn.appendChild(desc);
    btn.addEventListener("click", () => {
      state.activeSubgroups = new Set(preset.subgroups || []);
      state.excludedBoxes.clear();
      render();
    });
    presetButtons.set(preset.key, btn);
    presetButtonsRow.appendChild(btn);
  }
  presetBar.appendChild(presetButtonsRow);
  rootEl.appendChild(presetBar);

  // 2. Expansion & Faction selector
  const expSection = el("div", "bs-section bs-expansions");
  expSection.appendChild(el("h3", "bs-title", "2. Expansions & Factions"));
  const expGrid = el("div", "bs-exp-grid");
  const expMasterInputs = new Map();
  const subgroupInputs = new Map();

  for (const exp of config.expansions || []) {
    const card = el(
      "div",
      `bs-exp-card ${exp.status === "planned" ? "is-planned" : "is-available"}`,
    );
    const headerRow = el("label", "bs-exp-header");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.disabled = exp.status !== "available" || Boolean(exp.required);
    headerRow.appendChild(cb);

    const titleWrap = el("div", "bs-exp-title-wrap");
    const titleLine = el("div", "bs-exp-title-line");
    titleLine.appendChild(el("strong", null, exp.name));
    if (exp.required) {
      titleLine.appendChild(el("span", "bs-badge is-core", "Base Core"));
    } else if (exp.status === "available") {
      titleLine.appendChild(el("span", "bs-badge is-ready", "Available"));
    } else {
      titleLine.appendChild(el("span", "bs-badge is-planned", "Planned"));
    }
    titleWrap.appendChild(titleLine);
    titleWrap.appendChild(el("div", "bs-exp-desc", exp.description));
    if (exp.notes) {
      titleWrap.appendChild(el("div", "bs-exp-notes", exp.notes));
    }
    headerRow.appendChild(titleWrap);
    card.appendChild(headerRow);

    if (exp.status === "available" && (exp.subgroups || []).length) {
      cb.addEventListener("change", () => {
        for (const sg of exp.subgroups) {
          if (cb.checked) state.activeSubgroups.add(sg);
          else if (!exp.required) state.activeSubgroups.delete(sg);
        }
        render();
      });
      expMasterInputs.set(exp.key, cb);

      const sgWrap = el("div", "bs-subgroups");
      for (const sgKey of exp.subgroups) {
        const sg = subgroupByKey.get(sgKey);
        if (!sg) continue;
        const sgLabel = el("label", "bs-subgroup-item");
        sgLabel.title = sg.description || "";
        const sgCb = document.createElement("input");
        sgCb.type = "checkbox";
        sgCb.addEventListener("change", () => {
          if (sgCb.checked) state.activeSubgroups.add(sgKey);
          else state.activeSubgroups.delete(sgKey);
          render();
        });
        sgLabel.appendChild(sgCb);
        sgLabel.appendChild(el("span", null, sg.name));
        sgWrap.appendChild(sgLabel);
        subgroupInputs.set(sgKey, sgCb);
      }
      card.appendChild(sgWrap);
    }

    expGrid.appendChild(card);
  }
  expSection.appendChild(expGrid);
  rootEl.appendChild(expSection);

  // 3. Breakdown by Type of Box & ZIP Downloads
  const breakdownSection = el("div", "bs-section bs-breakdown");
  const bdHeader = el("div", "bs-breakdown-top");
  bdHeader.appendChild(el("h3", "bs-title", "3. Box Type Breakdown & ZIP Downloads"));

  const masterActions = el("div", "bs-master-actions");
  const spacerToggleLabel = el("label", "bs-spacer-toggle");
  const spacerToggleCb = document.createElement("input");
  spacerToggleCb.type = "checkbox";
  spacerToggleCb.checked = true;
  spacerToggleCb.addEventListener("change", () => {
    state.includeSpacers = spacerToggleCb.checked;
    render();
  });
  spacerToggleLabel.appendChild(spacerToggleCb);
  spacerToggleLabel.appendChild(el("span", null, "Include fitting spacer trays"));

  const downloadAllBtn = el("button", "bs-btn bs-btn-primary", "Download Selected Bundle (.zip)");
  downloadAllBtn.type = "button";
  const statusSpan = el("span", "bs-status", "");
  masterActions.appendChild(spacerToggleLabel);
  masterActions.appendChild(downloadAllBtn);
  bdHeader.appendChild(masterActions);
  breakdownSection.appendChild(bdHeader);

  const summaryNote = el("div", "bs-summary-note");
  breakdownSection.appendChild(summaryNote);

  const catGrid = el("div", "bs-category-grid");
  breakdownSection.appendChild(catGrid);

  const lidBreakdownRow = el("div", "bs-lid-breakdown");
  breakdownSection.appendChild(lidBreakdownRow);
  breakdownSection.appendChild(statusSpan);
  rootEl.appendChild(breakdownSection);

  // 4. Synchronized 3-D Preview
  const viewerSection = el("div", "bs-section bs-preview-section");
  viewerSection.appendChild(el("h3", "bs-title", "4. Interactive Preview of Selected Boxes"));
  const viewerEl = container.querySelector(".stl-viewer");
  if (viewerEl) {
    viewerSection.appendChild(viewerEl);
  }
  rootEl.appendChild(viewerSection);

  // 5. Box Checklist Table
  const detailSection = el("details", "bs-section bs-detail-section");
  detailSection.open = true;
  const detailSummary = el("summary", "bs-title bs-detail-summary", "5. Selected Boxes List");
  detailSection.appendChild(detailSummary);
  const tableWrap = el("div", "bs-table-wrap");
  detailSection.appendChild(tableWrap);
  rootEl.appendChild(detailSection);

  mount.appendChild(rootEl);

  // Helper to resolve current preset / spacer set
  function resolveActiveExpansionPreset() {
    const selectedArr = Array.from(state.activeSubgroups).sort();
    for (const preset of presets) {
      const pArr = [...(preset.subgroups || [])].sort();
      if (
        pArr.length === selectedArr.length &&
        pArr.every((v, idx) => v === selectedArr[idx])
      ) {
        return preset;
      }
    }
    return null;
  }

  function resolveSpacers(activePreset) {
    if (activePreset && spacerSets[activePreset.spacerPresetKey]) {
      return {
        exact: true,
        presetName: activePreset.name,
        items: spacerSets[activePreset.spacerPresetKey],
      };
    }
    const baseKeys = new Set(subgroupsByExpansion.get("base") || []);
    const allRiverfolkPresent = (subgroupsByExpansion.get("riverfolk") || []).every((sg) =>
      state.activeSubgroups.has(sg),
    );
    const allBasePresent = Array.from(baseKeys).every((sg) =>
      state.activeSubgroups.has(sg),
    );
    if (allBasePresent && allRiverfolkPresent && spacerSets["base+riverfolk"]) {
      return {
        exact: true,
        presetName: "Base + Riverfolk",
        items: spacerSets["base+riverfolk"],
      };
    }
    if (allBasePresent && spacerSets.base) {
      return {
        exact: false,
        presetName: "Base Game",
        items: spacerSets.base,
      };
    }
    return {
      exact: false,
      presetName: "Full Layout",
      items: spacerSets["base+riverfolk"] || [],
    };
  }

  async function triggerZip(btn, files, zipName) {
    if (state.busy || !files.length) return;
    state.busy = true;
    const prevText = btn.textContent;
    btn.disabled = true;
    statusSpan.className = "bs-status";
    statusSpan.textContent = `Preparing ${zipName}\u2026`;
    try {
      await downloadFilesAsZip(files, zipName, (done, total) => {
        btn.textContent = `Packing ${done}/${total}\u2026`;
        statusSpan.textContent = `Fetching STL ${done} of ${total} for ${zipName}\u2026`;
      });
      statusSpan.textContent = `Downloaded ${zipName} (${files.length} STL files).`;
    } catch (err) {
      statusSpan.className = "bs-status is-error";
      statusSpan.textContent =
        "Could not fetch STL files to build ZIP (serve docs over HTTP/HTTPS, not file://).";
    } finally {
      btn.textContent = prevText;
      btn.disabled = false;
      state.busy = false;
    }
  }

  function render() {
    const activePreset = resolveActiveExpansionPreset();

    // Update preset highlights
    for (const [key, btn] of presetButtons.entries()) {
      btn.classList.toggle("is-active", Boolean(activePreset && activePreset.key === key));
    }

    // Sync expansion & subgroup checkboxes
    for (const [expKey, masterCb] of expMasterInputs.entries()) {
      const sgs = subgroupsByExpansion.get(expKey) || [];
      const activeCount = sgs.filter((sg) => state.activeSubgroups.has(sg)).length;
      masterCb.checked = sgs.length > 0 && activeCount === sgs.length;
      masterCb.indeterminate = activeCount > 0 && activeCount < sgs.length;
    }
    for (const [sgKey, sgCb] of subgroupInputs.entries()) {
      sgCb.checked = state.activeSubgroups.has(sgKey);
    }

    // Active boxes (matching active subgroups and not manually unchecked)
    const candidateBoxes = boxes.filter((b) => state.activeSubgroups.has(b.subgroup));
    const selectedBoxes = candidateBoxes.filter((b) => !state.excludedBoxes.has(b.label));
    const spacerInfo = resolveSpacers(activePreset);
    const activeSpacers = state.includeSpacers ? spacerInfo.items : [];

    const allSelectedFiles = [];
    for (const b of selectedBoxes) {
      for (const f of b.files || []) allSelectedFiles.push(f);
    }
    for (const sp of activeSpacers) {
      for (const f of sp.files || []) allSelectedFiles.push(f);
    }

    const bundleSuffix = activePreset ? sanitizeFilename(activePreset.key) : "custom";
    const fullZipName = `${sanitizeFilename(config.projectName || "Insert")}_${bundleSuffix}.zip`;

    downloadAllBtn.disabled = allSelectedFiles.length === 0;
    downloadAllBtn.textContent = `Download Selected Bundle (${allSelectedFiles.length} STLs .zip)`;
    downloadAllBtn.onclick = () => triggerZip(downloadAllBtn, allSelectedFiles, fullZipName);

    // Summary line
    summaryNote.textContent = "";
    const sumStrong = el(
      "strong",
      null,
      `${selectedBoxes.length} box(es)` +
        (activeSpacers.length ? ` + ${activeSpacers.length} spacer tray(s)` : "") +
        ` (${allSelectedFiles.length} printable STL files)`,
    );
    summaryNote.appendChild(sumStrong);
    if (activePreset) {
      summaryNote.appendChild(
        document.createTextNode(` — Preset: ${activePreset.name}`),
      );
    } else {
      summaryNote.appendChild(
        document.createTextNode(" — Custom selection"),
      );
      if (state.includeSpacers && !spacerInfo.exact) {
        summaryNote.appendChild(
          document.createTextNode(
            ` (using closest spacer layout: ${spacerInfo.presetName}; regenerate via build_root_project() if printing a custom partial subset)`,
          ),
        );
      }
    }

    // Category cards (Card Boxes, Faction Boxes, Items & Dice, Spacer Trays)
    catGrid.innerHTML = "";
    for (const cat of categoryList) {
      const card = el("div", "bs-cat-card");
      const isSpacers = cat.key === "spacers";
      const items = isSpacers
        ? activeSpacers
        : selectedBoxes.filter((b) => b.category === cat.key);
      const files = [];
      for (const item of items) {
        for (const f of item.files || []) files.push(f);
      }

      const catHead = el("div", "bs-cat-head");
      catHead.appendChild(el("div", "bs-cat-name", cat.name));
      catHead.appendChild(
        el("span", "bs-badge", isSpacers ? `${items.length} tray(s)` : `${items.length} box(es)`),
      );
      card.appendChild(catHead);
      card.appendChild(el("div", "bs-cat-desc", cat.description));

      const itemList = el(
        "div",
        "bs-cat-items",
        items.length ? items.map((x) => x.label).join(", ") : "None selected",
      );
      card.appendChild(itemList);

      const zipBtn = el(
        "button",
        "bs-btn bs-btn-secondary",
        files.length ? `Download ${cat.name} (${files.length} STLs .zip)` : "None Selected",
      );
      zipBtn.type = "button";
      zipBtn.disabled = files.length === 0;
      const catZipName = `${sanitizeFilename(config.projectName || "Insert")}_${sanitizeFilename(cat.name)}_${bundleSuffix}.zip`;
      zipBtn.addEventListener("click", () => triggerZip(zipBtn, files, catZipName));
      card.appendChild(zipBtn);

      catGrid.appendChild(card);
    }

    // Construction / lid type breakdown pills
    lidBreakdownRow.innerHTML = "";
    lidBreakdownRow.appendChild(el("span", "bs-lid-label", "By lid construction:"));
    const byType = new Map();
    for (const b of selectedBoxes) {
      const list = byType.get(b.boxTypeLabel) || [];
      list.push(b);
      byType.set(b.boxTypeLabel, list);
    }
    for (const [typeLabel, typeBoxes] of byType.entries()) {
      const files = typeBoxes.flatMap((b) => b.files || []);
      const btn = el(
        "button",
        "bs-pill-btn",
        `${typeLabel}: ${typeBoxes.length} box(es) \u2193 .zip`,
      );
      btn.type = "button";
      const zipName = `${sanitizeFilename(config.projectName || "Insert")}_${sanitizeFilename(typeLabel)}_${bundleSuffix}.zip`;
      btn.addEventListener("click", () => triggerZip(btn, files, zipName));
      lidBreakdownRow.appendChild(btn);
    }
    if (activeSpacers.length) {
      const spFiles = activeSpacers.flatMap((s) => s.files || []);
      const btn = el(
        "button",
        "bs-pill-btn",
        `Spacer Trays (Open): ${activeSpacers.length} tray(s) \u2193 .zip`,
      );
      btn.type = "button";
      const zipName = `${sanitizeFilename(config.projectName || "Insert")}_Spacers_${bundleSuffix}.zip`;
      btn.addEventListener("click", () => triggerZip(btn, spFiles, zipName));
      lidBreakdownRow.appendChild(btn);
    }

    // Table of selected candidate boxes + spacers
    tableWrap.innerHTML = "";
    const table = el("table", "bs-table");
    const thead = document.createElement("thead");
    const hr = document.createElement("tr");
    for (const colTitle of [
      "Include",
      "Box / Spacer",
      "Expansion / Group",
      "Box Type",
      "Lid Style",
      "Dimensions",
      "STL Files",
    ]) {
      hr.appendChild(el("th", null, colTitle));
    }
    thead.appendChild(hr);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const b of candidateBoxes) {
      const tr = document.createElement("tr");
      const checked = !state.excludedBoxes.has(b.label);
      if (!checked) tr.classList.add("is-muted");

      const tdCb = document.createElement("td");
      const bCb = document.createElement("input");
      bCb.type = "checkbox";
      bCb.checked = checked;
      bCb.addEventListener("change", () => {
        if (bCb.checked) state.excludedBoxes.delete(b.label);
        else state.excludedBoxes.add(b.label);
        render();
      });
      tdCb.appendChild(bCb);
      tr.appendChild(tdCb);

      const tdName = document.createElement("td");
      const anchor = el("a", null, b.label);
      anchor.href = `#${b.anchor}`;
      tdName.appendChild(anchor);
      if (b.description) {
        tdName.appendChild(el("div", "bs-table-sub", b.description));
      }
      tr.appendChild(tdName);

      const expName = expByKey.get(b.expansion)?.name || b.expansion;
      const sgName = subgroupByKey.get(b.subgroup)?.name || b.subgroup;
      const tdExp = document.createElement("td");
      tdExp.appendChild(el("div", null, sgName));
      tdExp.appendChild(el("div", "bs-table-sub", expName));
      tr.appendChild(tdExp);

      tr.appendChild(el("td", null, b.categoryName));
      tr.appendChild(el("td", null, b.boxTypeLabel));
      tr.appendChild(el("td", "bs-mono", b.dimensions));

      const tdFiles = document.createElement("td");
      tdFiles.className = "bs-files-cell";
      for (const f of b.files || []) {
        const dl = el("a", "bs-file-link", f.kind === "body" ? "Body" : "Lid");
        dl.href = f.uri;
        dl.download = f.filename;
        tdFiles.appendChild(dl);
      }
      tr.appendChild(tdFiles);
      tbody.appendChild(tr);
    }

    for (const sp of activeSpacers) {
      const tr = document.createElement("tr");
      tr.classList.add("is-spacer");
      tr.appendChild(el("td", null, "\u2713"));
      const tdName = el("td");
      tdName.appendChild(el("strong", null, sp.label));
      tdName.appendChild(el("div", "bs-table-sub", `Pos: ${sp.position}`));
      tr.appendChild(tdName);
      tr.appendChild(el("td", null, `${spacerInfo.presetName} Layout`));
      tr.appendChild(el("td", null, "Spacer Trays"));
      tr.appendChild(el("td", null, "No Lid (Spacer)"));
      tr.appendChild(el("td", "bs-mono", sp.dimensions));
      const tdFiles = document.createElement("td");
      for (const f of sp.files || []) {
        const dl = el("a", "bs-file-link", "STL");
        dl.href = f.uri;
        dl.download = f.filename;
        tdFiles.appendChild(dl);
      }
      tr.appendChild(tdFiles);
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    tableWrap.appendChild(table);

    detailSummary.textContent =
      `5. Selected Boxes & STL Parts (${selectedBoxes.length} boxes` +
      (activeSpacers.length ? `, ${activeSpacers.length} spacers` : "") +
      ")";

    // Sync 3-D viewer
    if (viewerEl) {
      const uris = allSelectedFiles.map((f) => f.uri);
      if (viewerEl._stlViewer && typeof viewerEl._stlViewer.setUris === "function") {
        viewerEl._stlViewer.setUris(uris);
      } else {
        viewerEl.dataset.stlUri = uris.join(",");
      }
    }
  }

  render();
}

function initAllSelectors() {
  const selectors = document.querySelectorAll("[data-box-selector]");
  for (const container of selectors) {
    if (container._boxSelectorInitialized) continue;
    container._boxSelectorInitialized = true;
    initBoxSelector(container);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initAllSelectors);
} else {
  initAllSelectors();
}
