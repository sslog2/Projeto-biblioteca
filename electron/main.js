const { app, BrowserWindow, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

let mainWindow = null;
let djangoProcess = null;
const PORT = 8000;
const SERVER_URL = `http://127.0.0.1:${PORT}`;

// ───────────────────────────────────────────────
// Encontra o servidor Django (bundle ou dev)
// ───────────────────────────────────────────────
function findServer() {
  // Modo produção: executável gerado pelo PyInstaller
  const bundledExe = path.join(
    process.resourcesPath,
    'django_server',
    process.platform === 'win32' ? 'django_server.exe' : 'django_server'
  );

  if (fs.existsSync(bundledExe)) {
    return {
      cmd: bundledExe,
      args: [],
      cwd: path.dirname(bundledExe),
    };
  }

  // Modo desenvolvimento: Python do virtualenv ou sistema
  const appRoot = path.join(__dirname, '..');
  const venvPython = path.join(
    appRoot,
    'env',
    'Scripts',
    process.platform === 'win32' ? 'python.exe' : 'python'
  );
  const python = fs.existsSync(venvPython) ? venvPython : 'python';

  return {
    cmd: python,
    args: [
      path.join(appRoot, 'manage.py'),
      'runserver',
      `127.0.0.1:${PORT}`,
      '--noreload',
    ],
    cwd: appRoot,
  };
}

// ───────────────────────────────────────────────
// Aguarda o servidor Django responder
// ───────────────────────────────────────────────
function waitForServer(timeoutMs = 60000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;

    function attempt() {
      const req = http.get(SERVER_URL, (res) => {
        res.resume(); // descarta o corpo
        resolve();
      });
      req.on('error', () => {
        if (Date.now() >= deadline) {
          reject(new Error('O servidor Django não respondeu no tempo limite.'));
        } else {
          setTimeout(attempt, 600);
        }
      });
      req.setTimeout(1000, () => req.destroy());
    }

    attempt();
  });
}

// ───────────────────────────────────────────────
// Inicializa o processo Django
// ───────────────────────────────────────────────
function startDjangoServer() {
  const { cmd, args, cwd } = findServer();

  console.log('[Django] Iniciando:', cmd, args.join(' '));

  djangoProcess = spawn(cmd, args, {
    cwd,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      DJANGO_SETTINGS_MODULE: 'project.settings_exe',
    },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  });

  djangoProcess.stdout.on('data', (d) =>
    console.log('[Django stdout]', d.toString().trim())
  );
  djangoProcess.stderr.on('data', (d) =>
    console.log('[Django stderr]', d.toString().trim())
  );
  djangoProcess.on('error', (err) =>
    console.error('[Django error]', err.message)
  );
  djangoProcess.on('exit', (code) =>
    console.log(`[Django] Processo encerrado com código ${code}`)
  );

  return waitForServer();
}

// ───────────────────────────────────────────────
// Cria a janela principal
// ───────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1366,
    height: 768,
    minWidth: 900,
    minHeight: 600,
    title: 'Sistema de Biblioteca',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  // Abre links externos no navegador padrão
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.loadURL(SERVER_URL);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ───────────────────────────────────────────────
// Ciclo de vida do app
// ───────────────────────────────────────────────
app.whenReady().then(async () => {
  try {
    await startDjangoServer();
    createWindow();
  } catch (err) {
    dialog.showErrorBox('Erro ao iniciar o servidor', err.message);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopDjango();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) createWindow();
});

app.on('before-quit', stopDjango);

function stopDjango() {
  if (djangoProcess) {
    djangoProcess.kill();
    djangoProcess = null;
  }
}
