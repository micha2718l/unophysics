export function getAudioUrl(filename: string): string {
    // Assumes backend serves raw audio at this endpoint
    return `http://localhost:8000/file/${filename}?raw=1`;
}
