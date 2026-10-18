import { Vesc } from './vesc.js';
import { BleTransport, SerialTransport } from './transport.js';
import { SimTransport } from './sim.js';
import { COMM, Writer } from './protocol.js';
import {
  T, definitionForFw, definitionForSignature, displayValue, fromDisplayValue, displayRange,
} from './config.js';

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

const state = {
  vesc: null,
  fw: null,
  configs: { mcconf: null, appconf: null },
  readSnap: { mcconf: null, appconf: null },
  page: 'connect',
};

// ---------------------------------------------------------------- utilitaires

let toastTimer = null;
function toast(msg, error = false) {
  const el = $('#toast');
  el.textContent = msg;
  el.classList.toggle('error', error);
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, error ? 6000 : 3000);
}

function fmt(v, dec = 2) {
  return Number.isFinite(v) ? v.toFixed(dec) : '–';
}

function download(name, content, type = 'text/plain') {
  const blob = content instanceof Blob ? content : new Blob([content], { type });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function pickFile(accept) {
  return new Promise((resolve) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = accept;
    input.onchange = () => resolve(input.files[0] || null);
    input.click();
  });
}

function setKv(dl, pairs) {
  dl.replaceChildren();
  for (const [k, v] of pairs) {
    const dt = document.createElement('dt');
    dt.textContent = k;
    const dd = document.createElement('dd');
    dd.textContent = v;
    dl.append(dt, dd);
  }
}

function connected() {
  return !!state.vesc;
}

function requireConn() {
  if (!connected()) {
    toast("Connecte-toi d'abord à un VESC", true);
    return false;
  }
  return true;
}

function setStatus(text, cls) {
  const el = $('#connStatus');
  el.textContent = text;
  el.className = 'status ' + cls;
}

// ---------------------------------------------------------------- navigation

function showPage(page) {
  state.page = page;
  for (const b of $$('#tabs button')) b.classList.toggle('active', b.dataset.page === page);
  for (const s of $$('.page')) s.classList.toggle('active', s.id === 'page-' + page);
  if (page !== 'control') stopHold();
  if (page === 'control') startControlPoll(); else stopControlPoll();
  if (page !== 'inputs') stopInputs();
  if (page === 'realtime') resizeChart();
}

$('#tabs').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-page]');
  if (b) showPage(b.dataset.page);
});

// ---------------------------------------------------------------- connexion

if (!BleTransport.supported) {
  const el = $('#bleSupport');
  el.hidden = false;
  el.textContent = "Ce navigateur ne gère pas le Bluetooth Web. Utilise Chrome ou Edge (Android, ordinateur). "
    + "Sur iPhone, l'application Bluefy permet d'utiliser cette page.";
  $('#btnBle').disabled = true;
}
if (!SerialTransport.supported) $('#btnUsb').hidden = true;

$('#btnBle').addEventListener('click', () => connect(new BleTransport()));
$('#btnUsb').addEventListener('click', () => connect(new SerialTransport()));
$('#btnDemo').addEventListener('click', () => connect(new SimTransport()));
$('#btnDisconnect').addEventListener('click', () => disconnect());

async function connect(transport) {
  if (state.vesc) await disconnect();
  const vesc = new Vesc(transport);
  setStatus('Connexion…', 'busy');
  try {
    await vesc.open();
  } catch (e) {
    setStatus('Déconnecté', 'off');
    if (e.name !== 'NotFoundError') toast('Connexion impossible : ' + e.message, true);
    return;
  }
  state.vesc = vesc;
  vesc.addEventListener('close', () => onDisconnected());
  vesc.addEventListener('print', (e) => termAppend(e.detail));
  $('#btnDisconnect').hidden = false;
  setStatus(transport.name, 'on');

  try {
    await loadTarget();
    toast('Connecté à ' + transport.name);
  } catch (e) {
    toast('Connecté, mais lecture impossible : ' + e.message, true);
  }
}

async function disconnect() {
  const v = state.vesc;
  if (!v) return;
  stopHold();
  await v.close();
  onDisconnected();
}

function onDisconnected() {
  if (!state.vesc) return;
  state.vesc = null;
  stopRealtime();
  stopHold();
  stopInputs();
  stopControlPoll();
  setStatus('Déconnecté', 'off');
  $('#btnDisconnect').hidden = true;
  $('#infoCard').hidden = true;
  const sel = $('#canTarget');
  sel.replaceChildren(new Option('Local', '-1'));
  toast('VESC déconnecté');
}

