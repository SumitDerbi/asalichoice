import { describe, expect, it } from 'vitest';
import { cn } from '@/lib/utils';

describe('cn', () => {
  it('merges tailwind classes, last-wins on conflicts', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4');
    const hidden: string | false = false;
    expect(cn('text-sm', hidden && 'hidden', 'font-medium')).toBe('text-sm font-medium');
  });
});
