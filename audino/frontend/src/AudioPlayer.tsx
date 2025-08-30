import React, { useRef, useState, useEffect } from 'react';
import { Box, IconButton, Slider } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';

interface AudioPlayerProps {
    url: string;
    duration: number;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ url, duration }) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const [playing, setPlaying] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (!audioRef.current) return;
        if (playing) {
            audioRef.current.play();
        } else {
            audioRef.current.pause();
        }
    }, [playing]);

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setProgress(audioRef.current.currentTime);
        }
    };

    const handleSliderChange = (_: any, value: number | number[]) => {
        if (audioRef.current) {
            const t = Array.isArray(value) ? value[0] : value;
            audioRef.current.currentTime = t;
            setProgress(t);
        }
    };

    return (
        <Box display="flex" alignItems="center" gap={2}>
            <IconButton onClick={() => setPlaying(p => !p)}>
                {playing ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
            <Slider
                min={0}
                max={duration}
                value={progress}
                step={0.01}
                onChange={handleSliderChange}
                sx={{ width: 300 }}
            />
            <audio
                ref={audioRef}
                src={url}
                onTimeUpdate={handleTimeUpdate}
                onEnded={() => setPlaying(false)}
                style={{ display: 'none' }}
            />
            <span>{progress.toFixed(1)} / {duration.toFixed(1)} s</span>
        </Box>
    );
};

export default AudioPlayer;
