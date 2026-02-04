from flask import Flask, jsonify, request, render_template_string
import requests
import urllib3
import time

# Desativa avisos de segurança (SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- O SITE (FRONTEND PROFISSIONAL) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>Web Monitor Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #0f766e; /* Azul Petróleo Profissional */
            --primary-hover: #115e59;
            --danger-color: #be123c; /* Vermelho Sóbrio */
            --danger-hover: #9f1239;
            --bg-color: #f1f5f9; /* Cinza azulado muito claro */
            --card-bg: #ffffff;
            --text-dark: #1e293b; /* Slate Gray Escuro */
            --text-muted: #64748b; /* Slate Gray Médio */
            --border-color: #e2e8f0;
            --success-color: #059669;
        }

        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color); 
            color: var(--text-dark);
            margin: 0;
            padding: 30px 15px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        /* ANIMAÇÃO DE ALERTA MAIS ELEGANTE (PULSO VERMELHO) */
        @keyframes pulseAlert {
            0% { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); border-color: transparent; }
            50% { box-shadow: 0 0 0 4px rgba(190, 18, 60, 0.3); border-color: var(--danger-color); }
            100% { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); border-color: transparent; }
        }
        .modo-alerta-card { 
            animation: pulseAlert 1.5s infinite; 
            border: 2px solid transparent; /* Espaço reservado para a borda */
        }

        .main-card { 
            background: var(--card-bg); 
            padding: 40px; 
            border-radius: 16px; 
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); /* Sombra suave moderna */
            width: 100%;
            max-width: 550px;
            box-sizing: border-box;
        }

        .header-area { text-align: center; margin-bottom: 35px; }
        h1 { color: var(--text-dark); font-size: 26px; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px; }
        .subtitle { color: var(--text-muted); font-size: 15px; }
        
        .form-group { margin-bottom: 20px; }
        label { font-weight: 500; font-size: 14px; color: var(--text-dark); display: block; margin-bottom: 8px; }
        
        input.form-control { 
            padding: 12px 15px; width: 100%; 
            border: 1px solid var(--border-color); 
            border-radius: 8px; font-size: 15px; 
            background-color: #f8fafc;
            transition: border-color 0.2s, box-shadow 0.2s;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }
        input.form-control:focus { 
            outline: none; 
            border-color: var(--primary-color); 
            box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.1); 
            background-color: #fff;
        }
        input:disabled { background-color: #e2e8f0; color: var(--text-muted); cursor: not-allowed; }
        
        .row { display: flex; gap: 15px; }
        .col { flex: 1; }

        .btn-main { 
            padding: 14px; border: none; border-radius: 8px; font-size: 16px; 
            cursor: pointer; font-weight: 600; width: 100%; transition: 0.2s; color: white;
            font-family: 'Inter', sans-serif;
            display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        #btnIniciar { background-color: var(--primary-color); box-shadow: 0 4px 6px -1px rgba(15, 118, 110, 0.2); }
        #btnIniciar:hover { background-color: var(--primary-hover); transform: translateY(-1px); }
        #btnIniciar:active { transform: translateY(0); }
        
        #btnParar { background-color: var(--danger-color); display: none; box-shadow: 0 4px 6px -1px rgba(190, 18, 60, 0.2); }
        #btnParar:hover { background-color: var(--danger-hover); }

        /* Painel de Resultados */
        #resultadoArea { 
            margin-top: 35px; display: none; 
            background-color: #f8fafc;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid var(--border-color);
            text-align: center;
        }
        .result-label { font-size: 14px; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
        #contador { 
            font-size: 72px; color: var(--text-dark); font-weight: 800; 
            line-height: 1; margin: 15px 0; 
            font-variant-numeric: tabular-nums; /* Números monoespaçados para não pular */
        }
        .status-container { 
            display: flex; flex-direction: column; gap: 5px; align-items: center;
            font-size: 14px; color: var(--text-muted); 
            padding-top: 15px; border-top: 1px solid var(--border-color);
        }
        .status-badge {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 13px;
        }
        .erro-detalhe { color: var(--danger-color); font-size: 12px; margin-top: 8px; background: #fee2e2; padding: 8px; border-radius: 6px; width: 100%; box-sizing: border-box; word-break: break-all;}
    </style>
</head>
<body>

    <div class="main-card" id="mainCardBox">
        <div class="header-area">
            <h1>Web Monitor Pro</h1>
            <div class="subtitle">Ferramenta de rastreamento de conteúdo em tempo real.</div>
        </div>
        
        <div class="form-group">
            <label for="urlInput">URL Alvo (Site)</label>
            <input type="text" id="urlInput" class="form-control" placeholder="https://exemplo.com/pagina-edital" value="https://funcern.br/concursos/ifpe-docente-2025/">
        </div>

        <div class="row">
            <div class="col form-group">
                <label for="palavraInput">Palavra-chave</label>
                <input type="text" id="palavraInput" class="form-control" placeholder="Ex: resultado" value="fevereiro">
            </div>
            <div class="col form-group">
                <label for="tempoInput">Intervalo (seg)</label>
                <input type="number" id="tempoInput" class="form-control" value="10" min="3">
            </div>
        </div>
        
        <div>
            <button id="btnIniciar" class="btn-main" onclick="iniciarMonitoramento()">
                <span>▶ Iniciar Monitoramento</span>
            </button>
            <button id="btnParar" class="btn-main" onclick="pararMonitoramento()">
                 <span>■ Parar Execução</span>
            </button>
        </div>

        <div id="resultadoArea">
            <div class="result-label">Ocorrências de "<span id="palavraMostrada">--</span>"</div>
            <div id="contador">--</div>
            
            <div class="status-container">
                 <div id="statusBadgeArea">
                    <span class="status-badge" style="background:#e2e8f0; color:var(--text-muted);">
                        💤 Aguardando início
                    </span>
                </div>
                <div>Última checagem: <span id="hora">--:--:--</span></div>
            </div>
            <div id="msgErro" class="erro-detalhe" style="display:none;"></div>
        </div>
    </div>

    <script>
        let intervaloID = null;
        const statusBadgeArea = document.getElementById('statusBadgeArea');

        function updateStatus(tipo, texto) {
            let bg, color, icon;
            if (tipo === 'loading') { bg = '#e0f2fe'; color = '#0284c7'; icon = '🔄'; }
            else if (tipo === 'success') { bg = '#dcfce7'; color = '#059669'; icon = '✅'; }
            else if (tipo === 'alert') { bg = '#fee2e2'; color = '#dc2626'; icon = '🚨'; }
            else if (tipo === 'error') { bg = '#fee2e2'; color = '#dc2626'; icon = '❌'; }
            else { bg = '#e2e8f0'; color = '#64748b'; icon = '💤'; }

            statusBadgeArea.innerHTML = `
                <span class="status-badge" style="background:${bg}; color:${color};">
                    ${icon} ${texto}
                </span>
            `;
        }

        function iniciarMonitoramento() {
            // 1. Configuração Inicial
            let url = document.getElementById('urlInput').value.trim();
            let palavra = document.getElementById('palavraInput').value.trim();
            let tempoSegundos = parseInt(document.getElementById('tempoInput').value);

            // 2. Validações
            if (!url) { document.getElementById('urlInput').focus(); return alert("Por favor, informe a URL."); }
            if (!palavra) { document.getElementById('palavraInput').focus(); return alert("Informe a palavra-chave."); }
            if (!url.startsWith('http')) { url = 'https://' + url; document.getElementById('urlInput').value = url; }
            if (isNaN(tempoSegundos) || tempoSegundos < 3) { tempoSegundos = 3; document.getElementById('tempoInput').value = 3;}

            // 3. Trava Interface
            document.getElementById('btnIniciar').style.display = 'none';
            document.getElementById('btnParar').style.display = 'flex';
            document.getElementById('resultadoArea').style.display = 'block';
            document.getElementById('palavraMostrada').innerText = palavra;
            
            ['urlInput', 'palavraInput', 'tempoInput'].forEach(id => document.getElementById(id).disabled = true);
            document.getElementById('msgErro').style.display = 'none';

            // 4. Função Principal
            const buscarDados = async () => {
                updateStatus('loading', 'Verificando site...');
                
                try {
                    const resposta = await fetch(`/api/contar?url=${encodeURIComponent(url)}&palavra=${encodeURIComponent(palavra)}`);
                    const dados = await resposta.json();

                    if (dados.erro) {
                        updateStatus('error', 'Falha na conexão');
                        document.getElementById('msgErro').innerText = dados.detalhe || dados.erro;
                        document.getElementById('msgErro').style.display = 'block';
                    } else {
                        document.getElementById('msgErro').style.display = 'none';
                        const contadorElem = document.getElementById('contador');
                        const valorAntigo = parseInt(contadorElem.innerText);
                        const valorNovo = dados.quantidade;
                        
                        // LÓGICA DE ALERTA
                        if (!isNaN(valorAntigo) && valorNovo > valorAntigo) {
                             updateStatus('alert', 'MUDANÇA DETECTADA! O valor aumentou.');
                             // Adiciona a classe que faz o card pulsar em vermelho
                             document.getElementById('mainCardBox').classList.add('modo-alerta-card');
                             alert(`ALERTA WEB MONITOR PRO\n\nA palavra '${palavra}' aumentou para: ${valorNovo}`);
                        } 
                        else if (isNaN(valorAntigo)) {
                             updateStatus('success', 'Monitoramento ativo e estável.');
                        }
                        else {
                             updateStatus('success', 'Sem alterações recentes.');
                             // Remove o alerta se voltar ao normal (opcional, dependendo da lógica desejada)
                             // document.getElementById('mainCardBox').classList.remove('modo-alerta-card');
                        }

                        contadorElem.innerText = valorNovo;
                        document.getElementById('hora').innerText = new Date().toLocaleTimeString();
                    }
                    
                } catch (e) {
                    updateStatus('error', 'Erro de rede ou servidor offline');
                    document.getElementById('msgErro').innerText = e.message;
                    document.getElementById('msgErro').style.display = 'block';
                }
            };

            buscarDados();
            intervaloID = setInterval(buscarDados, tempoSegundos * 1000); 
        }

        function pararMonitoramento() {
            clearInterval(intervaloID);
            
            // Remove o alerta visual se estiver ativo
            document.getElementById('mainCardBox').classList.remove('modo-alerta-card');
            
            document.getElementById('btnIniciar').style.display = 'flex';
            document.getElementById('btnParar').style.display = 'none';
            updateStatus('default', 'Monitoramento parado pelo usuário.');
            
            ['urlInput', 'palavraInput', 'tempoInput'].forEach(id => document.getElementById(id).disabled = false);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# --- BACKEND (API) ---
@app.route('/api/contar')
def contar_palavra():
    url = request.args.get('url')
    palavra = request.args.get('palavra')

    if not url or not palavra:
        return jsonify({"erro": "Parâmetros faltando"}), 400

    try:
        # Simula um navegador moderno para evitar bloqueios simples
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }

        # Timeout um pouco maior para sites lentos
        resposta = requests.get(url, headers=headers, timeout=20, verify=False)
        
        if resposta.status_code != 200:
            # Retorna um erro formatado se o site alvo der problema
            return jsonify({
                "erro": "Site alvo retornou erro", 
                "detalhe": f"Código HTTP: {resposta.status_code}. O site pode estar fora do ar ou bloqueando acessos."
            }), 502

        conteudo = resposta.text.lower()
        quantidade = conteudo.count(palavra.lower())
        
        return jsonify({ "quantidade": quantidade })

    except requests.exceptions.Timeout:
        return jsonify({"erro": "Timeout", "detalhe": "O site demorou muito para responder (mais de 20s)."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"erro": "Erro de Conexão", "detalhe": "Não foi possível conectar ao servidor. Verifique a URL."}), 502
    except Exception as e:
        return jsonify({"erro": "Erro Interno", "detalhe": str(e)}), 500

if __name__ == '__main__':
    # O host '0.0.0.0' é importante para rodar em alguns servidores, no seu PC local não faz diferença.
    app.run(debug=True, host='0.0.0.0')
