import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid2';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';

import { toast } from 'src/components/snackbar';

// ----------------------------------------------------------------------

// Display-only component for retriever general status

// ----------------------------------------------------------------------


type RetrieverGeneralProps = {
  retriever?: any;
};

export function RetrieverGeneral({ retriever }: RetrieverGeneralProps) {
  const r = retriever ?? {};

  const boolLabel = (v?: boolean) => (v ? 'Enabled' : 'Disabled');
  const colorLabel = (v?: boolean) => (v ? 'success' : 'default');

  return (
    <Grid container spacing={3}>
      <Grid sx={{xs:12, md:4}}>
        <Card sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Retriever Summary
          </Typography>

          <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
            Read-only status for this retriever. For configuration changes, use the other tabs.
          </Typography>

          <Box sx={{ display: 'grid', gap: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Query rewrite</Typography>
              <Chip size="small" label={boolLabel(r.queryRewrite)} color={colorLabel(r.queryRewrite)} />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">OID security filter</Typography>
              <Chip size="small" label={boolLabel(r.useOidFilter)} color={colorLabel(r.useOidFilter)} />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Group security filter</Typography>
              <Chip size="small" label={boolLabel(r.useGroupFilter)} color={colorLabel(r.useGroupFilter)} />
            </Box>
          </Box>

          <Box sx={{ mt: 2 }}>
            <Button variant="outlined" onClick={() => toast.info('Run diagnostic (demo)')}>
              Run diagnostic
            </Button>
          </Box>
        </Card>
      </Grid>

      <Grid sx={{ xs: 12, md: 8 }}>
        <Card sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Retriever Details
          </Typography>

          <Box sx={{ display: 'grid', rowGap: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Name</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>{r.name ?? '-'}</Typography>
            </Box>

            <Divider />

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Retrieval mode</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>{r.retrievalMode ?? '-'}</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Indexer</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>{r.indexer ?? '-'}</Typography>
            </Box>

            <Divider />

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Text embeddings</Typography>
              <Chip size="small" label={boolLabel(r.textEmbeddings)} color={colorLabel(r.textEmbeddings)} />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Embeddings (general)</Typography>
              <Chip size="small" label={boolLabel(r.embeddings)} color={colorLabel(r.embeddings)} />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Image embeddings</Typography>
              <Chip size="small" label={boolLabel(r.imageEmbeddings)} color={colorLabel(r.imageEmbeddings)} />
            </Box>

            <Divider />

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Allowed OIDs</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: 300, textAlign: 'right' }}>{r.allowedOids || '-'}</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Allowed Groups</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: 300, textAlign: 'right' }}>{r.allowedGroups || '-'}</Typography>
            </Box>

            <Divider />

            <Box>
              <Typography variant="body2">Description</Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mt: 1 }}>{r.description || '-'}</Typography>
            </Box>
          </Box>
        </Card>
      </Grid>
    </Grid>
  );
}
