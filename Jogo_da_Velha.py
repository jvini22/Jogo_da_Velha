import sys
import random
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                             QLabel, QGridLayout, QMessageBox, QMainWindow, 
                             QComboBox, QStackedWidget, QGraphicsOpacityEffect,
                             QLineEdit)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect

# --- Classe de Lógica do Jogo (Melhoria 1: Estrutura) ---
# A lógica do jogo permanece bem estruturada, mas será expandida.
class TicTacToeLogic:
    FACIL = 'Fácil'
    MEDIO = 'Médio'
    IMPOSSIVEL = 'Impossível'

    def __init__(self):
        self.reset_board()
        self.player_names = {'X': 'Jogador 1', 'O': 'Jogador 2'}

    def reset_board(self):
        self.tabuleiro = [[' ']*3 for _ in range(3)]
        self.jogador_atual = 'X'
        self.vencedor = None

    def set_player_names(self, name_x, name_o):
        self.player_names['X'] = name_x if name_x else 'Jogador X'
        self.player_names['O'] = name_o if name_o else 'Jogador O'

    def fazer_jogada(self, x, y):
        if self.tabuleiro[x][y] == ' ':
            self.tabuleiro[x][y] = self.jogador_atual
            return True
        return False

    def alternar_jogador(self):
        self.jogador_atual = 'O' if self.jogador_atual == 'X' else 'X'

    def verificar_fim_de_jogo(self):
        for i in range(3):
            if self.tabuleiro[i][0] == self.tabuleiro[i][1] == self.tabuleiro[i][2] != ' ':
                self.vencedor = self.tabuleiro[i][0]
                return True, [(i, 0), (i, 1), (i, 2)]
            if self.tabuleiro[0][i] == self.tabuleiro[1][i] == self.tabuleiro[2][i] != ' ':
                self.vencedor = self.tabuleiro[0][i]
                return True, [(0, i), (1, i), (2, i)]
        
        if self.tabuleiro[0][0] == self.tabuleiro[1][1] == self.tabuleiro[2][2] != ' ':
            self.vencedor = self.tabuleiro[0][0]
            return True, [(0, 0), (1, 1), (2, 2)]
        if self.tabuleiro[0][2] == self.tabuleiro[1][1] == self.tabuleiro[2][0] != ' ':
            self.vencedor = self.tabuleiro[0][2]
            return True, [(0, 2), (1, 1), (2, 0)]

        if all(self.tabuleiro[i][j] != ' ' for i in range(3) for j in range(3)):
            self.vencedor = "Empate"
            return True, []
            
    def estrategia_cpu(self, dificuldade):
        if dificuldade == self.FACIL:
            return self.jogada_aleatoria()
        elif dificuldade == self.MEDIO:
            return self.jogada_media()
        elif dificuldade == self.IMPOSSIVEL:
            return self.jogada_minimax_alfa_beta()
        elif dificuldade == TicTacToeLogic.MEDIO:
            return self.jogada_media()
        elif dificuldade == TicTacToeLogic.IMPOSSIVEL:
            return self.jogada_minimax_alfa_beta()

    def jogada_aleatoria(self):
        jogadas_possiveis = [(i, j) for i in range(3) for j in range(3) if self.tabuleiro[i][j] == ' ']
        return random.choice(jogadas_possiveis) if jogadas_possiveis else None

    # --- Melhoria 3: IA Média mais inteligente ---
    def jogada_media(self):
        jogada = self._tentar_ganhar()
        if jogada:
            return jogada
        jogada = self._tentar_bloquear()
        if jogada:
            return jogada
        jogada = self._ocupar_centro()
        if jogada:
            return jogada
        jogada = self._ocupar_cantos()
        if jogada:
            return jogada
        return self.jogada_aleatoria()

    def _tentar_ganhar(self):
        for i in range(3):
            for j in range(3):
                if self.tabuleiro[i][j] == ' ':
                    self.tabuleiro[i][j] = 'O'
                    vitoria, _ = self.verificar_fim_de_jogo()
                    self.tabuleiro[i][j] = ' '
                    if vitoria and self.vencedor == 'O':
                        return (i, j)
        return None

    def _tentar_bloquear(self):
        for i in range(3):
            for j in range(3):
                if self.tabuleiro[i][j] == ' ':
                    self.tabuleiro[i][j] = 'X'
                    vitoria, _ = self.verificar_fim_de_jogo()
                    self.tabuleiro[i][j] = ' '
                    if vitoria and self.vencedor == 'X':
                        return (i, j)
        return None

    def _ocupar_centro(self):
        if self.tabuleiro[1][1] == ' ':
            return (1, 1)
        return None

    def _ocupar_cantos(self):
        cantos = [(0, 0), (0, 2), (2, 0), (2, 2)]
        random.shuffle(cantos)
        for i, j in cantos:
            if self.tabuleiro[i][j] == ' ':
                return (i, j)
        return None

    def jogada_minimax_alfa_beta(self):
        melhor_valor = -float('inf')
        melhor_jogada = None
        for i in range(3):
            for j in range(3):
                if self.tabuleiro[i][j] == ' ':
                    self.tabuleiro[i][j] = 'O'
                    valor = self.minimax_alfa_beta(self.tabuleiro, 0, -float('inf'), float('inf'), False)
                    self.tabuleiro[i][j] = ' '
                    if valor > melhor_valor:
                        melhor_valor = valor
                        melhor_jogada = (i, j)
        return melhor_jogada

    def minimax_alfa_beta(self, tabuleiro_simulado, profundidade, alfa, beta, is_max):
        temp_logic = TicTacToeLogic()
        temp_logic.tabuleiro = [row[:] for row in tabuleiro_simulado]
        fim, _ = temp_logic.verificar_fim_de_jogo()
        if fim:
            return self._avaliar_resultado(temp_logic.vencedor, profundidade)

        if is_max:
            return self._minimax_branch(tabuleiro_simulado, profundidade, alfa, beta, 'O', False, max, -float('inf'))
        else:
            return self._minimax_branch(tabuleiro_simulado, profundidade, alfa, beta, 'X', True, min, float('inf'))

    def _avaliar_resultado(self, vencedor, profundidade):
        if vencedor == 'O':
            return 10 - profundidade
        elif vencedor == 'X':
            return profundidade - 10
        else:
            return 0

    def _minimax_branch(self, tabuleiro_simulado, profundidade, alfa, beta, jogador, prox_is_max, func, valor_inicial):
        melhor_valor = valor_inicial
        for i, j in self._casas_vazias(tabuleiro_simulado):
            tabuleiro_simulado[i][j] = jogador
            valor = self.minimax_alfa_beta(tabuleiro_simulado, profundidade + 1, alfa, beta, prox_is_max)
            tabuleiro_simulado[i][j] = ' '
            melhor_valor = func(melhor_valor, valor)
            if func == max:
                alfa = max(alfa, melhor_valor)
            else:
                beta = min(beta, melhor_valor)
            if beta <= alfa:
                break
        return melhor_valor

    def _casas_vazias(self, tabuleiro):
        return [(i, j) for i in range(3) for j in range(3) if tabuleiro[i][j] == ' ']

