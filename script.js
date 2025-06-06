const startRecordButton = document.getElementById('start-record-button');
const stopRecordButton = document.getElementById('stop-record-button');
const recordingStatus = document.getElementById('recording-status');
const aiResponse = document.getElementById('ai-response');
const storyText = document.getElementById('story-text');
const errorMessage = document.getElementById('error-message');

const API_URL = 'http://127.0.0.1:8000/ask_ai_audio';

let mediaRecorder;
let audioChunks = [];
let audioBlob;

const CURRENT_RIDDLE = "Sou leve como uma pena, mas nem o homem mais forte consegue me segurar por muito tempo. O que sou eu?";
const CURRENT_RIDDLE_ANSWER = "Respiração";

let currentStorySnippet = `Você se encontra em uma mansão antiga e escura. Há um sussurro no ar. A charada que você precisa resolver é: "${CURRENT_RIDDLE}". O que você quer perguntar à entidade?`;

document.addEventListener('DOMContentLoaded', () => {
    storyText.textContent = currentStorySnippet;
});

startRecordButton.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendAudioToAPI(audioBlob);
        };

        mediaRecorder.start();
        updateButtonStates(true, false);
        recordingStatus.textContent = 'Gravando... Fale sua pergunta.';
        aiResponse.textContent = '';
        errorMessage.textContent = '';
    } catch (err) {
        console.error('Erro ao acessar o microfone:', err);
        errorMessage.textContent = 'Não foi possível acessar o microfone. Verifique as permissões.';
        recordingStatus.textContent = 'Erro ao gravar.';
        updateButtonStates(false, false);
    }
});

stopRecordButton.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        updateButtonStates(true, false);
        recordingStatus.textContent = 'Processando sua pergunta...';
    }
});

function updateButtonStates(isRecordingActive, isProcessingActive) {
    startRecordButton.disabled = isRecordingActive || isProcessingActive;
    stopRecordButton.disabled = !isRecordingActive || isProcessingActive;
}

async function sendAudioToAPI(blob) {
    aiResponse.textContent = "A entidade está ouvindo e ponderando sua pergunta...";
    errorMessage.textContent = "";

    const formData = new FormData();
    formData.append('audio_file', blob, 'recording.webm');
    formData.append('riddle', CURRENT_RIDDLE);
    formData.append('riddle_answer', CURRENT_RIDDLE_ANSWER);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Erro na API: ${response.status} ${response.statusText} - ${errorData.detail || 'Detalhe desconhecido'}`);
        }

        const data = await response.json();
        aiResponse.textContent = `A Entidade responde: ${data.response || '... silêncio inquietante ...'}`;
    } catch (err) {
        console.error('Erro ao enviar áudio:', err);
        errorMessage.textContent = 'Houve um problema ao processar sua pergunta.';
        aiResponse.textContent = '';
    } finally {
        updateButtonStates(false, false);
        recordingStatus.textContent = 'Pronto para gravar.';
    }
}


// Essa é a parte do efeito das particulas:

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('particle-canvas');
  const ctx = canvas.getContext('2d');

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = [];
  const numParticles = 150;
  const maxDistance = 100;

  let mouse = { x: null, y: null };

  for (let i = 0; i < numParticles; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 1.5 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random()
    });
  }

  function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let p of particles) {
      // distância do mouse à partícula
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      // altera a opacidade se o mouse estiver próximo
      if (distance < maxDistance) {
        p.opacity -= 0.02;
      } else {
        p.opacity += 0.005;
      }

      // manter a opacidade entre 0 e 1
      p.opacity = Math.max(0, Math.min(1, p.opacity));

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      // Alternância entre roxo e azul claro
      const colors = ['rgba(255,250,255,OP)', 'rgba(255,255,250,OP)', 'rgba(255,255,255,OP)'];
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)].replace('OP', p.opacity);

      ctx.fill();

      p.x += p.speedX;
      p.y += p.speedY;

      // rebote nas bordas
      if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
      if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
    }

    requestAnimationFrame(drawParticles);
  }

  drawParticles();

  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = null;
    mouse.y = null;
  });
});
