import type { ISegmentorCard } from 'src/types/segmentor';

import { useState, useEffect, useCallback } from 'react';

import Box from '@mui/material/Box';
import Pagination from '@mui/material/Pagination';

import { SegmentorCard } from './segment-card';

// ----------------------------------------------------------------------

type Props = {
  segments: ISegmentorCard[];
  onUpdate?: (segment: ISegmentorCard) => void;
};

export function SegmentorCardList({ segments, onUpdate }: Props) {
  // keep a local, mutable copy of the segments so demo-mode updates are visible
  const [localSegments, setLocalSegments] = useState<ISegmentorCard[]>(() => segments.slice());
  const [page, setPage] = useState(1);

  // keep local copy in sync when parent provides a new segments prop
  useEffect(() => {
    setLocalSegments(segments.slice());
  }, [segments]);

  const rowsPerPage = 12;

  const handleChangePage = useCallback((event: React.ChangeEvent<unknown>, newPage: number) => {
    setPage(newPage);
  }, []);

  return (
    <>
      <Box
        sx={{
          gap: 3,
          display: 'grid',
          gridTemplateColumns: { xs: 'repeat(1, 1fr)', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
        }}
      >
        {localSegments
          .slice((page - 1) * rowsPerPage, (page - 1) * rowsPerPage + rowsPerPage)
          .map((segment) => (
            <SegmentorCard
              key={segment.id}
              segment={segment}
              onUpdate={(updated) => {
                // update local state so UI reflects the change immediately
                setLocalSegments((prev) => prev.map((s) => (s.id === updated.id ? { ...s, ...updated } : s)));
                // forward to parent if provided
                if (onUpdate) onUpdate(updated);
              }}
            />
          ))}
      </Box>

      <Pagination
        page={page}
        shape="circular"
        count={Math.ceil(localSegments.length / rowsPerPage)}
        onChange={handleChangePage}
        sx={{ mt: { xs: 5, md: 8 }, mx: 'auto' }}
      />
    </>
  );
}