// Lit les informations et les configurations du VESC ciblé (local ou CAN).
async function loadTarget() {
  const v = state.vesc;
  const fw = await v.getFwVersion();
  state.fw = fw;
  const hwTypes = ['VESC', 'VESC BMS', 'Module'];
  setKv($('#fwInfo'), [
    ['Firmware', fw.major + '.' + String(fw.minor).padStart(2, '0') + (fw.isTestFw ? ' (test ' + fw.isTestFw + ')' : '')],
    ['Matériel', fw.hw || '?'],
    ['Type', hwTypes[fw.hwType] ?? '?'],
    ['UUID', fw.uuid || '?'],
    ['Nom', fw.fwName || '–'],
    ['Appairé', fw.isPaired ? 'oui' : 'non'],
  ]);
  $('#fwHwName').textContent = fw.hw || '?';
  $('#infoCard').hidden = false;

  if (fw.hwType && fw.hwType !== 0) {
    state.configs = { mcconf: null, appconf: null };
    renderConfigPages();
    return;
  }
  await readConfig('mcconf', false, true);
  await readConfig('appconf', false, true);
}

$('#canTarget').addEventListener('change', async (e) => {
  if (!state.vesc) return;
  state.vesc.canId = Number(e.target.value);
  try {
    await loadTarget();
    toast(state.vesc.canId < 0 ? 'Cible : VESC local' : 'Cible : CAN ' + state.vesc.canId);
  } catch (err) {
    toast('Lecture impossible : ' + err.message, true);
  }
});

$('#btnScanCan').addEventListener('click', async () => {
  if (!requireConn()) return;
  const list = $('#canList');
  list.replaceChildren();
  try {
    const devs = await state.vesc.pingCan();
    const sel = $('#canTarget');
    const current = sel.value;
    sel.replaceChildren(new Option('Local', '-1'));
    for (const id of devs) {
      sel.append(new Option('CAN ' + id, String(id)));
      const li = document.createElement('li');
      li.className = 'chip';
      li.textContent = 'CAN ' + id;
      li.onclick = () => { sel.value = String(id); sel.dispatchEvent(new Event('change')); };
      list.append(li);
    }
    sel.value = [...sel.options].some((o) => o.value === current) ? current : '-1';
    toast(devs.length ? devs.length + ' VESC trouvé(s) sur le CAN' : 'Aucun autre VESC sur le CAN');
  } catch (e) {
    toast('Scan CAN : ' + e.message, true);
  }
});

$('#btnReboot').addEventListener('click', () => {
  if (!requireConn()) return;
  if (confirm('Redémarrer le VESC ?')) state.vesc.reboot();
});

// ---------------------------------------------------------------- configurations

async function readConfig(kind, defaults = false, quiet = false) {
  if (!requireConn()) return;
  const v = state.vesc;
  const bytes = await v.getConfigBytes(kind, defaults);
  const sig = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).getUint32(0);
  let cfg = state.configs[kind];
  if (!cfg || cfg.signature !== sig) {
    cfg = await definitionForSignature(kind, sig);
    if (!cfg && state.fw) cfg = await definitionForFw(kind, state.fw.major, state.fw.minor);
    if (!cfg || cfg.signature !== sig) {
      state.configs[kind] = null;
      renderConfigPages();
      throw new Error('Version de configuration non reconnue (signature ' + sig + ')');
    }
  }
  cfg.deserialize(bytes);
  state.configs[kind] = cfg;
  if (!defaults) state.readSnap[kind] = cfg.snapshot();
  renderConfigPage(kind);
  if (!quiet) toast((kind === 'mcconf' ? 'Config moteur' : 'Config app') + (defaults ? ' par défaut chargée' : ' lue'));
}

async function writeConfig(kind) {
  if (!requireConn()) return;
  const cfg = state.configs[kind];
  if (!cfg) return;
  const n = state.readSnap[kind] ? cfg.diff(state.readSnap[kind]).length : 0;
  if (!confirm('Écrire la configuration ' + (kind === 'mcconf' ? 'moteur' : 'app')
    + ' dans le VESC ? (' + n + ' paramètre(s) modifié(s))')) return;
  try {
    await state.vesc.setConfig(cfg);
    // Relit pour vérifier, comme VESC Tool.
    const wanted = cfg.snapshot();
    await readConfig(kind, false, true);
    const diff = cfg.diff(wanted);
    if (diff.length) {
      toast('Écrit, mais le VESC a modifié : ' + diff.slice(0, 5).join(', ') + (diff.length > 5 ? '…' : ''), true);
    } else {
      toast('Configuration écrite');
    }
  } catch (e) {
    toast("Échec de l'écriture : " + e.message, true);
  }
}

const viewState = { mcconf: { group: 0, sub: 0, search: '' }, appconf: { group: 0, sub: 0, search: '' } };
const unsubscribers = { mcconf: null, appconf: null };

function renderConfigPages() {
  renderConfigPage('mcconf');
  renderConfigPage('appconf');
}

