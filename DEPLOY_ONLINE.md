# 🌐 GUIA COMPLETO: COLOCAR CRAWLER PDF ONLINE

## 🚀 **OPÇÕES DE DEPLOY:**

### **1. 🟢 HEROKU (Gratuito/Pago) - MAIS FÁCIL**

#### **Pré-requisitos:**
- Conta no [Heroku](https://heroku.com)
- [Git](https://git-scm.com/) instalado
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) instalado

#### **Passos:**

```bash
# 1. Fazer login no Heroku
heroku login

# 2. Criar aplicação
heroku create crawler-pdf-seu-nome

# 3. Inicializar Git (se necessário)
git init
git add .
git commit -m "Deploy inicial do Crawler PDF"

# 4. Fazer deploy
git push heroku main

# 5. Abrir aplicação
heroku open
```

#### **URL Final:**
`https://crawler-pdf-seu-nome.herokuapp.com`

---

### **2. 🔵 RAILWAY (Gratuito/Pago) - MUITO FÁCIL**

#### **Passos:**
1. Acesse [Railway](https://railway.app)
2. Conecte sua conta GitHub
3. Clique "Deploy from GitHub repo"
4. Selecione este repositório
5. ✅ Deploy automático!

#### **Vantagens:**
- Deploy automático via GitHub
- SSL gratuito
- Fácil escalabilidade

---

### **3. 🟠 RENDER (Gratuito/Pago) - SIMPLES**

#### **Passos:**
1. Acesse [Render](https://render.com)
2. Conecte GitHub
3. "New Web Service"
4. Selecione repositório
5. Configurações:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: `Python 3`

---

### **4. 🟡 VERCEL (Gratuito) - RÁPIDO**

Precisa criar `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

#### **Deploy:**
```bash
npm i -g vercel
vercel
```

---

### **5. 🔴 DIGITALOCEAN APP PLATFORM**

1. Acesse [DigitalOcean](https://digitalocean.com)
2. "Create App"
3. Conecte GitHub
4. Selecione repositório
5. ✅ Deploy automático!

---

## 📁 **ARQUIVOS NECESSÁRIOS (JÁ CRIADOS):**

### **✅ `app.py`** - Aplicação web otimizada
- Versão simplificada para servidores
- Interface responsiva
- Debug integrado

### **✅ `requirements.txt`** - Dependências
```
Flask==3.0.0
pandas==2.1.4
PyPDF2==3.0.1
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0
openpyxl==3.1.2
gunicorn==21.2.0
```

### **✅ `Procfile`** - Para Heroku
```
web: gunicorn app:app
```

### **✅ `runtime.txt`** - Versão Python
```
python-3.11.7
```

---

## 🛠️ **CONFIGURAÇÃO AVANÇADA:**

### **Variáveis de Ambiente:**
```bash
# Para produção
export FLASK_ENV=production
export SECRET_KEY=sua_chave_secreta_aqui
```

### **Para HTTPS (SSL):**
Todos os serviços mencionados incluem SSL gratuito automaticamente.

### **Limites de Arquivo:**
```python
# Em app.py, adicionar:
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

---

## 🎯 **RECOMENDAÇÃO PARA INICIANTES:**

### **🥇 1º LUGAR: RAILWAY**
- ✅ Mais fácil (conecta GitHub automaticamente)
- ✅ SSL gratuito
- ✅ Deploy automático
- ✅ Interface amigável

### **🥈 2º LUGAR: RENDER**
- ✅ Gratuito com boa performance
- ✅ SSL incluído
- ✅ Fácil configuração

### **🥉 3º LUGAR: HEROKU**
- ✅ Muito conhecido
- ✅ Boa documentação
- ⚠️ Gratuito limitado

---

## 🚀 **DEPLOY RÁPIDO (RAILWAY):**

1. **Fazer push para GitHub:**
```bash
git init
git add .
git commit -m "Crawler PDF para deploy"
git branch -M main
git remote add origin https://github.com/seu-usuario/crawler-pdf.git
git push -u origin main
```

2. **Acessar [Railway](https://railway.app)**

3. **"Deploy from GitHub repo"**

4. **Selecionar repositório**

5. **✅ PRONTO! URL disponível em 2-3 minutos**

---

## 🔧 **SOLUÇÃO DE PROBLEMAS:**

### **Erro de memória:**
- Aumentar plano do serviço
- Otimizar processamento de PDFs grandes

### **Timeout:**
- Implementar processamento assíncrono
- Usar worker queues (Celery + Redis)

### **Arquivos grandes:**
- Configurar upload limits
- Usar storage externo (AWS S3)

---

## 📱 **FUNCIONALIDADES DA VERSÃO ONLINE:**

✅ **Interface responsiva** (mobile-friendly)  
✅ **Upload de arquivos** Excel e PDF  
✅ **Processamento em tempo real** com barra de progresso  
✅ **Download de resultados** automático  
✅ **Algoritmos de busca avançados** (5 tipos)  
✅ **Debug detalhado** nos logs do servidor  
✅ **Tolerância ajustável** (50-100%)  
✅ **Relatórios completos** com estatísticas  

---

## 🎉 **PRÓXIMOS PASSOS:**

1. **Escolha uma plataforma** (recomendo Railway)
2. **Faça o deploy** seguindo os passos
3. **Teste com seus arquivos** reais
4. **Compartilhe a URL** com sua equipe

**Sua aplicação estará online e acessível de qualquer lugar do mundo!** 🌍 