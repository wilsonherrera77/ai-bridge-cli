import { useState, useEffect } from 'react';
import {
  Rocket,
  CheckCircle2,
  Circle,
  AlertCircle,
  Sparkles,
  FileCode,
  GitBranch,
  Settings,
  Play,
  RefreshCw,
  ArrowRight
} from 'lucide-react';

const ProjectGuide = () => {
  const [projects, setProjects] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [projectName, setProjectName] = useState('');
  const [validationLevel, setValidationLevel] = useState('professional');
  const [currentProject, setCurrentProject] = useState(null);
  const [guidance, setGuidance] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('create'); // create, projects, guide

  useEffect(() => {
    loadTemplates();
    loadProjects();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/project/templates');
      const data = await response.json();
      setTemplates(data.templates || []);
      if (data.templates?.length > 0) {
        setSelectedTemplate(data.templates[0].id);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/project/list');
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const createProject = async () => {
    if (!projectName.trim()) {
      alert('Por favor ingresa un nombre para el proyecto');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/project/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          project_type: selectedTemplate,
          validation_level: validationLevel
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`✅ Proyecto ${projectName} creado exitosamente!`);
        setProjectName('');
        loadProjects();
        setActiveTab('projects');
      }
    } catch (error) {
      console.error('Error creating project:', error);
      alert('❌ Error al crear proyecto');
    } finally {
      setLoading(false);
    }
  };

  const validateProject = async (projectName) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/project/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          validation_level: 'standard',
          auto_correct: true
        })
      });

      const data = await response.json();
      setValidationResult(data);
    } catch (error) {
      console.error('Error validating project:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGuidance = async (projectName) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/project/guidance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_name: projectName })
      });

      const data = await response.json();
      setGuidance(data);
      setCurrentProject(projectName);
      setActiveTab('guide');
    } catch (error) {
      console.error('Error getting guidance:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderCreateTab = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-lg text-white">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Rocket className="w-6 h-6" />
          Crear Nuevo Proyecto Full Stack
        </h2>
        <p className="text-blue-100">
          Comienza tu proyecto con templates profesionales y guía paso a paso
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Formulario */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Nombre del Proyecto</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="mi-app-increible"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Template</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Nivel de Validación</label>
            <select
              value={validationLevel}
              onChange={(e) => setValidationLevel(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="basic">Básico - Estructura</option>
              <option value="standard">Estándar - + Linting</option>
              <option value="professional">Profesional - + Tests y Docs</option>
              <option value="production">Producción - + Security y Performance</option>
            </select>
          </div>

          <button
            onClick={createProject}
            disabled={loading || !projectName.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Creando...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Crear Proyecto
              </>
            )}
          </button>
        </div>

        {/* Info del template */}
        <div className="bg-gray-50 p-6 rounded-lg">
          {templates.find(t => t.id === selectedTemplate) && (
            <>
              <h3 className="font-bold text-lg mb-2">
                {templates.find(t => t.id === selectedTemplate).name}
              </h3>
              <p className="text-gray-600 mb-4">
                {templates.find(t => t.id === selectedTemplate).description}
              </p>
              <div>
                <p className="font-medium mb-2">Stack incluido:</p>
                <div className="flex flex-wrap gap-2">
                  {templates.find(t => t.id === selectedTemplate).stack.map(tech => (
                    <span
                      key={tech}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  const renderProjectsTab = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <FileCode className="w-6 h-6" />
          Mis Proyectos
        </h2>
        <button
          onClick={loadProjects}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Actualizar
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileCode className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">No hay proyectos creados aún</p>
          <button
            onClick={() => setActiveTab('create')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Crear tu primer proyecto
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map(project => (
            <div
              key={project.name}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-bold text-lg">{project.name}</h3>
                  <p className="text-sm text-gray-500">{project.type}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  project.phase === 'completed' ? 'bg-green-100 text-green-700' :
                  project.phase === 'development' ? 'bg-blue-100 text-blue-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {project.phase}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span>Progreso</span>
                  <span className="font-medium">{project.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${project.progress}%` }}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => getGuidance(project.name)}
                  className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm flex items-center justify-center gap-1"
                >
                  <Play className="w-4 h-4" />
                  Guía
                </button>
                <button
                  onClick={() => validateProject(project.name)}
                  className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm flex items-center justify-center gap-1"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Validar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderGuideTab = () => {
    if (!guidance) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-600">Selecciona un proyecto para ver la guía</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-green-500 to-blue-600 p-6 rounded-lg text-white">
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <GitBranch className="w-6 h-6" />
            Guía de Proyecto: {currentProject}
          </h2>
          <div className="flex items-center gap-4">
            <span className="px-3 py-1 bg-white/20 rounded-full text-sm">
              Fase: {guidance.phase}
            </span>
            <span className="px-3 py-1 bg-white/20 rounded-full text-sm">
              Progreso: {guidance.progress}%
            </span>
            <span className="px-3 py-1 bg-white/20 rounded-full text-sm">
              Completado: {guidance.checklist_completion}
            </span>
          </div>
        </div>

        {validationResult && (
          <div className={`p-4 rounded-lg border-l-4 ${
            validationResult.validation.passed
              ? 'bg-green-50 border-green-500'
              : 'bg-yellow-50 border-yellow-500'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {validationResult.validation.passed ? (
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <h3 className="font-bold">
                Resultado de Validación: {validationResult.validation.score}/100
              </h3>
            </div>
            <p className="text-sm mb-2">
              {validationResult.validation.issues} issues encontrados,
              {validationResult.validation.auto_fixable} auto-corregibles
            </p>
            {validationResult.corrections_applied.length > 0 && (
              <div className="mt-2">
                <p className="text-sm font-medium mb-1">Correcciones aplicadas:</p>
                <ul className="text-sm space-y-1">
                  {validationResult.corrections_applied.map((correction, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      {correction}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div>
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <ArrowRight className="w-5 h-5 text-blue-600" />
            Próximos Pasos
          </h3>

          {guidance.next_steps && guidance.next_steps.length > 0 ? (
            <div className="space-y-4">
              {guidance.next_steps.map((step, i) => (
                <div key={i} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold mb-1">{step.task}</h4>
                      {step.guidance && (
                        <p className="text-sm text-gray-600 mb-2">{step.guidance}</p>
                      )}
                      <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                        Fase: {step.phase}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 bg-green-50 rounded-lg">
              <CheckCircle2 className="w-12 h-12 mx-auto text-green-600 mb-2" />
              <p className="text-green-800 font-medium">¡Proyecto completado!</p>
              <p className="text-green-600 text-sm">Listo para deployment</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('create')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'create'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Rocket className="w-4 h-4 inline mr-2" />
          Crear Proyecto
        </button>
        <button
          onClick={() => setActiveTab('projects')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'projects'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <FileCode className="w-4 h-4 inline mr-2" />
          Mis Proyectos ({projects.length})
        </button>
        <button
          onClick={() => setActiveTab('guide')}
          className={`px-4 py-2 font-medium border-b-2 transition-colors ${
            activeTab === 'guide'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <GitBranch className="w-4 h-4 inline mr-2" />
          Guía
        </button>
      </div>

      {/* Content */}
      {activeTab === 'create' && renderCreateTab()}
      {activeTab === 'projects' && renderProjectsTab()}
      {activeTab === 'guide' && renderGuideTab()}
    </div>
  );
};

export default ProjectGuide;
