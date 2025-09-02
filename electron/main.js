const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');

let mainWindow;
let backendProcess;
const BACKEND_PORT = 8001;
const FRONTEND_PORT = 5173;

function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.listen(port, () => {
      server.once('close', () => resolve(true));
      server.close();
    });
    server.on('error', () => resolve(false));
  });
}

function waitForBackend(timeout = 30000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const checkBackend = () => {
      const client = new net.Socket();
      
      client.connect(BACKEND_PORT, 'localhost', () => {
        client.destroy();
        resolve();
      });
      
      client.on('error', () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Backend startup timeout'));
        } else {
          setTimeout(checkBackend, 1000);
        }
      });
    };
    
    checkBackend();
  });
}

async function startBackend() {
  console.log('Starting backend process...');
  
  const isDev = process.env.NODE_ENV === 'development';
  let backendPath;
  
  if (isDev) {
    const backendDir = path.join(__dirname, '..', 'backend');
    backendProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', BACKEND_PORT.toString()], {
      cwd: backendDir,
      env: {
        ...process.env,
        DATABASE_URL: 'sqlite+aiosqlite:///./ipam.db',
        JWT_SECRET_KEY: 'dev-secret-key-change-in-production',
        JWT_REFRESH_SECRET_KEY: 'dev-refresh-secret-key-change-in-production',
        ACCESS_TOKEN_EXPIRE_MINUTES: '15',
        REFRESH_TOKEN_EXPIRE_DAYS: '7',
        ADMIN_USERNAME: 'admin',
        ADMIN_EMAIL: 'admin@example.com',
        ADMIN_PASSWORD: 'Cisco!123',
        CORS_ORIGINS: `http://localhost:${FRONTEND_PORT}`,
        ENV: 'development',
        LOG_LEVEL: 'info'
      }
    });
  } else {
    const resourcesPath = process.resourcesPath || path.join(__dirname, '..');
    backendPath = path.join(resourcesPath, 'backend', process.platform === 'win32' ? 'ipam-backend.exe' : 'ipam-backend');
    
    if (!fs.existsSync(backendPath)) {
      throw new Error(`Backend executable not found at ${backendPath}`);
    }
    
    const appDataPath = path.join(app.getPath('userData'), 'ipam-data');
    if (!fs.existsSync(appDataPath)) {
      fs.mkdirSync(appDataPath, { recursive: true });
    }
    
    backendProcess = spawn(backendPath, [], {
      env: {
        ...process.env,
        DATABASE_URL: `sqlite+aiosqlite:///${path.join(appDataPath, 'ipam.db')}`,
        JWT_SECRET_KEY: 'prod-secret-key-change-me',
        JWT_REFRESH_SECRET_KEY: 'prod-refresh-secret-key-change-me',
        ACCESS_TOKEN_EXPIRE_MINUTES: '15',
        REFRESH_TOKEN_EXPIRE_DAYS: '7',
        ADMIN_USERNAME: 'admin',
        ADMIN_EMAIL: 'admin@example.com',
        ADMIN_PASSWORD: 'Cisco!123',
        CORS_ORIGINS: `http://localhost:${FRONTEND_PORT}`,
        ENV: 'production',
        LOG_LEVEL: 'info'
      }
    });
  }
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`);
  });
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    if (code !== 0 && mainWindow) {
      dialog.showErrorBox('Backend Error', `Backend process exited with code ${code}`);
    }
  });
  
  try {
    await waitForBackend();
    console.log('Backend is ready!');
  } catch (error) {
    console.error('Backend failed to start:', error);
    throw error;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png'), // Add icon if available
    title: 'IPAM Tool - IP Address Management'
  });
  
  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL(`http://localhost:${FRONTEND_PORT}`);
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'frontend', 'index.html'));
  }
  
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(async () => {
  try {
    const backendAvailable = await isPortAvailable(BACKEND_PORT);
    if (!backendAvailable) {
      dialog.showErrorBox('Port Error', `Backend port ${BACKEND_PORT} is already in use`);
      app.quit();
      return;
    }
    
    await startBackend();
    
    createWindow();
    
  } catch (error) {
    console.error('Failed to start application:', error);
    dialog.showErrorBox('Startup Error', `Failed to start application: ${error.message}`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    console.log('Terminating backend process...');
    backendProcess.kill();
  }
});

process.on('SIGINT', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  app.quit();
});

process.on('SIGTERM', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  app.quit();
});
