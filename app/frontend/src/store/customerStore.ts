import type { ICustomerItem } from 'src/types/customer';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

import axios, { endpoints } from 'src/lib/axios';

import { JWT_STORAGE_KEY } from 'src/auth/context/jwt';

type CustomerState = {
  customers: ICustomerItem[];
  loading: boolean;
  error: Error | null;
  setCustomers: (customers: ICustomerItem[]) => void;
  fetchCustomers: () => Promise<void>;
  addCustomer: (customer: ICustomerItem) => Promise<void>;
  editCustomer: (customer: ICustomerItem) => Promise<void>;
  deleteCustomer: (customer: ICustomerItem) => Promise<void>;
};

export const useCustomerStore = create<CustomerState>()(
  persist(
    (set) => ({
      customers: [],
      loading: false,
      error: null,
      setCustomers: (customers) => set({ customers }),
      fetchCustomers: async () => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          const response = await axios.get<ICustomerItem[]>(endpoints.customer.list, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          set({ customers: response.data, loading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to fetch customers');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
      addCustomer: async (customer) => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          const response = await axios.post(endpoints.customer.create, customer, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          set((state) => ({
            customers: [...state.customers, response.data],
            loading: false
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to create customer');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },

      editCustomer: async (customer) => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          await axios.put(`${endpoints.customer.update}${customer.id}`, customer, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          set((state) => ({
            customers: state.customers.map((c) =>
              c.id === customer.id ? { ...c, ...customer } : c
            ),
            loading: false
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to update customer');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },

      deleteCustomer: async (customer) => {
        try {
          set({ loading: true, error: null });
          const accessToken = sessionStorage.getItem(JWT_STORAGE_KEY);
          await axios.delete(`${endpoints.customer.delete}${customer.id}`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });
          set((state) => ({
            customers: state.customers.filter((c) => c.id !== customer.id),
            loading: false
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to delete customer');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      }

    }),
    {
      name: 'customer-storage', // Key for localStorage
      storage: createJSONStorage(() => localStorage), // Change to sessionStorage if needed
    }
  )
);