# --- Melhoria 4: Widget de tabuleiro customizado para desenhar a linha ---
class BoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.winning_line_coords = None
        self.winning_player = None

    def set_winning_line(self, start_pos, end_pos, player):
        self.winning_line_coords = (start_pos, end_pos)
        self.winning_player = player
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
    def __init__(self):
        super().__init__()
        self.jogo_logica = TicTacToeLogic()
        self.stats = {'X': 0, 'O': 0, 'Empate': 0}
        self.modo_vs_cpu = False
        self.dificuldade_cpu = 'Fácil'
        # --- Melhoria 5: Carregar temas de um ficheiro JSON ---
        self.carregar_temas()
        self.tema_atual = 'dark'
        self.setup_UI()

    def carregar_temas(self):
        try:
            theme_path = Path(__file__).parent / "themes.json"
            with open(theme_path, 'r') as f:
                self.themes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Tema padrão caso o ficheiro falhe
            self.themes = {
                "dark": {"bg": "#1a252f", "grid_bg": "#2c3e50", "cell_bg": "#34495e", "text": "#ecf0f1", "x": "#3498db", "o": "#e74c3c", "btn": "#3498db", "btn_hover": "#2980b9"},
                "light": {"bg": "#ecf0f1", "grid_bg": "#bdc3c7", "cell_bg": "#ffffff", "text": "#2c3e50", "x": "#2980b9", "o": "#c0392b", "btn": "#2980b9", "btn_hover": "#3498db"}
            }

    def setup_UI(self):
        self.setWindowTitle('Jogo da Velha')
        self.setFixedSize(400, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.criar_menu_inicial()
        self.criar_menu_nomes()
        self.criar_menu_dificuldade()
        self.criar_tela_jogo()
        
        self.aplicar_tema(self.tema_atual)
        self.stacked_widget.setCurrentIndex(0)

    def aplicar_tema(self, nome_tema):
        # --- Melhoria 6: Funcionalidade de Temas ---
        self.tema_atual = nome_tema
        theme = self.themes[nome_tema]
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: {theme['bg']}; }}
            QLabel {{ color: {theme['text']}; }}
            QPushButton {{ 
                background-color: {theme['btn']}; 
                color: white; border: none; padding: 15px; 
                font-size: 16px; border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {theme['btn_hover']}; }}
            QComboBox, QLineEdit {{ 
                border: 1px solid {theme['btn']}; border-radius: 5px; 
                padding: 10px; font-size: 14px; color: {theme['text']};
                background-color: {theme['cell_bg']};
            }}
        """)
        # Atualizar botões do tabuleiro
        if hasattr(self, 'botoes'):
            for i in range(3):
                for j in range(3):
                    self.botoes[i][j].setStyleSheet(f"background-color: {theme['cell_bg']}; border-radius: 8px;")

    def criar_menu_inicial(self):
        menu_widget = QWidget()
        layout = QVBoxLayout(menu_widget); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(20)
        title = QLabel("Jogo da Velha"); title.setFont(QFont('Arial', 32, QFont.Bold)); title.setAlignment(Qt.AlignCenter)
        btn_vs_cpu = QPushButton('Jogador vs CPU'); btn_vs_cpu.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        btn_vs_jogador = QPushButton('Jogador vs Jogador'); btn_vs_jogador.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        theme_combo = QComboBox()
        theme_combo.addItems(self.themes.keys())
        theme_combo.currentTextChanged.connect(self.aplicar_tema)

        layout.addWidget(title); layout.addWidget(btn_vs_cpu); layout.addWidget(btn_vs_jogador); layout.addWidget(theme_combo)
        self.stacked_widget.addWidget(menu_widget)

    # --- Melhoria 7: Ecrã para Nomes dos Jogadores ---
    def criar_menu_nomes(self):
        nomes_widget = QWidget()
        layout = QVBoxLayout(nomes_widget); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(15)
        title = QLabel("Nomes dos Jogadores"); title.setFont(QFont('Arial', 24, QFont.Bold))
        self.nome_jogador1 = QLineEdit(); self.nome_jogador1.setPlaceholderText("Nome do Jogador 1 (X)")
        self.nome_jogador2 = QLineEdit(); self.nome_jogador2.setPlaceholderText("Nome do Jogador 2 (O)")
        iniciar_btn = QPushButton('Iniciar Jogo'); iniciar_btn.clicked.connect(self.iniciar_jogo_vs_jogador)
        voltar_btn = QPushButton('Voltar'); voltar_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(title); layout.addWidget(self.nome_jogador1); layout.addWidget(self.nome_jogador2); layout.addWidget(iniciar_btn); layout.addWidget(voltar_btn)
        self.stacked_widget.addWidget(nomes_widget)

        self.combo_dificuldade = QComboBox(); self.combo_dificuldade.addItems([TicTacToeLogic.FACIL, TicTacToeLogic.MEDIO, TicTacToeLogic.IMPOSSIVEL])
        dificuldade_widget = QWidget()
        layout = QVBoxLayout(dificuldade_widget); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(20)
        title = QLabel("Selecione a Dificuldade"); title.setFont(QFont('Arial', 24, QFont.Bold))
        self.combo_dificuldade = QComboBox(); self.combo_dificuldade.addItems([TicTacToeLogic.FACIL, TicTacToeLogic.MEDIO, TicTacToeLogic.IMPOSSIVEL])
        iniciar_btn = QPushButton('Iniciar Jogo'); iniciar_btn.clicked.connect(self.iniciar_jogo_vs_cpu)
        voltar_btn = QPushButton('Voltar'); voltar_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(title); layout.addWidget(self.combo_dificuldade); layout.addWidget(iniciar_btn); layout.addWidget(voltar_btn)
        self.stacked_widget.addWidget(dificuldade_widget)

    def criar_tela_jogo(self):
        jogo_widget = QWidget()
        self.v_layout = QVBoxLayout(jogo_widget)
        self.placar_label = QLabel(); self.placar_label.setFont(QFont('Arial', 16)); self.placar_label.setAlignment(Qt.AlignCenter)
        self.info_label = QLabel(); self.info_label.setFont(QFont('Arial', 16)); self.info_label.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.placar_label); self.v_layout.addWidget(self.info_label)

        # Usar o widget customizado
        self.board_container = QWidget()
        grid_layout = QGridLayout(self.board_container)
        grid_layout.setSpacing(10)
        self.board_widget = BoardWidget()
        grid_layout.addWidget(self.board_widget, 0, 0, 3, 3)

        self.botoes = [[QPushButton() for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = self.botoes[i][j]; btn.setFixedSize(100, 100); btn.setFont(QFont('Arial', 36, QFont.Bold))
                btn.clicked.connect(lambda _, x=i, y=j: self.fazer_jogada_gui(x, y))
                grid_layout.addWidget(btn, i, j)
        self.v_layout.addWidget(self.board_container)
        
        btn_menu = QPushButton("Voltar ao Menu"); btn_menu.clicked.connect(self.voltar_ao_menu)
        self.v_layout.addWidget(btn_menu)
        self.stacked_widget.addWidget(jogo_widget)

    def iniciar_jogo_vs_cpu(self):
        self.modo_vs_cpu = True
        self.dificuldade_cpu = self.combo_dificuldade.currentText()
        self.jogo_logica.set_player_names("Você", "CPU")
        self.reiniciar_jogo_completo()
        self.stacked_widget.setCurrentIndex(3)

    def iniciar_jogo_vs_jogador(self):
        self.modo_vs_cpu = False
        self.jogo_logica.set_player_names(self.nome_jogador1.text(), self.nome_jogador2.text())
        self.reiniciar_jogo_completo()
        self.stacked_widget.setCurrentIndex(3)
        
    def voltar_ao_menu(self):
        # --- Melhoria 8: Estatísticas de Jogo ---
        self.stats = {'X': 0, 'O': 0, 'Empate': 0}
        self.atualizar_placar()
        self.stacked_widget.setCurrentIndex(0)

    def fazer_jogada_gui(self, x, y):
        if self.jogo_logica.vencedor or (self.modo_vs_cpu and self.jogo_logica.jogador_atual == 'O'): return
        if self.jogo_logica.fazer_jogada(x, y):
            self.atualizar_botao(x, y)
            self.verificar_estado_jogo()

    def jogada_cpu_gui(self):
        if not self.jogo_logica.vencedor:
            jogada = self.jogo_logica.estrategia_cpu(self.dificuldade_cpu)
            if jogada:
                self.jogo_logica.fazer_jogada(jogada[0], jogada[1])
                self.atualizar_botao(jogada[0], jogada[1])
                self.verificar_estado_jogo()

    def verificar_estado_jogo(self):
        fim, linha_vencedora = self.jogo_logica.verificar_fim_de_jogo()
        if fim:
            self.fim_de_jogo(linha_vencedora)
        else:
            self.jogo_logica.alternar_jogador()
            nome_jogador = self.jogo_logica.player_names[self.jogo_logica.jogador_atual]
            self.info_label.setText(f"Vez de: {nome_jogador} ({self.jogo_logica.jogador_atual})")
            if self.modo_vs_cpu and self.jogo_logica.jogador_atual == 'O':
                QTimer.singleShot(500, self.jogada_cpu_gui)

    def fim_de_jogo(self, linha_vencedora):
        vencedor = self.jogo_logica.vencedor
        if vencedor == "Empate":
            msg = "O jogo terminou empatado!"; self.info_label.setText("Empate!"); self.stats['Empate'] += 1
        else:
            nome_vencedor = self.jogo_logica.player_names[vencedor]
            msg = f'{nome_vencedor} ({vencedor}) venceu!'; self.info_label.setText(f"{nome_vencedor} Venceu!")
            self.stats[vencedor] += 1
            self.destacar_vitoria(linha_vencedora)
        
        self.atualizar_placar()
        QTimer.singleShot(1500, lambda: (QMessageBox.information(self, 'Fim de Jogo', msg), self.reiniciar_jogo()))

    def reiniciar_jogo(self):
        self.jogo_logica.reset_board()
        self.board_widget.clear_line()
        theme = self.themes[self.tema_atual]
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setText('')
                self.botoes[i][j].setStyleSheet(f"background-color: {theme['cell_bg']}; border-radius: 8px;")
        nome_jogador = self.jogo_logica.player_names[self.jogo_logica.jogador_atual]
        self.info_label.setText(f"Vez de: {nome_jogador} ({self.jogo_logica.jogador_atual})")

    def reiniciar_jogo_completo(self):
        self.stats = {'X': 0, 'O': 0, 'Empate': 0}
        self.atualizar_placar()
        self.reiniciar_jogo()

    def atualizar_botao(self, x, y):
        # --- Melhoria 9: Animação de Jogada ---
        jogador = self.jogo_logica.tabuleiro[x][y]
        btn = self.botoes[x][y]
        btn.setText(jogador)
        theme = self.themes[self.tema_atual]
        cor_jogador = theme['x'] if jogador == 'X' else theme['o']
        btn.setStyleSheet(f"color: {cor_jogador}; background-color: {theme['grid_bg']}; font-size: 36px; font-weight: bold; border-radius: 8px;")
        
        self.anim = QPropertyAnimation(btn, b"geometry")
        self.anim.setDuration(150)
        start_rect = btn.geometry()
        self.anim.setStartValue(QRect(start_rect.center(), start_rect.size()/2))
        self.anim.setEndValue(start_rect)
        self.anim.setEasingCurve(QEasingCurve.OutBounce)
        self.anim.start()

    def destacar_vitoria(self, linha):
        # --- Melhoria 10: Linha de Vitória Visual ---
        start_cell, end_cell = self.botoes[linha[0][0]][linha[0][1]], self.botoes[linha[2][0]][linha[2][1]]
        start_pos = start_cell.geometry().center()
        end_pos = end_cell.geometry().center()
        self.board_widget.set_winning_line(start_pos, end_pos, self.jogo_logica.vencedor)

    def atualizar_placar(self):
        self.placar_label.setText(f"{self.jogo_logica.player_names['X']}: {self.stats['X']} | "
                                  f"{self.jogo_logica.player_names['O']}: {self.stats['O']} | "
                                  f"Empates: {self.stats['Empate']}")

if __name__ == '__main__':
    # Criar ficheiro de temas se não existir
    theme_path = Path(__file__).parent / "themes.json"
    if not theme_path.exists():
        default_themes = {
            "dark": {"bg": "#1a252f", "grid_bg": "#2c3e50", "cell_bg": "#34495e", "text": "#ecf0f1", "x": "#3498db", "o": "#e74c3c", "btn": "#3498db", "btn_hover": "#2980b9"},
            "light": {"bg": "#ecf0f1", "grid_bg": "#bdc3c7", "cell_bg": "#ffffff", "text": "#2c3e50", "x": "#2980b9", "o": "#c0392b", "btn": "#2980b9", "btn_hover": "#3498db"}
        }
        with open(theme_path, 'w') as f:
            json.dump(default_themes, f, indent=4)

    app = QApplication(sys.argv)
    jogo = JogoDaVelhaGUI()
    jogo.show()
    sys.exit(app.exec_())
