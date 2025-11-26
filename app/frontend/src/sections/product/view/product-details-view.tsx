'use client';

import type { ILeaveItem2 } from 'src/types/product';

import { useState, useEffect, useCallback } from 'react';

import Grid from '@mui/material/Grid2';

import { paths } from 'src/routes/paths';

import { PRODUCT_PUBLISH_OPTIONS } from 'src/_mock';
import { DashboardContent } from 'src/layouts/dashboard';

import { useAuthContext } from 'src/auth/hooks';

import { ProductDetailsSummary } from '../product-details-summary';
import { ProductDetailsToolbar } from '../product-details-toolbar';

// ----------------------------------------------------------------------

type Props = {
  product?: ILeaveItem2;
};

export function ProductDetailsView({ product }: Props) {

  const [publish, setPublish] = useState('');
  const { user } = useAuthContext();
  const disableActions = user?.role === 'admin';

  useEffect(() => {
    if (product) {
      setPublish(product?.leave_type);
    }
  }, [product]);

  const handleChangePublish = useCallback((newValue: string) => {
    setPublish(newValue);
  }, []);

  return (
    <DashboardContent>
      <ProductDetailsToolbar
        backHref={paths.dashboard.leave.root}
        liveHref={paths.leave.details(`${product?.id}`)}
        editHref={paths.dashboard.leave.edit(`${product?.id}`)}
        publish={publish}
        onChangePublish={handleChangePublish}
        publishOptions={PRODUCT_PUBLISH_OPTIONS}
      />

      <Grid container spacing={{ xs: 3, md: 12 }}>
        <Grid size={{ xs: 12, md: 12 }}>
          {product && <ProductDetailsSummary disableActions={disableActions} product={product} user={user} />}
        </Grid>
      </Grid>


    </DashboardContent>
  );
}
