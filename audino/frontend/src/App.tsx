import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, Select, MenuItem, CircularProgress } from '@mui/material';
import Plot from 'react-plotly.js';
import AudioPlayer from './AudioPlayer';

interface AudioFile {
    filename: string;
    samplerate: number;
    duration: number;
    waveform: number[];
}

const API_URL = 'http://localhost:8000';

function App() {
    const [files, setFiles] = useState<string[]>([]);
    const [selected, setSelected] = useState<string>('');
    const [audio, setAudio] = useState<AudioFile | null>(null);
    const [loading, setLoading] = useState(false);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(`${API_URL}/files`)
            .then(res => res.json())
            .then(data => setFiles(data.files));
    }, []);

    useEffect(() => {
        if (selected) {
            setLoading(true);
            setError(null);
            fetch(`${API_URL}/file/${selected}`)
                .then(async res => {
                    if (!res.ok) {
                        const err = await res.json().catch(() => ({}));
                        throw new Error(err.detail || 'Failed to load file');
                    }
                    return res.json();
                })
                .then(data => {
                    setAudio(data);
                    setLoading(false);
                })
                .catch(e => {
                    setError(e.message);
                    setAudio(null);
                    setLoading(false);
                });
            // Fetch audio as blob for playback
            fetch(`${API_URL}/file/${selected}?raw=1`)
                .then(res => res.blob())
                .then(blob => {
                    setAudioUrl(URL.createObjectURL(blob));
                });
        }
    }, [selected]);

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>Audino: Audio Explorer</Typography>
            <Box mb={2}>
                <Select
                    value={selected}
                    onChange={e => setSelected(e.target.value)}
                    displayEmpty
                    fullWidth
                >
                    <MenuItem value="" disabled>Select an audio file</MenuItem>
                    {files.map(f => (
                        <MenuItem key={f} value={f}>{f}</MenuItem>
                    ))}
                </Select>
            </Box>
            {loading && <CircularProgress />}
            {error && (
                <Box color="error.main" mb={2}>
                    <Typography color="error">{error}</Typography>
                </Box>
            )}
            {audio && !loading && audio.duration !== undefined && (
                <Box>
                    <Typography variant="subtitle1">
                        {audio.filename} — {audio.samplerate} Hz — {audio.duration.toFixed(2)} s
                    </Typography>
                    <Plot
                        data={[
                            {
                                y: audio.waveform,
                                type: 'scatter',
                                mode: 'lines',
                                line: { color: '#1976d2' },
                            },
                        ]}
                        layout={{
                            width: 800,
                            height: 300,
                            margin: { t: 30, l: 40, r: 20, b: 40 },
                            xaxis: { title: 'Sample' },
                            yaxis: { title: 'Amplitude' },
                            title: 'Waveform',
                        }}
                        config={{ displayModeBar: false }}
                    />
                    {audioUrl && (
                        <AudioPlayer url={audioUrl} duration={audio.duration} />
                    )}
                </Box>
            )}
        </Container>
    );
}

export default App;
