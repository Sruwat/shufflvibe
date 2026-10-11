export const MAX_SECURE_STORE_CHUNK_BYTES = 1500;

function utf8Bytes(character: string) {
  const point = character.codePointAt(0) ?? 0;
  if (point <= 0x7f) return 1;
  if (point <= 0x7ff) return 2;
  if (point <= 0xffff) return 3;
  return 4;
}

export function splitSecureStoreValue(value: string, maxBytes = MAX_SECURE_STORE_CHUNK_BYTES) {
  if (!Number.isInteger(maxBytes) || maxBytes < 4) throw new RangeError('SecureStore chunk limit must be at least four bytes.');
  const chunks: string[] = [];
  let chunk = '';
  let chunkBytes = 0;

  for (const character of value) {
    const characterBytes = utf8Bytes(character);
    if (chunk && chunkBytes + characterBytes > maxBytes) {
      chunks.push(chunk);
      chunk = '';
      chunkBytes = 0;
    }
    chunk += character;
    chunkBytes += characterBytes;
  }

  if (chunk || chunks.length === 0) chunks.push(chunk);
  return chunks;
}
