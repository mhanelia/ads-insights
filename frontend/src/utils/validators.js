/**
 * Utilitários para validação
 */

/**
 * Valida se o arquivo é um CSV
 */
export function isValidCSVFile(file) {
  if (!file) return false;
  
  const validTypes = [
    'text/csv',
    'application/csv',
    'application/vnd.ms-excel',
    'text/plain'
  ];
  
  const validExtensions = ['.csv'];
  
  const hasValidType = validTypes.includes(file.type);
  const hasValidExtension = validExtensions.some(ext => 
    file.name.toLowerCase().endsWith(ext)
  );
  
  return hasValidType || hasValidExtension;
}

/**
 * Valida o tamanho do arquivo (máximo 10MB)
 */
export function isValidFileSize(file, maxSizeMB = 10) {
  if (!file) return false;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
}

/**
 * Extrai mensagens de erro da resposta da API
 */
export function extractValidationErrors(error) {
  if (!error.response) {
    return ['Erro ao conectar com o servidor'];
  }

  const { status, data } = error.response;

  if (status === 400 && data?.validation_result?.errors) {
    return data.validation_result.errors.map(err => 
      `${err.field}: ${err.message}`
    );
  }

  if (status === 422) {
    return [data?.detail || 'Arquivo CSV inválido'];
  }

  if (status === 500) {
    return ['Erro interno do servidor. Tente novamente mais tarde.'];
  }

  return [data?.detail || 'Erro desconhecido'];
}
