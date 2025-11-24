import type { IUserItem } from 'src/types/user';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

import { _userList } from 'src/_mock';

export type UserState = {
  users: IUserItem[];
  loading: boolean;
  error: Error | null;
  setUsers: (users: IUserItem[]) => void;
  fetchUsers: () => Promise<void>;
  editUser: (user: IUserItem) => Promise<void>;
  deleteUser: (user: IUserItem) => Promise<void>;
};

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      users: [],
      loading: false,
      error: null,
      setUsers: (users) => set({ users }),
      fetchUsers: async () => {
        try {
          set({ loading: true, error: null });
          await new Promise((resolve) => setTimeout(resolve, 400));
          set({ users: _userList, loading: false });
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to fetch users');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
      editUser: async (user) => {
        try {
          set({ loading: true, error: null });
          await new Promise((resolve) => setTimeout(resolve, 400));
          set((state) => ({
            users: state.users.map((u) => (u.id === user.id ? { ...u, ...user } : u)),
            loading: false,
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to update user');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
      deleteUser: async (user) => {
        try {
          set({ loading: true, error: null });
          await new Promise((resolve) => setTimeout(resolve, 400));
          set((state) => ({
            users: state.users.filter((u) => u.id !== user.id),
            loading: false,
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error : new Error('Failed to delete user');
          set({ error: errorMessage, loading: false });
          throw errorMessage;
        }
      },
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
