import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Branch {
  id: number;
  code: string;
  name: string;
}

interface BranchState {
  branches: Branch[];
  currentBranchId: number | null;
  setCurrentBranchId: (id: number | null) => void;
  setBranches: (branches: Branch[]) => void;
}

const DEFAULT_BRANCHES: Branch[] = [
  { id: 1, code: 'HQ', name: 'Head Office' },
  { id: 2, code: 'WH1', name: 'Warehouse 1' },
];

export const useBranchStore = create<BranchState>()(
  persist(
    (set) => ({
      branches: DEFAULT_BRANCHES,
      currentBranchId: DEFAULT_BRANCHES[0].id,
      setCurrentBranchId: (id) => set({ currentBranchId: id }),
      setBranches: (branches) => set({ branches }),
    }),
    { name: 'asalichoice.branch.v1' },
  ),
);

export function currentBranch(state: BranchState): Branch | null {
  return state.branches.find((b) => b.id === state.currentBranchId) ?? null;
}
