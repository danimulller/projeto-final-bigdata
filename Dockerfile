FROM apache/airflow:2.7.3

# Instalar dependências do sistema
USER root
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    build-essential \
    python3-dev \
    gcc \
    libffi-dev \
    libssl-dev \
    && apt-get clean

# Configurar JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
ENV PATH $JAVA_HOME/bin:$PATH

# Instalar dependências do Python
USER airflow
RUN pip install --upgrade pip && \
    pip install boto3 botocore apache-airflow-providers-amazon