-- ============================================================
-- EXECUTAR COMO SYSDBA ou usuário com privilégio DBA
-- Conectar em: sqlplus sys/senha@192.168.0.98:1521/WINT as sysdba
-- ============================================================

-- 1. Criar o usuário/schema de escrita
CREATE USER ocorrencias_app IDENTIFIED BY "senha_aqui"
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;

-- 2. Privilégios mínimos necessários
GRANT CREATE SESSION     TO ocorrencias_app;
GRANT CREATE TABLE       TO ocorrencias_app;
GRANT CREATE SEQUENCE    TO ocorrencias_app;
GRANT CREATE TRIGGER     TO ocorrencias_app;

COMMIT;