function renderConfigPage(kind) {
  const page = $('#page-' + kind);
  const cfg = state.configs[kind];
  const title = kind === 'mcconf' ? 'Configuration moteur' : "Configuration de l'application";

  page.replaceChildren();
  const toolbar = document.createElement('div');
  toolbar.className = 'toolbar';
  const mk = (label, cls, fn, title) => {
    const b = document.createElement('button');
    b.className = 'btn ' + cls;
    b.textContent = label;
    if (title) b.title = title;
    b.onclick = fn;
    toolbar.append(b);
    return b;
  };
  mk('Lire', 'primary', () => readConfig(kind).catch((e) => toast(e.message, true)), 'Lire la configuration du VESC');
  mk('Lire défauts', '', () => readConfig(kind, true).catch((e) => toast(e.message, true)), 'Charger les valeurs par défaut du firmware (sans les écrire)');
  mk('Écrire', 'primary', () => writeConfig(kind), 'Écrire la configuration dans le VESC');
  mk('Annuler modifs', 'ghost', () => {
    if (cfg && state.readSnap[kind]) cfg.restore(state.readSnap[kind]);
  }, 'Revenir aux dernières valeurs lues');
  mk('Exporter XML', 'ghost', () => {
    if (!cfg) return;
    download((kind === 'mcconf' ? 'mcconf' : 'appconf') + '_' + new Date().toISOString().slice(0, 10) + '.xml', cfg.toXml(), 'application/xml');
  }, 'Fichier compatible avec VESC Tool');
  mk('Importer XML', 'ghost', async () => {
    if (!cfg) return;
    const f = await pickFile('.xml');
    if (!f) return;
    try {
      const n = cfg.fromXml(await f.text());
      toast(n + ' paramètres importés. Vérifie puis clique sur Écrire.');
    } catch (e) {
      toast('Import impossible : ' + e.message, true);
    }
  }, 'Charger un fichier XML de VESC Tool');
  page.append(toolbar);

  if (unsubscribers[kind]) unsubscribers[kind]();
  unsubscribers[kind] = null;

  if (!cfg) {
    const empty = document.createElement('div');
    empty.className = 'card cfg-empty';
    empty.textContent = connected()
      ? "Configuration non disponible pour ce contrôleur."
      : 'Connecte-toi à un VESC (ou au mode démo) pour afficher la configuration.';
    page.append(empty);
    return;
  }

  const layout = document.createElement('div');
  layout.className = 'cfg-layout';
  const nav = document.createElement('div');
  nav.className = 'card cfg-groups';
  const body = document.createElement('div');
  body.className = 'card';
  layout.append(nav, body);
  page.append(layout);

  const vs = viewState[kind];
  if (vs.group >= cfg.groups.length) { vs.group = 0; vs.sub = 0; }

  const subButtons = [];
  cfg.groups.forEach(([gname, subs], gi) => {
    const det = document.createElement('details');
    det.open = gi === vs.group;
    const sum = document.createElement('summary');
    sum.textContent = gname;
    det.append(sum);
    subs.forEach(([sname, names], si) => {
      const b = document.createElement('button');
      b.textContent = sname;
      b.dataset.names = names.join(',');
      b.classList.toggle('active', gi === vs.group && si === vs.sub && !vs.search);
      b.onclick = () => {
        vs.group = gi;
        vs.sub = si;
        vs.search = '';
        search.value = '';
        for (const x of subButtons) x.classList.toggle('active', x === b);
        mobileSel.value = gi + ':' + si;
        drawParams();
      };
      subButtons.push(b);
      det.append(b);
    });
    nav.append(det);
  });

  // Sur téléphone, un menu déroulant remplace la liste des groupes.
  const mobileSel = document.createElement('select');
  mobileSel.className = 'cfg-mobile-nav';
  cfg.groups.forEach(([gname, subs], gi) => {
    const og = document.createElement('optgroup');
    og.label = gname;
    subs.forEach(([sname], si) => og.append(new Option(sname, gi + ':' + si)));
    mobileSel.append(og);
  });
  mobileSel.value = vs.group + ':' + vs.sub;
  mobileSel.onchange = () => {
    const [gi, si] = mobileSel.value.split(':').map(Number);
    subButtons.find((b, i) => i === cfg.groups.slice(0, gi).reduce((n, g) => n + g[1].length, 0) + si)?.click();
  };

  const head = document.createElement('div');
  head.className = 'cfg-head';
  const h2 = document.createElement('h2');
  const search = document.createElement('input');
  search.type = 'search';
  search.placeholder = 'Rechercher un paramètre…';
  search.className = 'cfg-search';
  search.value = vs.search;
  search.oninput = () => {
    vs.search = search.value.trim();
    for (const x of subButtons) x.classList.toggle('active', !vs.search && x === subButtons[subIndex()]);
    drawParams();
  };
  head.append(h2, search);
  const list = document.createElement('div');
  body.append(mobileSel, head, list);

  function subIndex() {
    let i = 0;
    for (let g = 0; g < vs.group; g++) i += cfg.groups[g][1].length;
    return i + vs.sub;
  }

  let rows = new Map();

  function drawParams() {
    list.replaceChildren();
    rows = new Map();
    let names;
    if (vs.search) {
      const q = vs.search.toLowerCase();
      names = Object.keys(cfg.params).filter((n) => n.toLowerCase().includes(q)
        || (cfg.params[n].n || '').toLowerCase().includes(q));
      h2.textContent = names.length + ' résultat(s)';
    } else {
      const [gname, subs] = cfg.groups[vs.group];
      const [sname, sn] = subs[vs.sub];
      names = sn;
      h2.textContent = gname + ' › ' + sname;
    }
    for (const name of names) {
      if (name.startsWith('::sep::')) {
        const s = document.createElement('div');
        s.className = 'sep';
        s.textContent = name.slice(7);
        list.append(s);
        continue;
      }
      if (!cfg.has(name)) continue;
      const row = makeParamRow(cfg, name);
      rows.set(name, row);
      list.append(row.el);
    }
    refreshMods();
  }

  function refreshMods() {
    const snap = state.readSnap[kind];
    const mods = new Set(snap ? cfg.diff(snap) : []);
    for (const [name, row] of rows) row.el.classList.toggle('mod', mods.has(name));
    for (const b of subButtons) b.classList.toggle('mod', b.dataset.names.split(',').some((n) => mods.has(n)));
  }

  unsubscribers[kind] = cfg.onChange((name) => {
    if (name === null) {
      for (const row of rows.values()) row.update();
    } else {
      rows.get(name)?.update();
    }
    refreshMods();
  });

  drawParams();
}

