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

  // Formulários de criação
  const [novoFornecedor, setNovoFornecedor] = useState({ razao_social: '', fantasia: '', cnpj: '' });
  const [novoTipoDespesa, setNovoTipoDespesa] = useState({ nome: '', descricao: '' });
  const [novaContaReceber, setNovaContaReceber] = useState({ numero_documento: '', data_emissao: '', descricao: '', valor_total: '', cliente_id: '' });
  const [clientes, setClientes] = useState([]);

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

    if (view === 'fornecedores') fetchFornecedores();
    if (view === 'tiposDespesa') fetchTiposDespesa();
    if (view === 'contasPagar') fetchContasPagar();
    if (view === 'contasReceber') { fetchContasReceber(); fetchClientes(); }
  }, [view]);

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
      await axios.post(`${API_BASE_URL}/api/save-invoice`, extractedData);
      setSuccess('Dados salvos no banco de dados com sucesso!');
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
                  const list = await axios.get(`${API_BASE_URL}/api/fornecedores`);
                  setFornecedores(list.data);
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="list">
              {fornecedores.map(f => (
                <div key={f.id} className="list-item">
                  <div>
                    <strong>{f.razao_social}</strong> — CNPJ: {f.cnpj}
                  </div>
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
                </div>
              ))}
              {fornecedores.length === 0 && <div>Nenhum fornecedor ativo.</div>}
            </div>
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
                  const list = await axios.get(`${API_BASE_URL}/api/tipos-despesa`);
                  setTiposDespesa(list.data);
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="list">
              {tiposDespesa.map(td => (
                <div key={td.id} className="list-item">
                  <div>
                    <strong>{td.nome}</strong> — {td.descricao}
                  </div>
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
                </div>
              ))}
              {tiposDespesa.length === 0 && <div>Nenhum tipo de despesa ativo.</div>}
            </div>
          </div>
        )}

        {/* Página: Contas a Pagar */}
        {view === 'contasPagar' && (
          <div className="card">
            <h3>💸 Contas a Pagar</h3>
            <p>Use "Analisar e Lançar" para criar novas contas a pagar.</p>
            <div className="list">
              {contasPagar.map(c => (
                <div key={c.id} className="list-item">
                  <div>
                    <strong>NF {c.numero_nota_fiscal}</strong> — Emissão: {c.data_emissao} — Valor: R$ {c.valor_total.toFixed ? c.valor_total.toFixed(2) : c.valor_total}
                    <br />Fornecedor: {c.fornecedor.razao_social} — CNPJ: {c.fornecedor.cnpj}
                    <br />Faturado: {c.faturado.nome_completo} — CPF: {c.faturado.cpf}
                  </div>
                </div>
              ))}
              {contasPagar.length === 0 && <div>Nenhuma conta a pagar ativa.</div>}
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
                  const list = await axios.get(`${API_BASE_URL}/api/contas-receber`);
                  setContasReceber(list.data);
                } catch (err) {
                  setError(err.response?.data?.error || err.message);
                }
              }}>➕ Criar</button>
            </div>
            <div className="list">
              {contasReceber.map(c => (
                <div key={c.id} className="list-item">
                  <div>
                    <strong>Doc {c.numero_documento}</strong> — Emissão: {c.data_emissao} — Valor: R$ {c.valor_total}
                    <br />Cliente: {c.cliente?.nome_completo} — CPF/CNPJ: {c.cliente?.cpf || c.cliente?.cnpj}
                  </div>
                </div>
              ))}
              {contasReceber.length === 0 && <div>Nenhuma conta a receber ativa.</div>}
            </div>
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