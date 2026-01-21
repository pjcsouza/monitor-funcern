from flask import Flask, jsonify, request, render_template_string
import requests
import urllib3

# Desativa avisos de segurança por não verificar o certificado (necessário para sites gov/edu)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- O SITE (FRONTEND) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MONITOR IFPE 2025</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; background-color: #f0f2f5; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
        h1 { color: #1a73e8; font-size: 22px; margin-bottom: 5px; }
        .subtitle { color: #666; margin-bottom: 20px; font-size: 14px; }
        
        input { 
            padding: 12px; width: 90%; margin-bottom: 15px; border: 1px solid #ccc; 
            border-radius: 6px; font-size: 14px; 
        }
        
        button { 
            padding: 12px 30px; background-color: #1a73e8; color: white; border: none; 
            border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; width: 100%;
        }
        button:hover { background-color: #1557b0; }
        button:disabled { background-color: #ccc; }

        #resultadoArea { margin-top: 25px; padding-top: 20px; border-top: 1px solid #eee; display: none; }
        #contador { font-size: 50px; color: #333; font-weight: bold; line-height: 1; }
        .status { font-size: 12px; color: #888; margin-top: 10px; }
        .erro-detalhe { color: red; font-size: 11px; margin-top: 5px; word-break: break-all; }
    </style>
</head>
<body>

    <div class="card">
        <h1>MONITOR IFPE 2025 FUNCERN</h1>
        <div class="subtitle">Monitorando a palavra <b>"janeiro"</b></div>
        
        <input type="text" id="urlAlvo" placeholder="Cole o link (Ex: https://funcern.br/...)" value="">
        <button id="btnIniciar" onclick="iniciarMonitoramento()">INICIAR AGORA</button>

        <div id="resultadoArea">
            <div>Ocorrências encontradas:</div>
            <div id="contador">--</div>
            <div class="status">
                <span id="statusTexto" style="color:orange">Conectando...</span><br>
                Atualizado às: <span id="hora">--:--:--</span>
            </div>
            <div id="msgErro" class="erro-detalhe"></div>
        </div>
    </div>

    <script>
        let intervaloID = null;

        function iniciarMonitoramento() {
            let url = document.getElementById('urlAlvo').value.trim();
            const btn = document.getElementById('btnIniciar');
            const msgErro = document.getElementById('msgErro');

            if (!url) { alert("Cole o link primeiro!"); return; }
            
            if (!url.startsWith('http')) {
                url = 'https://' + url;
                document.getElementById('urlAlvo').value = url;
            }

            btn.innerText = "MONITORANDO...";
            btn.disabled = true; 
            document.getElementById('resultadoArea').style.display = 'block';
            msgErro.innerText = "";

            const buscarDados = async () => {
                const statusTexto = document.getElementById('statusTexto');
                statusTexto.innerText = "Checando...";
                statusTexto.style.color = "orange";

                try {
                    const resposta = await fetch(`/api/contar?url=${encodeURIComponent(url)}&palavra=janeiro`);
                    const dados = await resposta.json();

                    if (dados.erro) {
                        statusTexto.innerText = "Falha ao acessar";
                        statusTexto.style.color = "red";
                        msgErro.innerText = dados.detalhe || dados.erro;
                    } else {
                        const contadorElem = document.getElementById('contador');
                        const valorAntigo = parseInt(contadorElem.innerText);
                        const valorNovo = dados.quantidade;

                        if (!isNaN(valorAntigo) && valorNovo > valorAntigo) {
                             statusTexto.innerText = "AUMENTOU! NOVIDADE!";
                             statusTexto.style.color = "green";
                             alert("ATENÇÃO: A palavra 'janeiro' apareceu mais vezes!");
                        } else if (!isNaN(valorAntigo) && valorNovo !== valorAntigo) {
                             statusTexto.innerText = "Mudou a quantidade";
                        } else {
                             statusTexto.innerText = "Sem alterações";
                             statusTexto.style.color = "#888";
                        }

                        contadorElem.innerText = valorNovo;
                        document.getElementById('hora').innerText = new Date().toLocaleTimeString();
                        msgErro.innerText = "";
                    }
                    
                } catch (e) {
                    statusTexto.innerText = "Erro de conexão";
                    msgErro.innerText = e.message;
                }
            };

            buscarDados();
            intervaloID = setInterval(buscarDados, 5000); // 5 segundos
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

# --- BACKEND ---
@app.route('/api/contar')
def contar_palavra():
    url = request.args.get('url')
    palavra = request.args.get('palavra', 'janeiro')

    if not url: return jsonify({"erro": "URL vazia"}), 400

    try:
        # Cabeçalhos para parecer um navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/'
        }

        # verify=False ignora erros de certificado SSL
        resposta = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if resposta.status_code != 200:
            return jsonify({"erro": f"Site respondeu com código {resposta.status_code}", "detalhe": f"Status HTTP: {resposta.status_code}"}), 502

        conteudo = resposta.text.lower()
        quantidade = conteudo.count(palavra.lower())
        
        return jsonify({ "quantidade": quantidade })

    except Exception as e:
        return jsonify({"erro": "Erro Interno", "detalhe": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