function makeParamRow(cfg, name) {
  const p = cfg.params[name];
  const el = document.createElement('div');
  el.className = 'param';

  const label = document.createElement('div');
  label.className = 'name';
  label.textContent = p.n || name;
  const small = document.createElement('small');
  small.textContent = name;
  label.append(small);

  const edit = document.createElement('div');
  edit.className = 'edit';
  let update = () => {};

  switch (p.t) {
    case T.DOUBLE:
    case T.INT: {
      const input = document.createElement('input');
      input.type = 'number';
      const [min, max] = displayRange(p);
      input.min = String(min);
      input.max = String(max);
      if (p.t === T.DOUBLE) {
        const dec = p.dec ?? 2;
        input.step = p.pct ? '0.1' : String(Math.pow(10, -dec));
      } else {
        input.step = String(p.step ?? 1);
      }
      input.inputMode = 'decimal';
      update = () => {
        const v = displayValue(p);
        input.value = p.t === T.DOUBLE ? String(Number(v.toFixed(p.pct ? 1 : Math.max(p.dec ?? 2, 4)))) : String(v);
      };
      input.onchange = () => {
        let v = Number(input.value);
        if (!Number.isFinite(v)) { update(); return; }
        v = Math.min(max, Math.max(min, v));
        cfg.set(name, fromDisplayValue(p, v));
        update();
      };
      edit.append(input);
      const unit = p.pct ? '%' : (p.u || '').trim();
      if (unit) {
        const u = document.createElement('span');
        u.className = 'unit';
        u.textContent = unit;
        edit.append(u);
      }
      break;
    }
    case T.ENUM: {
      const sel = document.createElement('select');
      (p.e || []).forEach((n, i) => sel.append(new Option(n, String(i))));
      update = () => { sel.value = String(p.value); };
      sel.onchange = () => cfg.set(name, Number(sel.value));
      edit.append(sel);
      break;
    }
    case T.BOOL: {
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      update = () => { cb.checked = !!p.value; };
      cb.onchange = () => cfg.set(name, cb.checked ? 1 : 0);
      edit.append(cb);
      break;
    }
    case T.BITFIELD: {
      const box = document.createElement('div');
      box.className = 'bits';
      const cbs = (p.e || []).map((n, i) => {
        const l = document.createElement('label');
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.onchange = () => {
          let v = p.value & 0xFF;
          v = cb.checked ? v | (1 << i) : v & ~(1 << i);
          cfg.set(name, v);
        };
        l.append(cb, n);
        box.append(l);
        return cb;
      });
      update = () => cbs.forEach((cb, i) => { cb.checked = !!((p.value >> i) & 1); });
      edit.append(box);
      break;
    }
    case T.STRING: {
      const input = document.createElement('input');
      input.type = 'text';
      if (p.ml) input.maxLength = p.ml;
      update = () => { input.value = p.value; };
      input.onchange = () => cfg.set(name, input.value);
      edit.append(input);
      break;
    }
    default:
      edit.textContent = '—';
  }

  const help = document.createElement('button');
  help.className = 'help-btn';
  help.textContent = '?';
  help.title = 'Aide';
  help.onclick = () => {
    $('#helpTitle').textContent = p.n || name;
    $('#helpBody').textContent = (p.d || 'Pas de description.') + '\n\n' + name;
    $('#helpDialog').showModal();
  };

  el.append(label, edit, help);
  update();
  return { el, update };
}

renderConfigPages();

// ---------------------------------------------------------------- temps réel

const TILES = [
  ['v_in', 'Tension', 'V', 1],
  ['current_motor', 'Courant moteur', 'A', 1],
  ['current_in', 'Courant batterie', 'A', 1],
  ['power', 'Puissance', 'W', 0],
  ['duty_now', 'Rapport cyclique', '%', 1],
  ['rpm', 'ERPM', '', 0],
  ['temp_mos', 'Temp. MOSFET', '°C', 1],
  ['temp_motor', 'Temp. moteur', '°C', 1],
  ['amp_hours', 'Consommé', 'Ah', 3],
  ['amp_hours_charged', 'Régénéré', 'Ah', 3],
  ['watt_hours', 'Consommé', 'Wh', 2],
  ['tachometer_abs', 'Tachymètre', '', 0],
];

