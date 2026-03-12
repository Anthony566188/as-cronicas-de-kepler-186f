import os
import oracledb
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="../templates")
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
    return render_template("index.html")

@app.route("/ativos")
def listar_ativos():
    setor = request.args.get("setor", "").upper().strip()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if setor and setor != "TODOS":
                    cur.execute(
                        "SELECT id_ativo, nome, setor, preco_base, estoque "
                        "FROM TB_ATIVOS_GALACTICOS WHERE setor = :setor ORDER BY id_ativo",
                        setor=setor,
                    )
                else:
                    cur.execute(
                        "SELECT id_ativo, nome, setor, preco_base, estoque "
                        "FROM TB_ATIVOS_GALACTICOS ORDER BY id_ativo"
                    )
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
                UPDATE TB_ATIVOS_GALACTICOS
                   SET preco_base = preco_base * v_fator_ajuste
                 WHERE id_ativo = r_ativo.id_ativo;
            END LOOP;
            COMMIT;
        END;
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for _ in range(repeticoes):
                    cur.execute(plsql, evento=evento)
        msgs = {
            "RADIACAO":   "Tempestade de radiação gama processada com sucesso.",
            "DESCOBERTA": "Nova jazida registrada. Preços atualizados pelo núcleo Oracle.",
        }
        return jsonify({"status": "ok", "evento": evento, "repeticoes": repeticoes, "mensagem": msgs[evento]})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000)
