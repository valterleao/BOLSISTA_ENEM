type Props = {
  open: boolean;
  logs: string[];
  onClose: () => void;
};

export default function ExecutionLogModal({ open, logs, onClose }: Props) {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal-panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="log-modal-title"
        aria-modal="true"
      >
        <div className="modal-header">
          <h2 id="log-modal-title">Log de execucao</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Fechar">
            x
          </button>
        </div>
        <div className="modal-body log-modal-body">
          {logs.length === 0 ? (
            <p className="log-empty">Nenhum log registrado ainda. Execute a selecao para gerar logs.</p>
          ) : (
            logs.map((line, i) => (
              <div key={i} className="log-line">
                {line}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