const SERIES = [
  { id: 'cur', label: 'Courants', on: true, keys: [['current_motor', 'Moteur', 'A'], ['current_in', 'Batterie', 'A']] },
  { id: 'duty', label: 'Rapport cyclique', on: true, keys: [['duty_now', 'Duty', '%']] },
  { id: 'rpm', label: 'ERPM', on: true, keys: [['rpm', 'ERPM', '']] },
  { id: 'v', label: 'Tension', on: false, keys: [['v_in', 'Vin', 'V']] },
  { id: 'temp', label: 'Températures', on: false, keys: [['temp_mos', 'MOSFET', '°C'], ['temp_motor', 'Moteur', '°C']] },
  { id: 'pow', label: 'Puissance', on: false, keys: [['power', 'Puissance', 'W']] },
  { id: 'dq', label: 'Id / Iq', on: false, keys: [['id', 'Id', 'A'], ['iq', 'Iq', 'A']] },
];
const COLORS = ['#0e7cbd', '#e8833a', '#2e9e5b', '#c2417a', '#7c5cd6'];

const rt = { running: false, timer: null, history: [], recording: null, maxPoints: 600 };

const tilesEl = $('#rtTiles');
const tileValues = {};
for (const [key, label, unit] of TILES) {
  const t = document.createElement('div');
  t.className = 'tile';
  t.innerHTML = '<div class="label"></div><div><span class="value">–</span><span class="unit"></span></div>';
  t.querySelector('.label').textContent = label;
  t.querySelector('.unit').textContent = unit;
  tileValues[key] = t.querySelector('.value');
  tilesEl.append(t);
}

const seriesEl = $('#chartSeries');
for (const s of SERIES) {
  const c = document.createElement('span');
  c.className = 'chip' + (s.on ? ' on' : '');
  c.textContent = s.label;
  c.onclick = () => { s.on = !s.on; c.classList.toggle('on', s.on); resizeChart(); };
  seriesEl.append(c);
}

function enrich(v) {
  v.power = v.v_in * v.current_in;
  v.duty_now *= 100;
  return v;
}

function showValues(v) {
  for (const [key, , , dec] of TILES) tileValues[key].textContent = fmt(v[key], dec);
  const fb = $('#faultBanner');
  fb.hidden = !v.fault_code;
  fb.textContent = v.fault_code ? 'Défaut : ' + v.fault_str : '';
}

async function rtLoop() {
  if (!rt.running || !state.vesc) return;
  const t0 = performance.now();
  try {
    const v = enrich(await state.vesc.getValues());
    v.t = Date.now();
    showValues(v);
    rt.history.push(v);
    if (rt.history.length > rt.maxPoints) rt.history.shift();
    if (rt.recording) rt.recording.push(v);
    drawChart();
  } catch (e) {
    console.warn(e);
  }
  const rate = Number($('#rtRate').value);
  rt.timer = setTimeout(rtLoop, Math.max(0, rate - (performance.now() - t0)));
}

function startRealtime() {
  if (!requireConn()) return;
  rt.running = true;
  $('#btnRtStream').textContent = 'Arrêter';
  rtLoop();
}

function stopRealtime() {
  rt.running = false;
  clearTimeout(rt.timer);
  $('#btnRtStream').textContent = 'Démarrer';
}

$('#btnRtStream').onclick = () => (rt.running ? stopRealtime() : startRealtime());
$('#btnRtClear').onclick = () => { rt.history = []; drawChart(); };
$('#btnRtRecord').onclick = () => {
  const b = $('#btnRtRecord');
  if (!rt.recording) {
    rt.recording = [];
    b.textContent = 'Arrêter et télécharger';
    if (!rt.running) startRealtime();
    return;
  }
  const rows = rt.recording;
  rt.recording = null;
  b.textContent = 'Enregistrer CSV';
  if (!rows.length) return;
  const cols = ['t', 'v_in', 'current_motor', 'current_in', 'id', 'iq', 'power', 'duty_now', 'rpm',
    'temp_mos', 'temp_motor', 'amp_hours', 'amp_hours_charged', 'watt_hours', 'watt_hours_charged',
    'tachometer', 'tachometer_abs', 'fault_code'];
  const csv = [cols.join(';')].concat(rows.map((r) => cols.map((c) => r[c]).join(';'))).join('\n');
  download('vesc_log_' + new Date().toISOString().replace(/[:.]/g, '-') + '.csv', csv, 'text/csv');
};

const canvas = $('#rtChart');
function resizeChart() {
  const panels = SERIES.filter((s) => s.on).length || 1;
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth || 600;
  const h = panels * 130;
  canvas.style.height = h + 'px';
  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(h * dpr);
  drawChart();
}
window.addEventListener('resize', resizeChart);

