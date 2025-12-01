import type { IPackageItem } from 'src/types/package';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

import { _packages } from 'src/_mock/_package';
import axios, { endpoints } from 'src/lib/axios';

import { JWT_STORAGE_KEY } from 'src/auth/context/jwt';

// Define the state and actions for the package store
export type PackageState = {
  packages: IPackageItem[];
  loading: boolean;
  error: Error | null;
  setPackages: (packages: IPackageItem[]) => void;
  fetchPackages: () => Promise<void>;
  editPackage: (pkg: IPackageItem) => Promise<void>;
  deletePackage: (pkg: IPackageItem) => Promise<void>;
};

export const usePackageStore = create<PackageState>()(
  persist(
    (set) => ({
      packages: [],
      loading: false,
      error: null,
      setPackages: (packages) => set({ packages }),
      fetchPackages: async () => {
        try {
          set({ loading: true, error: null });
        //   const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
        //   const response = await axios.get(endpoints.package.list, {
        //     headers: {
        //       Authorization: `Bearer ${accessToken}`,
        //       'Content-Type': 'application/json',
        //     },
        //   });
          // Simulate API delay
          await new Promise((resolve) => setTimeout(resolve, 400));
          set({ packages: _packages, loading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to fetch packages');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
      editPackage: async (pkg) => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          await axios.put(`${endpoints.package.update}${pkg.id}`, pkg, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            },
          });
          set((state) => ({
            packages: state.packages.map((p) => (p.id === pkg.id ? { ...p, ...pkg } : p)),
            loading: false,
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to update package');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
      deletePackage: async (pkg) => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          await axios.delete(`${endpoints.package.delete}${pkg.id}`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json',
            },
          });
          set((state) => ({
            packages: state.packages.filter((p) => p.id !== pkg.id),
            loading: false,
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to delete package');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
    }),
    {
      name: 'package-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
