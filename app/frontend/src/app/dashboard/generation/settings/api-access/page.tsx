'use client';

// import type { Metadata } from 'next';

import { useState } from 'react';

import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

import { DashboardContent } from 'src/layouts/dashboard';

import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------
;

export default function Page() {
  const [tenantId, setTenantId] = useState<string>('');
  const [clientId, setClientId] = useState<string>('');
  const [clientSecretHint] = useState<string>('•••••••• (rotate via Azure portal)');

  const handleRotate = () => {
    toast.info('Rotate client secret (demo)');
  };

  return (
    <DashboardContent>
      <Typography variant="h5" sx={{ mb: 2 }}>
        API & Access
      </Typography>

      <Grid container spacing={3}>
        <Grid sx={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1">Azure AD / App Registration</Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Configure the Azure AD application used for server-to-server authentication. You can use
              managed identities or an App Registration. For production, prefer managed identities
              where possible.
            </Typography>

            <Box sx={{ display: 'grid', gap: 2, mb: 2 }}>
              <TextField
                fullWidth
                label="Tenant ID"
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
              />

              <TextField fullWidth label="Client ID" value={clientId} onChange={(e) => setClientId(e.target.value)} />

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TextField fullWidth label="Client Secret" value={clientSecretHint} disabled />
                <Button variant="outlined" onClick={handleRotate}>
                  Rotate
                </Button>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2">Ingress / Network</Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              Restrict which IPs or VNets can call your retriever API. When running in Azure, combine
              this with Private Endpoints and Service Endpoints for tighter network control.
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
              <Button variant="contained" onClick={() => toast.info('Save (demo)')}>
                Save
              </Button>
              <Button variant="outlined" href="https://portal.azure.com">
                Open Azure Portal
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
