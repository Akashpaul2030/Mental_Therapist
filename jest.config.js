module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/tests/frontend', '<rootDir>/tests'],
  // You might want to specify testMatch if you have tests in multiple places
  // or with different naming conventions. Default is usually fine for files ending in .test.js or .spec.js:
  // testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[tj]s?(x)'],
  // If your static/script.js uses ES6 modules and you encounter syntax errors,
  // you might need to configure Babel for Jest. For now, we assume Vanilla JS
  // compatible with Node's execution in JSDOM.
}; 