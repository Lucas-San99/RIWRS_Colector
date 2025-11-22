# ==============================================================================
# src/GUI.py
# Interface Gráfica do Usuário.
# ==============================================================================
import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import font as tkfont
import sys
import os
import time
import webbrowser

# --- Configuração de Path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.SearchEngine import SearchEngine
    from logging import getLogger
    # Usaremos este logger para registrar as ações do usuário
    logger = getLogger('ColetorLogger') 
except ImportError as e:
    tk.messagebox.showerror("Erro Crítico", f"Não foi possível importar módulos.\nErro: {e}")
    sys.exit(1)

class PhishingSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Search Engine - RIWRS")
        self.root.geometry("900x700")
        self.root.configure(bg='white')

        # --- ESTADO DA PAGINAÇÃO ---
        self.pagina_atual = 1
        self.resultados_por_pagina = 10
        self.total_resultados = 0
        self.query_atual = ""
        # ---------------------------

        logger.info("--- [GUI STARTUP] Inicializando aplicação gráfica ---")
        # O construtor do SearchEngine já loga sua própria inicialização
        self.engine = SearchEngine()
        
        # Configuração de Fontes (sem alterações)
        self.title_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.result_font_title = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.result_font_url = tkfont.Font(family="Helvetica", size=10, underline=True)
        self.result_font_meta = tkfont.Font(family="Arial", size=9)
        self.pagination_font = tkfont.Font(family="Arial", size=10)

        # Construção dos Widgets (sem alterações)
        self._criar_cabecalho()
        self._criar_barra_busca()
        self._criar_area_resultados()
        self._criar_rodape_paginacao()

        # Handler de fechamento seguro (relembramos de adicionar)
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar_janela_handler)

    # ... (Os métodos _criar_cabecalho, _criar_barra_busca, _criar_area_resultados,
    def _criar_cabecalho(self):
        header_frame = tk.Frame(self.root, bg='white', pady=30)
        header_frame.pack()
        colors = ['#4285F4', '#EA4335', '#FBBC05', '#4285F4', '#34A853', '#EA4335', '#FBBC05', '#4285F4']
        chars = "Phishing"
        for char, color in zip(chars, colors):
             tk.Label(header_frame, text=char, font=self.title_font, fg=color, bg='white').pack(side=tk.LEFT)
        search_label = tk.Label(header_frame, text=" Search", font=("Helvetica", 16), fg='#5f6368', bg='white')
        search_label.pack(side=tk.LEFT, padx=10, pady=(15,0))

    def _criar_barra_busca(self):
        search_frame = tk.Frame(self.root, bg='white')
        search_frame.pack(pady=10, fill=tk.X, padx=100)
        self.query_entry = tk.Entry(search_frame, font=("Helvetica", 14), bd=2, relief=tk.RIDGE)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 10))
        self.query_entry.bind("<Return>", self.nova_busca_evento)
        search_btn = tk.Button(search_frame, text="Pesquisar Phishing", font=("Helvetica", 11), 
                               bg='#f8f9fa', fg='#3c4043', relief=tk.FLAT, padx=20, pady=5,
                               command=self.nova_busca_evento)
        search_btn.pack(side=tk.RIGHT)

    def _criar_area_resultados(self):
        results_frame = tk.Frame(self.root, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=(0, 10))
        self.results_display = scrolledtext.ScrolledText(results_frame, bg='white', fg='black', 
                                                         font=("Helvetica", 11), state='disabled', 
                                                         bd=0, wrap=tk.WORD, cursor="arrow")
        self.results_display.pack(fill=tk.BOTH, expand=True)
        self.results_display.tag_config('titulo', font=self.result_font_title, foreground='#1a0dab')
        self.results_display.tag_config('url', font=self.result_font_url, foreground='#006621')
        self.results_display.tag_bind('url', '<Enter>', lambda e: self.results_display.config(cursor="hand2"))
        self.results_display.tag_bind('url', '<Leave>', lambda e: self.results_display.config(cursor="arrow"))
        self.results_display.tag_config('meta', font=self.result_font_meta, foreground='#545454')
        self.results_display.tag_config('separator', spacing3=15)

    def _criar_rodape_paginacao(self):
        self.pagination_frame = tk.Frame(self.root, bg='white', pady=20)
        self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.btn_prev = tk.Button(self.pagination_frame, text="< Anterior", font=self.pagination_font,
                                  command=self.pagina_anterior, state='disabled', bg='#f8f9fa', relief=tk.FLAT)
        self.btn_prev.pack(side=tk.LEFT, padx=(50, 10))
        self.lbl_pagination = tk.Label(self.pagination_frame, text="", font=self.pagination_font, bg='white', fg='#70757a')
        self.lbl_pagination.pack(side=tk.LEFT, padx=10)
        self.btn_next = tk.Button(self.pagination_frame, text="Próximo >", font=self.pagination_font,
                                  command=self.proxima_pagina, state='disabled', bg='#f8f9fa', relief=tk.FLAT)
        self.btn_next.pack(side=tk.LEFT, padx=10)

    def abrir_url(self, event):
        index = self.results_display.index(f"@{event.x},{event.y}")
        tags = self.results_display.tag_names(index)
        for tag in tags:
            if tag.startswith('link-'):
                logger.info(f"[GUI ACTION] Usuário clicou no link: {tag[5:]}")
                webbrowser.open(tag[5:])
                break

    def nova_busca_evento(self, event=None):
        """Chamado quando o usuário faz uma NOVA pesquisa."""
        query = self.query_entry.get().strip()
        if not query: return
        
        # Registra o termo exato
        logger.info(f"--- [NEW SEARCH] Usuário submeteu nova busca: '{query}' ---")
        
        self.query_atual = query
        self.pagina_atual = 1
        self.executar_busca_paginada()

    def pagina_anterior(self):
        if self.pagina_atual > 1:
            nova_pagina = self.pagina_atual - 1
            # Registra a ação de paginação
            logger.info(f"[PAGINATION] Usuário clicou 'Anterior'. Movendo: Pág {self.pagina_atual} -> Pág {nova_pagina}")
            self.pagina_atual = nova_pagina
            self.executar_busca_paginada()

    def proxima_pagina(self):
        total_paginas = (self.total_resultados + self.resultados_por_pagina - 1) // self.resultados_por_pagina
        if self.pagina_atual < total_paginas:
            nova_pagina = self.pagina_atual + 1
            # Registra a ação de paginação
            logger.info(f"[PAGINATION] Usuário clicou 'Próximo'. Movendo: Pág {self.pagina_atual} -> Pág {nova_pagina}")
            self.pagina_atual = nova_pagina
            self.executar_busca_paginada()

    def executar_busca_paginada(self):
        """Executa a busca no backend e mede o tempo total da operação."""
        self.results_display.config(state='normal')
        self.results_display.delete('1.0', tk.END)
        self.results_display.insert(tk.END, "Carregando resultados...\n", 'meta')
        self.root.update()

        try:
            # Início da cronometragem da operação completa
            start_time = time.time()
            logger.info(f"[SEARCH OP] Iniciando requisição ao backend para '{self.query_atual}' (Página {self.pagina_atual})")
            
            resultados_pagina, total_resultados = self.engine.buscar(
                self.query_atual, 
                pagina=self.pagina_atual, 
                resultados_por_pagina=self.resultados_por_pagina
            )
            
            # Fim da cronometragem
            end_time = time.time()
            duration = end_time - start_time
            
            self.total_resultados = total_resultados
            self.results_display.delete('1.0', tk.END)

            if not resultados_pagina:
                 logger.info(f"[SEARCH OP] Finalizado. 0 resultados encontrados em {duration:.4f}s.")
                 self.results_display.insert(tk.END, f"Nenhum resultado encontrado para: '{self.query_atual}'\n", 'meta')
            else:
                 logger.info(f"[SEARCH OP] Finalizado. Total: {total_resultados} docs. Página atual exibida em {duration:.4f}s.")
                 
                 self.results_display.insert(tk.END, f"Cerca de {self.total_resultados} resultados ({duration:.2f} segundos).\n\n", 'meta')
                 
                 for i, (doc_id, score, url) in enumerate(resultados_pagina):
                     rank_global = ((self.pagina_atual - 1) * self.resultados_por_pagina) + (i + 1)
                     titulo_ficticio = f"Resultado de Phishing #{rank_global} relacionado a '{self.query_atual}'"
                     link_tag = f"link-{url}"
                     self.results_display.tag_bind(link_tag, '<Button-1>', self.abrir_url)
                     
                     self.results_display.insert(tk.END, f"{titulo_ficticio}\n", 'titulo')
                     self.results_display.insert(tk.END, f"{url}\n", ('url', link_tag))
                     self.results_display.insert(tk.END, f"Rank: {rank_global} | Score: {score:.4f} | DocID: {doc_id}\n", ('meta', 'separator'))
                 
            self.atualizar_controles_paginacao((self.total_resultados + self.resultados_por_pagina - 1) // self.resultados_por_pagina)

        except Exception as e:
             messagebox.showerror("Erro na Busca", f"Ocorreu um erro:\n{e}")
             logger.critical(f"[GUI ERROR] Erro crítico durante busca paginada: {e}")
        finally:
            self.results_display.config(state='disabled')

    def atualizar_controles_paginacao(self, total_paginas):
        if total_paginas <= 1:
            self.btn_prev.config(state='disabled')
            self.btn_next.config(state='disabled')
            self.lbl_pagination.config(text="")
            if total_paginas == 1:
                 self.lbl_pagination.config(text="Página 1 de 1")
        else:
            self.lbl_pagination.config(text=f"Página {self.pagina_atual} de {total_paginas}")
            if self.pagina_atual > 1:
                self.btn_prev.config(state='normal', cursor="hand2")
            else:
                self.btn_prev.config(state='disabled', cursor="arrow")
            if self.pagina_atual < total_paginas:
                self.btn_next.config(state='normal', cursor="hand2")
            else:
                self.btn_next.config(state='disabled', cursor="arrow")

    def ao_fechar_janela_handler(self):
        if messagebox.askokcancel("Sair", "Deseja fechar a busca e liberar a memória?"):
            logger.info("--- [GUI SHUTDOWN] Usuário fechou a aplicação ---")
            self.root.config(cursor="watch")
            self.root.update()
            if self.engine:
                self.engine.liberar_memoria_explicitamente()
                self.engine = None
            self.root.destroy()

# ... (Funções iniciar_gui) ...
def iniciar_gui():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_path, 'logs')
    missing_artifacts = []
    if not os.path.exists(os.path.join(logs_dir, 'indice_invertido.json')): missing_artifacts.append('indice_invertido.json')
    if not os.path.exists(os.path.join(logs_dir, 'document_map.json')): missing_artifacts.append('document_map.json')
    if not os.path.exists(os.path.join(logs_dir, 'idf.json')): missing_artifacts.append('idf.json')

    if missing_artifacts:
        erro_msg = f"Artefatos de indexação não encontrados: {', '.join(missing_artifacts)}.\nPor favor, execute as etapas anteriores primeiro."
        try: getLogger('ColetorLogger').critical(erro_msg)
        except: pass
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro de Inicialização", erro_msg)
        except: pass
        return
    root = tk.Tk()
    app = PhishingSearchGUI(root)
    root.mainloop()

if __name__ == '__main__':
    iniciar_gui()