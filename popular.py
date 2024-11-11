import pandas as pd
from sqlalchemy import create_engine, String, Enum
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, date
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

# Configurações do banco de dados (SQLite, mas pode ser substituído por outro tipo)
DATABASE_URL = f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"

# Definição da classe base
class Base(DeclarativeBase):
    pass

# Configuração do SQLAlchemy e da classe base
engine = create_engine(DATABASE_URL)

# Definição da tabela com o novo padrão SQLAlchemy
class Aluno(Base):
    __tablename__ = 'alunos'

    ra: Mapped[str] = mapped_column(String(20), primary_key=True)
    dig_ra: Mapped[Optional[str]] = mapped_column(String(5), primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data_nascimento: Mapped[Optional[date]] = mapped_column(nullable=True)  # Use `date` como tipo Python
    email_microsoft: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email_google: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    situacao_aluno: Mapped[Optional[str]] = mapped_column(Enum(
        'Ativo', 'Não Comparecimento', 'Remanejamento', 'Transferido', 'BAIXA - TRANSFERÊNCIA', name='situacao_enum'), nullable=True
    )
    turma: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

# Cria a tabela no banco de dados
Base.metadata.create_all(engine)

# Função para popular os dados a partir de um CSV
def popular_dados_csv(caminho_csv):
    # Carrega o CSV
    df = pd.read_csv(caminho_csv, delimiter=',')

    # Abre a sessão
    with Session(engine) as session:
        for _, row in df.iterrows():
            # Converte `RA` e `Dig. RA` para string para evitar erro de tipo
            ra = str(row['RA'])
            dig_ra = str(row['Dig. RA'])

            # Verifica se o registro já existe
            aluno_existente = session.query(Aluno).filter_by(ra=ra, dig_ra=dig_ra).first()
            
            # Se o aluno já existe, atualiza o registro apenas se a situação for "Ativo"
            if aluno_existente:
                if aluno_existente.situacao_aluno != "Ativo" and row['Situação do Aluno'] == "Ativo":
                    # Atualiza os campos necessários
                    aluno_existente.nome = row['Nome do Aluno']
                    aluno_existente.data_nascimento = (
                        datetime.strptime(row['Data de Nascimento'], '%d/%m/%Y').date()
                        if not pd.isnull(row['Data de Nascimento']) else None
                    )
                    aluno_existente.email_microsoft = row['Email Microsoft']
                    aluno_existente.email_google = row['Email Google']
                    aluno_existente.situacao_aluno = row['Situação do Aluno']
                    aluno_existente.turma = row['Turma']
            else:
                # Cria um novo registro se não houver duplicata
                aluno = Aluno(
                    nome=row['Nome do Aluno'],
                    ra=ra,
                    dig_ra=dig_ra,
                    data_nascimento=(
                        datetime.strptime(row['Data de Nascimento'], '%d/%m/%Y').date()
                        if not pd.isnull(row['Data de Nascimento']) else None
                    ),
                    email_microsoft=row['Email Microsoft'],
                    email_google=row['Email Google'],
                    situacao_aluno=row['Situação do Aluno'],
                    turma=row['Turma']
                )
                session.add(aluno)

        # Confirma as alterações
        session.commit()
        print("Dados inseridos ou atualizados com sucesso!")



# Caminho do arquivo CSV
caminho_csv = './file.csv'
popular_dados_csv(caminho_csv)

