from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

# Uma DAG representa um workflow, um conjunto de task
with DAG(
        dag_id="ola_mundo",  # nome da DAG
        start_date=datetime(2024, 8, 1),  # A data em que o DAG deve começar a funcionar pela primeira vez
        end_date=datetime(2024, 8, 6),  # A data em que o DAG deve encerrar o funcionamento
        schedule_interval=None
) as dag:
    # As Tasks são representadas por operadores
    hello = BashOperator(task_id="exibir_mensagem", bash_command="echo 'olá mundo'")

    @task()
    def airflow():
        print("teste!!!")

    # Definindo a dependencia entre tasks
    hello >> airflow()