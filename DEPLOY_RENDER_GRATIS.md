# 🆓 **DEPLOY GRATUITO NO RENDER.COM**

## 🎯 **PASSO A PASSO COMPLETO**

### **📋 O QUE VOCÊ TEM:**
- ✅ Conta GitHub: ARibeiroFIUS
- ✅ Git configurado
- ✅ Repositório local criado
- ✅ Arquivos commitados
- ✅ Aplicação funcionando

---

## **🚀 DEPLOY EM 5 MINUTOS:**

### **1️⃣ CRIAR REPOSITÓRIO NO GITHUB**

1. Acesse: https://github.com/ARibeiroFIUS
2. Clique **"New repository"** (botão verde)
3. Nome do repositório: `crawler-pdf-v2`
4. Descrição: `Crawler PDF - Busca clientes em PDFs`
5. ✅ **Public** (para usar Render gratuito)
6. **NÃO** marque "Add README"
7. Clique **"Create repository"**

### **2️⃣ CONECTAR SEU CÓDIGO AO GITHUB**

No seu terminal (já estamos na pasta certa):

```bash
cd crawler-pdf-v2
git remote add origin https://github.com/ARibeiroFIUS/crawler-pdf-v2.git
git branch -M main
git push -u origin main
```

### **3️⃣ FAZER DEPLOY NO RENDER**

1. **Acesse:** https://render.com
2. **Clique:** "Get Started for Free"
3. **Login:** Use sua conta GitHub (ARibeiroFIUS)
4. **Autorize:** Render a acessar seus repositórios
5. **Dashboard:** Clique "New +" → "Web Service"
6. **Conectar:** Selecione `crawler-pdf-v2`
7. **Configurar:**

```
Name: crawler-pdf-andre
Region: Oregon (US West)
Branch: main
Root Directory: (deixe vazio)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --host=0.0.0.0 --port=$PORT
```

8. **Plan:** Free (0$/mês)
9. **Deploy:** Clique "Create Web Service"

---

## **⚡ SEU LINK SERÁ:**
`https://crawler-pdf-andre.onrender.com`

---

## **🎯 VERIFICAÇÃO RÁPIDA:**

### **Status do Deploy:**
- 🟢 **Building:** Instalando dependências
- 🔵 **Live:** Aplicação online!
- 🔴 **Failed:** Erro (veja logs)

### **Teste Imediato:**
1. Abra o link da sua aplicação
2. Upload de arquivo Excel + PDF
3. ✅ Resultados aparecem!

---

## **💡 VANTAGENS RENDER GRATUITO:**

- ✅ **Totalmente gratuito**
- ✅ SSL automático (HTTPS)
- ✅ 500 horas/mês (suficiente!)
- ✅ Deploy automático (push = update)
- ✅ Logs em tempo real
- ✅ Domínio personalizado

---

## **🔧 COMANDOS PARA EXECUTAR:**

### **Push para GitHub:**
```bash
cd crawler-pdf-v2
git remote add origin https://github.com/ARibeiroFIUS/crawler-pdf-v2.git
git branch -M main
git push -u origin main
```

### **Futuras atualizações:**
```bash
git add .
git commit -m "Atualização do crawler"
git push
```
*(Deploy automático no Render!)*

---

## **📞 SUPPORT:**

### **Se der erro:**
1. **Logs:** Render Dashboard → Logs
2. **Rebuild:** Settings → Manual Deploy
3. **Restart:** Settings → Restart Service

### **Link da aplicação:**
Após deploy: `https://crawler-pdf-andre.onrender.com`

---

## **🎉 PRÓXIMOS PASSOS:**

1. ✅ Criar repositório GitHub
2. ✅ Push do código
3. ✅ Deploy no Render
4. ✅ Testar aplicação
5. ✅ Compartilhar link!

**Tempo estimado: 5-7 minutos** ⏱️ 