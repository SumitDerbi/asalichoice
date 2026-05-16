import { describe, expect, it, vi, afterEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { Toaster } from 'sonner';
import { InlineEditCell } from '@/lib/forms/inline-edit';
import { ApiError } from '@/lib/api/errors';

afterEach(() => {
  vi.restoreAllMocks();
});

function setup(value: string, onCommit: (next: string) => Promise<unknown>) {
  return render(
    <>
      <Toaster />
      <table>
        <tbody>
          <tr>
            <td>
              <InlineEditCell value={value} name="sku" onCommit={onCommit} />
            </td>
          </tr>
        </tbody>
      </table>
    </>,
  );
}

describe('InlineEditCell', () => {
  it('renders the persisted value as a button in read mode', () => {
    setup('ABC-1', vi.fn().mockResolvedValue(undefined));
    expect(screen.getByRole('button', { name: /edit sku/i })).toHaveTextContent('ABC-1');
  });

  it('commits the new value on blur (happy path)', async () => {
    const onCommit = vi.fn().mockResolvedValue({ ok: true });
    setup('ABC-1', onCommit);

    fireEvent.click(screen.getByRole('button', { name: /edit sku/i }));
    const input = screen.getByRole('textbox') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'ABC-2' } });
    fireEvent.blur(input);

    await waitFor(() => expect(onCommit).toHaveBeenCalledWith('ABC-2'));
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /edit sku/i })).toHaveTextContent('ABC-2'),
    );
  });

  it('rolls back on a rejected commit', async () => {
    const onCommit = vi
      .fn()
      .mockRejectedValueOnce(new ApiError({ code: 'API-400', message: 'Bad value.' }, 400));
    setup('ABC-1', onCommit);

    fireEvent.click(screen.getByRole('button', { name: /edit sku/i }));
    const input = screen.getByRole('textbox') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'ABC-2' } });
    fireEvent.blur(input);

    await waitFor(() => expect(onCommit).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /edit sku/i })).toHaveTextContent('ABC-1'),
    );
  });

  it('cancels editing on Escape without committing', async () => {
    const onCommit = vi.fn().mockResolvedValue(undefined);
    setup('ABC-1', onCommit);

    fireEvent.click(screen.getByRole('button', { name: /edit sku/i }));
    const input = screen.getByRole('textbox') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'ABC-2' } });
    fireEvent.keyDown(input, { key: 'Escape' });

    expect(onCommit).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: /edit sku/i })).toHaveTextContent('ABC-1');
  });
});
