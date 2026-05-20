-- ============================================================
-- MIGRATION: adequar tabela ocorrencias ao novo schema
-- EXECUTAR COMO gestao_sac
-- ============================================================

-- 1. Adicionar colunas novas
ALTER TABLE ocorrencias ADD id_carregamento         INTEGER;
ALTER TABLE ocorrencias ADD data_faturamento        DATE;
ALTER TABLE ocorrencias ADD data_saida_carregamento DATE;
ALTER TABLE ocorrencias ADD valor_total             NUMBER(15, 2);
ALTER TABLE ocorrencias ADD encaminhamento          VARCHAR2(2000);

-- 2. Renomear coluna antiga (DATA_SAIDA_CARGA já existia, mas agora temos a nova)
--    Marcar as colunas antigas como UNUSED (Oracle não permite DROP direto com dados)
ALTER TABLE ocorrencias SET UNUSED COLUMN numero_carregamento;
ALTER TABLE ocorrencias SET UNUSED COLUMN tipo_carregamento;
ALTER TABLE ocorrencias SET UNUSED COLUMN data_saida_carga;

-- 3. Atualizar constraint de SITUACAO
ALTER TABLE ocorrencias DROP CONSTRAINT ck_ocor_situacao;
ALTER TABLE ocorrencias ADD CONSTRAINT ck_ocor_situacao CHECK (situacao IN (
    'DEVOLUCAO_TOTAL', 'DEVOLUCAO_PARCIAL', 'INVERSAO_MERCADORIA',
    'SOBRA', 'AVARIA', 'COLETA'
));

-- 4. Atualizar constraint de STATUS
ALTER TABLE ocorrencias DROP CONSTRAINT ck_ocor_status;
ALTER TABLE ocorrencias ADD CONSTRAINT ck_ocor_status CHECK (status IN (
    'NOVO', 'ENCAMINHADO', 'FINALIZADO'
));

COMMIT;
