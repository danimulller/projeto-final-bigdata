# Laboratório Airflow

Este repositório é o projeto final da disciplina de Engenharia de Dados.

## Arquitetura dos Dados
![Captura de tela 2024-11-03 184539](https://github.com/user-attachments/assets/3fef8925-f561-44de-bc0b-0900d1fee394)

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

![nifi](https://github.com/user-attachments/assets/dd509862-cf7c-4e5e-b012-606032e92531)

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

![minio](https://github.com/user-attachments/assets/e84bc812-ac92-4da9-8b2c-f933363d318b)

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

![airflow](https://github.com/user-attachments/assets/1f6f19d7-dc25-4b65-a281-6925e5f8a620)

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
CREATE DATABASE IF NOT EXISTS sp_trans LOCATION 's3a://trusted/';
```

```sql
CREATE EXTERNAL TABLE sp_trans.posicao (
  	letreiro STRING,
	codigo_linha BIGINT,
	sentido_operacao BIGINT,
	letreiro_destino STRING,
	letreiro_origem STRING,
	prefixo BIGINT,
	acessivel BOOLEAN,
	horario STRING,
	latitude DOUBLE,
	longitude DOUBLE
)
PARTITIONED BY (ano string, mes string, dia string, hora string)
STORED AS PARQUET
LOCATION 's3a://trusted/posicao/';
```

```sql
MSCK REPAIR TABLE sp_trans.posicao;
```

## Configurar Presto e Metabase

1. Execute o seguinte comando:

```shell
docker-compose up -d presto metabase
```

2. Conect-se ao Metabase em [http://localhost:3000](http://localhost:3000)
3. Configure a conexão do Metabase com o Presto:
    - `Host: presto`
    - `Porta: 8080`
    - `Nome de Usuário: hive`
    - `Schema: sp_trans`
