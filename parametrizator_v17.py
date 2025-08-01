import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip  # pip install pyperclip

utm_config = {
    "utm_source": {
        "descritivo": "Canal Veiculado",
        "opcoes": [
            "app_unificado", "app_residencial", "site_minhas", "dma",
            "cautivo", "totem"
        ],
        "filhos": {
            "totem": ["estado", "cidade", "loja"]
        },
        "valores_filhos": {
            "estado": ["sp", "rj", "mg"],
            "cidade": {
                "sp": ["sao_paulo", "ribeirao_preto", "campinas"],
                "rj": ["rio_de_janeiro", "volta_redonda"],
                "mg": ["belo_horizonte", "3_coracoes", "adamantina"]
            },
            "loja": {
                "sao_paulo": ["loja1_sp", "loja2_sp", "loja3_sp"],
                "ribeirao_preto": ["loja1_rp", "loja2_rp", "loja3_rp"],
                "campinas": ["loja1_cp", "loja2_cp", "loja3_cp"],
                "rio_de_janeiro": ["loja1_rj", "loja2_rj", "loja3_rj"],
                "volta_redonda": ["loja1_vr", "loja2_vr", "loja3_vr"],
                "belo_horizonte": ["loja1_bh", "loja2_bh", "loja3_bh"],
                "3_coracoes": ["loja1_tc", "loja2_tc", "loja3_tc"],
                "adamantina": ["loja1_ad", "loja2_ad", "loja3_ad"]
            }
        }
    },
    "utm_medium": {
        "descritivo": "Informações da ferramenta, formato e bloco",
        "blocos": [
            {"nome": "Ferramenta", "opcoes": ["gam", "hardcode", "gerenciador", "pzn", "admintotem"], "obrigatorio": True},
            {"nome": "Formato", "opcoes": ["banner_hc", "deck_de_vendas", "fsc", "hub", "bnn", "psh", "card_web", "codeless"], "obrigatorio": True},
            {"nome": "Bloco/Posição", "opcoes": [
                "tp", "md", "ft", "direita_codeless", "esquerda_codeless",
                "cima_codeless", "baixo_codeless", "firsc_screen_codeless"], "obrigatorio": True}
        ],
        # Regras hierárquicas para utm_medium
        "regras_hierarquicas": {
            "gam": {
                "banner_hc": ["tp", "md", "ft"],
                "codeless": ["direita_codeless", "esquerda_codeless", "cima_codeless", "baixo_codeless", "firsc_screen_codeless"]
            },
            "hardcode": {
                "banner_hc": ["tp", "md", "ft"]
            },
            "gerenciador": {
                "banner_hc": ["tp", "md", "ft"],
                "fsc": []  # Lista vazia significa "cancelar opção do bloco/posição"
            },
            "pzn": {
                "fsc": [],
                "hub": [],
                "bnn": [],
                "psh": [],
                "card_web": []
            },
            "admintotem": {
                # Sem formatos - cancela formato e bloco/posição
            }
        }
    },
    "utm_campaign": {
        "descritivo": "Informações da campanha",
        "blocos": [
            {"nome": "frente_", "opcoes": [
                "pacote_de_dados", "migracao_pre_controle", "migracao_controle_conta",
                "movimentacao_conta_upgrade", "movimentacao_controle_upgrade",
                "banda_larga", "aparelhos", "acessorios", "flex", "outros",
                "claro_box", "skeelo", "conect_car"], "obrigatorio": True},
            {"nome": "produto/serviço", "placeholder": "Digite o produto/serviço", "obrigatorio": True},
            {"nome": "versão", "placeholder": "Digite a versão"}
        ]
    },
    "utm_term": {
        "descritivo": "Segmentação por jornada e posse",
        "blocos": [
            {"nome": "Posse/Jornada", "opcoes": [
                "pre", "pos", "controle_facil", "controle_tradicional",
                "residencial", "combo_multi", "fatura_facil", "acesso_rapido",
                "fale_com_a_claro_movel", "consulta_internet"], "obrigatorio": True},
            {"nome": "Logado", "opcoes": ["logado", "nao_logado"], "obrigatorio": True}
        ]
    }
}

class ParametrizatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Parametrizator UTM - Gerador de Campanhas")
        master.geometry("900x750")
        master.configure(bg="#f0f0f0")
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.widgets = {}
        self.dynamic_widgets = {}
        self.all_widgets = {}
        self.pzn_note_label = None
        self.campaign_pzn_note = None
        
        # Variáveis para controle do valor
        self.tem_valor = tk.BooleanVar()
        self.valor_frame = None
        self.valor_reais_widget = None
        self.valor_centavos_widget = None
        self.valor_question_frame = None
        
        self.create_interface()
        self.bind_events()
    
    def create_interface(self):
        # Frame principal com scroll
        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(main_frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        title_label = tk.Label(
            self.scrollable_frame, 
            text="🎯 Gerador de Parâmetros UTM", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        # Criar seções
        self.create_utm_sections()
        
        # Botões de ação
        self.create_action_buttons()
        
        # Área de resultado
        self.create_result_area()
        
        # Bind scroll do mouse
        self.bind_mousewheel()
    
    def create_utm_sections(self):
        for utm_key, utm_info in utm_config.items():
            # Frame da seção
            section_frame = tk.LabelFrame(
                self.scrollable_frame,
                text=f"{utm_key.upper()} - {utm_info['descritivo']}",
                font=("Arial", 12, "bold"),
                bg="#ffffff",
                fg="#34495e",
                padx=15,
                pady=10
            )
            section_frame.pack(fill="x", pady=(0, 15), padx=5)
            
            self.widgets[utm_key] = {}
            
            if "opcoes" in utm_info:
                self.create_main_selection(section_frame, utm_key, utm_info)
            
            if "blocos" in utm_info:
                if utm_key == "utm_campaign":
                    self.create_campaign_section(section_frame, utm_key, utm_info)
                else:
                    self.create_blocks_section(section_frame, utm_key, utm_info)
    
    def create_main_selection(self, parent, utm_key, utm_info):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(fill="x", pady=5)
        
        # utm_source é sempre obrigatório
        obrigatorio_text = " *" if utm_key == "utm_source" else ""
        
        label = tk.Label(
            frame, 
            text=f"Selecione uma opção{obrigatorio_text}:", 
            font=("Arial", 10),
            bg="#ffffff"
        )
        label.pack(anchor="w")
        
        combo = ttk.Combobox(
            frame, 
            values=utm_info["opcoes"],
            state="readonly",
            width=30
        )
        combo.pack(anchor="w", pady=(5, 0))
        combo.set("-- Selecione --")
        
        self.widgets[utm_key]["main"] = combo
        
        # Guardar referência para controle geral
        self.all_widgets[f"{utm_key}_main"] = {
            'widget': combo,
            'type': 'combobox',
            'default': "-- Selecione --",
            'obrigatorio': utm_key == "utm_source"
        }
        
        # Frame para widgets dinâmicos (filhos)
        if "filhos" in utm_info:
            dynamic_frame = tk.Frame(parent, bg="#ffffff")
            dynamic_frame.pack(fill="x", pady=10)
            self.dynamic_widgets[utm_key] = dynamic_frame
    
    def create_campaign_section(self, parent, utm_key, utm_info):
        """Cria seção especial para utm_campaign com lógica de valor condicional"""
        blocks_frame = tk.Frame(parent, bg="#ffffff")
        blocks_frame.pack(fill="x", pady=5)
        
        # Processar campos em ordem específica para garantir que o valor apareça no lugar certo
        for i, bloco in enumerate(utm_info["blocos"]):
            # Criar campo normal
            self.create_campaign_field(blocks_frame, utm_key, bloco)
            
            # Depois do campo "produto/serviço", adicionar pergunta sobre valor
            if bloco["nome"] == "produto/serviço":
                self.create_valor_question(blocks_frame, utm_key)
                # Os campos de valor serão inseridos aqui quando ativados
    
    def create_campaign_field(self, parent, utm_key, bloco):
        """Cria um campo individual da campanha"""
        row_frame = tk.Frame(parent, bg="#ffffff")
        row_frame.pack(fill="x", pady=5)
        
        # Label com indicação de obrigatório
        nome_display = bloco["nome"].replace("_", " ").title()
        obrigatorio_text = " *" if bloco.get("obrigatorio", False) else ""
        
        label = tk.Label(
            row_frame,
            text=f"{nome_display}{obrigatorio_text}:",
            font=("Arial", 10),
            bg="#ffffff",
            width=20,
            anchor="w"
        )
        label.pack(side="left", padx=(0, 10))
        
        # Widget (Combobox ou Entry)
        if "opcoes" in bloco:
            widget = ttk.Combobox(
                row_frame,
                values=bloco["opcoes"],
                state="readonly",
                width=25
            )
            widget.set("-- Selecione --")
            
            self.all_widgets[f"{utm_key}_{bloco['nome']}"] = {
                'widget': widget,
                'type': 'combobox',
                'default': "-- Selecione --",
                'obrigatorio': bloco.get("obrigatorio", False)
            }
                
        else:
            widget = tk.Entry(row_frame, width=30)
            placeholder = ""
            if "placeholder" in bloco:
                placeholder = bloco["placeholder"]
                widget.insert(0, placeholder)
                widget.bind("<FocusIn>", lambda e, w=widget, p=placeholder: self.clear_placeholder(w, p))
                widget.bind("<FocusOut>", lambda e, w=widget, p=placeholder: self.restore_placeholder(w, p))
                widget.config(fg="gray")
            
            self.all_widgets[f"{utm_key}_{bloco['nome']}"] = {
                'widget': widget,
                'type': 'entry',
                'placeholder': placeholder,
                'obrigatorio': bloco.get("obrigatorio", False)
            }
        
        widget.pack(side="left")
        self.widgets[utm_key][bloco["nome"]] = widget
    
    def create_valor_question(self, parent, utm_key):
        """Cria a pergunta sobre valor e campos condicionais"""
        # Frame simples para a pergunta (igual aos outros campos)
        question_frame = tk.Frame(parent, bg="#ffffff")
        question_frame.pack(fill="x", pady=5)
        
        # Label igual aos outros campos
        question_label = tk.Label(
            question_frame,
            text="Possui Valor *:",
            font=("Arial", 10),
            bg="#ffffff",
            width=20,
            anchor="w"
        )
        question_label.pack(side="left", padx=(0, 10))
        
        # Checkbox simples
        valor_checkbox = tk.Checkbutton(
            question_frame,
            text="✅ Sim, possui valor",
            variable=self.tem_valor,
            command=self.toggle_valor_fields,
            bg="#ffffff",
            font=("Arial", 10),
            fg="#000000"
        )
        valor_checkbox.pack(side="left")
        
        # Selecionar "Não" por padrão
        self.tem_valor.set(False)
        
        # Frame para campos de valor (logo após a pergunta, ANTES de continuar os outros campos)
        self.valor_frame = tk.Frame(parent, bg="#ffffff")
        # NÃO fazer pack agora - será feito em toggle_valor_fields quando necessário
        
        # Criar campos de valor
        self.create_valor_fields()
    
    def create_valor_fields(self):
        """Cria os campos de reais e centavos"""
        if not self.valor_frame:
            return
        
        # Label principal
        valor_label = tk.Label(
            self.valor_frame,
            text="Valor *:",
            font=("Arial", 10),
            bg="#ffffff",
            width=20,
            anchor="w"
        )
        valor_label.pack(side="left", padx=(0, 10))
        
        # Frame para os campos de valor
        campos_frame = tk.Frame(self.valor_frame, bg="#ffffff")
        campos_frame.pack(side="left")
        
        # Label R$
        rs_label = tk.Label(
            campos_frame,
            text="R$",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#27ae60"
        )
        rs_label.pack(side="left", padx=(0, 5))
        
        # Campo reais
        self.valor_reais_widget = tk.Entry(campos_frame, width=8, font=("Arial", 10))
        self.valor_reais_widget.pack(side="left")
        self.valor_reais_widget.bind("<KeyPress>", lambda e: self.validate_numeric_input(e))
        
        # Vírgula visual
        virgula_label = tk.Label(
            campos_frame,
            text=",",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#27ae60"
        )
        virgula_label.pack(side="left", padx=2)
        
        # Campo centavos
        self.valor_centavos_widget = tk.Entry(campos_frame, width=4, font=("Arial", 10))
        self.valor_centavos_widget.pack(side="left")
        self.valor_centavos_widget.bind("<KeyPress>", lambda e: self.validate_numeric_input(e, max_length=2))
        
        # Placeholder nos campos
        self.valor_reais_widget.insert(0, "99")
        self.valor_reais_widget.config(fg="gray")
        self.valor_reais_widget.bind("<FocusIn>", lambda e: self.clear_valor_placeholder(self.valor_reais_widget, "99"))
        self.valor_reais_widget.bind("<FocusOut>", lambda e: self.restore_valor_placeholder(self.valor_reais_widget, "99"))
        
        self.valor_centavos_widget.insert(0, "99")
        self.valor_centavos_widget.config(fg="gray")
        self.valor_centavos_widget.bind("<FocusIn>", lambda e: self.clear_valor_placeholder(self.valor_centavos_widget, "99"))
        self.valor_centavos_widget.bind("<FocusOut>", lambda e: self.restore_valor_placeholder(self.valor_centavos_widget, "99"))
        
        # Registrar nos widgets de controle
        self.all_widgets["utm_campaign_valor_reais"] = {
            'widget': self.valor_reais_widget,
            'type': 'entry',
            'placeholder': "99",
            'obrigatorio': False  # Será validado manualmente quando visível
        }
        
        self.all_widgets["utm_campaign_valor_centavos"] = {
            'widget': self.valor_centavos_widget,
            'type': 'entry',
            'placeholder': "99",
            'obrigatorio': False  # Será validado manualmente quando visível
        }
    
    def validate_numeric_input(self, event, max_length=None):
        """Valida entrada numérica"""
        char = event.char
        if char.isdigit():
            # Verificar limite de caracteres
            if max_length and len(event.widget.get()) >= max_length:
                return "break"
            return True
        elif char in ['\b', '\x7f']:  # Backspace, Delete
            return True
        else:
            return "break"
    
    def clear_valor_placeholder(self, widget, placeholder):
        """Limpa placeholder dos campos de valor"""
        current_value = widget.get()
        if current_value == placeholder or widget.cget("fg") == "gray":
            widget.delete(0, tk.END)
            widget.config(fg="black")
    
    def restore_valor_placeholder(self, widget, placeholder):
        """Restaura placeholder dos campos de valor"""
        current_value = widget.get().strip()
        if not current_value:
            widget.insert(0, placeholder)
            widget.config(fg="gray")
    
    def toggle_valor_fields(self):
        """Mostra/oculta campos de valor baseado na seleção"""
        if self.tem_valor.get():
            # Posicionar o frame de valor logo após o checkbox
            checkbox_frame = self.valor_frame.master
            widgets_list = checkbox_frame.pack_slaves()
            
            # Encontrar a posição do checkbox para inserir o valor logo após
            for i, widget in enumerate(widgets_list):
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Checkbutton):
                            # Inserir após este frame
                            self.valor_frame.pack(fill="x", pady=5, after=widget)
                            return
            
            # Fallback: mostrar no final se não encontrar posição específica
            self.valor_frame.pack(fill="x", pady=5)
        else:
            self.valor_frame.pack_forget()
    
    def create_blocks_section(self, parent, utm_key, utm_info):
        blocks_frame = tk.Frame(parent, bg="#ffffff")
        blocks_frame.pack(fill="x", pady=5)
        
        for i, bloco in enumerate(utm_info["blocos"]):
            row_frame = tk.Frame(blocks_frame, bg="#ffffff")
            row_frame.pack(fill="x", pady=5)
            
            # Label com indicação de obrigatório
            nome_display = bloco["nome"].replace("_", " ").title()
            obrigatorio_text = " *" if bloco.get("obrigatorio", False) else ""
            
            label = tk.Label(
                row_frame,
                text=f"{nome_display}{obrigatorio_text}:",
                font=("Arial", 10),
                bg="#ffffff",
                width=20,
                anchor="w",
                fg="#d32f2f" if obrigatorio_text else "#000000"
            )
            label.pack(side="left", padx=(0, 10))
            
            # Widget (Combobox ou Entry)
            if "opcoes" in bloco:
                widget = ttk.Combobox(
                    row_frame,
                    values=bloco["opcoes"],
                    state="readonly",
                    width=25
                )
                widget.set("-- Selecione --")
                
                # Bind especial para campos hierárquicos do utm_medium
                if utm_key == "utm_medium":
                    if bloco["nome"] == "Ferramenta":
                        widget.bind("<<ComboboxSelected>>", self.handle_ferramenta_selection)
                    elif bloco["nome"] == "Formato":
                        widget.bind("<<ComboboxSelected>>", self.handle_formato_selection)
                
                self.all_widgets[f"{utm_key}_{bloco['nome']}"] = {
                    'widget': widget,
                    'type': 'combobox',
                    'default': "-- Selecione --",
                    'obrigatorio': bloco.get("obrigatorio", False)
                }
                    
            else:
                widget = tk.Entry(row_frame, width=30)
                placeholder = ""
                if "placeholder" in bloco:
                    placeholder = bloco["placeholder"]
                    widget.insert(0, placeholder)
                    widget.bind("<FocusIn>", lambda e, w=widget, p=placeholder: self.clear_placeholder(w, p))
                    widget.bind("<FocusOut>", lambda e, w=widget, p=placeholder: self.restore_placeholder(w, p))
                    widget.config(fg="gray")
                
                self.all_widgets[f"{utm_key}_{bloco['nome']}"] = {
                    'widget': widget,
                    'type': 'entry',
                    'placeholder': placeholder,
                    'obrigatorio': bloco.get("obrigatorio", False)
                }
            
            widget.pack(side="left")
            self.widgets[utm_key][bloco["nome"]] = widget
    
    def bind_events(self):
        # Bind para utm_source
        if "utm_source" in self.widgets and "main" in self.widgets["utm_source"]:
            self.widgets["utm_source"]["main"].bind("<<ComboboxSelected>>", self.handle_source_selection)
    
    def handle_ferramenta_selection(self, event=None):
        """Controla as regras hierárquicas baseadas na ferramenta selecionada"""
        ferramenta_widget = self.widgets["utm_medium"]["Ferramenta"]
        selected_ferramenta = ferramenta_widget.get()
        
        # Reset dos campos formato e bloco/posição
        formato_widget = self.widgets["utm_medium"]["Formato"]
        bloco_widget = self.widgets["utm_medium"]["Bloco/Posição"]
        
        if selected_ferramenta == "pzn":
            self.block_all_fields()
            ferramenta_widget.config(state="readonly")
            ferramenta_widget.set("pzn")
            return
        else:
            self.unblock_all_fields()
            ferramenta_widget.set(selected_ferramenta)
        
        # Aplicar regras hierárquicas específicas
        regras = utm_config["utm_medium"].get("regras_hierarquicas", {})
        
        if selected_ferramenta in regras:
            ferramenta_regras = regras[selected_ferramenta]
            
            if selected_ferramenta == "admintotem":
                formato_widget.set("-- Não aplicável --")
                formato_widget.config(state="disabled")
                bloco_widget.set("-- Não aplicável --")
                bloco_widget.config(state="disabled")
            else:
                formato_widget.config(state="readonly")
                formatos_disponiveis = list(ferramenta_regras.keys())
                formato_widget["values"] = formatos_disponiveis
                formato_widget.set("-- Selecione --")
                
                bloco_widget.config(state="readonly")
                bloco_widget.set("-- Selecione --")
                bloco_widget["values"] = []
        else:
            formato_widget.config(state="readonly")
            formato_widget["values"] = utm_config["utm_medium"]["blocos"][1]["opcoes"]
            formato_widget.set("-- Selecione --")
            
            bloco_widget.config(state="readonly")
            bloco_widget["values"] = utm_config["utm_medium"]["blocos"][2]["opcoes"]
            bloco_widget.set("-- Selecione --")
    
    def handle_formato_selection(self, event=None):
        """Controla as opções de bloco/posição baseadas no formato selecionado"""
        ferramenta_widget = self.widgets["utm_medium"]["Ferramenta"]
        formato_widget = self.widgets["utm_medium"]["Formato"]
        bloco_widget = self.widgets["utm_medium"]["Bloco/Posição"]
        
        selected_ferramenta = ferramenta_widget.get()
        selected_formato = formato_widget.get()
        
        if selected_ferramenta == "admintotem":
            return
        
        regras = utm_config["utm_medium"].get("regras_hierarquicas", {})
        
        if selected_ferramenta in regras and selected_formato in regras[selected_ferramenta]:
            blocos_disponiveis = regras[selected_ferramenta][selected_formato]
            
            if len(blocos_disponiveis) == 0:
                bloco_widget.set("-- Não aplicável --")
                bloco_widget.config(state="disabled")
            else:
                bloco_widget.config(state="readonly")
                bloco_widget["values"] = blocos_disponiveis
                bloco_widget.set("-- Selecione --")
        else:
            bloco_widget.config(state="readonly")
            bloco_widget["values"] = utm_config["utm_medium"]["blocos"][2]["opcoes"]
            bloco_widget.set("-- Selecione --")
    
    def block_all_fields(self):
        """Bloqueia TODOS os campos exceto o botão limpar e mostra nota explicativa"""
        
        for widget_key, widget_info in self.all_widgets.items():
            widget = widget_info['widget']
            
            if widget_key == "utm_medium_Ferramenta":
                continue
            
            if widget_info['type'] == 'combobox':
                widget.set("-- Bloqueado (PZN) --")
                widget.config(state="disabled")
            else:  # entry
                widget.delete(0, tk.END)
                widget.insert(0, "-- Bloqueado (PZN) --")
                widget.config(state="disabled", fg="gray")
        
        self.disable_buttons_except_clear()
        
        if not self.pzn_note_label:
            note_frame = tk.Frame(self.scrollable_frame, bg="#dc3545")
            note_frame.pack(fill="x", pady=(0, 20), padx=5)
            
            self.pzn_note_label = tk.Label(
                note_frame,
                text="🚨 ATENÇÃO PZN: Em campanhas PZN todas as utm's são parametrizadas por Martech.\nEncaminhar o link puro para o responsável por veicular a campanha PZN.",
                font=("Arial", 11, "bold"),
                bg="#dc3545",
                fg="white",
                padx=20,
                pady=15,
                justify="center",
                wraplength=800
            )
            self.pzn_note_label.pack(fill="x")
            note_frame.lift()
        
        if not self.campaign_pzn_note:
            utm_campaign_frame = None
            for widget in self.scrollable_frame.winfo_children():
                if isinstance(widget, tk.LabelFrame) and "UTM_CAMPAIGN" in widget.cget("text"):
                    utm_campaign_frame = widget
                    break
            
            if utm_campaign_frame:
                self.campaign_pzn_note = tk.Label(
                    utm_campaign_frame,
                    text="🔒 Campos bloqueados: Campanhas PZN são parametrizadas exclusivamente por Martech",
                    font=("Arial", 10, "italic"),
                    bg="#fff3cd",
                    fg="#856404",
                    padx=15,
                    pady=10,
                    relief="solid",
                    borderwidth=1
                )
                self.campaign_pzn_note.pack(fill="x", pady=10)
    
    def unblock_all_fields(self):
        """Desbloqueia todos os campos e remove nota explicativa"""
        
        valores_salvos = {}
        for widget_key, widget_info in self.all_widgets.items():
            widget = widget_info['widget']
            try:
                current_value = widget.get()
                if (current_value and 
                    current_value != "-- Selecione --" and 
                    "Bloqueado" not in current_value and
                    current_value != widget_info.get('placeholder', '')):
                    valores_salvos[widget_key] = current_value
            except:
                pass
        
        for widget_key, widget_info in self.all_widgets.items():
            widget = widget_info['widget']
            
            if widget_info['type'] == 'combobox':
                widget.config(state="readonly")
                if widget_key in valores_salvos:
                    widget.set(valores_salvos[widget_key])
                else:
                    widget.set(widget_info['default'])
            else:  # entry
                widget.config(state="normal", fg="black")
                widget.delete(0, tk.END)
                if widget_key in valores_salvos:
                    widget.insert(0, valores_salvos[widget_key])
                    widget.config(fg="black")
                elif widget_info.get('placeholder'):
                    widget.insert(0, widget_info['placeholder'])
                    widget.config(fg="gray")
        
        self.enable_all_buttons()
        
        if self.pzn_note_label:
            self.pzn_note_label.master.destroy()
            self.pzn_note_label = None
        
        if self.campaign_pzn_note:
            self.campaign_pzn_note.destroy()
            self.campaign_pzn_note = None
    
    def disable_buttons_except_clear(self):
        """Desabilita botões exceto o Limpar"""
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        button_text = child.cget("text")
                        if "Limpar" not in button_text:
                            child.config(state="disabled", bg="gray")
    
    def enable_all_buttons(self):
        """Reabilita todos os botões"""
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        button_text = child.cget("text")
                        child.config(state="normal")
                        if "Gerar" in button_text:
                            child.config(bg="#27ae60")
                        elif "Limpar" in button_text:
                            child.config(bg="#e74c3c")
                        elif "Copiar" in button_text:
                            child.config(bg="#3498db")
    
    def handle_source_selection(self, event=None):
        selected_value = self.widgets["utm_source"]["main"].get()
        
        if "utm_source" in self.dynamic_widgets:
            for widget in self.dynamic_widgets["utm_source"].winfo_children():
                widget.destroy()
        
        if selected_value == "totem":
            self.create_totem_fields()
    
    def create_totem_fields(self):
        parent = self.dynamic_widgets["utm_source"]
        
        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill="x", pady=10)
        
        title = tk.Label(
            parent,
            text="📍 Configurações do Totem",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            fg="#e74c3c"
        )
        title.pack(pady=(0, 10))
        
        self.create_dynamic_field(parent, "estado", "Estado *:", utm_config["utm_source"]["valores_filhos"]["estado"], obrigatorio=True)
        self.create_dynamic_field(parent, "cidade", "Cidade *:", [], obrigatorio=True)
        self.create_dynamic_field(parent, "loja", "Loja *:", [], obrigatorio=True)
        
        if hasattr(self, 'estado_combo'):
            self.estado_combo.bind("<<ComboboxSelected>>", self.update_cidades)
        if hasattr(self, 'cidade_combo'):
            self.cidade_combo.bind("<<ComboboxSelected>>", self.update_lojas)
    
    def create_dynamic_field(self, parent, field_name, label_text, values, obrigatorio=False):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(fill="x", pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 10),
            bg="#ffffff",
            width=15,
            anchor="w"
        )
        label.pack(side="left", padx=(20, 10))
        
        combo = ttk.Combobox(
            frame,
            values=values,
            state="readonly",
            width=25
        )
        combo.set("-- Selecione --")
        combo.pack(side="left")
        
        setattr(self, f"{field_name}_combo", combo)
        if "utm_source" not in self.widgets:
            self.widgets["utm_source"] = {}
        self.widgets["utm_source"][field_name] = combo
        
        self.all_widgets[f"utm_source_{field_name}"] = {
            'widget': combo,
            'type': 'combobox',
            'default': "-- Selecione --",
            'obrigatorio': obrigatorio
        }
    
    def update_cidades(self, event=None):
        estado_valor = self.estado_combo.get()
        if estado_valor == "-- Selecione --":
            return
            
        cidades = utm_config["utm_source"]["valores_filhos"]["cidade"].get(estado_valor, [])
        self.cidade_combo["values"] = cidades
        self.cidade_combo.set("-- Selecione --")
        
        self.loja_combo["values"] = []
        self.loja_combo.set("-- Selecione --")
    
    def update_lojas(self, event=None):
        cidade_valor = self.cidade_combo.get()
        if cidade_valor == "-- Selecione --":
            return
            
        lojas = utm_config["utm_source"]["valores_filhos"]["loja"].get(cidade_valor, [])
        self.loja_combo["values"] = lojas
        self.loja_combo.set("-- Selecione --")
    
    def clear_placeholder(self, widget, placeholder):
        current_value = widget.get()
        if current_value == placeholder or widget.cget("fg") == "gray":
            widget.delete(0, tk.END)
            widget.config(fg="black")
    
    def restore_placeholder(self, widget, placeholder):
        current_value = widget.get().strip()
        if not current_value:
            widget.insert(0, placeholder)
            widget.config(fg="gray")
    
    def validate_required_fields(self):
        """Valida se todos os campos obrigatórios foram preenchidos"""
        errors = []
        
        for widget_key, widget_info in self.all_widgets.items():
            if not widget_info.get('obrigatorio', False):
                continue
            
            widget = widget_info['widget']
            
            try:
                value = widget.get().strip()
                
                # Verificar se o campo está visível (para campos condicionais de valor)
                if widget_key.startswith("utm_campaign_valor_"):
                    if not self.tem_valor.get():
                        continue  # Pular validação se valor não é obrigatório
                    
                    # Validação especial para campos de valor
                    if widget_key == "utm_campaign_valor_reais":
                        placeholder = "99"
                        if not value or value == placeholder:
                            # Verificar cor do texto
                            try:
                                if widget.cget("fg") == "gray":
                                    field_name = "Campaign Valor Reais"
                                    errors.append(field_name)
                                    continue
                            except:
                                pass
                            # Se chegou aqui, o campo está vazio
                            if not value:
                                field_name = "Campaign Valor Reais"
                                errors.append(field_name)
                        continue
                    
                    elif widget_key == "utm_campaign_valor_centavos":
                        placeholder = "99"
                        if not value or value == placeholder:
                            # Verificar cor do texto
                            try:
                                if widget.cget("fg") == "gray":
                                    field_name = "Campaign Valor Centavos"
                                    errors.append(field_name)
                                    continue
                            except:
                                pass
                            # Se chegou aqui, o campo está vazio
                            if not value:
                                field_name = "Campaign Valor Centavos"
                                errors.append(field_name)
                        continue
                
                # Validação normal para outros campos
                is_valid = False
                
                if widget_info['type'] == 'combobox':
                    if value and value != "-- Selecione --" and "Bloqueado" not in value:
                        is_valid = True
                else:  # entry
                    placeholder = widget_info.get('placeholder', '')
                    if value and value != placeholder and "Bloqueado" not in value:
                        try:
                            if widget.cget("fg") != "gray":
                                is_valid = True
                        except:
                            if value:
                                is_valid = True
                
                if not is_valid:
                    field_name = widget_key.replace("_", " ").replace("utm ", "").title()
                    errors.append(field_name)
            
            except Exception as e:
                print(f"Erro ao validar {widget_key}: {e}")
                continue
        
        return errors
    
    def create_action_buttons(self):
        button_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
        button_frame.pack(pady=20)
        
        generate_btn = tk.Button(
            button_frame,
            text="🚀 Gerar UTM",
            command=self.gerar_resultado,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        generate_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Limpar",
            command=self.limpar_campos,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        copy_btn = tk.Button(
            button_frame,
            text="📋 Copiar",
            command=self.copiar_resultado,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        copy_btn.pack(side="left")
    
    def create_result_area(self):
        result_frame = tk.LabelFrame(
            self.scrollable_frame,
            text="📊 Resultado Gerado",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            padx=15,
            pady=10
        )
        result_frame.pack(fill="x", pady=10, padx=5)
        
        self.result_text = tk.Text(
            result_frame,
            height=8,
            width=80,
            font=("Consolas", 10),
            bg="#f8f9fa",
            fg="#2c3e50",
            border=1,
            relief="solid"
        )
        self.result_text.pack(fill="x")
    
    def gerar_resultado(self):
        pzn_selected = False
        if "utm_medium" in self.widgets and "Ferramenta" in self.widgets["utm_medium"]:
            ferramenta_value = self.widgets["utm_medium"]["Ferramenta"].get()
            pzn_selected = (ferramenta_value == "pzn")
        
        if pzn_selected:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "🚨 CAMPANHA PZN DETECTADA\n" + "="*50 + "\n\n")
            self.result_text.insert(tk.END, "❌ Não é possível gerar parâmetros UTM para campanhas PZN.\n\n")
            self.result_text.insert(tk.END, "📋 INSTRUÇÃO:\n")
            self.result_text.insert(tk.END, "Encaminhe o LINK PURO (sem parâmetros) para o responsável\n")
            self.result_text.insert(tk.END, "por veicular a campanha PZN.\n\n")
            self.result_text.insert(tk.END, "⚙️ O time de Martech será responsável por toda a parametrização UTM.")
            messagebox.showwarning("Atenção - Campanha PZN", 
                                "Campanhas PZN devem ser parametrizadas pelo Martech!\n\n" +
                                "Encaminhe apenas o link puro para o responsável.")
            return
        
        errors = self.validate_required_fields()
        
        # Validação especial para campos de valor quando visíveis
        if self.tem_valor.get():
            if self.valor_reais_widget and self.valor_centavos_widget:
                reais = self.valor_reais_widget.get().strip()
                centavos = self.valor_centavos_widget.get().strip()
                
                # Verificar se reais está preenchido
                if not reais or reais == "99" or self.valor_reais_widget.cget("fg") == "gray":
                    errors.append("Valor - Reais")
                
                # Verificar se centavos está preenchido  
                if not centavos or centavos == "99" or self.valor_centavos_widget.cget("fg") == "gray":
                    errors.append("Valor - Centavos")
        
        if errors:
            error_msg = "Os seguintes campos obrigatórios (*) não foram preenchidos:\n\n"
            error_msg += "• " + "\n• ".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... e mais {len(errors) - 10} campo(s)"
            
            messagebox.showerror("Campos Obrigatórios", error_msg)
            return
        
        utm_params = {}
        
        for utm_key, widgets_dict in self.widgets.items():
            valores_utm = []
            
            # Para utm_campaign, definir ordem específica dos campos
            if utm_key == "utm_campaign":
                # Ordem desejada: frente_ -> produto/serviço -> valor -> versão
                field_order = ["frente_", "produto/serviço", "valor", "versão"]
                
                # Processar campos na ordem definida
                for field_name in field_order:
                    if field_name == "valor":
                        # Processar campo valor se estiver ativo
                        if self.tem_valor.get() and self.valor_reais_widget and self.valor_centavos_widget:
                            try:
                                reais = self.valor_reais_widget.get().strip()
                                centavos = self.valor_centavos_widget.get().strip()
                                
                                reais_valid = False
                                centavos_valid = False
                                
                                if reais and reais != "99":
                                    try:
                                        if self.valor_reais_widget.cget("fg") != "gray":
                                            reais_valid = True
                                    except:
                                        reais_valid = True
                                
                                if centavos and centavos != "99":
                                    try:
                                        if self.valor_centavos_widget.cget("fg") != "gray":
                                            centavos_valid = True
                                    except:
                                        centavos_valid = True
                                
                                if reais_valid and centavos_valid:
                                    valor_concatenado = reais + centavos
                                    valores_utm.append(valor_concatenado)
                            except Exception as e:
                                print(f"Erro ao processar campos de valor: {e}")
                    
                    elif field_name in widgets_dict:
                        # Processar outros campos
                        widget = widgets_dict[field_name]
                        try:
                            value = widget.get().strip()
                            
                            if "Bloqueado (PZN)" in value or "Não aplicável" in value:
                                continue
                            
                            if value and value != "-- Selecione --":
                                is_valid_value = True
                                
                                blocos = utm_config.get(utm_key, {}).get("blocos", [])
                                for bloco in blocos:
                                    if bloco["nome"] == field_name and "placeholder" in bloco:
                                        if value == bloco["placeholder"]:
                                            is_valid_value = False
                                            break
                                        if isinstance(widget, tk.Entry):
                                            try:
                                                if widget.cget("fg") == "gray":
                                                    is_valid_value = False
                                                    break
                                            except:
                                                pass
                                
                                if isinstance(widget, tk.Entry) and is_valid_value:
                                    try:
                                        if widget.cget("fg") == "gray":
                                            is_valid_value = False
                                    except:
                                        pass
                                
                                if is_valid_value:
                                    valores_utm.append(value)
                        
                        except Exception as e:
                            print(f"Erro ao processar {utm_key}.{field_name}: {e}")
                            continue
            
            else:
                # Para outras UTMs, manter o processamento original
                for field_name, widget in widgets_dict.items():
                    try:
                        value = widget.get().strip()
                        
                        if "Bloqueado (PZN)" in value or "Não aplicável" in value:
                            continue
                        
                        if value and value != "-- Selecione --":
                            is_valid_value = True
                            
                            blocos = utm_config.get(utm_key, {}).get("blocos", [])
                            for bloco in blocos:
                                if bloco["nome"] == field_name and "placeholder" in bloco:
                                    if value == bloco["placeholder"]:
                                        is_valid_value = False
                                        break
                                    if isinstance(widget, tk.Entry):
                                        try:
                                            if widget.cget("fg") == "gray":
                                                is_valid_value = False
                                                break
                                        except:
                                            pass
                            
                            if isinstance(widget, tk.Entry) and is_valid_value:
                                try:
                                    if widget.cget("fg") == "gray":
                                        is_valid_value = False
                                except:
                                    pass
                            
                            if is_valid_value:
                                valores_utm.append(value)
                    
                    except Exception as e:
                        print(f"Erro ao processar {utm_key}.{field_name}: {e}")
                        continue
            
            if valores_utm:
                utm_params[utm_key] = "_".join(valores_utm)
        
        if not utm_params:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, "⚠️ Nenhum parâmetro foi preenchido.\n\nPreencha pelo menos um campo em cada seção UTM que deseja gerar.")
            messagebox.showwarning("Atenção", "Preencha pelo menos um campo para gerar o resultado!")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"🎯 Parâmetros UTM Gerados\n{'='*50}\n\n")
        
        for utm_key, valor_concatenado in utm_params.items():
            self.result_text.insert(tk.END, f"{utm_key}={valor_concatenado}\n")
        
        self.result_text.insert(tk.END, f"\n📊 Resumo:\n{'-'*30}\n")
        self.result_text.insert(tk.END, f"✅ {len(utm_params)} parâmetro(s) gerado(s)\n")
        
        utms_nao_preenchidas = []
        for utm_key in utm_config.keys():
            if utm_key not in utm_params:
                utms_nao_preenchidas.append(utm_key)
        
        if utms_nao_preenchidas:
            self.result_text.insert(tk.END, f"⚪ {len(utms_nao_preenchidas)} parâmetro(s) não preenchido(s): {', '.join(utms_nao_preenchidas)}")
        
        print("UTMs geradas:", utm_params)
    
    def limpar_campos(self):
        for utm_key, widgets_dict in self.widgets.items():
            for widget in widgets_dict.values():
                if isinstance(widget, ttk.Combobox):
                    widget.set("-- Selecione --")
                    widget.config(state="readonly")
                elif isinstance(widget, tk.Entry):
                    widget.config(state="normal", fg="black")
                    widget.delete(0, tk.END)
        
        if self.valor_reais_widget:
            self.valor_reais_widget.delete(0, tk.END)
            self.valor_reais_widget.insert(0, "99")
            self.valor_reais_widget.config(fg="gray")
        
        if self.valor_centavos_widget:
            self.valor_centavos_widget.delete(0, tk.END)
            self.valor_centavos_widget.insert(0, "99")
            self.valor_centavos_widget.config(fg="gray")
        
        self.tem_valor.set(False)
        if self.valor_frame:
            self.valor_frame.pack_forget()
        
        for dynamic_frame in self.dynamic_widgets.values():
            for widget in dynamic_frame.winfo_children():
                widget.destroy()
        
        self.unblock_all_fields()
        
        for utm_key, utm_info in utm_config.items():
            if "blocos" in utm_info:
                for bloco in utm_info["blocos"]:
                    if "placeholder" in bloco and utm_key in self.widgets and bloco["nome"] in self.widgets[utm_key]:
                        widget = self.widgets[utm_key][bloco["nome"]]
                        if isinstance(widget, tk.Entry):
                            widget.insert(0, bloco["placeholder"])
                            widget.config(fg="gray")
        
        if "utm_medium" in self.widgets:
            ferramenta_widget = self.widgets["utm_medium"]["Ferramenta"]
            formato_widget = self.widgets["utm_medium"]["Formato"]
            bloco_widget = self.widgets["utm_medium"]["Bloco/Posição"]
            
            ferramenta_widget["values"] = utm_config["utm_medium"]["blocos"][0]["opcoes"]
            formato_widget["values"] = utm_config["utm_medium"]["blocos"][1]["opcoes"]
            bloco_widget["values"] = utm_config["utm_medium"]["blocos"][2]["opcoes"]
            
            ferramenta_widget.config(state="readonly")
            formato_widget.config(state="readonly")
            bloco_widget.config(state="readonly")
        
        self.result_text.delete(1.0, tk.END)
        messagebox.showinfo("Sucesso", "Todos os campos foram limpos!")
    
    def copiar_resultado(self):
        content = self.result_text.get(1.0, tk.END).strip()
        if not content or "Nenhum parâmetro foi preenchido" in content:
            messagebox.showwarning("Atenção", "Não há resultado para copiar!")
            return
        
        lines = content.split('\n')
        utm_lines = []
        for line in lines:
            if line.strip().startswith('utm_') and '=' in line:
                utm_lines.append(line.strip())
        
        if not utm_lines:
            messagebox.showwarning("Atenção", "Nenhum parâmetro UTM encontrado para copiar!")
            return
        
        utm_text = '\n'.join(utm_lines)
        
        try:
            pyperclip.copy(utm_text)
            messagebox.showinfo("Sucesso", f"Parâmetros UTM copiados para a área de transferência!\n\nTotal: {len(utm_lines)} parâmetro(s)")
        except:
            messagebox.showinfo("Parâmetros UTM", f"Copie manualmente:\n\n{utm_text}")
    
    def bind_mousewheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParametrizatorApp(root)
    root.mainloop()
