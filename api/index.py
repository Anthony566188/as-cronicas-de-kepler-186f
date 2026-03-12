import os
import oracledb
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "kepler-fallback-key")

def get_connection():
    """Retorna uma conexão Oracle usando variáveis de ambiente."""
    return oracledb.connect(
        user=os.environ["ORACLE_USER"],
        password=os.environ["ORACLE_PASSWORD"],
        dsn=os.environ["ORACLE_DSN"],
    )

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>As Crônicas de Kepler-186f</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Exo+2:ital,wght@0,300;0,400;0,600;1,300&display=swap" rel="stylesheet"/>
<style>
  :root {
    --void: #03080f; --deep: #070f1c; --panel: #0b1929; --panel2: #0e1f30;
    --border: #112840; --border2: #1a3a5c; --cyan: #00d4ff; --cyan2: #00a8cc;
    --amber: #f5a623; --amber2: #c07a00; --red: #ff3b5c; --green: #00ffb0;
    --green2: #00cc8a; --purple: #b060ff; --text: #c0daf0; --text2: #7aa0bf; --text3: #3d6080;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--void); color: var(--text); font-family: 'Exo 2', sans-serif; min-height: 100vh; position: relative; overflow-x: hidden; }
  body::before { content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none; background: radial-gradient(1px 1px at 8% 12%, rgba(255,255,255,.55) 0,transparent 100%), radial-gradient(1px 1px at 22% 67%, rgba(255,255,255,.35) 0,transparent 100%), radial-gradient(1px 1px at 37% 28%, rgba(200,230,255,.50) 0,transparent 100%), radial-gradient(1px 1px at 51% 82%, rgba(255,255,255,.30) 0,transparent 100%), radial-gradient(1px 1px at 68% 18%, rgba(255,255,255,.48) 0,transparent 100%), radial-gradient(1px 1px at 80% 55%, rgba(200,230,255,.38) 0,transparent 100%), radial-gradient(1px 1px at 91% 78%, rgba(255,255,255,.28) 0,transparent 100%), radial-gradient(2px 2px at 14% 88%, rgba(0,212,255,.25) 0,transparent 100%), radial-gradient(2px 2px at 63% 42%, rgba(245,166,35,.18) 0,transparent 100%), radial-gradient(1px 1px at 45% 6%, rgba(255,255,255,.45) 0,transparent 100%), radial-gradient(1px 1px at 76% 93%, rgba(255,255,255,.35) 0,transparent 100%), radial-gradient(1px 1px at 29% 50%, rgba(200,230,255,.28) 0,transparent 100%); }
  .planet-glow { position: fixed; top: -160px; right: -160px; width: 480px; height: 480px; border-radius: 50%; background: radial-gradient(circle, rgba(0,168,204,.10) 0%, rgba(0,50,120,.06) 40%, transparent 70%); pointer-events: none; z-index: 0; animation: planet-breathe 8s ease-in-out infinite; }
  @keyframes planet-breathe { 0%,100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.06); opacity: .7; } }
  .scanlines { position: fixed; inset: 0; z-index: 999; pointer-events: none; background: repeating-linear-gradient(to bottom, transparent 0, transparent 2px, rgba(0,0,0,.025) 2px, rgba(0,0,0,.025) 4px); }
  .wrap { max-width: 960px; margin: 0 auto; padding: 0 28px; position: relative; z-index: 1; }
  header { padding: 24px 0 20px; border-bottom: 1px solid var(--border); position: relative; }
  header::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 260px; height: 1px; background: linear-gradient(to right, var(--cyan), transparent); box-shadow: 0 0 12px rgba(0,212,255,.5); }
  .header-inner { display: flex; align-items: center; gap: 18px; }
  .h-icon { width: 48px; height: 48px; border-radius: 50%; border: 1.5px solid var(--cyan); display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; box-shadow: 0 0 18px rgba(0,212,255,.4), inset 0 0 12px rgba(0,212,255,.08); animation: icon-pulse 4s ease-in-out infinite; }
  @keyframes icon-pulse { 0%,100% { box-shadow: 0 0 18px rgba(0,212,255,.4), inset 0 0 12px rgba(0,212,255,.08); } 50% { box-shadow: 0 0 32px rgba(0,212,255,.7), inset 0 0 18px rgba(0,212,255,.15); } }
  .h-titles h1 { font-family: 'Orbitron', monospace; font-size: clamp(1rem, 3vw, 1.4rem); font-weight: 900; color: var(--cyan); letter-spacing: .12em; text-shadow: 0 0 20px rgba(0,212,255,.5); }
  .h-titles p { font-family: 'Share Tech Mono', monospace; font-size: .62rem; color: var(--text3); letter-spacing: .22em; margin-top: 3px; }
  .h-right { margin-left: auto; font-family: 'Share Tech Mono', monospace; font-size: .65rem; color: var(--text3); text-align: right; line-height: 1.7; }
  .h-right .online { color: var(--green); display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
  .dot-live { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); animation: blink 2s step-end infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }
  .control-panel { margin-top: 28px; background: var(--panel); border: 1px solid var(--border); border-top: 2px solid var(--amber); padding: 20px 24px; position: relative; }
  .control-panel::before { content: '▸ PAINEL DE CONTROLE · GOVERNADOR DA COLÔNIA'; display: block; font-family: 'Share Tech Mono', monospace; font-size: .6rem; color: var(--amber); letter-spacing: .22em; margin-bottom: 16px; }
  .controls-row { display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap; }
  .ctrl-group { display: flex; flex-direction: column; gap: 5px; }
  .ctrl-group label { font-family: 'Share Tech Mono', monospace; font-size: .58rem; color: var(--text3); letter-spacing: .2em; text-transform: uppercase; }
  select, input[type="number"] { background: var(--deep); border: 1px solid var(--border2); color: var(--text); font-family: 'Share Tech Mono', monospace; font-size: .8rem; padding: 9px 12px; outline: none; transition: border-color .2s, box-shadow .2s; -webkit-appearance: none; appearance: none; border-radius: 0; }
  select { cursor: pointer; padding-right: 28px; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%233d6080'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 10px center; }
  input[type="number"] { width: 80px; }
  .btn-aplicar { background: transparent; border: 1px solid var(--cyan); color: var(--cyan); font-family: 'Orbitron', monospace; font-size: .68rem; font-weight: 700; letter-spacing: .15em; padding: 10px 22px; cursor: pointer; transition: all .2s; position: relative; overflow: hidden; white-space: nowrap; }
  .btn-aplicar::before { content: ''; position: absolute; inset: 0; background: var(--cyan); transform: translateX(-101%); transition: transform .25s ease; z-index: 0; }
  .btn-aplicar span { position: relative; z-index: 1; }
  .btn-aplicar:hover { color: var(--void); box-shadow: 0 0 20px rgba(0,212,255,.35); }
  .btn-aplicar:hover::before { transform: translateX(0); }
  .btn-aplicar:disabled { opacity: .4; cursor: not-allowed; }
  .btn-reload { background: transparent; border: 1px solid var(--border2); color: var(--text3); font-family: 'Share Tech Mono', monospace; font-size: .72rem; padding: 10px 14px; cursor: pointer; transition: all .2s; }
  .event-hint { margin-top: 12px; font-family: 'Share Tech Mono', monospace; font-size: .62rem; color: var(--text3); line-height: 1.6; min-height: 1.6em; }
  .status-bar { margin-top: 12px; display: flex; align-items: center; gap: 10px; font-family: 'Share Tech Mono', monospace; font-size: .65rem; min-height: 28px; }
  .status-bar .status-msg { color: var(--text2); }
  .status-bar.ok .status-msg { color: var(--green); }
  .status-bar.erro .status-msg { color: var(--red); }
  .section-label { font-family: 'Orbitron', monospace; font-size: .65rem; font-weight: 700; letter-spacing: .3em; color: var(--cyan2); text-transform: uppercase; display: flex; align-items: center; gap: 10px; margin-top: 32px; margin-bottom: 14px; }
  .section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, var(--border), transparent); }
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: .82rem; }
  thead th { font-family: 'Share Tech Mono', monospace; font-size: .6rem; letter-spacing: .2em; color: var(--text3); text-transform: uppercase; padding: 10px 14px; text-align: left; font-weight: 400; border-bottom: 1px solid var(--border2); }
  tbody tr { border-bottom: 1px solid var(--border); transition: background .2s; animation: row-in .35s ease both; }
  @keyframes row-in { from{opacity:0;transform:translateX(-8px)} to{opacity:1;transform:translateX(0)} }
  tbody td { padding: 13px 14px; vertical-align: middle; }
  .td-id { font-family: 'Share Tech Mono', monospace; font-size: .65rem; color: var(--text3); }
  .td-nome { font-weight: 600; color: #e0f0ff; }
  .td-setor span { font-family: 'Share Tech Mono', monospace; font-size: .6rem; letter-spacing: .12em; padding: 3px 9px; border-radius: 2px; }
  .setor-MINERAL { color: var(--cyan); border: 1px solid rgba(0,212,255,.3); background: rgba(0,212,255,.06); }
  .setor-COMBUSTIVEL { color: var(--amber); border: 1px solid rgba(245,166,35,.3); background: rgba(245,166,35,.06); }
  .setor-DADOS { color: var(--green); border: 1px solid rgba(0,255,176,.3); background: rgba(0,255,176,.06); }
  .td-preco { font-family: 'Share Tech Mono', monospace; font-size: .9rem; color: var(--cyan); font-weight: 700; }
  .table-empty { text-align: center; padding: 36px; font-family: 'Share Tech Mono', monospace; font-size: .72rem; color: var(--text3); letter-spacing: .2em; }
  footer { margin-top: 48px; padding: 20px 0; border-top: 1px solid var(--border); text-align: center; font-family: 'Share Tech Mono', monospace; font-size: .58rem; color: var(--text3); letter-spacing: .2em; }
</style>
</head>
<body>
<div class="planet-glow"></div>
<div class="scanlines"></div>
<div class="wrap">
  <header>
    <div class="header-inner">
      <div class="h-icon">⬡</div>
      <div class="h-titles">
        <h1>AS CRÔNICAS DE KEPLER-186f</h1>
        <p>APLICAÇÃO ARM · PYTHON + ORACLE · INTERGALACTIC TRADE CORP</p>
      </div>
      <div class="h-right">
        <div class="online"><span class="dot-live"></span>ORACLE DB ONLINE</div>
        <div>STARDATE 2142.071</div>
      </div>
    </div>
  </header>
  <div class="control-panel">
    <div class="controls-row">
      <div class="ctrl-group">
        <label>Evento de Flutuação</label>
        <select id="sel-evento" onchange="atualizarHint()">
          <option value="RADIACAO">RADIACAO</option>
          <option value="DESCOBERTA">DESCOBERTA</option>
        </select>
      </div>
      <div class="ctrl-group">
        <label>Filtrar Setor</label>
        <select id="sel-setor" onchange="carregarAtivos()">
          <option value="TODOS">TODOS</option>
          <option value="MINERAL">MINERAL</option>
          <option value="COMBUSTIVEL">COMBUSTIVEL</option>
          <option value="DADOS">DADOS</option>
        </select>
      </div>
      <div class="ctrl-group">
        <label>Repetições</label>
        <input type="number" id="inp-rep" value="1" min="1" max="50"/>
      </div>
      <button class="btn-aplicar" id="btn-aplicar" onclick="aplicarEvento()"><span>▶ APLICAR EVENTO</span></button>
      <button class="btn-reload" onclick="carregarAtivos()">↻</button>
    </div>
    <div class="event-hint" id="event-hint"></div>
    <div class="status-bar" id="status-bar"><span class="status-icon">◈</span><span class="status-msg">Sistema pronto.</span></div>
  </div>
  <div class="section-label">▸ ATIVOS GALÁCTICOS EM CIRCULAÇÃO</div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>ID</th><th>Nome</th><th>Setor</th><th>Preço (CR₹)</th><th>Estoque</th></tr></thead>
      <tbody id="tbody"><tr><td colspan="5" class="table-empty">SINCRONIZANDO COM NÚCLEO ORACLE...</td></tr></tbody>
    </table>
  </div>
</div>
<footer>INTERGALACTIC TRADE CORP · © 2142</footer>
<script>
  const HINTS = { RADIACAO: '☢ Radiação gama · DADOS ↑25% · MINERAL ↓10% · COMBUSTIVEL ↑5%', DESCOBERTA: '⛏ Nova jazida · MINERAL ↓50% · demais setores ↑10%' };
  let precosAnt = {};
  function atualizarHint() { const ev = document.getElementById('sel-evento').value; document.getElementById('event-hint').textContent = HINTS[ev] || ''; }
  function setStatus(msg, tipo) { const bar = document.getElementById('status-bar'); bar.className = 'status-bar ' + (tipo || ''); bar.querySelector('.status-msg').textContent = msg; }
  async function carregarAtivos() {
    const setor = document.getElementById('sel-setor').value;
    const url = setor === 'TODOS' ? '/ativos' : `/ativos?setor=${setor}`;
    try {
      const res = await fetch(url);
      const data = await res.json();
      if (data.status !== 'ok') throw new Error(data.mensagem);
      const tbody = document.getElementById('tbody');
      tbody.innerHTML = data.ativos.map(a => `<tr class="${precosAnt[a.id_ativo] < a.preco_base ? 'flash-up' : 'flash-down'}"><td class="td-id">${a.id_ativo}</td><td class="td-nome">${a.nome}</td><td class="td-setor"><span class="setor-${a.setor}">${a.setor}</span></td><td class="td-preco">${parseFloat(a.preco_base).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td><td class="td-estoque">${a.estoque}</td></tr>`).join('');
      data.ativos.forEach(a => precosAnt[a.id_ativo] = a.preco_base);
    } catch (e) { document.getElementById('tbody').innerHTML = `<tr><td colspan="5" class="table-empty">FALHA: ${e.message}</td></tr>`; }
  }
  async function aplicarEvento() {
    const evento = document.getElementById('sel-evento').value;
    const rep = document.getElementById('inp-rep').value;
    const btn = document.getElementById('btn-aplicar');
    btn.disabled = true;
    try {
      const res = await fetch('/processar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ evento, repeticoes: rep }) });
      const data = await res.json();
      setStatus(data.mensagem, 'ok');
      await carregarAtivos();
    } catch (e) { setStatus(e.message, 'erro'); } finally { btn.disabled = false; }
  }
  atualizarHint(); carregarAtivos();
</script>
</body>
</html>
"""

@app.route("/ativos")
def listar_ativos():
    setor = request.args.get("setor", "").upper().strip()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = "SELECT id_ativo, nome, setor, preco_base, estoque FROM TB_ATIVOS_GALACTICOS"
                if setor and setor != "TODOS":
                    cur.execute(query + " WHERE setor = :setor ORDER BY id_ativo", setor=setor)
                else:
                    cur.execute(query + " ORDER BY id_ativo")
                cols = [c[0].lower() for c in cur.description]
                ativos = [dict(zip(cols, row)) for row in cur.fetchall()]
        return jsonify({"status": "ok", "ativos": ativos})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/processar", methods=["POST"])
def processar_evento():
    dados = request.get_json(force=True)
    evento = dados.get("evento", "").upper().strip()
    repeticoes = max(1, min(int(dados.get("repeticoes", 1)), 50))
    if evento not in {"RADIACAO", "DESCOBERTA"}:
        return jsonify({"status": "erro", "mensagem": "Evento inválido."}), 400
    plsql = """
        DECLARE
            v_fator_ajuste NUMBER;
            v_evento VARCHAR2(20) := :evento;
        BEGIN
            FOR r_ativo IN (SELECT id_ativo, setor, preco_base FROM TB_ATIVOS_GALACTICOS) LOOP
                IF v_evento = 'RADIACAO' THEN
                    IF    r_ativo.setor = 'DADOS'   THEN v_fator_ajuste := 1.25;
                    ELSIF r_ativo.setor = 'MINERAL' THEN v_fator_ajuste := 0.90;
                    ELSE                                 v_fator_ajuste := 1.05;
                    END IF;
                ELSIF v_evento = 'DESCOBERTA' THEN
                    IF r_ativo.setor = 'MINERAL' THEN v_fator_ajuste := 0.50;
                    ELSE                              v_fator_ajuste := 1.10;
                    END IF;
                END IF;
                UPDATE TB_ATIVOS_GALACTICOS SET preco_base = preco_base * v_fator_ajuste WHERE id_ativo = r_ativo.id_ativo;
            END LOOP;
            COMMIT;
        END;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for _ in range(repeticoes):
                    cur.execute(plsql, evento=evento)
        msgs = {"RADIACAO": "Tempestade de radiação processada.", "DESCOBERTA": "Nova jazida registrada."}
        return jsonify({"status": "ok", "mensagem": msgs[evento]})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)