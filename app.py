from flask import Flask, jsonify, render_template_string
import requests
import urllib3

# Desativa avisos de segurança (SSL) para o site da Funcern
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# URL FIXA (Não precisa mais digitar)
URL_ALVO_FIXA = "https://funcern.br/concursos/ifpe-docente-2025/"

# --- O SITE (FRONTEND) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MONITOR IFPE - FUNCERN</title>
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; 
            text-align: center; 
            padding: 20px; 
            background-color: #f0f2f5; 
            transition: background-color 0.3s;
        }

        /* ANIMAÇÃO DE PISCAR (AMARELO E VERMELHO) */
        @keyframes piscarAlerta {
            0% { background-color: #ffeb3b; } /* Amarelo */
            100% { background-color: #ff0000; } /* Vermelho */
        }

        .modo-alerta {
            animation: piscarAlerta 0.5s infinite alternate;
        }

        .modo-alerta h1, .modo-alerta p, .modo-alerta div {
            color: black !important; /* Garante leitura no fundo vermelho */
        }

        .card { 
            background: white; 
            padding: 40px; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
            max-width: 600px; 
            margin: auto; 
            border: 2px solid #ddd;
        }

        h1 { color: #1a73e8; font-size: 24px; margin-bottom: 10px; }
        .target-url { font-size: 12px; color: #777; margin-bottom: 20px; word-break: break-all; }
        
        button { 
            padding: 15px 40px; background-color: #1a73e8; color: white; border: none; 
            border-radius: 8px; font-size: 18px; cursor: pointer; font-weight: bold; 
            width: 100%; transition: 0.2s;
        }
        button:hover { background-color: #1557b0; }
        button:disabled { background-color: #ccc; cursor: default; }

        #resultadoArea { margin-top: 30px; display: none; }
        #contador { font-size: 80px; color: #333; font-weight: bold; line-height: 1; margin: 10px 0; }
        .status { font-size: 14px; color: #666; }
        .erro-detalhe { color: red; font-size: 11px; margin-top: 5px; }
    </style>
</head>
<body>

    <div class="card">
        <h1>MONITOR IFPE 2025</h1>
        <p>Procurando por: <b>"janeiro"</b></p>
        <div class="target-url">Alvo: https://funcern.br/concursos/ifpe-docente-2025/</div>
        
        <button id="btnIniciar" onclick="iniciarMonitoramento()">INICIAR RASTREAMENTO</button>

        <div id="resultadoArea">
            <div>Ocorrências encontradas:</div>
            <div id="contador">--</div>
            <div class="status">
                <span id="statusTexto" style="color:orange">Conectando...</span><br>
                Última checagem: <span id="hora">--:--:--</span>
            </div>
            <div id="msgErro" class="erro-detalhe"></div>
        </div>
    </div>

    <script>
        let intervaloID = null;

        function iniciarMonitoramento() {
            const btn = document.getElementById('btnIniciar');
            const msgErro = document.getElementById('msgErro');

            btn.innerText = "MONITORANDO EM TEMPO REAL...";
            btn.disabled = true; 
            document.getElementById('resultadoArea').style.display = 'block';

            const buscarDados = async () => {
                const statusTexto = document.getElementById('statusTexto');
                
                try {
                    // Chama a API interna
                    const resposta = await fetch(`/api/contar`);
                    const dados = await resposta.json();

                    if (dados.erro) {
                        statusTexto.innerText = "Falha ao acessar";
                        statusTexto.style.color = "red";
                        msgErro.innerText = dados.detalhe || dados.erro;
                    } else {
                        const contadorElem = document.getElementById('contador');
                        const valorAntigo = parseInt(contadorElem.innerText);
                        const valorNovo = dados.quantidade;
                        const horaAtual = new Date().toLocaleTimeString();

                        // LÓGICA DO ALERTA E PISCAR TELA
                        if (!isNaN(valorAntigo) && valorNovo > valorAntigo) {
                             statusTexto.innerText = "MUDANÇA DETECTADA! EDITAL ATUALIZADO!";
                             
                             // Ativa o modo pisca-pisca no corpo do site
                             document.body.classList.add('modo-alerta');
                             
                             // Toca um som de alerta do navegador (se permitido)
                             alert("ALERTA! A QUANTIDADE MUDOU PARA " + valorNovo);
                        } 
                        else if (isNaN(valorAntigo)) {
                             statusTexto.innerText = "Monitoramento ativo. Aguardando mudanças...";
                             statusTexto.style.color = "green";
                        }
                        else {
                             // Resetar texto se estiver normal
                             statusTexto.innerText = "Nenhuma alteração detectada.";
                             statusTexto.style.color = "#888";
                        }

                        contadorElem.innerText = valorNovo;
                        document.getElementById('hora').innerText = horaAtual;
                        msgErro.innerText = "";
                    }
                    
                } catch (e) {
                    statusTexto.innerText = "Erro de conexão";
                    msgErro.innerText = e.message;
                }
            };

            // Executa a primeira vez e agenda
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
    try:
        # Cabeçalhos para parecer um navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/'
        }

        # Conecta no site FIXO
        resposta = requests.get(URL_ALVO_FIXA, headers=headers, timeout=15, verify=False)
        
        if resposta.status_code != 200:
            return jsonify({"erro": f"Site respondeu com código {resposta.status_code}", "detalhe": f"Status HTTP: {resposta.status_code}"}), 502

        conteudo = resposta.text.lower()
        # Conta a palavra "janeiro"
        quantidade = conteudo.count("janeiro")
        
        return jsonify({ "quantidade": quantidade })

    except Exception as e:
        return jsonify({"erro": "Erro Interno", "detalhe": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
