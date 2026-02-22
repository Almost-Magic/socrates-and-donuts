import { create } from 'zustand';

interface AppState {
  isCrisisMode: boolean;
  setCrisisMode: (value: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isCrisisMode: false,
  setCrisisMode: (value) => set({ isCrisisMode: value }),
}));
