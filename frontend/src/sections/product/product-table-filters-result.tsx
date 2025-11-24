import type { ILeaveTableFilters } from 'src/types/product';
import type { UseSetStateReturn } from 'minimal-shared/hooks';
import type { FiltersResultProps } from 'src/components/filters-result';

import { useCallback } from 'react';
import { upperFirst } from 'es-toolkit';

import Chip from '@mui/material/Chip';

import { chipProps, FiltersBlock, FiltersResult } from 'src/components/filters-result';

// ----------------------------------------------------------------------

type Props = FiltersResultProps & {
  filters: UseSetStateReturn<ILeaveTableFilters>;
};

export function ProductTableFiltersResult({ filters, totalResults, sx }: Props) {
  const { state: currentFilters, setState: updateFilters, resetState: resetFilters } = filters;

  const handleRemoveStock = useCallback(
    (inputValue: string) => {
      const newValue = currentFilters.status.filter((item) => item !== inputValue);

      updateFilters({ status: newValue });
    },
    [updateFilters, currentFilters.status]
  );

  const handleRemovePublish = useCallback(
    (inputValue: string) => {
      const newValue = currentFilters.leave_type.filter((item) => item !== inputValue);

      updateFilters({ leave_type: newValue });
    },
    [updateFilters, currentFilters.leave_type]
  );

  return (
    <FiltersResult totalResults={totalResults} onReset={() => resetFilters()} sx={sx}>
      <FiltersBlock label="Status:" isShow={!!currentFilters.status.length}>
        {currentFilters.status.map((item) => (
          <Chip
            {...chipProps}
            key={item}
            label={upperFirst(item)}
            onDelete={() => handleRemoveStock(item)}
          />
        ))}
      </FiltersBlock>

      <FiltersBlock label="Leave Type:" isShow={!!currentFilters.leave_type.length}>
        {currentFilters.leave_type.map((item) => (
          <Chip
            {...chipProps}
            key={item}
            label={upperFirst(item)}
            onDelete={() => handleRemovePublish(item)}
          />
        ))}
      </FiltersBlock>
    </FiltersResult>
  );
}
