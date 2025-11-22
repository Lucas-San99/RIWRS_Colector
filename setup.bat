@echo off
REM =================================================================
REM Script de Setup, Instalação e Atualização de Dependências (Windows)
REM =================================================================
REM Este script automatiza as seguintes tarefas:
REM 1. Cria um ambiente virtual chamado 'venv' (se não existir).
REM 2. Ativa o ambiente virtual.
REM 3. Atualiza o 'pip' para a versão mais recente.
REM 4. Instala ou atualiza todas as bibliotecas Python necessárias.
REM 5. Baixa os dados linguísticos necessários para o NLTK.
REM 6. Executa a migração do índice para o formato otimizado (RAM/SSD), se necessário.
REM =================================================================

REM --- PASSO 1 ---
echo [1/6] Criando Ambiente Virtual (venv)...
if exist venv\ goto :VenvExists
python -m venv venv
if not exist venv\Scripts\activate.bat goto :VenvError
echo Ambiente virtual 'venv' criado com sucesso.
goto :Step2

:VenvExists
echo Ambiente virtual 'venv' ja existe. Pulando criacao.
goto :Step2

:VenvError
echo.
echo ==============================================================
echo ERRO CRITICO: Falha ao criar o ambiente virtual.
echo Verifique se o Python esta instalado e adicionado ao PATH do sistema.
echo ==============================================================
pause
exit /b 1

REM --- PASSO 2 ---
:Step2
echo.
echo [2/6] Ativando ambiente virtual...
call .\venv\Scripts\activate

REM --- PASSO 3 ---
echo.
echo [3/6] Atualizando PIP para a versao mais recente...
python.exe -m pip install --upgrade pip

REM --- PASSO 4 ---
echo.
echo [4/6] Instalando e/ou atualizando dependencias do projeto...
REM Instala todas as dependencias e força a atualização (--upgrade)
pip install --upgrade pandas requests tqdm beautifulsoup4 nltk ijson tk

REM --- PASSO 5 ---
echo.
echo [5/6] Baixando dados linguisticos do NLTK (stopwords, etc.)...
python -m nltk.downloader -q stopwords punkt

REM --- PASSO 6 ---
echo.
echo [6/6] Verificando necessidade de migracao de indice (Otimizacao RAM/SSD)...

REM Checagem 1: Se o arquivo fonte NÃO existe, pula tudo.
if not exist "logs\indice_invertido.json" goto :SkipMigrationSourceMissing

REM Checagem 2: Se o arquivo destino JÁ existe, não precisa fazer de novo.
if exist "logs\postings.bin" goto :SkipMigrationAlreadyDone

REM Se chegou aqui: Fonte existe E destino não existe. Executa migração.
echo Arquivo de indice monolitico encontrado.
echo Iniciando migracao automatica para formato otimizado (Isso pode demorar)...
echo.
python tools/MigrarIndice.py
goto :MigrationEnd

:SkipMigrationAlreadyDone
echo O indice ja esta migrado e otimizado para SSD. Pulando etapa.
goto :MigrationEnd

:SkipMigrationSourceMissing
echo AVISO: 'logs\indice_invertido.json' nao encontrado.
echo Se esta for uma instalacao limpa, voce precisara rodar a COLETA e INDEXACAO primeiro via Coletor.py.
echo A migracao automatica foi pulada.
goto :MigrationEnd

:MigrationEnd
REM --- FIM ---
echo.
echo ==========================================================
echo INSTALACAO CONCLUIDA COM SUCESSO!
echo ==========================================================
echo O ambiente virtual 'venv' foi configurado, as bibliotecas foram atualizadas,
echo o NLTK foi configurado e o indice foi verificado.
echo.
echo PARA USAR O AMBIENTE, execute o seguinte comando no seu terminal:
echo   .\venv\Scripts\activate
echo.
echo Depois, voce pode rodar o programa principal (Menu):
echo   python Coletor.py
echo.
echo Para iniciar diretamente a interface grafica de busca (GUI):
echo   python Coletor.py --etapa gui
echo.
echo Para mais informacoes, leia o arquivo README.md
echo.

pause