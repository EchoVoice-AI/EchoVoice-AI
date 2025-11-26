import type { SWRConfiguration } from 'swr';
import type { ILeaveItem2, ILeaveBalance } from 'src/types/product';

import useSWR from 'swr';
import { useMemo } from 'react';

import { poster, putter, fetcher, deleter, endpoints } from 'src/lib/axios';

// ----------------------------------------------------------------------

const swrOptions: SWRConfiguration = {
  revalidateIfStale: false,
  revalidateOnFocus: false,
  revalidateOnReconnect: false,
};

// ----------------------------------------------------------------------



export function useGetProducts() {
  const url = endpoints.leave.list;

  const { data, isLoading, error, isValidating } = useSWR<ILeaveItem2[]>(url, fetcher, swrOptions);

  const memoizedValue = useMemo(
    () => ({
      products: data || [],
      productsLoading: isLoading,
      productsError: error,
      productsValidating: isValidating,
      productsEmpty: !isLoading && !isValidating && !data,
    }),
    [data, error, isLoading, isValidating]
  );

  return memoizedValue;
}

// ----------------------------------------------------------------------

interface ILeaveBalanceData {
  status: boolean;
  data: ILeaveBalance[];
}

export function useGetLeaveBalances() {
  const url = endpoints.leave.balances.list;

  const { data, isLoading, error, isValidating } = useSWR<ILeaveBalanceData>(url, fetcher, swrOptions);

  const memoizedValue = useMemo(
    () => ({
      balances: data?.data || [],
      balancesLoading: isLoading,
      balancesError: error,
      balancesValidating: isValidating,
      balancesEmpty: !isLoading && !isValidating && !data,
    }),
    [data, error, isLoading, isValidating]
  );

  return memoizedValue;
}

// ----------------------------------------------------------------------

type ProductData = {
  leave: ILeaveItem2;
};

export function useGetProduct(productId: string) {
  const url = productId ? [endpoints.leave.details, { params: { productId } }] : '';

  const { data, isLoading, error, isValidating } = useSWR<ProductData>(url, fetcher, swrOptions);

  const memoizedValue = useMemo(
    () => ({
      product: data?.leave,
      productLoading: isLoading,
      productError: error,
      productValidating: isValidating,
    }),
    [data?.leave, error, isLoading, isValidating]
  );

  return memoizedValue;
}

// ----------------------------------------------------------------------

type SearchResultsData = {
  results: ILeaveItem2[];
};

export function useSearchProducts(query: string) {
  const url = query ? [endpoints.leave.search, { params: { query } }] : '';

  const { data, isLoading, error, isValidating } = useSWR<SearchResultsData>(url, fetcher, {
    ...swrOptions,
    keepPreviousData: true,
  });

  const memoizedValue = useMemo(
    () => ({
      searchResults: data?.results || [],
      searchLoading: isLoading,
      searchError: error,
      searchValidating: isValidating,
      searchEmpty: !isLoading && !isValidating && !data?.results.length,
    }),
    [data?.results, error, isLoading, isValidating]
  );

  return memoizedValue;
}


export function createProduct(data: any) {
  return poster([endpoints.leave.create, {
    ...data,
  }]);
}

export function updateProduct(productId: string, data: any) {
  return putter([endpoints.leave.update, {
    ...data,
  }]);
}

export function deleteProduct(productId: string) {
  const URL = `${endpoints.leave.delete}/${productId}/`;
  return deleter(URL);
}
