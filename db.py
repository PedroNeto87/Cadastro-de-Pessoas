import sqlite3

class DataBase:
    def __init__(self, name = 'cadastros.db') -> None:
        self.name = name

    def conectar(self):
        self.conexao = sqlite3.connect(self.name)

    def desconectar(self):
        try:
            self.conexao.close()
        except ConnectionError:
            print('Erro: Não foi possível conectar ao banco de dados')

    def tabPessoas(self):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Pessoas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT,
                nome TEXT,
                dtNasc DATE,
                cep TEXT,
                logradouro TEXT,
                numero TEXT,
                bairro TEXT,
                cidade TEXT,
                uf TEXT,
                telFixo TEXT,
                telCelular TEXT,
                email TEXT
                );
            """)
        except AttributeError:
            print('Não foi possível criar a tabela de pessoas.')

    def inserirPessoa(self, cpf, nome, dtNasc, cep, logradouro, numero, bairro, cidade, uf, telFixo, telCelular, email):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("""INSERT INTO Pessoas (cpf, nome, dtNasc, cep, logradouro, numero, bairro, cidade, uf, telFixo, telCelular, email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (cpf, nome, dtNasc, cep, logradouro, numero, bairro, cidade, uf, telFixo, telCelular, email))
            self.conexao.commit()
        except Exception as ex:
            print(f'Erro: {ex}')

    def selectPessoas(self):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("SELECT * FROM Pessoas ORDER BY id")
            pessoas = cursor.fetchall()
            return pessoas
        except AttributeError:
            print('Faça a conexão')

    def editarPessoa(self, fullDataSet):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(f"""UPDATE Pessoas SET
                id = '{fullDataSet[0]}',
                cpf = '{fullDataSet[1]}',
                nome = '{fullDataSet[2]}',
                dtNasc = '{fullDataSet[3]}',
                cep = '{fullDataSet[4]}',
                logradouro = '{fullDataSet[5]}',
                numero = '{fullDataSet[6]}',
                bairro = '{fullDataSet[7]}',
                cidade = '{fullDataSet[8]}',
                uf = '{fullDataSet[9]}',
                telFixo = '{fullDataSet[10]}',
                telCelular = '{fullDataSet[11]}',
                email = '{fullDataSet[12]}'

                WHERE id = '{fullDataSet[0]}'
            """)
            self.conexao.commit()
        except AttributeError:
            print('Faça a conexão')

    def deletarPessoa(self, id):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(f"DELETE FROM Pessoas WHERE id = {id}")
            self.conexao.commit()
            return('Cadastro excluído com sucesso')
        except:
            return('Erro ao excluir cadastro.')
