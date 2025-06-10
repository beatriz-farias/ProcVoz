// --- Constantes e Seleção de Elementos ---
const introScreen = document.getElementById('intro-screen');
const mainGame = document.getElementById('main-game');
const startGameButton = document.getElementById('start-game-button');

const startAskButton = document.getElementById('start-ask-button');
const startAnswerButton = document.getElementById('start-answer-button');
const stopRecordButton = document.getElementById('stop-record-button');

const recordingStatus = document.getElementById('recording-status');
const aiResponse = document.getElementById('ai-response');
const storyText = document.getElementById('story-text');
const errorMessage = document.getElementById('error-message');

const API_BASE_URL = 'https://backend-darkmysteria.onrender.com'; // Base URL para sua API
const ASK_API_URL = `${API_BASE_URL}/ask_ai_audio`;
const INITIAL_RIDDLE_URL = `${API_BASE_URL}/get_initial_riddle`;

// Variáveis de Gravação e Estado do Jogo
let mediaRecorder;
let audioChunks = [];
let audioBlob;
let currentRiddleId = null; // Armazena o ID da charada atual
let activeIntent = null; // Armazena a intenção do jogador ('ask_question' ou 'say_answer')

// --- Lógica do Canvas de Partículas ---
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');

    // Funções para redimensionar o canvas
    const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };

    // Inicializa o canvas e redimensiona
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas); // Responde a redimensionamentos da janela

    const particles = [];
    const numParticles = 120;
    const maxDistance = 100;

    let mouse = { x: null, y: null };

    // Cria as partículas
    for (let i = 0; i < numParticles; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 12 + 10,
            speedX: (Math.random() - 0.5) * 0.6,
            speedY: (Math.random() - 0.5) * 0.6,
            opacity: Math.random() * 0.6 + 0.4,
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 0.5
        });
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let p of particles) {
            const dx = p.x - mouse.x;
            const dy = p.y - mouse.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < maxDistance) {
                p.opacity -= 0.02;
            } else {
                p.opacity += 0.01;
            }
            p.opacity = Math.max(0.1, Math.min(1, p.opacity));

            p.x += p.speedX;
            p.y += p.speedY;
            p.rotation += p.rotationSpeed;

            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;

            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate((p.rotation * Math.PI) / 180);
            ctx.font = `${p.size}px Arial`;
            ctx.fillStyle = `rgba(217,216,217, ${p.opacity.toFixed(2)})`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('.', 0, 0);
            ctx.restore();
        }

        requestAnimationFrame(drawParticles);
    }

    drawParticles(); // Inicia a animação

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseout', () => {
        mouse.x = null;
        mouse.y = null;
    });
});
// --- Fim da Lógica do Canvas de Partículas ---


