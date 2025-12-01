import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function App() {
  // Navegação
  const [view, setView] = useState('extracao');

  // Estados gerais
  const [file, setFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Estados da análise e lançamento
  const [analysisMessage, setAnalysisMessage] = useState('');
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  const [analyzeForm, setAnalyzeForm] = useState({
    fornecedor: { razao_social: '', fantasia: '', cnpj: '' },
    faturado: { nome_completo: '', cpf: '' },
    classificacao_despesa: '',
    numero_nota_fiscal: '',
    data_emissao: '',
    descricao_produtos: '',
    valor_total: '',
    data_vencimento: '',
    classificacoes: []
  });

  // Listas para páginas de manutenção
  const [fornecedores, setFornecedores] = useState([]);
  const [tiposDespesa, setTiposDespesa] = useState([]);
  const [contasPagar, setContasPagar] = useState([]);
  const [contasReceber, setContasReceber] = useState([]);
  const [clientesList, setClientesList] = useState([]);
  const [faturadosList, setFaturadosList] = useState([]);

  // Formulários de criação
  const [novoFornecedor, setNovoFornecedor] = useState({ razao_social: '', fantasia: '', cnpj: '' });
  const [novoTipoDespesa, setNovoTipoDespesa] = useState({ nome: '', descricao: '' });
  const [novaContaReceber, setNovaContaReceber] = useState({ numero_documento: '', data_emissao: '', descricao: '', valor_total: '', cliente_id: '' });
  const [clientes, setClientes] = useState([]);
  const [novoCliente, setNovoCliente] = useState({ nome_completo: '', cpf: '', cnpj: '' });
  const [novoFaturado, setNovoFaturado] = useState({ nome_completo: '', cpf: '' });
  const [novoTipoReceita, setNovoTipoReceita] = useState({ nome: '', descricao: '' });

  const [shouldFetch, setShouldFetch] = useState({ fornecedores: false, tiposDespesa: false, contasPagar: false, contasReceber: false, clientes: false, faturados: false, tiposReceita: false });
  const [search, setSearch] = useState({ fornecedores: { nome: '', cnpj: '' }, clientes: { nome: '', cpf: '', cnpj: '' }, tiposDespesa: { nome: '' }, tiposReceita: { nome: '' } });
  const [sort, setSort] = useState({ fornecedores: { col: 'razao_social', dir: 'asc' }, clientes: { col: 'nome_completo', dir: 'asc' }, tiposDespesa: { col: 'nome', dir: 'asc' }, tiposReceita: { col: 'nome', dir: 'asc' } });
  const [editingFornecedor, setEditingFornecedor] = useState(null);
  const [editingCliente, setEditingCliente] = useState(null);
  const [editingTipoDespesa, setEditingTipoDespesa] = useState(null);
  const [editingTipoReceita, setEditingTipoReceita] = useState(null);

  // Upload PDF
  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
      setSuccess('');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  // Efeitos para carregar dados conforme a visualização
  useEffect(() => {
    const fetchFornecedores = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/fornecedores`);
        setFornecedores(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchTiposDespesa = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/tipos-despesa`);
        setTiposDespesa(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchContasPagar = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/contas-pagar`);
        setContasPagar(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchContasReceber = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/contas-receber`);
        setContasReceber(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchClientes = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/clientes`);
        setClientes(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchClientesList = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/clientes`);
        setClientesList(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchFaturadosList = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/faturados`);
        setFaturadosList(res.data);
      } catch (e) { /* silencioso */ }
    };
    const fetchTiposReceita = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/tipos-receita`);
        setTiposReceita(res.data);
      } catch (e) { /* silencioso */ }
    };

    if (view === 'fornecedores' && shouldFetch.fornecedores) fetchFornecedores();
    if (view === 'tiposDespesa' && shouldFetch.tiposDespesa) fetchTiposDespesa();
    if (view === 'contasPagar' && shouldFetch.contasPagar) fetchContasPagar();
    if (view === 'contasReceber' && shouldFetch.contasReceber) { fetchContasReceber(); fetchClientes(); }
    if (view === 'clientes' && shouldFetch.clientes) fetchClientesList();
    if (view === 'faturados' && shouldFetch.faturados) fetchFaturadosList();
    if (view === 'tiposReceita' && shouldFetch.tiposReceita) fetchTiposReceita();
  }, [view, shouldFetch]);

  const onTodos = (key) => {
    setError(''); setSuccess('');
    setShouldFetch(prev => ({ ...prev, [key]: true }));
  };

  const onBuscarFornecedores = () => {
    const qn = (search.fornecedores.nome || '').toLowerCase();
    const qc = (search.fornecedores.cnpj || '').toLowerCase();
    const base = fornecedores.filter(f => f.is_active !== false);
    const filtered = base.filter(f => (
      (!qn || (f.razao_social || '').toLowerCase().includes(qn)) && (!qc || (f.cnpj || '').toLowerCase().includes(qc))
    ));
    const dir = sort.fornecedores.dir === 'asc' ? 1 : -1;
    filtered.sort((a,b)=>((a[sort.fornecedores.col]||'').toString()).localeCompare((b[sort.fornecedores.col]||'').toString())*dir);
    setFornecedores(filtered);
  };

  const onBuscarClientes = () => {
    const qn = (search.clientes.nome || '').toLowerCase();
    const qcpf = (search.clientes.cpf || '').toLowerCase();
    const qcnpj = (search.clientes.cnpj || '').toLowerCase();
    const base = clientesList.filter(c => c.is_active !== false);
    const filtered = base.filter(c => (
      (!qn || (c.nome_completo || '').toLowerCase().includes(qn)) && (!qcpf || (c.cpf || '').toLowerCase().includes(qcpf)) && (!qcnpj || (c.cnpj || '').toLowerCase().includes(qcnpj))
    ));
    const dir = sort.clientes.dir === 'asc' ? 1 : -1;
    filtered.sort((a,b)=>((a[sort.clientes.col]||'').toString()).localeCompare((b[sort.clientes.col]||'').toString())*dir);
    setClientesList(filtered);
  };

  const onBuscarTiposDespesa = () => {
    const qn = (search.tiposDespesa.nome || '').toLowerCase();
    const base = tiposDespesa.filter(t => t.is_active !== false);
    const filtered = base.filter(t => (!qn || (t.nome || '').toLowerCase().includes(qn)));
    const dir = sort.tiposDespesa.dir === 'asc' ? 1 : -1;
    filtered.sort((a,b)=>((a[sort.tiposDespesa.col]||'').toString()).localeCompare((b[sort.tiposDespesa.col]||'').toString())*dir);
    setTiposDespesa(filtered);
  };

  const [tiposReceita, setTiposReceita] = useState([]);
  const onBuscarTiposReceita = () => {
    const qn = (search.tiposReceita.nome || '').toLowerCase();
    const base = tiposReceita.filter(t => t.is_active !== false);
    const filtered = base.filter(t => (!qn || (t.nome || '').toLowerCase().includes(qn)));
    const dir = sort.tiposReceita.dir === 'asc' ? 1 : -1;
    filtered.sort((a,b)=>((a[sort.tiposReceita.col]||'').toString()).localeCompare((b[sort.tiposReceita.col]||'').toString())*dir);
    setTiposReceita(filtered);
  };

  // Fluxo de extração
  const extractData = async () => {
    if (!file) {
      setError('Por favor, selecione um arquivo PDF');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setExtractedData(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setExtractedData(response.data);
      setSuccess('Dados extraídos com sucesso!');
    } catch (err) {
      setError('Erro ao extrair dados: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Salvar dados extraídos (fluxo antigo)
  const saveToDatabase = async () => {
    if (!extractedData) {
      setError('Nenhum dado para salvar');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const fornecedor = extractedData.fornecedor || {};
      const faturado = extractedData.faturado || {};
      const razao = (fornecedor.razao_social || '').trim();
      const cnpj = (fornecedor.cnpj || '').trim();
      const nomeFat = (faturado.nome_completo || '').trim();
      const cpfFat = (faturado.cpf || '').trim();
      if (!razao) { setError('Fornecedor: razão social é obrigatória'); return; }
      if (!cnpj) { setError('Fornecedor: CNPJ é obrigatório'); return; }
      if (!cpfFat) { setError('Faturado: CPF é obrigatório'); return; }
      const res = await axios.post(`${API_BASE_URL}/api/save-invoice`, { ...extractedData });
      setSuccess(res.data.message || 'Dados salvos no banco de dados com sucesso!');
    } catch (err) {
      setError('Erro ao salvar dados: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (extractedData) {
      navigator.clipboard.writeText(JSON.stringify(extractedData, null, 2));
      setSuccess('JSON copiado para a área de transferência!');
    }
  };

  // Fluxo Analisar e Lançar
  const handleAnalyzeChange = (path, value) => {
    setAnalyzeForm(prev => {
      const copy = { ...prev };
      const keys = path.split('.');
      let obj = copy;
      for (let i = 0; i < keys.length - 1; i++) {
        obj[keys[i]] = { ...obj[keys[i]] };
        obj = obj[keys[i]];
      }
      obj[keys[keys.length - 1]] = value;
      return copy;
    });
  };

  const startAnalyzeAndSave = async () => {
    setAnalyzeLoading(true);
    setError('');
    setSuccess('');
    setAnalysisMessage('');
    try {
      const razao = (analyzeForm.fornecedor.razao_social || '').trim();
      const cnpj = (analyzeForm.fornecedor.cnpj || '').trim();
      const nomeFat = (analyzeForm.faturado.nome_completo || '').trim();
      const cpfFat = (analyzeForm.faturado.cpf || '').trim();
      if (!razao) { setError('Fornecedor: razão social é obrigatória'); return; }
      if (!cnpj) { setError('Fornecedor: CNPJ é obrigatório'); return; }
      if (!cpfFat) { setError('Faturado: CPF é obrigatório'); return; }
      // preparar payload convertendo valor_total para número
      const payload = {
        ...analyzeForm,
        valor_total: Number(analyzeForm.valor_total || 0)
      };
      const res = await axios.post(`${API_BASE_URL}/api/analyze-and-save`, payload);
      const data = res.data;
      setAnalysisMessage(data.analysis_message || '');
      setSuccess(data.message || 'Registro foi lançado com sucesso.');
    } catch (err) {
      setError('Erro ao analisar e salvar: ' + (err.response?.data?.error || err.message));
    } finally {
      setAnalyzeLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        {/* Navegação */}
        <div className="nav">
          <button className={`nav-item ${view === 'extracao' ? 'active' : ''}`} onClick={() => setView('extracao')}>🧾 Extração</button>
          <button className={`nav-item ${view === 'analisar' ? 'active' : ''}`} onClick={() => setView('analisar')}>🔎 Analisar e Lançar</button>
          <button className={`nav-item ${view === 'fornecedores' ? 'active' : ''}`} onClick={() => setView('fornecedores')}>🏢 Fornecedores</button>
          <button className={`nav-item ${view === 'tiposDespesa' ? 'active' : ''}`} onClick={() => setView('tiposDespesa')}>🏷️ Tipos de Despesa</button>
          <button className={`nav-item ${view === 'contasPagar' ? 'active' : ''}`} onClick={() => setView('contasPagar')}>💸 Contas a Pagar</button>
          <button className={`nav-item ${view === 'contasReceber' ? 'active' : ''}`} onClick={() => setView('contasReceber')}>💰 Contas a Receber</button>
          <button className={`nav-item ${view === 'clientes' ? 'active' : ''}`} onClick={() => setView('clientes')}>👥 Clientes</button>
          <button className={`nav-item ${view === 'faturados' ? 'active' : ''}`} onClick={() => setView('faturados')}>🧑‍💼 Faturados</button>
          <button className={`nav-item ${view === 'tiposReceita' ? 'active' : ''}`} onClick={() => setView('tiposReceita')}>📈 Tipos de Receita</button>
        </div>

        {/* Cabeçalho */}
        <div className="header">
          <h1>🧾 Sistema Financeiro</h1>
          <p>Menu para acessar funcionalidades separadamente conforme a 2ª etapa.</p>
        </div>

        {/* Página: Extração */}
        {view === 'extracao' && (
          <div>
            {/* Card de Upload */}
            <div className="card">
              <h3>📤 Upload de Arquivo</h3>
              <div {...getRootProps()} className={`upload-area ${isDragActive ? 'dragover' : ''}`}>
                <input {...getInputProps()} />
                {isDragActive ? (
                  <div>
                    <div className="upload-icon">📄</div>
                    <p><strong>Solte o arquivo aqui...</strong></p>
                  </div>
                ) : (
                  <div>
                    <div className="upload-icon">📄</div>
                    <p><strong>Arraste e solte seu PDF aqui</strong></p>
                    <p>ou clique para selecionar o arquivo</p>
                    <div className="file-types">Aceita apenas arquivos PDF</div>
                  </div>
                )}
              </div>

              {file && (
                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <div className="file-details">
                    <strong>{file.name}</strong>
                    <div className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                  </div>
                  <button onClick={() => setFile(null)} className="btn btn-remove" title="Remover arquivo">✕</button>
                </div>
              )}

              <div className="button-group">
                <button onClick={extractData} disabled={loading || !file} className="btn btn-primary btn-large">
                  {loading ? (<><div className="spinner"></div>Processando...</>) : (<>🔍 Extrair Dados</>)}
                </button>
              </div>
            </div>

            {/* Mensagens de Status */}
            {error && <div className="error">❌ {error}</div>}
            {success && <div className="success">✅ {success}</div>}

            {/* Card de Resultados */}
            {extractedData && (
              <div className="card">
                <h3>📊 Dados Extraídos</h3>
                <div className="button-group">
                  <button onClick={copyToClipboard} className="btn btn-secondary">📋 Copiar JSON</button>
                  <button onClick={saveToDatabase} disabled={loading} className="btn btn-success">
                    {loading ? (<><div className="spinner"></div>Salvando...</>) : (<>💾 Salvar no Banco</>)}
                  </button>
                </div>
                <div className="json-container">
                  <h4>📋 Dados em JSON</h4>
                  <pre>{JSON.stringify(extractedData, null, 2)}</pre>
                </div>
                <div className="info-text">
                  <p>💡 Este JSON contém todos os dados extraídos da nota fiscal e pode ser usado para integração com outros sistemas.</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Página: Analisar e Lançar */}
        {view === 'analisar' && (
          <div className="card">
            <h3>🔎 Analisar Existência e Lançar Movimento</h3>
            <div className="form-grid">
              <div>
                <h4>FORNECEDOR</h4>
                <input placeholder="Razão Social" value={analyzeForm.fornecedor.razao_social} onChange={e => handleAnalyzeChange('fornecedor.razao_social', e.target.value)} />
                <input placeholder="Fantasia" value={analyzeForm.fornecedor.fantasia} onChange={e => handleAnalyzeChange('fornecedor.fantasia', e.target.value)} />
                <input placeholder="CNPJ" value={analyzeForm.fornecedor.cnpj} onChange={e => handleAnalyzeChange('fornecedor.cnpj', e.target.value)} />
              </div>
              <div>
                <h4>FATURADO</h4>
                <input placeholder="Nome Completo" value={analyzeForm.faturado.nome_completo} onChange={e => handleAnalyzeChange('faturado.nome_completo', e.target.value)} />
                <input placeholder="CPF" value={analyzeForm.faturado.cpf} onChange={e => handleAnalyzeChange('faturado.cpf', e.target.value)} />
              </div>
              <div>
                <h4>DESPESA</h4>
                <input placeholder="Classificação de Despesa" value={analyzeForm.classificacao_despesa} onChange={e => handleAnalyzeChange('classificacao_despesa', e.target.value)} />
              </div>
            </div>

            <div className="form-grid">
              <div>
                <h4>DOCUMENTO</h4>
                <input placeholder="Número NF" value={analyzeForm.numero_nota_fiscal} onChange={e => handleAnalyzeChange('numero_nota_fiscal', e.target.value)} />
                <input type="date" placeholder="Data Emissão" value={analyzeForm.data_emissao} onChange={e => handleAnalyzeChange('data_emissao', e.target.value)} />
                <input placeholder="Descrição dos Produtos" value={analyzeForm.descricao_produtos} onChange={e => handleAnalyzeChange('descricao_produtos', e.target.value)} />
                <input type="number" step="0.01" placeholder="Valor Total" value={analyzeForm.valor_total} onChange={e => handleAnalyzeChange('valor_total', e.target.value)} />
                <input type="date" placeholder="Data Vencimento" value={analyzeForm.data_vencimento} onChange={e => handleAnalyzeChange('data_vencimento', e.target.value)} />
              </div>
            </div>

            <div className="button-group">
              <button onClick={startAnalyzeAndSave} disabled={analyzeLoading} className="btn btn-primary btn-large">
                {analyzeLoading ? (<><div className="spinner"></div>Analisando...</>) : (<>🚀 Analisar e Lançar</>)}
              </button>
            </div>

            {error && <div className="error">❌ {error}</div>}
            {success && <div className="success">✅ {success}</div>}

            {analysisMessage && (
              <div className="json-container">
                <h4>📋 Resposta da Consulta</h4>
                <pre>{analysisMessage}</pre>
              </div>
            )}
          </div>
        )}

        {/* Página: Fornecedores */}
        {view === 'fornecedores' && (
          <div className="card">
            <h3>🏢 Manter Fornecedor</h3>
            <div className="form-inline">
              <input placeholder="Razão Social" value={novoFornecedor.razao_social} onChange={e => setNovoFornecedor({ ...novoFornecedor, razao_social: e.target.value })} />
              <input placeholder="Fantasia" value={novoFornecedor.fantasia} onChange={e => setNovoFornecedor({ ...novoFornecedor, fantasia: e.target.value })} />
              <input placeholder="CNPJ" value={novoFornecedor.cnpj} onChange={e => setNovoFornecedor({ ...novoFornecedor, cnpj: e.target.value })} />
              <button className="btn btn-success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  const res = await axios.post(`${API_BASE_URL}/api/fornecedores`, novoFornecedor);
                  setSuccess(res.data.message || 'Fornecedor criado com sucesso');
                  setNovoFornecedor({ razao_social: '', fantasia: '', cnpj: '' });
                  if (shouldFetch.fornecedores) {
                    const list = await axios.get(`${API_BASE_URL}/api/fornecedores`);
                    setFornecedores(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <input placeholder="Buscar por nome" value={search.fornecedores.nome} onChange={e => setSearch({ ...search, fornecedores: { ...search.fornecedores, nome: e.target.value } })} />
              <input placeholder="Buscar por CNPJ" value={search.fornecedores.cnpj} onChange={e => setSearch({ ...search, fornecedores: { ...search.fornecedores, cnpj: e.target.value } })} />
              <button className="btn btn-secondary" onClick={() => onBuscarFornecedores()}>Buscar</button>
              <button className="btn btn-primary" onClick={() => onTodos('fornecedores')}>TODOS</button>
            </div>
            <table style={{ width: '100%', marginTop: 12 }}>
              <thead>
                <tr>
                  <th onClick={() => setSort({ ...sort, fornecedores: { col: 'razao_social', dir: sort.fornecedores.dir === 'asc' ? 'desc' : 'asc' } })}>Razão Social</th>
                  <th onClick={() => setSort({ ...sort, fornecedores: { col: 'cnpj', dir: sort.fornecedores.dir === 'asc' ? 'desc' : 'asc' } })}>CNPJ</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {fornecedores.filter(f => shouldFetch.fornecedores).map(f => (
                  <tr key={f.id}>
                    <td>{editingFornecedor?.id === f.id ? (<input value={editingFornecedor.razao_social} onChange={e=>setEditingFornecedor({...editingFornecedor, razao_social: e.target.value})} />) : f.razao_social}</td>
                    <td>{editingFornecedor?.id === f.id ? (<input value={editingFornecedor.cnpj} onChange={e=>setEditingFornecedor({...editingFornecedor, cnpj: e.target.value})} />) : f.cnpj}</td>
                    <td>
                      {editingFornecedor?.id === f.id ? (
                        <button className="btn btn-success" onClick={async ()=>{
                          setError(''); setSuccess('');
                          try {
                            await axios.put(`${API_BASE_URL}/api/fornecedores/${f.id}`, editingFornecedor);
                            setSuccess('Fornecedor atualizado');
                            const list = await axios.get(`${API_BASE_URL}/api/fornecedores`);
                            setFornecedores(list.data);
                            setEditingFornecedor(null);
                          } catch (err) {
                            setError(err.response?.data?.error || err.message);
                          }
                        }}>Salvar</button>
                      ) : (
                        <button className="btn btn-primary" onClick={()=>setEditingFornecedor({ id: f.id, razao_social: f.razao_social || '', cnpj: f.cnpj || '' })}>Editar</button>
                      )}
                      <button className="btn btn-secondary" onClick={async () => {
                        setError(''); setSuccess('');
                        try {
                          await axios.patch(`${API_BASE_URL}/api/fornecedores/${f.id}/inativar`);
                          setSuccess('Fornecedor inativado com sucesso');
                          const list = await axios.get(`${API_BASE_URL}/api/fornecedores`);
                          setFornecedores(list.data);
                        } catch (err) {
                          setError(err.response?.data?.error || err.message);
                        }
                      }}>Inativar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!shouldFetch.fornecedores || fornecedores.length === 0) && <div style={{ marginTop: 8 }}>Tabela vazia. Use Buscar ou TODOS.</div>}
          </div>
        )}

        {/* Página: Tipos de Despesa */}
        {view === 'tiposDespesa' && (
          <div className="card">
            <h3>🏷️ Manter Tipo de Despesa</h3>
            <div className="form-inline">
              <input placeholder="Nome" value={novoTipoDespesa.nome} onChange={e => setNovoTipoDespesa({ ...novoTipoDespesa, nome: e.target.value })} />
              <input placeholder="Descrição" value={novoTipoDespesa.descricao} onChange={e => setNovoTipoDespesa({ ...novoTipoDespesa, descricao: e.target.value })} />
              <button className="btn btn-success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  const res = await axios.post(`${API_BASE_URL}/api/tipos-despesa`, novoTipoDespesa);
                  setSuccess(res.data.message || 'Tipo de despesa criado com sucesso');
                  setNovoTipoDespesa({ nome: '', descricao: '' });
                  if (shouldFetch.tiposDespesa) {
                    const list = await axios.get(`${API_BASE_URL}/api/tipos-despesa`);
                    setTiposDespesa(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <input placeholder="Buscar por nome" value={search.tiposDespesa.nome} onChange={e => setSearch({ ...search, tiposDespesa: { nome: e.target.value } })} />
              <button className="btn btn-secondary" onClick={() => onBuscarTiposDespesa()}>Buscar</button>
              <button className="btn btn-primary" onClick={() => onTodos('tiposDespesa')}>TODOS</button>
            </div>
            <table style={{ width: '100%', marginTop: 12 }}>
              <thead>
                <tr>
                  <th onClick={() => setSort({ ...sort, tiposDespesa: { col: 'nome', dir: sort.tiposDespesa.dir === 'asc' ? 'desc' : 'asc' } })}>Nome</th>
                  <th>Descrição</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {tiposDespesa.filter(t => shouldFetch.tiposDespesa).map(td => (
                  <tr key={td.id}>
                    <td>{editingTipoDespesa?.id === td.id ? (<input value={editingTipoDespesa.nome} onChange={e=>setEditingTipoDespesa({...editingTipoDespesa, nome: e.target.value})} />) : td.nome}</td>
                    <td>{editingTipoDespesa?.id === td.id ? (<input value={editingTipoDespesa.descricao || ''} onChange={e=>setEditingTipoDespesa({...editingTipoDespesa, descricao: e.target.value})} />) : td.descricao}</td>
                    <td>
                      {editingTipoDespesa?.id === td.id ? (
                        <button className="btn btn-success" onClick={async ()=>{
                          setError(''); setSuccess('');
                          try {
                            await axios.put(`${API_BASE_URL}/api/tipos-despesa/${td.id}`, editingTipoDespesa);
                            setSuccess('Tipo de despesa atualizado');
                            const list = await axios.get(`${API_BASE_URL}/api/tipos-despesa`);
                            setTiposDespesa(list.data);
                            setEditingTipoDespesa(null);
                          } catch (err) {
                            setError(err.response?.data?.error || err.message);
                          }
                        }}>Salvar</button>
                      ) : (
                        <button className="btn btn-primary" onClick={()=>setEditingTipoDespesa({ id: td.id, nome: td.nome || '', descricao: td.descricao || '' })}>Editar</button>
                      )}
                      <button className="btn btn-secondary" onClick={async () => {
                        setError(''); setSuccess('');
                        try {
                          await axios.patch(`${API_BASE_URL}/api/tipos-despesa/${td.id}/inativar`);
                          setSuccess('Tipo de despesa inativado com sucesso');
                          const list = await axios.get(`${API_BASE_URL}/api/tipos-despesa`);
                          setTiposDespesa(list.data);
                        } catch (err) {
                          setError(err.response?.data?.error || err.message);
                        }
                      }}>Inativar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!shouldFetch.tiposDespesa || tiposDespesa.length === 0) && <div style={{ marginTop: 8 }}>Tabela vazia. Use Buscar ou TODOS.</div>}
          </div>
        )}

        {/* Página: Contas a Pagar */}
        {view === 'contasPagar' && (
          <div className="card">
            <h3>💸 Contas a Pagar</h3>
            <p>Use "Analisar e Lançar" para criar novas contas a pagar.</p>
            <div className="form-inline">
              <button className="btn btn-primary" onClick={() => onTodos('contasPagar')}>TODOS</button>
            </div>
            <div className="list">
              {contasPagar.filter(c => shouldFetch.contasPagar).map(c => (
                <div key={c.id} className="list-item">
                  <div>
                    <strong>NF {c.numero_nota_fiscal}</strong> — Emissão: {c.data_emissao} — Valor: R$ {c.valor_total.toFixed ? c.valor_total.toFixed(2) : c.valor_total}
                    <br />Fornecedor: {c.fornecedor.razao_social} — CNPJ: {c.fornecedor.cnpj}
                    <br />Faturado: {c.faturado.nome_completo} — CPF: {c.faturado.cpf}
                  </div>
                  <button className="btn btn-secondary" onClick={async () => {
                    setError(''); setSuccess('');
                    try {
                      await axios.patch(`${API_BASE_URL}/api/contas-pagar/${c.id}/inativar`);
                      setSuccess('Conta a pagar inativada');
                      const list = await axios.get(`${API_BASE_URL}/api/contas-pagar`);
                      setContasPagar(list.data);
                    } catch (err) {
                      setError(err.response?.data?.error || err.message);
                    }
                  }}>Inativar</button>
                </div>
              ))}
              {(!shouldFetch.contasPagar || contasPagar.length === 0) && <div>Tabela vazia. Use TODOS.</div>}
            </div>
          </div>
        )}

        {/* Página: Contas a Receber */}
        {view === 'contasReceber' && (
          <div className="card">
            <h3>💰 Contas a Receber</h3>
            <div className="form-inline">
              <input placeholder="Número Documento" value={novaContaReceber.numero_documento} onChange={e => setNovaContaReceber({ ...novaContaReceber, numero_documento: e.target.value })} />
              <input type="date" placeholder="Data Emissão" value={novaContaReceber.data_emissao} onChange={e => setNovaContaReceber({ ...novaContaReceber, data_emissao: e.target.value })} />
              <input placeholder="Descrição" value={novaContaReceber.descricao} onChange={e => setNovaContaReceber({ ...novaContaReceber, descricao: e.target.value })} />
              <input type="number" step="0.01" placeholder="Valor Total" value={novaContaReceber.valor_total} onChange={e => setNovaContaReceber({ ...novaContaReceber, valor_total: e.target.value })} />
              <select value={novaContaReceber.cliente_id} onChange={e => setNovaContaReceber({ ...novaContaReceber, cliente_id: e.target.value })}>
                <option value="">Selecionar Cliente</option>
                {clientes.map(c => (
                  <option key={c.id} value={c.id}>{c.nome_completo} ({c.cpf || c.cnpj || 'ID ' + c.id})</option>
                ))}
              </select>
              <button className="btn btn-success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  const payload = { ...novaContaReceber, valor_total: Number(novaContaReceber.valor_total || 0), cliente_id: novaContaReceber.cliente_id ? Number(novaContaReceber.cliente_id) : undefined };
                  const res = await axios.post(`${API_BASE_URL}/api/contas-receber`, payload);
                  setSuccess(res.data.message || 'Conta a receber criada com sucesso');
                  setNovaContaReceber({ numero_documento: '', data_emissao: '', descricao: '', valor_total: '', cliente_id: '' });
                  if (shouldFetch.contasReceber) {
                    const list = await axios.get(`${API_BASE_URL}/api/contas-receber`);
                    setContasReceber(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <button className="btn btn-primary" onClick={() => onTodos('contasReceber')}>TODOS</button>
            </div>
            <div className="list">
              {contasReceber.filter(c => shouldFetch.contasReceber).map(c => (
                <div key={c.id} className="list-item">
                  <div>
                    <strong>Doc {c.numero_documento}</strong> — Emissão: {c.data_emissao} — Valor: R$ {c.valor_total}
                    <br />Cliente: {c.cliente?.nome_completo} — CPF/CNPJ: {c.cliente?.cpf || c.cliente?.cnpj}
                  </div>
                  <button className="btn btn-secondary" onClick={async () => {
                    setError(''); setSuccess('');
                    try {
                      await axios.patch(`${API_BASE_URL}/api/contas-receber/${c.id}/inativar`);
                      setSuccess('Conta a receber inativada');
                      const list = await axios.get(`${API_BASE_URL}/api/contas-receber`);
                      setContasReceber(list.data);
                    } catch (err) {
                      setError(err.response?.data?.error || err.message);
                    }
                  }}>Inativar</button>
                </div>
              ))}
              {(!shouldFetch.contasReceber || contasReceber.length === 0) && <div>Tabela vazia. Use TODOS.</div>}
            </div>
          </div>
        )}

        {view === 'clientes' && (
          <div className="card">
            <h3>👥 Manter Cliente</h3>
            <div className="form-inline">
              <input placeholder="Nome Completo" value={novoCliente.nome_completo} onChange={e => setNovoCliente({ ...novoCliente, nome_completo: e.target.value })} />
              <input placeholder="CPF" value={novoCliente.cpf} onChange={e => setNovoCliente({ ...novoCliente, cpf: e.target.value })} />
              <input placeholder="CNPJ" value={novoCliente.cnpj} onChange={e => setNovoCliente({ ...novoCliente, cnpj: e.target.value })} />
              <button className="btn btn.success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  const res = await axios.post(`${API_BASE_URL}/api/clientes`, novoCliente);
                  setSuccess(res.data.message || 'Cliente criado com sucesso');
                  setNovoCliente({ nome_completo: '', cpf: '', cnpj: '' });
                  if (shouldFetch.clientes) {
                    const list = await axios.get(`${API_BASE_URL}/api/clientes`);
                    setClientesList(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <input placeholder="Buscar por nome" value={search.clientes.nome} onChange={e => setSearch({ ...search, clientes: { ...search.clientes, nome: e.target.value } })} />
              <input placeholder="Buscar por CPF" value={search.clientes.cpf} onChange={e => setSearch({ ...search, clientes: { ...search.clientes, cpf: e.target.value } })} />
              <input placeholder="Buscar por CNPJ" value={search.clientes.cnpj} onChange={e => setSearch({ ...search, clientes: { ...search.clientes, cnpj: e.target.value } })} />
              <button className="btn btn-secondary" onClick={() => onBuscarClientes()}>Buscar</button>
              <button className="btn btn-primary" onClick={() => onTodos('clientes')}>TODOS</button>
            </div>
            <table style={{ width: '100%', marginTop: 12 }}>
              <thead>
                <tr>
                  <th onClick={() => setSort({ ...sort, clientes: { col: 'nome_completo', dir: sort.clientes.dir === 'asc' ? 'desc' : 'asc' } })}>Nome</th>
                  <th>CPF</th>
                  <th>CNPJ</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {clientesList.filter(c => shouldFetch.clientes).map(c => (
                  <tr key={c.id}>
                    <td>{editingCliente?.id === c.id ? (<input value={editingCliente.nome_completo} onChange={e=>setEditingCliente({...editingCliente, nome_completo: e.target.value})} />) : c.nome_completo}</td>
                    <td>{editingCliente?.id === c.id ? (<input value={editingCliente.cpf || ''} onChange={e=>setEditingCliente({...editingCliente, cpf: e.target.value})} />) : c.cpf}</td>
                    <td>{editingCliente?.id === c.id ? (<input value={editingCliente.cnpj || ''} onChange={e=>setEditingCliente({...editingCliente, cnpj: e.target.value})} />) : c.cnpj}</td>
                    <td>
                      {editingCliente?.id === c.id ? (
                        <button className="btn btn-success" onClick={async ()=>{
                          setError(''); setSuccess('');
                          try {
                            await axios.put(`${API_BASE_URL}/api/clientes/${c.id}`, editingCliente);
                            setSuccess('Cliente atualizado');
                            const list = await axios.get(`${API_BASE_URL}/api/clientes`);
                            setClientesList(list.data);
                            setEditingCliente(null);
                          } catch (err) {
                            setError(err.response?.data?.error || err.message);
                          }
                        }}>Salvar</button>
                      ) : (
                        <button className="btn btn-primary" onClick={()=>setEditingCliente({ id: c.id, nome_completo: c.nome_completo || '', cpf: c.cpf || '', cnpj: c.cnpj || '' })}>Editar</button>
                      )}
                      <button className="btn btn-secondary" onClick={async () => {
                        setError(''); setSuccess('');
                        try {
                          await axios.patch(`${API_BASE_URL}/api/clientes/${c.id}/inativar`);
                          setSuccess('Cliente inativado com sucesso');
                          const list = await axios.get(`${API_BASE_URL}/api/clientes`);
                          setClientesList(list.data);
                        } catch (err) {
                          setError(err.response?.data?.error || err.message);
                        }
                      }}>Inativar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!shouldFetch.clientes || clientesList.length === 0) && <div style={{ marginTop: 8 }}>Tabela vazia. Use Buscar ou TODOS.</div>}
          </div>
        )}

        {view === 'faturados' && (
          <div className="card">
            <h3>🧑‍💼 Manter Faturado</h3>
            <div className="form-inline">
              <input placeholder="Nome Completo" value={novoFaturado.nome_completo} onChange={e => setNovoFaturado({ ...novoFaturado, nome_completo: e.target.value })} />
              <input placeholder="CPF" value={novoFaturado.cpf} onChange={e => setNovoFaturado({ ...novoFaturado, cpf: e.target.value })} />
              <button className="btn btn-success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  if (!novoFaturado.cpf.trim()) {
                    setError('CPF é obrigatório');
                    return;
                  }
                  const res = await axios.post(`${API_BASE_URL}/api/faturados`, novoFaturado);
                  setSuccess(res.data.message || 'Faturado criado com sucesso');
                  setNovoFaturado({ nome_completo: '', cpf: '' });
                  if (shouldFetch.faturados) {
                    const list = await axios.get(`${API_BASE_URL}/api/faturados`);
                    setFaturadosList(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <button className="btn btn-primary" onClick={() => onTodos('faturados')}>TODOS</button>
            </div>
            <table style={{ width: '100%', marginTop: 12 }}>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>CPF</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {faturadosList.filter(f => shouldFetch.faturados).map(f => (
                  <tr key={f.id}>
                    <td>{f.nome_completo}</td>
                    <td>{f.cpf}</td>
                    <td>
                      <button className="btn btn-secondary" onClick={async () => {
                        setError(''); setSuccess('');
                        try {
                          await axios.patch(`${API_BASE_URL}/api/faturados/${f.id}/inativar`);
                          setSuccess('Faturado inativado com sucesso');
                          const list = await axios.get(`${API_BASE_URL}/api/faturados`);
                          setFaturadosList(list.data);
                        } catch (err) {
                          setError(err.response?.data?.error || err.message);
                        }
                      }}>Inativar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!shouldFetch.faturados || faturadosList.length === 0) && <div style={{ marginTop: 8 }}>Tabela vazia. Use TODOS.</div>}
          </div>
        )}

        {view === 'tiposReceita' && (
          <div className="card">
            <h3>📈 Manter Tipo de Receita</h3>
            <div className="form-inline">
              <input placeholder="Nome" value={novoTipoReceita.nome} onChange={e => setNovoTipoReceita({ ...novoTipoReceita, nome: e.target.value })} />
              <input placeholder="Descrição" value={novoTipoReceita.descricao} onChange={e => setNovoTipoReceita({ ...novoTipoReceita, descricao: e.target.value })} />
              <button className="btn btn.success" onClick={async () => {
                setError(''); setSuccess('');
                try {
                  const res = await axios.post(`${API_BASE_URL}/api/tipos-receita`, novoTipoReceita);
                  setSuccess(res.data.message || 'Tipo de receita criado com sucesso');
                  setNovoTipoReceita({ nome: '', descricao: '' });
                  if (shouldFetch.tiposReceita) {
                    const list = await axios.get(`${API_BASE_URL}/api/tipos-receita`);
                    setTiposReceita(list.data);
                  }
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="form-inline">
              <input placeholder="Buscar por nome" value={search.tiposReceita.nome} onChange={e => setSearch({ ...search, tiposReceita: { nome: e.target.value } })} />
              <button className="btn btn-secondary" onClick={() => onBuscarTiposReceita()}>Buscar</button>
              <button className="btn btn-primary" onClick={() => onTodos('tiposReceita')}>TODOS</button>
            </div>
            <table style={{ width: '100%', marginTop: 12 }}>
              <thead>
                <tr>
                  <th onClick={() => setSort({ ...sort, tiposReceita: { col: 'nome', dir: sort.tiposReceita.dir === 'asc' ? 'desc' : 'asc' } })}>Nome</th>
                  <th>Descrição</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {tiposReceita.filter(t => shouldFetch.tiposReceita).map(tr => (
                  <tr key={tr.id}>
                    <td>{editingTipoReceita?.id === tr.id ? (<input value={editingTipoReceita.nome} onChange={e=>setEditingTipoReceita({...editingTipoReceita, nome: e.target.value})} />) : tr.nome}</td>
                    <td>{editingTipoReceita?.id === tr.id ? (<input value={editingTipoReceita.descricao || ''} onChange={e=>setEditingTipoReceita({...editingTipoReceita, descricao: e.target.value})} />) : tr.descricao}</td>
                    <td>
                      {editingTipoReceita?.id === tr.id ? (
                        <button className="btn btn-success" onClick={async ()=>{
                          setError(''); setSuccess('');
                          try {
                            await axios.put(`${API_BASE_URL}/api/tipos-receita/${tr.id}`, editingTipoReceita);
                            setSuccess('Tipo de receita atualizado');
                            const list = await axios.get(`${API_BASE_URL}/api/tipos-receita`);
                            setTiposReceita(list.data);
                            setEditingTipoReceita(null);
                          } catch (err) {
                            setError(err.response?.data?.error || err.message);
                          }
                        }}>Salvar</button>
                      ) : (
                        <button className="btn btn-primary" onClick={()=>setEditingTipoReceita({ id: tr.id, nome: tr.nome || '', descricao: tr.descricao || '' })}>Editar</button>
                      )}
                      <button className="btn btn-secondary" onClick={async () => {
                        setError(''); setSuccess('');
                        try {
                          await axios.patch(`${API_BASE_URL}/api/tipos-receita/${tr.id}/inativar`);
                          setSuccess('Tipo de receita inativado com sucesso');
                          const list = await axios.get(`${API_BASE_URL}/api/tipos-receita`);
                          setTiposReceita(list.data);
                        } catch (err) {
                          setError(err.response?.data?.error || err.message);
                        }
                      }}>Inativar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!shouldFetch.tiposReceita || tiposReceita.length === 0) && <div style={{ marginTop: 8 }}>Tabela vazia. Use Buscar ou TODOS.</div>}
          </div>
        )}

        {/* Mensagens globais quando fora de extração/analisar */}
        {(view !== 'extracao') && (error && <div className="error">❌ {error}</div>)}
        {(view !== 'extracao') && (success && <div className="success">✅ {success}</div>)}
      </div>
    </div>
  );
}

export default App;
