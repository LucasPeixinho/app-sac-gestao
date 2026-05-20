-- Migration: renomear situações para singular (SOBRAS->SOBRA, AVARIAS->AVARIA, COLETAS->COLETA)
-- Executar como gestao_sac

-- 1. Atualizar registros existentes (se houver)
UPDATE ocorrencias SET situacao = 'SOBRA'  WHERE situacao = 'SOBRAS';
UPDATE ocorrencias SET situacao = 'AVARIA' WHERE situacao = 'AVARIAS';
UPDATE ocorrencias SET situacao = 'COLETA' WHERE situacao = 'COLETAS';

-- 2. Recriar CHECK constraint com os novos valores
ALTER TABLE ocorrencias DROP CONSTRAINT ck_ocor_situacao;
ALTER TABLE ocorrencias ADD CONSTRAINT ck_ocor_situacao CHECK (situacao IN (
    'DEVOLUCAO_TOTAL', 'DEVOLUCAO_PARCIAL', 'INVERSAO_MERCADORIA',
    'SOBRA', 'AVARIA', 'COLETA'
));

COMMIT;
