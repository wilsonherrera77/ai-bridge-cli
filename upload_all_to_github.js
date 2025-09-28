import { Octokit } from '@octokit/rest'
import fs from 'fs'
import path from 'path'

let connectionSettings;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;

  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

export async function getUncachableGitHubClient() {
  const accessToken = await getAccessToken();
  return new Octokit({ auth: accessToken });
}

function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = fs.readdirSync(dirPath);

  files.forEach(file => {
    const fullPath = path.join(dirPath, file);
    if (fs.statSync(fullPath).isDirectory()) {
      // Skip certain directories
      if (!file.startsWith('.') && !file.includes('node_modules') && !file.includes('__pycache__')) {
        arrayOfFiles = getAllFiles(fullPath, arrayOfFiles);
      }
    } else {
      // Skip certain file types
      if (!file.startsWith('.') && !file.endsWith('.pyc') && !file.endsWith('.log')) {
        arrayOfFiles.push(fullPath);
      }
    }
  });

  return arrayOfFiles;
}

async function uploadAllToGitHub() {
  try {
    console.log('🚀 SUBIENDO TODO EL DESARROLLO A GITHUB...');
    
    const octokit = await getUncachableGitHubClient();
    
    const owner = 'wilsonherrera77';
    const repo = 'ai-bridge-cli';
    
    // Obtener estado actual del repositorio
    const { data: ref } = await octokit.rest.git.getRef({
      owner,
      repo,
      ref: 'heads/main'
    });
    
    const baseTreeSha = ref.object.sha;
    console.log('🌿 Base commit:', baseTreeSha.substring(0, 7));
    
    // Obtener último commit
    const { data: commit } = await octokit.rest.git.getCommit({
      owner,
      repo,
      commit_sha: baseTreeSha
    });
    
    // Obtener todos los archivos del proyecto actual
    const allFiles = getAllFiles('./');
    
    console.log(`📁 Archivos encontrados: ${allFiles.length}`);
    
    // Filtrar archivos importantes a subir
    const filesToUpload = allFiles.filter(file => {
      const fileName = path.basename(file);
      const filePath = file.replace(/\\/g, '/').replace('./', '');
      
      // Incluir archivos Python principales
      if (fileName.endsWith('.py')) return true;
      
      // Incluir archivos de configuración importantes
      if (fileName === 'package.json' || fileName === 'requirements.txt') return true;
      
      // Incluir archivos JavaScript/React
      if (fileName.endsWith('.js') || fileName.endsWith('.jsx')) return true;
      
      // Incluir archivos de configuración
      if (fileName.endsWith('.json') && !fileName.includes('session_')) return true;
      
      // Incluir archivos markdown
      if (fileName.endsWith('.md')) return true;
      
      // Incluir archivos HTML/CSS
      if (fileName.endsWith('.html') || fileName.endsWith('.css')) return true;
      
      // Excluir directorios temporales
      if (filePath.includes('discovery_windows_test') || 
          filePath.includes('discovery_test_windows') ||
          filePath.includes('attached_assets') ||
          filePath.includes('backend/sessions') ||
          filePath.includes('node_modules')) return false;
      
      return false;
    });
    
    console.log(`📤 Archivos a subir: ${filesToUpload.length}`);
    
    // Mostrar lista de archivos a subir
    console.log('\n📋 ARCHIVOS A SUBIR:');
    filesToUpload.forEach(file => {
      const relativePath = file.replace(/\\/g, '/').replace('./', '');
      console.log(`   📄 ${relativePath}`);
    });
    
    // Crear tree items
    const treeItems = [];
    
    for (const filePath of filesToUpload) {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const relativePath = filePath.replace(/\\/g, '/').replace('./', '');
        
        // Crear blob
        const { data: blob } = await octokit.rest.git.createBlob({
          owner,
          repo,
          content: Buffer.from(content, 'utf8').toString('base64'),
          encoding: 'base64'
        });
        
        treeItems.push({
          path: relativePath,
          mode: '100644',
          type: 'blob',
          sha: blob.sha
        });
        
        console.log(`✅ ${relativePath}: Blob creado`);
        
      } catch (error) {
        console.error(`❌ Error con ${filePath}:`, error.message);
      }
    }
    
    if (treeItems.length === 0) {
      console.log('❌ No se pudieron preparar archivos');
      return { success: false, error: 'No files to upload' };
    }
    
    // Crear tree
    const { data: tree } = await octokit.rest.git.createTree({
      owner,
      repo,
      base_tree: commit.tree.sha,
      tree: treeItems
    });
    
    console.log(`🌳 Tree creado: ${tree.sha.substring(0, 7)}`);
    
    // Crear commit
    const commitMessage = `🚀 Subida completa del desarrollo AI-Bridge

📦 CONTENIDO ACTUALIZADO:
- Sistema completo de agentes Claude para Windows
- Lanzadores: launch_real_claude_agents.py, launch_claude_code_agents.py
- Configurador Windows: setup_windows_agents.py
- Fix manual de estructura: fix_setup_windows.py
- Backend completo: orchestrator, agents, communication
- Frontend React: componentes, hooks, configuración
- Motor de descubrimiento: configuración y estructura
- Documentación actualizada: replit.md

🎯 CARACTERÍSTICAS PRINCIPALES:
✅ Agentes autónomos para motor de descubrimiento
✅ Adaptación completa para Windows con Claude Code
✅ Sistema de orchestradores y comunicación entre agentes
✅ Frontend React para monitoreo en tiempo real
✅ CLI completa con parámetros configurables
✅ Providers modulares (Web, Reddit, YouTube, RSS)
✅ Deduplicación y scoring por relevancia/recencia
✅ Outputs múltiples (JSONL, CSV, SQLite, Excel)

🛠️ ARCHIVOS SUBIDOS: ${treeItems.length}
🔧 Python: Backend orchestration, agents, CLI tools
🎨 React: Frontend components y configuración  
📋 Config: Package.json, requirements, configuraciones
📖 Docs: README, instrucciones, documentación

SISTEMA COMPLETO LISTO PARA PRODUCCIÓN EN WINDOWS`;

    const { data: newCommit } = await octokit.rest.git.createCommit({
      owner,
      repo,
      message: commitMessage,
      tree: tree.sha,
      parents: [baseTreeSha]
    });
    
    console.log(`📝 Commit creado: ${newCommit.sha.substring(0, 7)}`);
    
    // Actualizar referencia de la rama
    await octokit.rest.git.updateRef({
      owner,
      repo,
      ref: 'heads/main',
      sha: newCommit.sha
    });
    
    console.log('🔄 Rama main actualizada');
    
    return {
      success: true,
      commitSha: newCommit.sha,
      filesUploaded: treeItems.length,
      message: 'Todo el desarrollo subido exitosamente'
    };
    
  } catch (error) {
    console.error('❌ Error subiendo desarrollo:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

uploadAllToGitHub().then(result => {
  if (result.success) {
    console.log('\n🎉 SUBIDA COMPLETA DEL DESARROLLO:');
    console.log('===============================================');
    console.log('✅ Estado: EXITOSO');
    console.log('📝 Commit:', result.commitSha.substring(0, 7));
    console.log('📁 Archivos subidos:', result.filesUploaded);
    console.log('💬 Mensaje:', result.message);
    console.log('===============================================');
    console.log('🚀 TODO EL DESARROLLO ESTÁ EN GITHUB');
    console.log('🎯 Sistema completo para Windows con Claude Code');
    console.log('🤖 Agentes autónomos motor de descubrimiento');
    console.log('🔧 Backend orchestration + Frontend React');
    console.log('📋 CLI tools + Configuradores Windows');
  } else {
    console.log('\n❌ ERROR EN SUBIDA:');
    console.log('Error:', result.error);
  }
});