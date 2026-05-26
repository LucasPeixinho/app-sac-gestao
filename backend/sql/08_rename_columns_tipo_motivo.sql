-- Migration 08: Renomear colunas tipo_ocorrencia → motivo e impacto → tipo_ocorrencia
-- Executar como usuário gestao_sac
--
-- Contexto:
--   Antes: tipo_ocorrencia = AVARIA/FALTA_MERCADORIA (era o "motivo")
--          impacto         = DEVOLUCAO_TOTAL/REENVIO  (era o "tipo")
--   Depois: motivo          = AVARIA/FALTA_MERCADORIA
--           tipo_ocorrencia = DEVOLUCAO_TOTAL/REENVIO

-- 1. Renomear a coluna que guardava o motivo da ocorrência
ALTER TABLE gestao_sac.ocorrencias RENAME COLUMN tipo_ocorrencia TO motivo;

-- 2. Renomear a coluna que guardava o tipo/impacto da ocorrência
ALTER TABLE gestao_sac.ocorrencias RENAME COLUMN impacto TO tipo_ocorrencia;

COMMIT;
