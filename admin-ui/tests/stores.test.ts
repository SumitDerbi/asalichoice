import { describe, expect, it, beforeEach } from 'vitest';
import { useBranchStore } from '@/lib/branch/store';
import { useThemeStore, applyTheme } from '@/lib/theme/store';

describe('branch store', () => {
  beforeEach(() => {
    window.localStorage.clear();
    useBranchStore.setState({
      branches: [
        { id: 1, code: 'HQ', name: 'Head Office' },
        { id: 2, code: 'WH1', name: 'Warehouse 1' },
      ],
      currentBranchId: 1,
    });
  });

  it('switches current branch and persists it', () => {
    useBranchStore.getState().setCurrentBranchId(2);
    expect(useBranchStore.getState().currentBranchId).toBe(2);

    const raw = window.localStorage.getItem('asalichoice.branch.v1');
    expect(raw).toBeTruthy();
    expect(raw).toContain('"currentBranchId":2');
  });
});

describe('theme store', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.classList.remove('dark');
    useThemeStore.setState({ theme: 'light' });
  });

  it('toggles between light and dark and applies the dark class', () => {
    useThemeStore.getState().toggleTheme();
    expect(useThemeStore.getState().theme).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    useThemeStore.getState().toggleTheme();
    expect(useThemeStore.getState().theme).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('applyTheme honours the requested theme', () => {
    applyTheme('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    applyTheme('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });
});
