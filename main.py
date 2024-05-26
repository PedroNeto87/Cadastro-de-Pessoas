import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from PyQt5.uic import loadUi
from ui_main import Ui_MainWindow
from consultaApi import consultaCep
from db import DataBase
from reportlab.lib.pagesizes import A3, A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.txt_cpf.editingFinished.connect(self.verificarCpf)
        self.txt_cep.editingFinished.connect(self.consultarApi)
        self.btn_salvar.clicked.connect(self.cadastrarPessoa)
        self.btn_cadastros.clicked.connect(self.telaTabela)


    def verificarCpf(self):
        cpf = self.txt_cpf.text()
        if self.validarCPF(cpf):
            self.lbl_cpf.setText('CPF Válido')
            self.lbl_cpf.setStyleSheet('color: green')
        else:
            self.lbl_cpf.setText('CPF Inválido')
            self.lbl_cpf.setStyleSheet('color: red')
            self.lbl_cpf.setAlignment(Qt.AlignCenter)

    def validarCPF(self, cpf):
        cpf = ''.join(filter(str.isdigit, cpf))

        if len(cpf) != 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        if resto < 2:
            digito_verificador1 = 0
        else:
            digito_verificador1 = 11 - resto

        if int(cpf[9]) != digito_verificador1:
            return False

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        if resto < 2:
            digito_verificador2 = 0
        else:
            digito_verificador2 = 11 - resto

        if int(cpf[10]) != digito_verificador2:
            return False
        return True

    def consultarApi(self):
        campos = consultaCep(self.txt_cep.text().replace('.', '').replace('-', ''))

        self.txt_logradouro.setText(campos[0])
        self.txt_numero.setText(campos[1])
        self.txt_bairro.setText(campos[2])
        self.txt_municipio.setText(campos[3])
        self.txt_uf.setText(campos[4])

    def cadastrarPessoa(self):
        cpf = self.txt_cpf.text()
        nome = self.txt_nome.text()
        dtNasc = self.dt_nascimento.date().toString("dd-MM-yyyy")
        cep = self.txt_cep.text()
        logradouro = self.txt_logradouro.text()
        numero = self.txt_numero.text()
        bairro = self.txt_bairro.text()
        cidade = self.txt_municipio.text()
        uf = self.txt_uf.text()
        telFixo = self.txt_fixo.text()
        telCelular = self.txt_celular.text()
        email = self.txt_email.text()

        db = DataBase()
        db.conectar()
        db.inserirPessoa(cpf, nome, dtNasc, cep, logradouro, numero, bairro, cidade, uf, telFixo, telCelular, email)
        db.desconectar()

        msg = QMessageBox()
        msg.setWindowTitle('Cadastro de Pessoa')
        msg.setText('Cadastro realizado com sucesso')
        msg.exec()

        self.txt_cpf.setText('')
        self.txt_nome.setText('')
        self.dt_nascimento.setDate(QDate.currentDate())
        self.txt_cep.setText('')
        self.txt_logradouro.setText('')
        self.txt_numero.setText('')
        self.txt_bairro.setText('')
        self.txt_municipio.setText('')
        self.txt_uf.setText('')
        self.txt_fixo.setText('')
        self.txt_celular.setText('')
        self.txt_email.setText('')

    def telaTabela(self):
        telaTabela = QDialog()
        loadUi('ui_tabela.ui', telaTabela)

        telaTabela.btn_editar.clicked.connect(lambda: self.editarPessoa(telaTabela))
        telaTabela.btn_excluir.clicked.connect(lambda: self.excluirPessoa(telaTabela))
        telaTabela.btn_imprimir.clicked.connect(lambda: self.imprimir(self.obterDadosTabela(telaTabela)))

        self.dadosTabela(telaTabela)

        telaTabela.exec_()
    
    def dadosTabela(self, telaTabela):
        db = DataBase()
        db.conectar()
        pessoas = db.selectPessoas()

        telaTabela.tb_pessoas.clearContents()
        telaTabela.tb_pessoas.setRowCount(len(pessoas))

        for linha, texto in enumerate(pessoas):
            for coluna, dado in enumerate(texto):
                telaTabela.tb_pessoas.setItem(linha, coluna, QTableWidgetItem(str(dado)))
        
        db.desconectar()

        telaTabela.tb_pessoas.setSortingEnabled(True)
        
        for i in range(1, 13):
            telaTabela.tb_pessoas.resizeColumnToContents(i)

    def editarPessoa(self, telaTabela):
        dados = []
        atualizarDados = []

        for linha in range(telaTabela.tb_pessoas.rowCount()):
            for coluna in range(telaTabela.tb_pessoas.columnCount()):
                dados.append(telaTabela. tb_pessoas.item(linha, coluna).text())
            atualizarDados.append(dados)
            dados = []

        db = DataBase()
        db.conectar()
        for pessoas in atualizarDados:
            db.editarPessoa(tuple(pessoas))
        db.desconectar()

        msg = QMessageBox()
        msg.setWindowTitle('Cadastro de Pessoa')
        msg.setText('Cadastro alterado com sucesso')
        msg.exec()

    def excluirPessoa(self, telaTabela):
        db = DataBase()
        db.conectar()

        msg = QMessageBox()
        msg.setWindowTitle('Excluir')
        msg.setText('Este registro será excluido')
        msg.setInformativeText('Você tem certeza que deseja excluir esse cadastro?')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        resp = msg.exec()

        if resp == QMessageBox.Yes:
            id = telaTabela.tb_pessoas.selectionModel().currentIndex().siblingAtColumn(0).data()
            resultado = db.deletarPessoa(id)
            self.dadosTabela(telaTabela)

            msg = QMessageBox()
            msg.setWindowTitle('Pessoas')
            msg.setText(resultado)
            msg.exec()
        
        db.desconectar()

    def obterDadosTabela(self, telaTabela):
        pessoas = []
        for row in range(telaTabela.tb_pessoas.rowCount()):
            pessoa = []
            for column in range(telaTabela.tb_pessoas.columnCount()):
                item = telaTabela.tb_pessoas.item(row, column)
                pessoa.append(item.text() if item is not None else '')
            pessoas.append(pessoa)
        return pessoas

    def imprimir(self, pessoas):
        doc = SimpleDocTemplate("tb_pessoas.pdf", pagesize=A4)
        elementos = []

        # Cabeçalho da tabela
        cabeçalho = ['ID', 'CPF', 'Nome', 'Data de Nascimento', 'CEP', 'Logradouro', 'Número', 'Bairro', 'Cidade', 'UF', 'Telefone Fixo', 'Telefone Celular', 'Email']
        elementos.append(cabeçalho)

        # Dados da tabela
        for pessoa in pessoas:
            linha = []
            for dado in pessoa:
                # Verifica se o comprimento do texto excede um certo limite
                if len(dado) > 30:
                    # Divide o texto em linhas se exceder o limite
                    linhas = dado.split('\n')
                    # Cria parágrafos para cada linha
                    for linha_texto in linhas:
                        estilo_paragrafo = getSampleStyleSheet()["Normal"]
                        paragrafo = Paragraph(linha_texto, estilo_paragrafo)
                        linha.append(paragrafo)
                else:
                    linha.append(dado)
        elementos.append(linha)

        # Estilo da tabela
        estilo = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

        # Criando a tabela
        tabela = Table(elementos)
        tabela.setStyle(estilo)

        # Adicionando a tabela ao documento
        doc.build([tabela])



if  __name__ == '__main__':
    db = DataBase()
    db.conectar()
    db.tabPessoas()
    db.desconectar()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())