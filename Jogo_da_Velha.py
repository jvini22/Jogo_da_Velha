"""
Jogo da Velha com interface gráfica em PyQt5.

Este script implementa um jogo da velha completo com os seguintes recursos:
- Modos de jogo: Jogador vs Jogador e Jogador vs CPU.
- Níveis de dificuldade da CPU: Fácil, Médio e Impossível (usando Minimax com poda Alfa-Beta).
- Interface gráfica com múltiplas telas (menu, seleção de nomes, jogo).
- Sistema de temas (claro e escuro) carregado a partir de um arquivo JSON.
- Animações de jogada e linha de vitória.
- Placar de estatísticas por partida.
- Efeitos sonoros, persistência de histórico, escolha de símbolo e mais melhorias.
"""
import sys
import random
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QLabel, QGridLayout, QMessageBox, QMainWindow,
                             QComboBox, QStackedWidget, QLineEdit, QGraphicsOpacityEffect,
                             QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect


class TicTacToeLogic:
    """
    Contém toda a lógica do Jogo da Velha, independente da interface gráfica.

    Atributos:
        FACIL, MEDIO, IMPOSSIVEL (str): Constantes para os níveis de dificuldade.
        tabuleiro (list): Representação 3x3 do tabuleiro.
        jogador_atual (str): 'X' ou 'O'.
        vencedor (str): 'X', 'O', 'Empate', ou None.
        player_names (dict): Mapeia 'X' e 'O' para os nomes dos jogadores.
    """
    FACIL = 'Fácil'
    MEDIO = 'Médio'
    IMPOSSIVEL = 'Impossível'

    def __init__(self):
        """Inicializa a lógica do jogo."""
        self.reset_board()
        self.player_names = {'X': 'Jogador 1', 'O': 'Jogador 2'}

    def reset_board(self):
        """Reseta o tabuleiro para o estado inicial."""
        self.tabuleiro = [[' '] * 3 for _ in range(3)]
        self.jogador_atual = 'X' # X sempre começa
        self.vencedor = None

    def set_player_names(self, name_x, name_o):
        """Define os nomes dos jogadores."""
        self.player_names['X'] = name_x if name_x else 'Jogador X'
        self.player_names['O'] = name_o if name_o else 'Jogador O'

    def fazer_jogada(self, x, y):
        """Tenta fazer uma jogada na posição (x, y)."""
        if self.tabuleiro[x][y] == ' ':
            self.tabuleiro[x][y] = self.jogador_atual
            return True
        return False

    def alternar_jogador(self):
        """Alterna o jogador atual."""
        self.jogador_atual = 'O' if self.jogador_atual == 'X' else 'X'

    def verificar_fim_de_jogo(self):
        """
        Verifica se o jogo terminou (vitória ou empate) e atualiza o estado.

        Retorna:
            tuple: (bool, list) indicando se o jogo acabou e a linha vencedora.
        """
        resultado, linha_vencedora = self._avaliar_tabuleiro(self.tabuleiro)
        if resultado:
            self.vencedor = resultado
            return True, linha_vencedora
        return False, []

    @staticmethod
    def _avaliar_tabuleiro(tabuleiro):
        """
        Método estático para avaliar um estado de tabuleiro sem modificar a instância.

        Retorna:
            tuple: (str, list) com o vencedor/empate e a linha da vitória, ou (None, []).
        """
        # Checar linhas e colunas
        for i in range(3):
            if tabuleiro[i][0] == tabuleiro[i][1] == tabuleiro[i][2] != ' ':
                return tabuleiro[i][0], [(i, 0), (i, 1), (i, 2)]
            if tabuleiro[0][i] == tabuleiro[1][i] == tabuleiro[2][i] != ' ':
                return tabuleiro[0][i], [(0, i), (1, i), (2, i)]

        # Checar diagonais
        if tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] != ' ':
            return tabuleiro[0][0], [(0, 0), (1, 1), (2, 2)]
        if tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] != ' ':
            return tabuleiro[0][2], [(0, 2), (1, 1), (2, 0)]

        # Checar empate
        if all(tabuleiro[i][j] != ' ' for i in range(3) for j in range(3)):
            return "Empate", []

        return None, []

    def estrategia_cpu(self, dificuldade, cpu_symbol):
        """Escolhe a melhor jogada para a CPU com base na dificuldade."""
        player_symbol = 'O' if cpu_symbol == 'X' else 'X'
        if dificuldade == self.FACIL:
            return self.jogada_aleatoria()
        if dificuldade == self.MEDIO:
            return self.jogada_media(cpu_symbol, player_symbol)
        if dificuldade == self.IMPOSSIVEL:
            is_maximizing = cpu_symbol == 'O' # 'O' é tradicionalmente o maximizador
            _, jogada = self.minimax_alfa_beta(self.tabuleiro, is_maximizing, cpu_symbol, player_symbol)
            return jogada
        return None

    def jogada_aleatoria(self):
        """Retorna uma jogada aleatória válida."""
        jogadas_possiveis = [(i, j) for i in range(3) for j in range(3) if self.tabuleiro[i][j] == ' ']
        return random.choice(jogadas_possiveis) if jogadas_possiveis else None

    def jogada_media(self, cpu_symbol, player_symbol):
        """Retorna uma jogada com base em uma estratégia intermediária."""
        # 1. Tenta ganhar
        for i, j in self._jogadas_possiveis():
            if self._teste_jogada_vencedora(i, j, cpu_symbol):
                return i, j
        # 2. Tenta bloquear
        for i, j in self._jogadas_possiveis():
            if self._teste_jogada_vencedora(i, j, player_symbol):
                return i, j
        # 3. Ocupa o centro
        if self.tabuleiro[1][1] == ' ': return (1, 1)
        # 4. Ocupa um canto
        cantos = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(cantos)
        for i, j in cantos:
            if self.tabuleiro[i][j] == ' ': return i, j
        # 5. Joga aleatoriamente
        return self.jogada_aleatoria()
    
    def _jogadas_possiveis(self):
        return [(i, j) for i in range(3) for j in range(3) if self.tabuleiro[i][j] == ' ']

    def _teste_jogada_vencedora(self, i, j, symbol):
        tabuleiro_copia = [linha[:] for linha in self.tabuleiro]
        tabuleiro_copia[i][j] = symbol
        vencedor, _ = self._avaliar_tabuleiro(tabuleiro_copia)
        return vencedor == symbol

    def _process_minimax_branch(self, tabuleiro, is_maximizing, cpu_symbol, player_symbol, alfa, beta):
        """Processa um único ramo (maximizando ou minimizando) do algoritmo minimax."""
        melhor_jogada = None
        if is_maximizing:
            melhor_valor = -float('inf')
            symbol_to_place = cpu_symbol
        else:
            melhor_valor = float('inf')
            symbol_to_place = player_symbol

        for i, j in self._jogadas_possiveis():
            tabuleiro[i][j] = symbol_to_place
            valor, _ = self.minimax_alfa_beta(tabuleiro, not is_maximizing, cpu_symbol, player_symbol, alfa, beta)
            tabuleiro[i][j] = ' '

            if is_maximizing:
                if valor > melhor_valor:
                    melhor_valor, melhor_jogada = valor, (i, j)
                alfa = max(alfa, melhor_valor)
            else: # Minimizing
                if valor < melhor_valor:
                    melhor_valor, melhor_jogada = valor, (i, j)
                beta = min(beta, melhor_valor)
            
            if beta <= alfa:
                break # Poda alfa-beta
        
        return melhor_valor, melhor_jogada

    def minimax_alfa_beta(self, tabuleiro, is_maximizing, cpu_symbol, player_symbol, alfa=-float('inf'), beta=float('inf')):
        """
        Algoritmo Minimax com poda Alfa-Beta para encontrar a jogada ótima.
        Refatorado para menor complexidade cognitiva.
        """
        vencedor, _ = self._avaliar_tabuleiro(tabuleiro)
        if vencedor:
            if vencedor == cpu_symbol: return 10, None
            if vencedor == player_symbol: return -10, None
            return 0, None # Empate
        
        return self._process_minimax_branch(tabuleiro, is_maximizing, cpu_symbol, player_symbol, alfa, beta)