function drawChart() {
  if (state.page !== 'realtime') return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.width / dpr;
  const H = canvas.height / dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);
  const css = getComputedStyle(document.documentElement);
  const grid = css.getPropertyValue('--border').trim();
  const muted = css.getPropertyValue('--muted').trim();
  const active = SERIES.filter((s) => s.on);
  const ph = H / (active.length || 1);
  const data = rt.history;
  const left = 52;

  active.forEach((s, si) => {
    const top = si * ph + 18;
    const bottom = (si + 1) * ph - 14;
    let min = Infinity;
    let max = -Infinity;
    for (const d of data) for (const [k] of s.keys) { min = Math.min(min, d[k]); max = Math.max(max, d[k]); }
    if (!Number.isFinite(min)) { min = 0; max = 1; }
    if (max - min < 1e-6) { max += 1; min -= 1; }
    const pad = (max - min) * 0.1;
    min -= pad; max += pad;
    const y = (v) => bottom - ((v - min) / (max - min)) * (bottom - top);

    ctx.strokeStyle = grid;
    ctx.lineWidth = 1;
    ctx.font = '11px system-ui, sans-serif';
    ctx.fillStyle = muted;
    for (let i = 0; i <= 2; i++) {
      const v = min + ((max - min) * i) / 2;
      const yy = y(v);
      ctx.beginPath(); ctx.moveTo(left, yy); ctx.lineTo(W, yy); ctx.stroke();
      ctx.fillText(Math.abs(v) >= 1000 ? v.toFixed(0) : v.toFixed(1), 2, yy + 4);
    }

    let lx = left;
    s.keys.forEach(([k, label, unit], ki) => {
      const color = COLORS[ki % COLORS.length];
      ctx.fillStyle = color;
      const last = data.length ? data[data.length - 1][k] : NaN;
      const txt = label + ' ' + (Number.isFinite(last) ? last.toFixed(1) : '–') + (unit ? ' ' + unit : '');
      ctx.fillText(txt, lx, top - 5);
      lx += ctx.measureText(txt).width + 14;
      if (data.length < 2) return;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      data.forEach((d, i) => {
        const x = left + (i / (rt.maxPoints - 1)) * (W - left);
        if (i === 0) ctx.moveTo(x, y(d[k])); else ctx.lineTo(x, y(d[k]));
      });
      ctx.stroke();
    });
  });
}

// ---------------------------------------------------------------- détection FOC

const MOTORS = [
  // Nom, pertes max (W), openloop ERPM, sensorless ERPM (préréglages de l'assistant VESC Tool)
  ['Mini outrunner (~75 g)', 20, 1400, 4000],
  ['Petit outrunner (~200 g)', 50, 1400, 4000],
  ['Outrunner moyen (~750 g)', 120, 700, 4000],
  ['Gros outrunner (~2000 g)', 400, 700, 4000],
  ['Petit inrunner (~200 g)', 50, 1400, 4000],
  ['Inrunner moyen (~750 g)', 140, 1400, 4000],
  ['Gros inrunner (~2000 g)', 400, 1000, 4000],
  ['Moteur moyeu vélo DD (~6 kg)', 150, 300, 2000],
  ['Inrunner EDF petit (~200 g)', 110, 1400, 4000],
];

const wizMotor = $('#wizMotor');
MOTORS.forEach(([n], i) => wizMotor.append(new Option(n, String(i))));
wizMotor.value = '2';
function applyMotorPreset() {
  const m = MOTORS[Number(wizMotor.value)];
  $('#wizLoss').value = m[1];
  $('#wizOl').value = m[2];
  $('#wizSl').value = m[3];
}
wizMotor.onchange = applyMotorPreset;
applyMotorPreset();

const DETECT_ERRORS = {
  '-1': 'Défaut persistant, regarde la page Temps réel',
  '-10': 'La détection du flux magnétique a échoué',
  '-50': 'Délai dépassé pour la détection CAN',
  '-51': 'La détection CAN a échoué',
  '-100': 'Pas de défaut, la détection a échoué pour une raison inconnue',
};