// --- Inicialização do Jogo ---
// Este evento é disparado pelo clique no botão "Vamos lá" na tela de introdução
startGameButton.addEventListener('click', async () => {
    introScreen.style.display = "none"; // Esconde a tela de intro
    mainGame.style.display = "block";   // Mostra a tela principal do jogo
    
    console.log("DEBUG FRONTEND: Botão 'Vamos lá' clicado. Carregando charada inicial...");
    storyText.textContent = "Carregando charada..."; // Exibe mensagem de carregamento
    updateButtonStates(false, true, false); // Desabilita botões enquanto carrega (isProcessing=true)

    try {
        const response = await fetch(INITIAL_RIDDLE_URL);
        if (!response.ok) {
            throw new Error(`Erro ao carregar charada inicial: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        currentRiddleId = data.riddle_id;
        storyText.textContent = `Você se encontra em uma mansão antiga e escura. Há um sussurro no ar. A charada é: "${data.riddle_text}". O que você quer perguntar à entidade?`;
        console.log("DEBUG FRONTEND: Charada inicial carregada. ID:", currentRiddleId);
        updateButtonStates(false, false, false); // Habilita botões de iniciar após carregar
    } catch (error) {
        console.error("DEBUG FRONTEND: Erro fatal ao carregar charada inicial:", error);
        errorMessage.textContent = `Erro ao iniciar o jogo: ${error.message}.`;
        storyText.textContent = "Erro ao carregar o jogo.";
        updateButtonStates(false, false, true); // Desabilita tudo em caso de erro fatal
    }
});


// --- Event Listeners para Gravação (para Perguntar ou Responder) ---
startAskButton.addEventListener('click', () => startRecording('ask_question'));
startAnswerButton.addEventListener('click', () => startRecording('say_answer'));

async function startRecording(intent) {
    activeIntent = intent; // Define a intenção ativa
    console.log(`DEBUG FRONTEND: Botão '${intent === 'ask_question' ? 'Perguntar' : 'Responder'}' clicado. Intenção: ${activeIntent}`);
    
    // Limpa mensagens anteriores ao iniciar nova interação
    aiResponse.textContent = '';
    errorMessage.textContent = '';

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("DEBUG FRONTEND: Microfone acessado com sucesso.");

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = []; // Limpa chunks anteriores

        mediaRecorder.ondataavailable = event => {
            console.log("DEBUG FRONTEND: Dados de áudio disponíveis.");
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            console.log("DEBUG FRONTEND: Gravação parada. Executando mediaRecorder.onstop...");
            // Parar a stream do microfone para liberar o recurso
            stream.getTracks().forEach(track => track.stop()); 
            audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            console.log(`DEBUG FRONTEND: Blob de áudio criado (tamanho: ${audioBlob.size} bytes).`);
            sendAudioToAPI(audioBlob, activeIntent);
        };

        mediaRecorder.start();
        console.log("DEBUG FRONTEND: mediaRecorder.start() chamado. Gravação ativa.");
        updateButtonStates(true, false, false); // Desabilita botões de iniciar, habilita parar
        recordingStatus.textContent = `Gravando... Fale sua ${intent === 'ask_question' ? 'pergunta.' : 'resposta.'}`;
        
    } catch (err) {
        console.error('DEBUG FRONTEND: Erro ao acessar o microfone:', err);
        errorMessage.textContent = 'Não foi possível acessar o microfone. Por favor, verifique as permissões.';
        recordingStatus.textContent = 'Erro ao gravar.';
        updateButtonStates(false, false, false); // Habilita botões de iniciar
    }
}

// Botão para parar a gravação (agora é genérico para pergunta ou resposta)
stopRecordButton.addEventListener('click', () => {
    console.log("DEBUG FRONTEND: Botão 'Parar Gravação' clicado.");
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        console.log("DEBUG FRONTEND: mediaRecorder.stop() chamado.");
        updateButtonStates(false, true, false); // Desabilita todos enquanto processa
        recordingStatus.textContent = 'Processando sua solicitação...';
    } else {
        console.log("DEBUG FRONTEND: mediaRecorder não estava gravando. Estado atual:", mediaRecorder ? mediaRecorder.state : "undefined");
    }
});

// --- Função para Gerenciar Estados dos Botões ---
// isRecording: true se estiver gravando (apenas o botão 'Parar' ativo)
// isProcessing: true se estiver processando requisição API (todos os botões desabilitados)
// isDisabledAll: true se for um erro fatal ou fim de jogo (todos os botões desabilitados)
function updateButtonStates(isRecording, isProcessing, isDisabledAll = false) {
    console.log(`DEBUG FRONTEND: updateButtonStates chamado. Gravando: ${isRecording}, Processando: ${isProcessing}, Desabilitar Tudo: ${isDisabledAll}`);
    
    // Botões de Iniciar (Perguntar / Responder)
    startAskButton.disabled = isRecording || isProcessing || isDisabledAll;
    startAnswerButton.disabled = isRecording || isProcessing || isDisabledAll;
    
    // Botão de Parar Gravação
    stopRecordButton.disabled = !isRecording || isProcessing || isDisabledAll;
    
    console.log(`DEBUG FRONTEND: Botões atualizados. Perguntar.disabled=${startAskButton.disabled}, Responder.disabled=${startAnswerButton.disabled}, Parar.disabled=${stopRecordButton.disabled}`);
}

// --- Função Chave: sendAudioToAPI (Envio, Recebimento e Exibição) ---
async function sendAudioToAPI(blob, intent) {
    console.log(`DEBUG FRONTEND: sendAudioToAPI iniciado. Intenção: ${intent}, Charada ID: ${currentRiddleId}`);
    aiResponse.textContent = "A entidade está ouvindo e ponderando sua solicitação...";
    errorMessage.textContent = "";

    const formData = new FormData();
    formData.append('audio_file', blob, 'recording.webm');
    formData.append('current_riddle_id', currentRiddleId); // Envia o ID da charada atual
    formData.append('player_intent', intent); // Envia a intenção do jogador

    console.log("DEBUG FRONTEND: FormData preparado.");

    try {
        console.log(`DEBUG FRONTEND: Enviando requisição para ${ASK_API_URL}...`);
        const response = await fetch(ASK_API_URL, {
            method: 'POST',
            body: formData
        });
        console.log(`DEBUG FRONTEND: Requisição Fetch completa. Status: ${response.status}`);
        console.log(`DEBUG FRONTEND: Resposta OK: ${response.ok}`);

        // Lê o corpo da resposta como JSON APENAS UMA VEZ.
        const data = await response.json(); 
        console.log("DEBUG FRONTEND: Dados da API recebidos e parseados (JSON).", data);

        // --- Lógica para Atualizar a UI com base na resposta da API ---
        let newStorySnippet = '';
        let entitySaysText = '';

        if (data.status === "error") {
            entitySaysText = data.message;
            newStorySnippet = `A entidade parece confusa. Tente novamente: ${data.message}.`;
        } else if (data.type === "question_response") {
            entitySaysText = data.message; // Sim, Não, Irrelevante
            newStorySnippet = `A entidade responde: "${data.message}". O que mais você quer perguntar sobre a charada?`;
            currentRiddleId = data.current_riddle_id; // Garante que o ID não mudou
        } else if (data.type === "answer_evaluation") {
            if (data.correct) {
                entitySaysText = data.message; // Parabéns!
                if (data.next_riddle_text) {
                    newStorySnippet = `${data.message} A próxima charada é: "${data.next_riddle_text}". O que você quer perguntar sobre ela?`;
                    currentRiddleId = data.current_riddle_id; // Atualiza para o ID da próxima charada
                } else {
                    newStorySnippet = `${data.message} O jogo foi concluído!`;
                    currentRiddleId = data.current_riddle_id; // Mantém o ID da última charada
                }
            } else {
                entitySaysText = data.message; // Resposta incorreta
                // Pega o texto da charada atual diretamente do elemento storyText antes de ser atualizado
                // Isso evita ter que passar riddle_text do backend para cada resposta incorreta.
                newStorySnippet = `${data.message} A charada ainda é: "${data.current_riddle_text}". Tente novamente.`;
                currentRiddleId = data.current_riddle_id;
            }
        } else if (data.type === "game_complete") {
            entitySaysText = data.message;
            newStorySnippet = `${data.message} O jogo foi concluído! Para jogar novamente, recarregue a página.`;
            currentRiddleId = data.current_riddle_id;
            updateButtonStates(false, false, true); // Desabilita tudo ao fim do jogo
        } else {
            console.warn("DEBUG FRONTEND: Tipo de resposta desconhecido:", data.type);
            entitySaysText = "A entidade parece não saber como responder a isso.";
            newStorySnippet = "A entidade permanece em silêncio. Tente novamente.";
        }

        console.log(`DEBUG FRONTEND: entitySaysText para exibição: '${entitySaysText}'`);
        aiResponse.textContent = `A Entidade diz: ${entitySaysText}`;
        console.log(`DEBUG FRONTEND: aiResponse.textContent atualizado.`);
        
        console.log(`DEBUG FRONTEND: newStorySnippet para exibição: '${newStorySnippet}'`);
        // storyText.textContent = newStorySnippet;
        console.log(`DEBUG FRONTEND: storyText.textContent atualizado.`);


        if (data.audio && data.audio.length > 0) { // Verifique se há dados de áudio
            console.log("DEBUG FRONTEND: Dados de áudio Base64 recebidos. Tentando reproduzir...");
            const audioBase64 = data.audio;
            const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
            audio.play().then(() => {
                console.log("DEBUG FRONTEND: Áudio reproduzido com sucesso.");
            }).catch(e => {
                console.error("DEBUG FRONTEND: Erro ao tentar tocar áudio:", e);
                errorMessage.textContent = "Erro ao tocar áudio da entidade. Verifique o console.";
            });
        } else {
            console.log("DEBUG FRONTEND: Nenhum dado de áudio recebido ou áudio vazio.");
            if (data.status === "success" && data.type !== "error") {
                 errorMessage.textContent = ""; // Limpa a mensagem de erro de áudio anterior
            }
        }

    } catch (error) {
        console.error("DEBUG FRONTEND: Erro ao chamar a API no catch:", error);
        errorMessage.textContent = `Erro ao contatar a Entidade: ${error.message}.`;
        aiResponse.textContent = ""; 
    } finally {
        console.log("DEBUG FRONTEND: sendAudioToAPI finally block.");
        updateButtonStates(false, false, false); // Habilita botões de iniciar
        recordingStatus.textContent = 'Pronto para gravar.';
    }
}