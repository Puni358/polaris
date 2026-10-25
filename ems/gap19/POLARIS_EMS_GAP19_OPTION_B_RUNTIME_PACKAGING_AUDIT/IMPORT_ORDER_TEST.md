# Import Order Test Results

1. **Order A (`scipy` then `highspy`)**:
   - `import scipy.optimize` $\to$ `import highspy` $\implies$ **SUCCESS (PASS)**
2. **Order B (`highspy` then `scipy`)**:
   - `import highspy` $\to$ `import scipy.optimize` $\implies$ **SUCCESS (PASS)**

```text
SCIPY_HIGHSPY_IMPORT_ORDER = PASS
```