$('#btnDetect').onclick = async () => {
  if (!requireConn()) return;
  if (!confirm('Le moteur va tourner. Hélice / roue retirée ou planche bloquée ?')) return;
  const out = $('#wizResult');
  out.hidden = false;
  out.textContent = 'Détection en cours… (jusqu\'à 3 minutes)';
  const btn = $('#btnDetect');
  btn.disabled = true;
  const v = state.vesc;
  try {
    // Comme VESC Tool : désactive la sortie des apps (télécommande) pendant la détection.
    await v.send(new Writer().uint8(COMM.APP_DISABLE_OUTPUT).int8(1).int32(180000).toBytes());
    const res = await v.detectAllFoc({
      detectCan: $('#wizCan').checked,
      maxPowerLoss: Number($('#wizLoss').value),
      minCurrentIn: -Math.abs(Number($('#wizImin').value)),
      maxCurrentIn: Number($('#wizImax').value),
      openloopRpm: Number($('#wizOl').value),
      slErpm: Number($('#wizSl').value),
    });
    if (res >= 0) {
      await readConfig('mcconf', false, true);
      await readConfig('appconf', false, true);
      const mc = state.configs.mcconf;
      const app = state.configs.appconf;
      const sensors = mc.params.foc_sensor_mode?.e?.[mc.get('foc_sensor_mode')] ?? '?';
      out.textContent = 'Succès !\n\n'
        + 'ID VESC            : ' + (app?.get('controller_id') ?? '?') + '\n'
        + 'Courant moteur     : ' + fmt(mc.get('l_current_max')) + ' A\n'
        + 'R moteur           : ' + fmt(mc.get('foc_motor_r') * 1e3) + ' mΩ\n'
        + 'L moteur           : ' + fmt(mc.get('foc_motor_l') * 1e6) + ' µH\n'
        + (mc.has('foc_motor_ld_lq_diff') ? 'Lq-Ld              : ' + fmt(mc.get('foc_motor_ld_lq_diff') * 1e6) + ' µH\n' : '')
        + 'Flux magnétique    : ' + fmt(mc.get('foc_motor_flux_linkage') * 1e3) + ' mWb\n'
        + 'Compensation temp. : ' + (mc.get('foc_temp_comp') ? 'oui' : 'non') + '\n'
        + 'Capteurs           : ' + sensors;
    } else {
      const reason = DETECT_ERRORS[res] || (res <= -100 && res > -200 ? 'Défaut ' + (res + 100) + ' pendant la détection' : 'Erreur ' + res);
      out.textContent = 'Échec de la détection : ' + reason;
    }
  } catch (e) {
    out.textContent = 'Erreur : ' + e.message;
  } finally {
    btn.disabled = false;
  }
};

$('#btnDetectRL').onclick = async () => {
  if (!requireConn()) return;
  const out = $('#wizResult');
  out.hidden = false;
  out.textContent = 'Mesure de R et L…';
  try {
    const r = await state.vesc.detectRL();
    out.textContent = 'R : ' + fmt(r.r * 1e3, 3) + ' mΩ\nL : ' + fmt(r.l, 2) + ' µH\nLd-Lq : ' + fmt(r.ldLqDiff, 2) + ' µH';
  } catch (e) {
    out.textContent = 'Erreur : ' + e.message;
  }
};

// ---------------------------------------------------------------- contrôle moteur

const hold = { timer: null, ctl: null };

for (const ctl of $$('.ctl')) {
  const range = $('input', ctl);
  const out = $('output', ctl);
  range.oninput = () => { out.textContent = range.value; };
  const btn = $('.hold', ctl);
  const start = (e) => { e.preventDefault(); startHold(ctl); };
  btn.addEventListener('pointerdown', start);
  for (const ev of ['pointerup', 'pointerleave', 'pointercancel']) btn.addEventListener(ev, stopHold);
  btn.addEventListener('contextmenu', (e) => e.preventDefault());
}

function sendControl(ctl) {
  const v = state.vesc;
  if (!v) return;
  const val = Number($('input', ctl).value);
  switch (ctl.dataset.mode) {
    case 'duty': v.setDuty(val); break;
    case 'current': v.setCurrent(val); break;
    case 'brake': v.setCurrentBrake(val); break;
    case 'rpm': v.setRpm(val); break;
    case 'handbrake': v.setHandbrake(val); break;
    default: break;
  }
}

function startHold(ctl) {
  if (!requireConn()) return;
  stopHold();
  hold.ctl = ctl;
  $('.hold', ctl).classList.add('active');
  sendControl(ctl);
  hold.timer = setInterval(() => sendControl(ctl), 100);
}

function stopHold() {
  if (!hold.ctl) return;
  clearInterval(hold.timer);
  $('.hold', hold.ctl).classList.remove('active');
  hold.ctl = null;
  state.vesc?.setCurrent(0);
}

$('#btnStop').onclick = () => {
  stopHold();
  state.vesc?.setCurrent(0);
};

document.addEventListener('visibilitychange', () => {
  if (document.hidden) stopHold();
});

const ctlPoll = { timer: null };
function startControlPoll() {
  stopControlPoll();
  const loop = async () => {
    if (state.vesc) {
      try {
        const v = enrich(await state.vesc.getValues());
        setKv($('#ctlLive'), [
          ['ERPM', fmt(v.rpm, 0)],
          ['Courant moteur', fmt(v.current_motor) + ' A'],
          ['Courant batterie', fmt(v.current_in) + ' A'],
          ['Rapport cyclique', fmt(v.duty_now, 1) + ' %'],
          ['Tension', fmt(v.v_in, 1) + ' V'],
          ['Défaut', v.fault_str],
        ]);
      } catch (e) { /* délai dépassé : on réessaie */ }
    }
    ctlPoll.timer = setTimeout(loop, 250);
  };
  loop();
}
function stopControlPoll() {
  clearTimeout(ctlPoll.timer);
}

