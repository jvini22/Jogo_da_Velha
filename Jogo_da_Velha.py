import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QMessageBox, QMainWindow, QAction, QComboBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QTimer

class JogoDaVelhaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Jogo da Velha')
        self.setFixedSize(600, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.v_layout = QVBoxLayout(self.central_widget)

        self.tabuleiro = [[' ']*3 for _ in range(3)]
        self.jogador_atual = 'X'  # Jogador começa como 'X'
        self.modo_vs_cpu = False
        self.dificuldade_cpu = 'Fácil'  # Definição inicial da dificuldade da CPU

        self.menu_inicial()

    def menu_inicial(self):
        self.limpar_layout()

        title = QLabel("Bem-vindo ao Jogo da Velha!", self)
        title.setFont(QFont('Arial', 20))
        title.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(title)

        self.btn_jogar = QPushButton('Jogar', self)
        self.btn_jogar.setFont(QFont('Arial', 16))
        self.btn_jogar.clicked.connect(self.selecionar_modo)
        self.v_layout.addWidget(self.btn_jogar)

        self.btn_dificuldade = QPushButton('Selecionar Dificuldade', self)
        self.btn_dificuldade.setFont(QFont('Arial', 16))
        self.btn_dificuldade.clicked.connect(self.selecionar_dificuldade)
        self.v_layout.addWidget(self.btn_dificuldade)

        self.btn_temas = QPushButton('Escolher Tema', self)
        self.btn_temas.setFont(QFont('Arial', 16))
        self.btn_temas.clicked.connect(self.selecionar_tema)
        self.v_layout.addWidget(self.btn_temas)

    def selecionar_modo(self):
        self.limpar_layout()

        title = QLabel("Selecione o Modo de Jogo:", self)
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(title)

        self.btn_vs_cpu = QPushButton('Jogar contra CPU', self)
        self.btn_vs_cpu.setFont(QFont('Arial', 16))
        self.btn_vs_cpu.clicked.connect(self.iniciar_jogo_vs_cpu)
        self.v_layout.addWidget(self.btn_vs_cpu)

        self.btn_vs_jogador = QPushButton('Jogar contra Jogador', self)
        self.btn_vs_jogador.setFont(QFont('Arial', 16))
        self.btn_vs_jogador.clicked.connect(self.iniciar_jogo_vs_jogador)
        self.v_layout.addWidget(self.btn_vs_jogador)

    def selecionar_dificuldade(self):
        self.limpar_layout()

        title = QLabel("Selecione a Dificuldade da CPU:", self)
        title.setFont(QFont('Arial', 18))
        title.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(title)

        dificuldade = QComboBox(self)
        dificuldade.addItems(['Fácil', 'Médio', 'Difícil'])
        dificuldade.setFont(QFont('Arial', 16))
        dificuldade.currentTextChanged.connect(self.definir_dificuldade)
        self.v_layout.addWidget(dificuldade)

        voltar_btn = QPushButton('Voltar', self)
        voltar_btn.setFont(QFont('Arial', 16))
        voltar_btn.clicked.connect(self.menu_inicial)
        self.v_layout.addWidget(voltar_btn)

    def definir_dificuldade(self, dificuldade):
        self.dificuldade_cpu = dificuldade

    def selecionar_tema(self):
        QMessageBox.information(self, 'Tema', 'Função de mudança de tema ainda será implementada.')
        self.menu_inicial()

    def iniciar_jogo_vs_cpu(self):
        self.modo_vs_cpu = True
        self.iniciar_jogo()

    def iniciar_jogo_vs_jogador(self):
        self.modo_vs_cpu = False
        self.iniciar_jogo()

    def iniciar_jogo(self):
        self.limpar_layout()

        # Informação sobre o jogador atual
        self.info_label = QLabel(f"Vez do jogador {self.jogador_atual}", self)
        self.info_label.setFont(QFont('Arial', 16))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.info_label)

        # Layout para o tabuleiro
        grid_layout = QGridLayout()
        self.botoes = [[QPushButton(self) for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setFixedSize(100, 100)
                self.botoes[i][j].setFont(QFont('Arial', 24))
                self.botoes[i][j].clicked.connect(lambda _, x=i, y=j: self.fazer_jogada(x, y))
                grid_layout.addWidget(self.botoes[i][j], i, j)
        self.v_layout.addLayout(grid_layout)

        self.reiniciar_jogo()

    def fazer_jogada(self, x, y):
        if self.tabuleiro[x][y] == ' ':
            self.tabuleiro[x][y] = self.jogador_atual
            self.botoes[x][y].setText(self.jogador_atual)

            if self.verificar_vitoria():
                self.mostrar_vencedor(self.jogador_atual)
            elif self.verificar_empate():
                self.mostrar_empate()
            else:
                self.alternar_jogador()
                if self.modo_vs_cpu and self.jogador_atual == 'O':
                    QTimer.singleShot(500, self.jogada_cpu)  # Pequeno atraso para simular a CPU jogando

    def jogada_cpu(self):
        jogada = self.estrategia_cpu()
        self.fazer_jogada(jogada[0], jogada[1])

    def estrategia_cpu(self):
        if self.dificuldade_cpu == 'Fácil':
            return self.jogada_aleatoria()
        elif self.dificuldade_cpu == 'Médio':
            return self.jogada_aleatoria()  # Implementação pode ser melhorada
        elif self.dificuldade_cpu == 'Difícil':
            return self.jogada_minimax()

    def jogada_aleatoria(self):
        jogadas_possiveis = [(i, j) for i in range(3) for j in range(3) if self.tabuleiro[i][j] == ' ']
        return random.choice(jogadas_possiveis)

    def jogada_minimax(self):
        melhor_valor = -float('inf')
        melhor_jogada = None
        for i in range(3):
            for j in range(3):
                if self.tabuleiro[i][j] == ' ':
                    self.tabuleiro[i][j] = 'O'
                    valor = self.minimax(self.tabuleiro, 0, False)
                    self.tabuleiro[i][j] = ' '
                    if valor > melhor_valor:
                        melhor_valor = valor
                        melhor_jogada = (i, j)
        return melhor_jogada

    def minimax(self, tabuleiro, profundidade, is_max):
        if self.verificar_vitoria():
            return 10 - profundidade if is_max else profundidade - 10
        if self.verificar_empate():
            return 0

        if is_max:
            melhor_valor = -float('inf')
            for i in range(3):
                for j in range(3):
                    if tabuleiro[i][j] == ' ':
                        tabuleiro[i][j] = 'O'
                        valor = self.minimax(tabuleiro, profundidade + 1, False)
                        tabuleiro[i][j] = ' '
                        melhor_valor = max(melhor_valor, valor)
            return melhor_valor
        else:
            melhor_valor = float('inf')
            for i in range(3):
                for j in range(3):
                    if tabuleiro[i][j] == ' ':
                        tabuleiro[i][j] = 'X'
                        valor = self.minimax(tabuleiro, profundidade + 1, True)
                        tabuleiro[i][j] = ' '
                        melhor_valor = min(melhor_valor, valor)
            return melhor_valor

    def alternar_jogador(self):
        self.jogador_atual = 'O' if self.jogador_atual == 'X' else 'X'
        self.info_label.setText(f"Vez do jogador {self.jogador_atual}")

    def verificar_vitoria(self):
        for i in range(3):
            if self.tabuleiro[i][0] == self.tabuleiro[i][1] == self.tabuleiro[i][2] != ' ':
                return True
            if self.tabuleiro[0][i] == self.tabuleiro[1][i] == self.tabuleiro[2][i] != ' ':
                return True
        if self.tabuleiro[0][0] == self.tabuleiro[1][1] == self.tabuleiro[2][2] != ' ':
            return True
        if self.tabuleiro[0][2] == self.tabuleiro[1][1] == self.tabuleiro[2][0] != ' ':
            return True
        return False

    def verificar_empate(self):
        for linha in self.tabuleiro:
            if ' ' in linha:
                return False
        return True

    def mostrar_vencedor(self, vencedor):
        QMessageBox.information(self, 'Fim de jogo', f'O jogador {vencedor} venceu!')
        self.desativar_botoes()

    def mostrar_empate(self):
        QMessageBox.information(self, 'Fim de jogo', 'O jogo terminou em empate!')
        self.desativar_botoes()

    def desativar_botoes(self):
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setEnabled(False)

    def reiniciar_jogo(self):
        self.tabuleiro = [[' ']*3 for _ in range(3)]
        self.jogador_atual = 'X'
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].setText('')
                self.botoes[i][j].setEnabled(True)

    def limpar_layout(self):
        while self.v_layout.count():
            child = self.v_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JogoDaVelhaGUI()
    ex.show()
    sys.exit(app.exec_())