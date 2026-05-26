-- Migration 09: corrige check constraint CK_OCOR_TIPO após renomeação das colunas
-- Executar como usuário gestao_sac

-- Remove constraint antiga (criada para a coluna que agora se chama tipo_ocorrencia, antes chamada impacto)
ALTER TABLE gestao_sac.ocorrencias DROP CONSTRAINT CK_OCOR_TIPO;

-- Recria com os valores corretos para tipo_ocorrencia (DEVOLUCAO_TOTAL, DEVOLUCAO_PARCIAL, REENVIO, REPOSICAO)
ALTER TABLE gestao_sac.ocorrencias ADD CONSTRAINT CK_OCOR_TIPO CHECK (
    tipo_ocorrencia IN ('DEVOLUCAO_TOTAL', 'DEVOLUCAO_PARCIAL', 'REENVIO', 'REPOSICAO')
);

-- Adiciona constraint para motivo (antigo tipo_ocorrencia)
ALTER TABLE gestao_sac.ocorrencias ADD CONSTRAINT CK_OCOR_MOTIVO CHECK (
    motivo IN (
        'AVARIA', 'INVERSAO_MERCADORIA', 'FALTA_MERCADORIA', 'SOBRA_MERCADORIA',
        'DEVOLUCAO_SOLICITADA', 'PEDIDO_TROCA', 'EXTRAVIO', 'ATRASO_ENTREGA',
        'PEDIDO_DUPLICADO', 'PEDIDO_DESACORDO', 'OUTRO'
    )
);

COMMIT;
