import { describe, expect, it } from 'vitest';
import { ApiError } from '@/lib/api/errors';
import { mapApiErrorToFields } from '@/lib/forms';

describe('master API error mapping', () => {
  it('maps MST-* envelope details to known fields', () => {
    const err = new ApiError(
      {
        code: 'MST-013',
        message: 'Validation failed.',
        details: { fields: { code: 'Code is required.', name: 'Name is required.' } },
      },
      400,
    );
    const mapped = mapApiErrorToFields(err, { knownFields: ['code', 'name'] });
    expect(mapped.fields).toMatchObject({
      code: 'Code is required.',
      name: 'Name is required.',
    });
  });

  it('falls back to formMessage when no field details are present', () => {
    const err = new ApiError({ code: 'MST-099', message: 'Unexpected branch error.' }, 400);
    const mapped = mapApiErrorToFields(err, { knownFields: ['code'] });
    expect(mapped.fields).toEqual({});
    expect(mapped.formMessage).toBe('Unexpected branch error.');
  });
});
