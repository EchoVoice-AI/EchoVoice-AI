"use client";

import { useState } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

import { DashboardContent } from 'src/layouts/dashboard';

import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------

export default function Page() {
  const [status] = useState<'Idle' | 'Running' | 'Failed'>('Idle');
  const [lastRun] = useState<string>('2025-11-27 14:02:11 UTC');
  const [nextRun] = useState<string>('2025-11-28 02:00:00 UTC');
  const [errors] = useState<number>(0);

  const handleRunNow = () => {
    toast.info('Indexer run triggered (demo)');
  };

  return (
    <DashboardContent>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Indexing Status
      </Typography>

      <Grid container spacing={3}>
        <Grid sx={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1">Indexer</Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Overview of the document ingestion & indexer that powers retrieval. This reflects the
              indexer referenced in docs/data_ingestion.md and the ingestion architecture.
            </Typography>

            <Box sx={{ display: 'grid', gap: 1, mb: 2 }}>
              <Typography>Current status: <strong>{status}</strong></Typography>
              <Typography>Last run: {lastRun}</Typography>
              <Typography>Next scheduled run: {nextRun}</Typography>
              <Typography>Recent errors: {errors}</Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" onClick={handleRunNow}>
                Run now
              </Button>
              <Button variant="outlined" href="/docs/data_ingestion.md">
                View ingestion docs
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
