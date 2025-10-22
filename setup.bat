@echo off
REM ==========================================================
REM Script de Setup e Instalação de Dependências (Windows/CMD)
REM Assume que você está na pasta raiz do projeto.
REM ==========================================================

echo [1/3] Criando Ambiente Virtual (venv)...
python -m venv venv

if exist venv\Scripts\activate.bat (
    echo Ambiente virtual criado com sucesso.
) else (
    echo ERRO: Falha ao criar o ambiente virtual ou o Python nao esta no PATH.
    pause
    exit /b 1
)

echo.
echo [2/3] Ativando e Instalando dependencias (pandas, requests, nltk)...
REM Tenta ativar o ambiente virtual para que o PIP instale os pacotes nele (Falhou no meu teste)
call .\venv\Scripts\activate

REM Instala as dependencias essenciais do coletor (Funciona)
pip install pandas requests tqdm
pip install nltk beautifulsoup4

echo.
echo [3/3] Instalacao concluida!
echo ==========================================================
echo O ambiente virtual (venv) foi configurado e as bibliotecas foram instaladas.
echo O ambiente VENV esta ATIVO (deve aparecer (venv) no prompt).
echo.

REM Depois que finalizar o setup
echo Agora inicie o ambiente venv com o comando abaixo:
echo .\venv\Scripts\activate
echo Depois execute:
echo python Coletor.py
echo.

REM Pressione ENTER para fechar a janela, mas o comando 'call' acima
REM deve manter o ambiente ativo na sessao atual do PowerShell/CMD se usado com 'call'
pause