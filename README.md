# Laboratório Airflow

Este repositório é o projeto final da disciplina de Engenharia de Dados.

## Arquitetura dos Dados
![arquitetura](https://github.com/user-attachments/assets/3c378656-7a07-439e-821a-fe4b62944f7a)

## Inicializar o Ambiente

Clone o respositório e siga as instruções:

## Configurar o Nifi

```shell
docker-compose up -d nifi
```

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

```shell
docker-compose up -d minio
```

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

```shell
docker-compose build
docker-compose up -d airflow-webserver
```

2. Crie um usuário Admin:

```shell
docker exec -it airflow-webserver /bin/bash
airflow users create --username admin --firstname Firstname --lastname Lastname --role Admin --email admin@example.com --password admin
```

3. Adicione acesso à pasta do Airflow:

```shell
sudo chmod -R 777 airflow/
```

4. Conect-se ao Airflow em [http://localhost:58080](http://localhost:58080)
5. Criando a conexão com o Minio:
    - Clique em `Admin` -> `Connections` -> `+`
    - `Connection Id: s3_minio`
    - `Connection Type: Amazon Web Services`
    - `AWS Access Key ID: datalake`
    - `AWS Secret Access Key: datalake`
    - `Extra: { "aws_access_key_id": "datalake", "aws_secret_access_key": "datalake", "host": "http://minio:9000" }`

## Configurar o Hive

1. Execute o seguinte comando:

```shell
docker-compose up -d hive datanode
```

2. Entre no DBeaver e crie uma conexão Apache Hive:
    - `Host: localhost`
    - `Porta: 1000`
    - `Nome de Usuário: datalake`
    - `Senha: datalake`

3. Abra um script SQL e crie a conexão com a pasta `posicao` do Minio:

```sql
CREATE EXTERNAL TABLE posicao (
  	letreiro STRING,
	codigo_linha INT,
	sentido_operacao INT,
	letreiro_destino STRING,
	letreiro_origem STRING,
	prefixo INT,
	acessivel BOOLEAN,
	horario STRING,
	latitude FLOAT,
	longitude FLOAT
)
STORED AS PARQUET
LOCATION 's3a://trusted/posicao/';
```

4. Teste a conexão:

```sql
SELECT * FROM default.posicao LIMIT 10
```
