# BioSonic Frontend

React + Vite dashboard for the BioSonic passive wildlife monitoring demo.

## Local Run

```bash
cd /home/nitir505/Ritin/hashhacks/BioSonic/frontend
npm install
npm run dev -- --host 127.0.0.1
```

## Production Build

```bash
npm run build
```

## Vercel Deploy

This app is ready to deploy on Vercel as a static Vite site.

### Option 1: Vercel Dashboard

1. Import the repository into Vercel.
2. Set the Root Directory to `BioSonic/frontend`.
3. Vercel should auto-detect:
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Deploy.

### Option 2: Vercel CLI

```bash
cd /home/nitir505/Ritin/hashhacks/BioSonic/frontend
npm install -g vercel
vercel
```

For production deployment:

```bash
vercel --prod
```

## Notes

- `vercel.json` includes an SPA rewrite to `index.html`.
- If you deploy from the repo root instead of `BioSonic/frontend`, Vercel will not find the correct `package.json` unless you set the Root Directory properly.
