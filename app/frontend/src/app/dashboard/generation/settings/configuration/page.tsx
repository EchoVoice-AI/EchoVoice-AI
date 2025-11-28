"use client";

import { useState } from "react";
import { usePopover } from "minimal-shared/hooks";

import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Grid from "@mui/material/Grid2";
import Paper from "@mui/material/Paper";
import Switch from "@mui/material/Switch";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import FormControlLabel from "@mui/material/FormControlLabel";

import { DashboardContent } from "src/layouts/dashboard";

import { toast } from "src/components/snackbar";
import { Iconify } from "src/components/iconify";
import { CustomPopover } from "src/components/custom-popover/custom-popover";

// --------------------------------------------------------

function FeatureRow({
  opt,
  hasToggle,
  checked,
  onToggle,
}: {
  opt: { key: string; label: string; desc: string };
  hasToggle?: boolean;
  checked?: boolean;
  onToggle?: (v: boolean) => void;
}) {
  const pop = usePopover();
  return (
    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 2 }}>
      <Typography sx={{ flex: 1 }}>{opt.label}</Typography>

      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <IconButton size="small" onClick={pop.onOpen} aria-label={`${opt.key}-info`}>
          <Iconify icon="eva:info-fill" />
        </IconButton>

        {hasToggle && (
          <Switch
            size="small"
            checked={!!checked}
            onChange={(e) => onToggle && onToggle(e.target.checked)}
            inputProps={{ 'aria-label': `${opt.key}-toggle` }}
          />
        )}
      </Box>

      <CustomPopover
        open={pop.open}
        onClose={pop.onClose}
        anchorEl={pop.anchorEl}
        slotProps={{ arrow: { placement: "top-right", offset: 16 } }}
      >
        <Box sx={{ p: 2, maxWidth: 320 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            {opt.label}
          </Typography>
          <Typography variant="body2" sx={{ color: "text.secondary" }}>
            {opt.desc}
          </Typography>
        </Box>
      </CustomPopover>
    </Box>
  );
}

// --------------------------------------------------------

export default function Page() {
  const [queryRewrite, setQueryRewrite] = useState(true);
  const [retrievalMode, setRetrievalMode] = useState("hybrid");
  const [indexer, setIndexer] = useState("default-indexer");
  const [textEmbeddingsEnabled, setTextEmbeddingsEnabled] = useState(true);
  const [embeddingsEnabled, setEmbeddingsEnabled] = useState(true);
  const [allowOidsEnabled, setAllowOidsEnabled] = useState(false);
  const [allowGOidsEnabled, setAllowGOidsEnabled] = useState(false);

  const handleSave = () => {
    toast.success("Retriever configuration saved (demo)");
  };

  return (
    <DashboardContent>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Retriever Configuration
      </Typography>

      <Grid container spacing={3}>
        <Grid sx={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 3 }}>
            {/* Query Rewriting */}
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Query Rewriting
            </Typography>

            <Typography variant="body2" sx={{ color: "text.secondary", mb: 2 }}>
              Toggle model-assisted query rewriting to normalize or expand user
              queries before performing retrieval.
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={queryRewrite}
                  onChange={(e) => setQueryRewrite(e.target.checked)}
                />
              }
              label={queryRewrite ? "Enabled" : "Disabled"}
            />

            {/* Feature Rows */}
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Embedding Features
              </Typography>

              <Box sx={{ display: "grid", gap: 2, mb: 2 }}>
                {[
                  {
                    key: "text-embeddings",
                    label: "Text embeddings",
                    desc: "Generate vector embeddings from text using the chosen model.",
                  },
                  {
                    key: "embeddings",
                    label: "Embeddings (general)",
                    desc: "Use precomputed embeddings or on-the-fly embeddings.",
                  },
                  {
                    key: "image-embeddings",
                    label: "Image embeddings",
                    desc: "Create embeddings from images for multimodal retrieval.",
                  },
                ].map((opt) => {
                  if (opt.key === "text-embeddings") {
                    return (
                      <FeatureRow
                        key={opt.key}
                        opt={opt}
                        hasToggle
                        checked={textEmbeddingsEnabled}
                        onToggle={(v) => setTextEmbeddingsEnabled(v)}
                      />
                    );
                  }

                  if (opt.key === "embeddings") {
                    return (
                      <FeatureRow
                        key={opt.key}
                        opt={opt}
                        hasToggle
                        checked={embeddingsEnabled}
                        onToggle={(v) => setEmbeddingsEnabled(v)}
                      />
                    );
                  }

                  return <FeatureRow key={opt.key} opt={opt} />;
                })}
              </Box>

              {/* Retrival Mode */}
              <TextField
                fullWidth
                select
                SelectProps={{ native: true }}
                label="Retrieval Mode"
                value={retrievalMode}
                onChange={(e) => setRetrievalMode(e.target.value)}
                sx={{ mb: 2 }}
              >
                <option value="vector">Vector Search </option>
                <option value="hybrid">Hybrid (Vector + Text)</option>
                <option value="bm25">Text</option>
              </TextField>

              {/* Indexer */}
              <TextField
                fullWidth
                label="Indexer"
                value={indexer}
                onChange={(e) => setIndexer(e.target.value)}
                sx={{ mb: 2 }}
                disabled
              />

              {/* Allowed OIDs (toggle + conditional input) */}
              <FeatureRow
                opt={{
                  key: "allowed-oids",
                  label: "Use OID security filter",
                  desc:
                    "When enabled, retrieval will be restricted to users in the listed Azure Entra ID OIDs .",
                }}
                hasToggle
                checked={allowOidsEnabled}
                onToggle={(v) => setAllowOidsEnabled(v)}
              />
              <FeatureRow
                opt={{
                  key: "allowed-oids",
                  label: "Use Group security filter",
                  desc:
                    "When enabled, retrieval will be restricted to groups in the listed Azure Entra ID Group IDs",
                }}
                hasToggle
                checked={allowGOidsEnabled}
                onToggle={(v) => setAllowGOidsEnabled(v)}
              />


              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: 2 }}>
                <Link sx={{ alignSelf: "center" }} href="/dashboard/data-sources">
                  Data ingestion docs
                </Link>

                <Box sx={{ display: "flex", gap: 2 }}>
                  <Button variant="contained" onClick={handleSave}>
                    Save
                  </Button>

                  <Button
                    variant="outlined"
                    onClick={() => toast.info("Reset (demo)")}
                  >
                    Reset
                  </Button>
                </Box>
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid sx={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Help & Docs
            </Typography>

            <Typography variant="body2" sx={{ color: "text.secondary", mb: 2 }}>
              Quick links and notes for configuring retrievers. Use OID or Group filters to restrict retrieval to specific Azure Entra identities.
            </Typography>

            <Link href="/coming-soon">Data ingestion docs</Link>
            <br />
            <Link href="/coming-soon">Monitoring guide</Link>
          </Paper>
        </Grid>
      </Grid>
    </DashboardContent>
  );
}
