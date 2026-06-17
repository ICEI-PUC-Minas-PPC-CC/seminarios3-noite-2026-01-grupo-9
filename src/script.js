const API_BASE = window.location.origin;


const SESSION_ID = crypto.randomUUID();


let paginaAtual = 1;
const POR_PAGINA = 10;

const btnGravar = document.getElementById('btn-gravar');
const statusDot  = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const textoEl    = document.getElementById('texto-reconhecido');
const btnLimpar  = document.getElementById('btn-limpar');


const historicoLista   = document.getElementById('historico-lista');
const historicoCount   = document.getElementById('historico-count');
const btnCarregarMais  = document.getElementById('btn-carregar-mais');


const statTotal     = document.getElementById('stat-total');
const statHoje      = document.getElementById('stat-hoje');
const statSessoes   = document.getElementById('stat-sessoes');
const statConfianca = document.getElementById('stat-confianca');


const PLACEHOLDER = '<span class="placeholder">O texto reconhecido pela voz aparecerá aqui...</span>';


let gravando = false;


let inicioGravacao = null;


const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;


if (!SpeechRecognition) {
  setStatus('error', 'Navegador sem suporte à API de voz');
  btnGravar.disabled = true;
  console.error('Web Speech API não suportada neste navegador. Use Chrome ou Edge.');
}


const reconhecedor = new SpeechRecognition();


reconhecedor.lang = 'pt-BR';


reconhecedor.continuous = false;


reconhecedor.interimResults = true;


function setStatus(state, msg) {
  statusDot.className = `dot dot--${state}`;
  statusText.textContent = msg;
}

function entrarModoGravacao() {
  gravando = true;
  inicioGravacao = Date.now();
  btnGravar.classList.add('recording');
  setStatus('active', 'Ouvindo...');
}


function sairModoGravacao() {
  gravando = false;
  btnGravar.classList.remove('recording');
  setStatus('idle', 'Aguardando...');
}


