"use client";

import { useState } from 'react';

import Box from '@mui/material/Box';
import List from '@mui/material/List';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import ListItem from '@mui/material/ListItem';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import ListItemText from '@mui/material/ListItemText';

import { DashboardContent } from 'src/layouts/dashboard';

import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------

export default function Page() {
  const [filter, setFilter] = useState<string>('');
  const [retentionDays, setRetentionDays] = useState<number>(30);

  const sampleLogs = [
    { id: '1', ts: '2025-11-27T14:01:02Z', q: 'pricing for X', found: 3, latency: 42 },
    { id: '2', ts: '2025-11-27T14:05:12Z', q: 'how to reset password', found: 1, latency: 88 },
    { id: '3', ts: '2025-11-27T14:12:33Z', q: 'refund policy', found: 2, latency: 60 },
  ];

  const handleExport = () => {
    toast.success('Export started (demo)');
  };

  return (
    <DashboardContent>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Retrieval Logs
      </Typography>

      <Grid container spacing={3}>
        <Grid sx={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField label="Filter" value={filter} onChange={(e) => setFilter(e.target.value)} />
              <TextField
                label="Retention (days)"
                type="number"
                value={retentionDays}
                onChange={(e) => setRetentionDays(Number(e.target.value))}
                sx={{ width: 160 }}
              />
              <Button variant="contained" onClick={handleExport}>
                Export
              </Button>
            </Box>

            <List>
              {sampleLogs
                .filter((l) => l.q.includes(filter))
                .map((l) => (
                  <ListItem key={l.id} divider>
                    <ListItemText primary={`${l.q}`} secondary={`ts: ${l.ts} • found: ${l.found} • ${l.latency}ms`} />
                  </ListItem>
                ))}
            </List>

            <Typography variant="caption" sx={{ color: 'text.secondary', mt: 2 }}>
              Tip: Use Azure Monitor or Diagnostic settings to capture and forward retrieval logs to Log
              Analytics for deeper analysis.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
