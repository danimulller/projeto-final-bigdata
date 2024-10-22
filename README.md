# Laboratório Airflow

Este repositório é o projeto final da disciplina de Engenharia de Dados.

## Inicializar o Ambiente

Clone o respositório e execute o seguinte comando:

```shell
docker-compose up -d minio nifi
```

## Configurar o Nifi

1. Conecte-se ao Nifi via [http://localhost:49090/](http://localhost:49090/).
2. Clique em `Upload Template` dentro do bloco `Operate`.
3. Busque o arquivo `projeto-final-bigdata/nifi/Template_Projeto_Final.xml`
4. Aplique o template carregado arrastando `Template` da barra superior, para o centro da tela.
5. Escolhe o template carregado.
6. Clique na engrenagem em `Operate`.
7. Clique em `Process group parameter context`, crie um novo contexto com as seguintes parâmetros.
    - `url: http://api.olhovivo.sptrans.com.br/v2.1/`
    - `token: SEU TOKEN EM https://www.sptrans.com.br/desenvolvedores/perfil-desenvolvedor/meus-aplicativos/`

## Configurar o Minio

1. Acesse a interface do Minio em [http://localhost:9051](http://localhost:9051) e faça login com:
    - `admin`
    - `minioadmin`
2. Vá para `Access Keys` -> `Create access key`:
    - `Acess Key: datalake`
    - `Secret Key: datalake`
3. Clique em `Create`:

## Testando a conexão

1. Vá até a tela do Nifi, clique com o botão direito no fundo da tela e em `Start`.
2. Se tudo estiver correto, os retornos .json devem aparecer dentro do bucket `raw` no Minio.

## Configurar o Airflow

1. Execute os seguintes comandos:
    - `docker-compose up -d airflow-scheduler airflow-worker`
    - `docker-compose run --rm airflow-webserver airflow db init`
    - `docker-compose up -d airflow-webserver`
2. - Crie um usuário Admin:
    - `docker compose -f docker-compose.yml exec airflow-webserver bash`
    - `airflow users create \
        --username admin \
        --firstname Firstname \
        --lastname Lastname \
        --role Admin \
        --email admin@example.com \
        --password admin`
3. Conect-se ao Airflow em [http://localhost:58080](http://localhost:58080)
4. Criando a conexão com o Minio:
    - Clique em `Admin` -> `Connections` -> `+`
    - `Connection Id: s3_minio`
    - `Connection Type: Amazon Web Services`
    - `AWS Access Key ID: datalake`
    - `AWS Secret Access Key: datalake`
    - `Extra: { "aws_access_key_id": "datalake", "aws_secret_access_key": "datalake", "host": "http://localhost:9050" }`