// ---------------------------------------------------------------- entrées

const inputs = { running: false, timer: null };
function stopInputs() {
  inputs.running = false;
  clearTimeout(inputs.timer);
  $('#btnInStream').textContent = 'Démarrer';
}
$('#btnInStream').onclick = () => {
  if (inputs.running) { stopInputs(); return; }
  if (!requireConn()) return;
  inputs.running = true;
  $('#btnInStream').textContent = 'Arrêter';
  const loop = async () => {
    if (!inputs.running || !state.vesc) return;
    const v = state.vesc;
    const [ppm, adc, imu] = await Promise.allSettled([v.getDecodedPpm(), v.getDecodedAdc(), v.getImuData()]);
    if (ppm.status === 'fulfilled') {
      setKv($('#inPpm'), [['Valeur', fmt(ppm.value.value * 100, 1) + ' %'], ['Impulsion', fmt(ppm.value.lastLen * 1000, 0) + ' µs']]);
    }
    if (adc.status === 'fulfilled') {
      const a = adc.value;
      setKv($('#inAdc'), [['ADC1', fmt(a.adc * 100, 1) + ' %'], ['Tension 1', fmt(a.voltage) + ' V'],
        ['ADC2', fmt(a.adc2 * 100, 1) + ' %'], ['Tension 2', fmt(a.voltage2) + ' V']]);
    }
    if (imu.status === 'fulfilled') {
      const m = imu.value;
      const deg = (r) => fmt(r * 180 / Math.PI, 1) + '°';
      setKv($('#inImu'), [['Roulis', deg(m.roll)], ['Tangage', deg(m.pitch)], ['Lacet', deg(m.yaw)],
        ['Accél.', [m.accX, m.accY, m.accZ].map((x) => fmt(x)).join(' / ') + ' g'],
        ['Gyro', [m.gyroX, m.gyroY, m.gyroZ].map((x) => fmt(x, 1)).join(' / ') + ' °/s']]);
    }
    inputs.timer = setTimeout(loop, 200);
  };
  loop();
};

// ---------------------------------------------------------------- terminal

const termOut = $('#termOut');
function termAppend(text) {
  termOut.textContent += text.endsWith('\n') ? text : text + '\n';
  termOut.scrollTop = termOut.scrollHeight;
}
function termSend(cmd) {
  if (!requireConn() || !cmd) return;
  termAppend('> ' + cmd);
  state.vesc.sendTerminal(cmd);
}
$('#termForm').onsubmit = (e) => {
  e.preventDefault();
  const input = $('#termIn');
  termSend(input.value.trim());
  input.value = '';
};
for (const b of $$('[data-cmd]')) b.onclick = () => termSend(b.dataset.cmd);
$('#btnTermClear').onclick = () => { termOut.textContent = ''; };

// ---------------------------------------------------------------- firmware

const fwState = { bytes: null, cancel: false };
$('#fwFile').onchange = async (e) => {
  const f = e.target.files[0];
  fwState.bytes = f ? new Uint8Array(await f.arrayBuffer()) : null;
  $('#btnFwUpload').disabled = !fwState.bytes;
  $('#fwStatus').textContent = f ? f.name + ' : ' + fwState.bytes.length + ' octets' : '';
};

$('#btnFwUpload').onclick = async () => {
  if (!requireConn() || !fwState.bytes) return;
  if (!confirm('Envoyer ce firmware au VESC (' + (state.fw?.hw || '?') + ') ? Ne coupe pas l\'alimentation pendant l\'envoi.')) return;
  stopRealtime();
  fwState.cancel = false;
  const bar = $('.progress');
  bar.hidden = false;
  $('#btnFwUpload').disabled = true;
  $('#btnFwCancel').hidden = false;
  const t0 = Date.now();
  try {
    await state.vesc.uploadFirmware(fwState.bytes, {
      allCan: $('#fwAllCan').checked,
      isCancelled: () => fwState.cancel,
      onProgress: (msg, p) => {
        bar.firstElementChild.style.width = (p * 100).toFixed(1) + '%';
        const el = (Date.now() - t0) / 1000;
        $('#fwStatus').textContent = msg + ' ' + (p * 100).toFixed(1) + ' %'
          + (p > 0.01 && p < 1 ? ' (reste ~' + Math.round(el / p - el) + ' s)' : '');
      },
    });
    $('#fwStatus').textContent = 'Firmware envoyé. Le VESC redémarre (environ 10 secondes) puis il faut se reconnecter.';
    toast('Firmware envoyé');
  } catch (e) {
    $('#fwStatus').textContent = 'Erreur : ' + e.message;
    toast(e.message, true);
  } finally {
    $('#btnFwUpload').disabled = false;
    $('#btnFwCancel').hidden = true;
  }
};
$('#btnFwCancel').onclick = () => { fwState.cancel = true; };

// Page par défaut selon l'ancre de l'URL (#realtime, #mcconf…)
const initial = location.hash.slice(1);
if (initial && $('#page-' + initial)) showPage(initial);
