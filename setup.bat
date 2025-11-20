@echo off
REM =================================================================
REM Script de Setup, Instalação e Atualização de Dependências (Windows)
REM =================================================================
REM Este script automatiza as seguintes tarefas:
REM 1. Cria um ambiente virtual chamado 'venv' (se não existir).
REM 2. Ativa o ambiente virtual.
REM 3. Atualiza o 'pip' para a versão mais recente.
REM 4. Instala ou atualiza todas as bibliotecas Python necessárias.
REM =================================================================

echo [1/4] Criando Ambiente Virtual (venv)...
if not exist venv\ (
    python -m venv venv
    if exist venv\Scripts\activate.bat (
        echo Ambiente virtual 'venv' criado com sucesso.
    ) else (
        echo ERRO: Falha ao criar o ambiente virtual. Verifique se o Python esta no PATH.
        pause
        exit /b 1
    )
) else (
    echo Ambiente virtual 'venv' ja existe. Pulando criacao.
)

echo.

echo [2/4] Ativando ambiente virtual...
call .\venv\Scripts\activate

echo.

echo [3/4] Atualizando PIP para a versao mais recente...
python.exe -m pip install --upgrade pip

echo.

echo [4/4] Instalando e/ou atualizando dependencias do projeto...
REM Instala todas as dependencias de uma vez e força a atualização (--upgrade)
pip install --upgrade pandas requests tqdm beautifulsoup4 nltk ijson

echo.
echo ==========================================================
echo INSTALACAO CONCLUIDA!
echo ==========================================================
echo O ambiente virtual 'venv' foi configurado e as bibliotecas foram atualizadas.
echo.
echo PARA USAR O AMBIENTE, execute o seguinte comando no seu terminal:
echo   .\venv\Scripts\activate
echo.
echo Depois, voce pode rodar o programa principal:
echo   python Coletor.py
echo.
echo Para usar a interface de busca (CLI):
echo   python Coletor.py --etapa busca
echo.
echo Para mais informacoes, abra o arquivo README.md
echo.

pause