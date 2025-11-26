import type { ILeaveItem2 } from 'src/types/product';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type DashState = {
    leave_requests: ILeaveItem2[];
    setLeaveRequests: (leave_requests: ILeaveItem2[]) => void;
};

export const useDashStore = create<DashState>()(
    persist(
        (set) => ({
            token: null,
            leave_requests: [],
            setLeaveRequests: (leave_requests) => set({ leave_requests }),
        }),
        {
            name: 'dash-storage', // Key for localStorage
            storage: createJSONStorage(() => localStorage), // Change to sessionStorage if needed
        }
    )
);
