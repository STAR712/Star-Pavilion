export interface FieldRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  message: string
  validate?: (value: string) => boolean | string
}

export interface FieldState {
  value: string
  error: string
  touched: boolean
}

export type FormSchema = Record<string, FieldRule[]>

export function useFormValidation(schema: FormSchema) {
  const fields: Record<string, FieldState> = {}

  // Initialize fields
  for (const key of Object.keys(schema)) {
    fields[key] = { value: '', error: '', touched: false }
  }

  function validateField(name: string): string {
    const rules = schema[name]
    if (!rules) return ''
    const field = fields[name]
    if (!field) return ''

    for (const rule of rules) {
      if (rule.required && !field.value.trim()) {
        return rule.message
      }
      if (rule.minLength && field.value.length < rule.minLength) {
        return rule.message
      }
      if (rule.maxLength && field.value.length > rule.maxLength) {
        return rule.message
      }
      if (rule.pattern && !rule.pattern.test(field.value)) {
        return rule.message
      }
      if (rule.validate) {
        const result = rule.validate(field.value)
        if (typeof result === 'string') return result
        if (result === false) return rule.message
      }
    }
    return ''
  }

  function validateAll(): boolean {
    let isValid = true
    for (const name of Object.keys(schema)) {
      fields[name].touched = true
      const error = validateField(name)
      fields[name].error = error
      if (error) isValid = false
    }
    return isValid
  }

  function touchField(name: string) {
    if (fields[name]) {
      fields[name].touched = true
      fields[name].error = validateField(name)
    }
  }

  function getField(name: string): FieldState {
    return fields[name]
  }

  function reset() {
    for (const key of Object.keys(fields)) {
      fields[key] = { value: '', error: '', touched: false }
    }
  }

  return { fields, validateField, validateAll, touchField, getField, reset }
}
