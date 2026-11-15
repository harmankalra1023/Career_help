import { create } from "zustand";

interface UiState {
  isSidebarOpen: boolean;
  activeExplainId: string | null;
  toggleSidebar: () => void;
  setExplainId: (id: string | null) => void;
}

export const useUiStore = create<UiState>((set) => ({
  isSidebarOpen: false,
  activeExplainId: null,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setExplainId: (id) => set({ activeExplainId: id }),
}));