async function salvarTranscricao(texto, confianca) {
  if (!texto || texto.trim().length === 0) return;

  const duracao = inicioGravacao ? Date.now() - inicioGravacao : null;

  const payload = {
    texto: texto.trim(),
    idioma: reconhecedor.lang,
    duracao_ms: duracao,
    confianca: confianca,
    session_id: SESSION_ID,
  };

  try {
    const response = await fetch(`${API_BASE}/api/transcricoes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      console.error('Erro ao salvar transcrição:', response.status);
      return;
    }

    const data = await response.json();
    console.log('Transcrição salva:', data);

   
    adicionarAoHistorico(data);
    carregarEstatisticas();
  } catch (err) {
    console.error('Erro de rede ao salvar transcrição:', err);
  }
}

async function carregarHistorico(reset = false) {
  if (reset) {
    paginaAtual = 1;
    historicoLista.innerHTML = '';
  }

  try {
    const url = `${API_BASE}/api/transcricoes?pagina=${paginaAtual}&por_pagina=${POR_PAGINA}&session_id=${SESSION_ID}`;
    const response = await fetch(url);

    if (!response.ok) return;

    const data = await response.json();

    if (data.items.length === 0 && paginaAtual === 1) {
      historicoLista.innerHTML = '<p class="placeholder">Nenhuma transcrição ainda. Grave algo para começar!</p>';
      historicoCount.textContent = '0 transcrições';
      btnCarregarMais.style.display = 'none';
      return;
    }

    historicoCount.textContent = `${data.total} transcrição${data.total !== 1 ? 'ões' : ''}`;

    data.items.forEach(item => {
      
      if (!document.getElementById(`hist-${item.id}`)) {
        adicionarAoHistorico(item);
      }
    });

    
    btnCarregarMais.style.display = paginaAtual < data.total_paginas ? '' : 'none';
  } catch (err) {
    console.error('Erro ao carregar histórico:', err);
  }
}

function adicionarAoHistorico(item) {
 
  const placeholder = historicoLista.querySelector('.placeholder');
  if (placeholder) placeholder.remove();

  const el = document.createElement('div');
  el.className = 'historico-item';
  el.id = `hist-${item.id}`;

  const data = new Date(item.criado_em);
  const hora = data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

  const confiancaStr = item.confianca != null
    ? `${Math.round(item.confianca * 100)}%`
    : '—';

  el.innerHTML = `
    <div class="historico-item-header">
      <span class="historico-hora">${hora}</span>
      <span class="historico-confianca" title="Confiança do reconhecimento">${confiancaStr}</span>
    </div>
    <p class="historico-texto">${escapeHtml(item.texto)}</p>
  `;

  // Inserir no topo (mais recente primeiro)
  historicoLista.prepend(el);

  // Atualizar contador
  const total = historicoLista.querySelectorAll('.historico-item').length;
  historicoCount.textContent = `${total} transcrição${total !== 1 ? 'ões' : ''}`;
}

/**
 * Carrega estatísticas gerais do backend.
 */
async function carregarEstatisticas() {
  try {
    const response = await fetch(`${API_BASE}/api/estatisticas`);
    if (!response.ok) return;

    const data = await response.json();

    statTotal.textContent = data.total_transcricoes;
    statHoje.textContent = data.transcricoes_hoje;
    statSessoes.textContent = data.total_sessoes;
    statConfianca.textContent = data.media_confianca != null
      ? `${Math.round(data.media_confianca * 100)}%`
      : '—';
  } catch (err) {
    console.error('Erro ao carregar estatísticas:', err);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

reconhecedor.onresult = (event) => {
  let textoInterim = '';  // Texto ainda sendo processado
  let textoFinal   = '';  // Texto já confirmado pelo reconhecedor
  let confiancaFinal = null;

  // Itera sobre todos os resultados recebidos até agora
  for (let i = event.resultIndex; i < event.results.length; i++) {
    const transcricao = event.results[i][0].transcript;

    if (event.results[i].isFinal) {
      textoFinal += transcricao;   // Resultado confirmado
      confiancaFinal = event.results[i][0].confidence;
    } else {
      textoInterim += transcricao; // Resultado parcial
    }
  }

  // Monta o HTML exibido: final em cor normal, interim em cor mais suave
  const html =
    (textoFinal   ? `<span class="texto-final">${escapeHtml(textoFinal)}</span>` : '') +
    (textoInterim ? `<span class="texto-interim">${escapeHtml(textoInterim)}</span>` : '');

  // Só atualiza o DOM se houver algum conteúdo para mostrar
  if (html) {
    textoEl.innerHTML = html;
  }

  // Enviar texto final ao backend para persistência
  if (textoFinal) {
    salvarTranscricao(textoFinal, confiancaFinal);
  }
};

reconhecedor.onend = () => {
  sairModoGravacao();

  // Se algum texto foi reconhecido, marca status como sucesso
  if (textoEl.innerHTML && !textoEl.querySelector('.placeholder')) {
    setStatus('success', 'Reconhecimento concluído');
  }
};

reconhecedor.onerror = (event) => {
  console.error('Erro no reconhecimento de voz:', event.error);

  sairModoGravacao();

  // Mensagens amigáveis por tipo de erro
  const mensagens = {
    'not-allowed':   'Permissão de microfone negada',
    'no-speech':     'Nenhuma fala detectada',
    'network':       'Erro de conexão com o servidor de voz',
    'aborted':       'Gravação cancelada',
  };

  const msg = mensagens[event.error] || `Erro no reconhecimento (${event.error})`;
  setStatus('idle', msg);
};


btnGravar.addEventListener('click', () => {
  if (gravando) {
    // Para o reconhecimento manualmente se o usuário clicar de novo
    reconhecedor.stop();
  } else {
    // Limpa resultados anteriores antes de iniciar nova gravação
    textoEl.innerHTML = PLACEHOLDER;
    entrarModoGravacao();
    reconhecedor.start();
  }
});

btnLimpar.addEventListener('click', () => {
  // Restaura o placeholder e reseta o status
  textoEl.innerHTML = PLACEHOLDER;
  setStatus('idle', 'Aguardando...');
});

btnCarregarMais.addEventListener('click', () => {
  paginaAtual++;
  carregarHistorico(false);
});

// Carregar dados ao abrir a pagina
document.addEventListener( ' DOMContentLoaded',() => {
 carregaHistorico(true);
 carregaEstatistica();

});
});