class BoardWidget(QWidget):
    """Widget customizado para desenhar a linha de vitória sobre o tabuleiro."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.winning_line_coords = None

    def set_winning_line(self, start_pos, end_pos):
        self.winning_line_coords = (start_pos, end_pos)
        self.update()

    def clear_line(self):
        self.winning_line_coords = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.winning_line_coords:
            painter = QPainter(self)
            pen = QPen(QColor("#27ae60"), 10, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            start_pos, end_pos = self.winning_line_coords
            painter.drawLine(start_pos, end_pos)


class JogoDaVelhaGUI(QMainWindow):
    """Classe principal da interface gráfica."""
    # --- Melhoria 9: Refatoração do Código (Constantes) ---
    THEME_FILE = "themes.json"
    STATS_FILE = "stats.json"

    def __init__(self):
        super().__init__()
        self.jogo_logica = TicTacToeLogic()
        self.stats_sessao = {'X': 0, 'O': 0, 'Empate': 0}
        self.stats_historico = self.carregar_stats()
        self.modo_vs_cpu = False
        self.dificuldade_cpu = 'Fácil'
        self.player_symbol = 'X'
        self.carregar_temas()
        self.tema_atual = 'dark'
        self.setup_ui()

    def carregar_temas(self):
        """Carrega os temas de um arquivo JSON externo."""
        try:
            theme_path = Path(__file__).parent / self.THEME_FILE
            with open(theme_path, 'r', encoding='utf-8') as f:
                self.themes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.themes = {
                "dark": {"bg": "#1a252f", "grid_bg": "#2c3e50", "cell_bg": "#34495e", "text": "#ecf0f1", "x": "#3498db", "o": "#e74c3c", "btn": "#3498db", "btn_hover": "#2980b9"},
                "light": {"bg": "#ecf0f1", "grid_bg": "#bdc3c7", "cell_bg": "#ffffff", "text": "#2c3e50", "x": "#2980b9", "o": "#c0392b", "btn": "#2980b9", "btn_hover": "#3498db"}
            }

    # --- Melhoria 4: Persistência de Histórico ---
    def carregar_stats(self):
        try:
            stats_path = Path(__file__).parent / self.STATS_FILE
            with open(stats_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'X': 0, 'O': 0, 'Empate': 0, 'cpu_X': 0, 'cpu_O': 0}

    def salvar_stats(self):
        try:
            stats_path = Path(__file__).parent / self.STATS_FILE
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.stats_historico, f, indent=4)
        except IOError:
            print("Erro ao salvar estatísticas.")

    def closeEvent(self, event):
        self.salvar_stats()
        event.accept()

    def setup_ui(self):
        self.setWindowTitle('Jogo da Velha')
        self.setFixedSize(400, 650)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.criar_menu_inicial()
        self.criar_menu_nomes()
        self.criar_menu_dificuldade()
        self.criar_tela_jogo()
        self.aplicar_tema(self.tema_atual)
        self.stacked_widget.setCurrentIndex(0)

    def aplicar_tema(self, nome_tema):
        self.tema_atual = nome_tema
        theme = self.themes[nome_tema]
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: {theme['bg']}; }}
            QLabel {{ color: {theme['text']}; }}
            QPushButton {{ background-color: {theme['btn']}; color: white; border: none; padding: 15px; font-size: 16px; border-radius: 8px;}}
            QPushButton:hover {{ background-color: {theme['btn_hover']}; }}
            QComboBox, QLineEdit {{ border: 1px solid {theme['btn']}; border-radius: 5px; padding: 10px; font-size: 14px; color: {theme['text']}; background-color: {theme['cell_bg']};}}
        """)
        if hasattr(self, 'botoes'):
            for i in range(3):
                for j in range(3):
                    if not self.jogo_logica.tabuleiro[i][j].strip():
                        self.botoes[i][j].setStyleSheet(f"background-color: {theme['cell_bg']}; border-radius: 8px;")

    def criar_menu_inicial(self):
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        title = QLabel("Jogo da Velha")
        title.setFont(QFont('Arial', 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        btn_vs_cpu = QPushButton('Jogador vs CPU')
        btn_vs_cpu.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        btn_vs_jogador = QPushButton('Jogador vs Jogador')
        btn_vs_jogador.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        theme_combo = QComboBox()
        theme_combo.addItems(self.themes.keys())
        theme_combo.currentTextChanged.connect(self.aplicar_tema)
        # --- Melhoria 10: Melhorias de Layout ---
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btn_vs_cpu)
        layout.addWidget(btn_vs_jogador)
        layout.addWidget(theme_combo)
        layout.addStretch()
        self.stacked_widget.addWidget(menu_widget)

    def criar_menu_nomes(self):
        nomes_widget = QWidget()
        layout = QVBoxLayout(nomes_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        title = QLabel("Nomes dos Jogadores")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        self.nome_jogador1 = QLineEdit()
        self.nome_jogador1.setPlaceholderText("Nome do Jogador 1 (X)")
        self.nome_jogador2 = QLineEdit()
        self.nome_jogador2.setPlaceholderText("Nome do Jogador 2 (O)")
        iniciar_btn = QPushButton('Iniciar Jogo')
        iniciar_btn.clicked.connect(self.iniciar_jogo_vs_jogador)
        voltar_btn = QPushButton('Voltar')
        voltar_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(title)
        layout.addWidget(self.nome_jogador1)
        layout.addWidget(self.nome_jogador2)
        layout.addWidget(iniciar_btn)
        layout.addWidget(voltar_btn)
        self.stacked_widget.addWidget(nomes_widget)

    def criar_menu_dificuldade(self):
        dificuldade_widget = QWidget()
        layout = QVBoxLayout(dificuldade_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        title = QLabel("Selecione a Dificuldade")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        self.combo_dificuldade = QComboBox()
        self.combo_dificuldade.addItems([TicTacToeLogic.FACIL, TicTacToeLogic.MEDIO, TicTacToeLogic.IMPOSSIVEL])
        # --- Melhoria 2: Escolha de Símbolo (X/O) ---
        label_simbolo = QLabel("Escolha o seu símbolo:")
        label_simbolo.setFont(QFont('Arial', 14))
        self.combo_simbolo = QComboBox()
        self.combo_simbolo.addItems(['X (começa a jogar)', 'O'])
        iniciar_btn = QPushButton('Iniciar Jogo')
        iniciar_btn.clicked.connect(self.iniciar_jogo_vs_cpu)
        voltar_btn = QPushButton('Voltar')
        voltar_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(title)
        layout.addWidget(self.combo_dificuldade)
        layout.addWidget(label_simbolo)
        layout.addWidget(self.combo_simbolo)
        layout.addWidget(iniciar_btn)
        layout.addWidget(voltar_btn)
        self.stacked_widget.addWidget(dificuldade_widget)

    def criar_tela_jogo(self):
        jogo_widget = QWidget()
        self.v_layout = QVBoxLayout(jogo_widget)
        self.v_layout.setContentsMargins(20, 20, 20, 20)
        self.placar_label = QLabel()
        self.placar_label.setFont(QFont('Arial', 14))
        self.placar_label.setAlignment(Qt.AlignCenter)
        self.info_label = QLabel()
        self.info_label.setFont(QFont('Arial', 16, QFont.Bold))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.placar_label)
        self.v_layout.addWidget(self.info_label)
        self.board_container = QWidget()
        grid_layout = QGridLayout(self.board_container)
        grid_layout.setSpacing(10)
        self.board_widget = BoardWidget()
        grid_layout.addWidget(self.board_widget, 0, 0, 3, 3)
        self.botoes = [[QPushButton() for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = self.botoes[i][j]
                btn.setFixedSize(100, 100)
                btn.setFont(QFont('Arial', 36, QFont.Bold))
                btn.clicked.connect(lambda _, x=i, y=j: self.fazer_jogada_gui(x, y))
                grid_layout.addWidget(btn, i, j)
        self.v_layout.addWidget(self.board_container)
        btn_menu = QPushButton("Voltar ao Menu")
        btn_menu.clicked.connect(self.voltar_ao_menu)
        self.v_layout.addWidget(btn_menu)
        self.stacked_widget.addWidget(jogo_widget)

    def iniciar_jogo_vs_cpu(self):
        self.modo_vs_cpu = True
        self.dificuldade_cpu = self.combo_dificuldade.currentText()
        escolha = self.combo_simbolo.currentText()
        self.player_symbol = 'X' if 'X' in escolha else 'O'
        cpu_symbol = 'O' if self.player_symbol == 'X' else 'X'
        # Usa as variáveis para nomes mais descritivos, corrigindo o aviso.
        self.jogo_logica.set_player_names(f"Você ({self.player_symbol})", f"CPU ({cpu_symbol})")
        self.reiniciar_jogo_completo()
        self.stacked_widget.setCurrentIndex(3)
        if self.player_symbol == 'O':
            self.ativar_tabuleiro(False)
            QTimer.singleShot(500, self.jogada_cpu_gui)

    def iniciar_jogo_vs_jogador(self):
        self.modo_vs_cpu = False
        self.player_symbol = 'X' # No modo P vs P, X sempre começa
        self.jogo_logica.set_player_names(self.nome_jogador1.text(), self.nome_jogador2.text())
        self.reiniciar_jogo_completo()
        self.stacked_widget.setCurrentIndex(3)
        
    def voltar_ao_menu(self):
        self.stats_sessao = {'X': 0, 'O': 0, 'Empate': 0}
        self.atualizar_placar()
        self.stacked_widget.setCurrentIndex(0)

    def fazer_jogada_gui(self, x, y):
        # --- Melhoria 1: Efeitos Sonoros ---
        QApplication.beep()
        cpu_turn = self.modo_vs_cpu and self.jogo_logica.jogador_atual != self.player_symbol
        if self.jogo_logica.vencedor or cpu_turn:
            return
        if self.jogo_logica.fazer_jogada(x, y):
            self.atualizar_botao(x, y)
            self.verificar_estado_jogo()

    def jogada_cpu_gui(self):
        if not self.jogo_logica.vencedor:
            cpu_symbol = 'O' if self.player_symbol == 'X' else 'X'
            jogada = self.jogo_logica.estrategia_cpu(self.dificuldade_cpu, cpu_symbol)
            if jogada:
                self.jogo_logica.fazer_jogada(jogada[0], jogada[1])
                self.atualizar_botao(jogada[0], jogada[1])
            self.verificar_estado_jogo()
            self.ativar_tabuleiro(True)

    def verificar_estado_jogo(self):
        fim, linha_vencedora = self.jogo_logica.verificar_fim_de_jogo()
        if fim:
            self.fim_de_jogo(linha_vencedora)
        else:
            self.jogo_logica.alternar_jogador()
            self.atualizar_info_label()
            cpu_turn = self.modo_vs_cpu and self.jogo_logica.jogador_atual != self.player_symbol
            if cpu_turn:
                self.ativar_tabuleiro(False)
                # --- Melhoria 5: Indicador "CPU a Pensar" ---
                if self.dificuldade_cpu != TicTacToeLogic.FACIL:
                    self.info_label.setText("CPU está a pensar...")
                QTimer.singleShot(500, self.jogada_cpu_gui)

    def fim_de_jogo(self, linha_vencedora):
        vencedor = self.jogo_logica.vencedor
        if vencedor == "Empate":
            msg = "O jogo terminou empatado!"
            self.info_label.setText("Empate!")
            self.stats_sessao['Empate'] += 1
            self.stats_historico['Empate'] += 1
        else:
            nome_vencedor = self.jogo_logica.player_names[vencedor]
            msg = f'{nome_vencedor} ({vencedor}) venceu!'
            self.info_label.setText(f"{nome_vencedor} Venceu!")
            self.stats_sessao[vencedor] += 1
            self.stats_historico[vencedor] += 1
            self.destacar_vitoria(linha_vencedora)
        
        # --- Melhoria 7: Desativar Tabuleiro no Fim ---
        self.ativar_tabuleiro(False)
        self.atualizar_placar()
        QTimer.singleShot(1500, lambda: self.mostrar_msg_fim_jogo(msg))

    def mostrar_msg_fim_jogo(self, msg):
        QMessageBox.information(self, 'Fim de Jogo', msg)
        self.reiniciar_jogo()

    def reiniciar_jogo(self):
        self.jogo_logica.reset_board()
        self.board_widget.clear_line()
        theme = self.themes[self.tema_atual]
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setText('')
                self.botoes[i][j].setStyleSheet(f"background-color: {theme['cell_bg']}; border-radius: 8px;")
                self.botoes[i][j].setGraphicsEffect(None) # Limpa efeito de opacidade
        self.ativar_tabuleiro(True)
        self.atualizar_info_label()
        
        # Se CPU começa (jogador escolheu 'O')
        if self.modo_vs_cpu and self.player_symbol == 'O':
            self.ativar_tabuleiro(False)
            QTimer.singleShot(500, self.jogada_cpu_gui)

    def reiniciar_jogo_completo(self):
        self.stats_sessao = {'X': 0, 'O': 0, 'Empate': 0}
        self.atualizar_placar()
        self.reiniciar_jogo()
    
    def atualizar_botao(self, x, y):
        jogador = self.jogo_logica.tabuleiro[x][y]
        btn = self.botoes[x][y]
        btn.setText(jogador)
        theme = self.themes[self.tema_atual]
        cor_jogador = theme['x'] if jogador == 'X' else theme['o']
        btn.setStyleSheet(f"color: {cor_jogador}; background-color: {theme['grid_bg']}; font-size: 36px; font-weight: bold; border-radius: 8px;")
        
        # --- Melhoria 3: Animação de Fade-In ---
        opacity_effect = QGraphicsOpacityEffect(btn)
        btn.setGraphicsEffect(opacity_effect)
        self.opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_anim.start()

    def destacar_vitoria(self, linha):
        start_cell = self.botoes[linha[0][0]][linha[0][1]]
        end_cell = self.botoes[linha[2][0]][linha[2][1]]
        start_pos = start_cell.geometry().center()
        end_pos = end_cell.geometry().center()
        self.board_widget.set_winning_line(start_pos, end_pos)

    def atualizar_placar(self):
        p_x = self.jogo_logica.player_names['X']
        p_o = self.jogo_logica.player_names['O']
        self.placar_label.setText(f"Placar da Sessão:\n"
                                  f"{p_x}: {self.stats_sessao['X']} | "
                                  f"{p_o}: {self.stats_sessao['O']} | "
                                  f"Empates: {self.stats_sessao['Empate']}")

    def atualizar_info_label(self):
        if not self.jogo_logica.vencedor:
            nome_jogador = self.jogo_logica.player_names[self.jogo_logica.jogador_atual]
            self.info_label.setText(f"Vez de: {nome_jogador} ({self.jogo_logica.jogador_atual})")
    
    def ativar_tabuleiro(self, enabled):
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setEnabled(enabled)

    # --- Melhoria 8: Atalhos de Teclado ---
    def keyPressEvent(self, event):
        # Apenas na tela de jogo
        if self.stacked_widget.currentIndex() == 3:
            if event.key() == Qt.Key_Escape:
                self.voltar_ao_menu()
            elif event.key() == Qt.Key_R:
                self.reiniciar_jogo_completo()


if __name__ == '__main__':
    theme_path = Path(__file__).parent / JogoDaVelhaGUI.THEME_FILE
    if not theme_path.exists():
        # --- Melhoria 6: Novos Temas Visuais ---
        default_themes = {
            "dark": {"bg": "#1a252f", "grid_bg": "#2c3e50", "cell_bg": "#34495e", "text": "#ecf0f1", "x": "#3498db", "o": "#e74c3c", "btn": "#3498db", "btn_hover": "#2980b9"},
            "light": {"bg": "#ecf0f1", "grid_bg": "#bdc3c7", "cell_bg": "#ffffff", "text": "#2c3e50", "x": "#2980b9", "o": "#c0392b", "btn": "#2980b9", "btn_hover": "#3498db"},
            "retro": {"bg": "#202020", "grid_bg": "#101010", "cell_bg": "#303030", "text": "#00ff00", "x": "#00ff00", "o": "#ff00ff", "btn": "#505050", "btn_hover": "#707070"},
            "floresta": {"bg": "#e8f5e9", "grid_bg": "#a5d6a7", "cell_bg": "#c8e6c9", "text": "#1b5e20", "x": "#2e7d32", "o": "#d84315", "btn": "#4caf50", "btn_hover": "#66bb6a"}
        }
        with open(theme_path, 'w', encoding='utf-8') as f:
            json.dump(default_themes, f, indent=4)

    app = QApplication(sys.argv)
    jogo = JogoDaVelhaGUI()
    jogo.show()
    sys.exit(app.exec_())

